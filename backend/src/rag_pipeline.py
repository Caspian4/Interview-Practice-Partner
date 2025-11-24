"""
RAG Pipeline with FAISS & HuggingFace Embeddings
Supports multi-turn conversational context.
"""

import PyPDF2
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import CharacterTextSplitter
from keybert import KeyBERT
from langchain_community.document_transformers import EmbeddingsRedundantFilter, LongContextReorder
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import DocumentCompressorPipeline

def load_vectorstore(faiss_dir: str = "data/vectordb",
                     emb_model: str = "sentence-transformers/all-mpnet-base-v2"):
    """Load FAISS vectorstore and return embeddings & base retriever."""
    embeddings = HuggingFaceEmbeddings(model_name=emb_model)
    db = FAISS.load_local(faiss_dir, embeddings=embeddings, allow_dangerous_deserialization=True)
    base_retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    return db, embeddings, base_retriever

def create_compression_retriever(embeddings, base_retriever, chunk_size=500, k=5, similarity_threshold=0.7):
    """Create a compression retriever."""
    splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0, separator=". ")
    
    redundant_filter = EmbeddingsRedundantFilter(embeddings=embeddings)
   
    relevant_filter = EmbeddingsFilter(embeddings=embeddings, k=k, similarity_threshold=similarity_threshold)
    
    reordering = LongContextReorder()
    
    compressor_pipeline = DocumentCompressorPipeline(
        transformers=[splitter, redundant_filter, relevant_filter, reordering]
    )
    
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor_pipeline,
        base_retriever=base_retriever
    )
    
    return compression_retriever


def create_rag_pipeline_with_memory(llm, retriever, prompt_template):
    """Create a RAG pipeline with conversation memory."""
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="question",
        output_key="answer",
        return_messages=True
    )

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt_template},
        return_source_documents=True,
        verbose=False,
        output_key="answer"
    )


def extract_text_from_pdf(file_path: str) -> str:
    """Extract full text from a PDF file."""
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def detect_role_from_resume(text: str) -> str:
    """Detect role from resume text."""
    text_lower = text.lower()

    if any(k in text_lower for k in ["python", "javascript", "developer", "engineer", "react", "backend"]):
        return "Software Engineer"
    if any(k in text_lower for k in ["sales", "crm", "leads", "negotiation", "quota","marketing"]):
        return "Sales Executive"

    return "General"

def add_resume_to_memory(rag_pipeline, pdf_path: str):
    """Split resume text into chunks and add to pipeline memory."""
    resume_text = extract_text_from_pdf(pdf_path)
    # Detect role
    detected_role = detect_role_from_resume(resume_text)
    # Save detected role into memory
    rag_pipeline.memory.chat_memory.add_user_message(
        f"DETECTED_JOB_ROLE: {detected_role}"
    )
    # Extract keywords for memory
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(resume_text, keyphrase_ngram_range=(1,2), stop_words='english', top_n=25)
    keywords_text = ", ".join([kw[0] for kw in keywords])

    rag_pipeline.memory.chat_memory.add_user_message(
        f"RESUME_KEYWORDS: {keywords_text}"
    )