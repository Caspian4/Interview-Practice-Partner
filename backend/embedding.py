"""
embedding.py
-----------------------

This module creates a persistent FAISS vector database from a directory
of knowledge base (`kb/`) text files.

Core Responsibilities:
    • Load and scan all `.txt` files from the configured KB directory.
    • Clean and normalize raw text documents.
    • Split long documents into overlapping chunks using
      `RecursiveCharacterTextSplitter`.
    • Embed all chunks using HuggingFace sentence-transformer embeddings
      (`all-mpnet-base-v2`).
    • Store the resulting vectors using FAISS inside
      `backend/data/vectordb/`.

"""

from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS

KB_DIR = Path(r"C:\Users\Ayushi Adhikari\Desktop\eightfold\kb")
VECTOR_DIR = Path("data/vectordb")
VECTOR_DIR.mkdir(parents=True, exist_ok=True)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


def build_vector_db():
    docs = []

    for file in KB_DIR.rglob("*.txt"):
        try:
            text = file.read_text(encoding="utf-8").strip()
            if text:
                docs.append({
                    "page_content": text,
                    "metadata": {"source": str(file)}
                })
                print("Added:", file)
            else:
                print("Skipped empty:", file)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if not docs:
        print("No documents found!")
        return

    print(f"Total documents: {len(docs)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150
    )

    chunks = splitter.create_documents(
        [d["page_content"] for d in docs],
        metadatas=[d["metadata"] for d in docs]
    )

    print("Chunks:", len(chunks))

    vectordb = FAISS.from_documents(
        documents=chunks,
        embedding=embedding_model
    )
    faiss_index_path = VECTOR_DIR / "faiss_index.bin"
    metadata_path = VECTOR_DIR / "faiss_metadata.pkl"

    vectordb.save_local(str(VECTOR_DIR))

    print("FAISS vector DB saved at:", VECTOR_DIR)


if __name__ == "__main__":
    build_vector_db()
