"""API for Interview Prep RAG."""
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.rag_pipeline import load_vectorstore, create_rag_pipeline_with_memory, add_resume_to_memory, create_compression_retriever
from src.llm.rag_agent import init_llm, get_prompt_template
from src.stt.stt import transcribe
from src.tts.tts import synthesize
import base64
import tempfile
import os
from pydub import AudioSegment
from langchain.schema import HumanMessage, AIMessage

app = FastAPI(title="Interview Prep RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    role: str | None = None

FAISS_DIR = "data/vectordb"

db, embeddings, base_retriever = load_vectorstore("data/vectordb")

retriever = create_compression_retriever(
    embeddings=embeddings,
    base_retriever=base_retriever,
    chunk_size=500,  
    k=5,                  
    similarity_threshold=0.7
)

llm = init_llm()
prompt = get_prompt_template()
qa_pipeline = create_rag_pipeline_with_memory(llm, retriever, prompt)

def extract_role_from_memory(memory):
    msgs = memory.chat_memory.messages
    for m in reversed(msgs):
        if isinstance(m.content, str) and "DETECTED_JOB_ROLE:" in m.content:
            return m.content.replace("DETECTED_JOB_ROLE:", "").strip()
    return "General"

@app.post("/chattext")
def chat_text(request: QueryRequest):
    if request.role:
        job_role = request.role
    else:
        job_role = extract_role_from_memory(qa_pipeline.memory)
        
    response =qa_pipeline.invoke({
        "question": request.query,
        "context": "",   
        "job_role": job_role, 
    })
    return {"query": request.query, "answer": response["answer"]}

@app.post("/upload_resume")
def upload_resume(file: UploadFile = File(...)):
    with open("temp_resume.pdf", "wb") as f:
        f.write(file.file.read())
    add_resume_to_memory(qa_pipeline, "temp_resume.pdf")
    return {"status": "Resume added to temporary context"}


@app.post("/voice_chat")
async def voice_chat(file: UploadFile = File(...), role: str = Form(None)):
    suffix = os.path.splitext(file.filename)[1] or ".webm"
    tmp_path = None
    wav_path = None

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Convert to WAV
        wav_path = tmp_path + ".wav"
        audio = AudioSegment.from_file(tmp_path)
        audio.export(wav_path, format="wav")

        # Transcribe (sync)
        transcript = transcribe(wav_path)
        qa_pipeline.memory.chat_memory.add_message(HumanMessage(content=transcript))

        # Query RAG
        job_role = role or extract_role_from_memory(qa_pipeline.memory)
        answer = qa_pipeline.invoke({"question": transcript, "job_role": job_role})
        ans_text = answer.get("answer", "")
        qa_pipeline.memory.chat_memory.add_message(AIMessage(content=ans_text))

        # Synthesize (await only if synthesize is async)
        audio_bytes = await synthesize(ans_text)  # keep if async
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        return {"transcript": transcript, "answer": ans_text, "audio_base64": audio_b64}

    except Exception as e:
        return {"error": str(e)}

    finally:
        for f in [tmp_path, wav_path]:
            if f and os.path.exists(f):
                os.remove(f)



@app.post("/transcribe")
async def transcribe_only(file: UploadFile = File(...)):
    """Accept an uploaded audio file and return only the transcription."""
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        transcript = transcribe(tmp_path)
    except Exception as e:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        return {"error": str(e)}

    try:
        os.remove(tmp_path)
    except Exception:
        pass

    return {"transcript": transcript}

@app.post("/reset_memory")
def reset_memory():
    try:
        qa_pipeline.memory.clear()
        return {"status": "cleared"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/greet")
async def greet(mode: str = "text", role: str = None):

    if role:
        job_role = role
    else:
        job_role = extract_role_from_memory(qa_pipeline.memory)

    greeting_query = f"Give a friendly greeting for a user preparing for a {job_role} interview."

    response = qa_pipeline({
        "question": greeting_query,
        "job_role": job_role
    })

    text = response["answer"]

    audio_b64 = None
    if mode == "voice":
        audio_bytes = await synthesize(text)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    return {
        "text": text,
        "audio_base64": audio_b64,
        "role": job_role
    }

@app.post("/end_interview")
def end_interview():
   
    chat_history = "\n".join([
        m.content for m in qa_pipeline.memory.chat_memory.messages
        if hasattr(m, "content")
    ])
  
    job_role = extract_role_from_memory(qa_pipeline.memory)

    feedback_prompt = f"""
You are an interview evaluator.

Candidate chat history:
{chat_history}

Job Role: {job_role}

Provide a final review including:
1. Scores (clarity, correctness, confidence)
2. Strengths
3. Weaknesses
4. Actionable improvement tips
Respond concisely and do not ask new questions.
"""

    llm = init_llm()
    feedback = llm([HumanMessage(content=feedback_prompt)]).content

    qa_pipeline.memory.clear()

    return {"feedback": feedback}
