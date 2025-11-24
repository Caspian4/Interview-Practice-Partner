# Interview Practice Partner

A **Retrieval-Augmented Generation (RAG)**–based AI Interviewer built with **FastAPI** backend and **Vite + React** frontend. Supports text and voice input, maintains multi-turn conversation memory, and generates tailored interview feedback based on job roles.

---

## Table of Contents

1. [Features](#features)  
2. [Architecture](#architecture)  
3. [Backend Components](#backend-components)  
4. [Frontend Components](#frontend-components)  
5. [API Endpoints](#api-endpoints)
6. [Tech Stack](#tech-stack)
7. [Setup & Installation](#setup--installation)  
8. [Interview Workflow](#interview-workflow)
9. [Design Decisions](#design-decisions)
10. [Error Handling & Edge Cases](#error-handling--edge-cases)
11. [Video Demo](#video-demo)

---

## Features

- RAG-based AI interviewer with **knowledge-grounded responses**  
- Supports **text and voice input**  
- **Multi-turn conversation memory** with reset functionality  
- **Role-based question tailoring** (from PDFs or manual selection)  
- **Vector database (FAISS)** for efficient knowledge retrieval  
- **Feedback generation** including strengths, weaknesses, and recommendations  
- Robust error handling and modular, maintainable architecture  

---

## Architecture
<img width="1404" height="718" alt="arch" src="https://github.com/user-attachments/assets/94f0253d-c24c-47c1-b6b3-9572652819e7" />


**Key Principles:**

- **Modular Design** – clear separation between API handling, memory, retrieval, and audio processing  
- **Type-Safe** – Python type hints for clarity and IDE support  
- **Context-Aware** – conversation buffer ensures coherent multi-turn dialogue  
- **Extensible** – easily add new knowledge sources, roles, or languages  

---

## Backend Components

| Component | Description |
|-----------|-------------|
| **FastAPI Server** (`server.py`) | Handles API requests and routing |
| **Vector Embeddings** (`embedding.py`) | Converts documents to vectors, stores in FAISS|
| **Base Retriever** | `load_vectorstore()` loads embeddings and returns a base retriever for similarity search|
| **Retriever** |`create_compression_retriever()` takes base retriever to filter irrelevant information and returns the final retriever|
| **RAG Pipeline** (`rag_pipeline.py`) | Handles retrieval and conversational AI responses |
| **Conversation Memory** (`ConversationBufferMemory`) | Maintains chat history for context-aware answers |
| **Audio Processing** (`pydub`) | Speech-to-Text (STT) (`whisper`) & Text-to-Speech (TTS) (`edge tts`) |
| **PDF Parsing** (`PyPDF2`) | Extracts text from PDFs for embeddings |
| **LLM Integration** (`langchain_google_genai`) ,(`langchain_ollama`)| Generates AI responses |
| **Feedback Generator** (`/end_interview`) | Evaluates candidate responses and provides structured feedback |

---

## Frontend Components

- **Framework:** React + Vite  
- **Key Features:**  
  - Mode selection for voice and text
  - Pdf Upload option 
  - Role selection for job-specific interviews
  - User Response counter 

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/greet` | GET | Generates greeting text/audio |
| `/chattext` | POST | Sends text input → retrieves context → LLM response |
| `/voice_chat` | POST | Sends voice input → STT → LLM → TTS |
| `/transcribe` | POST | Converts audio to text |
| `/synthesize` | POST | Converts text to audio |
| `/reset_memory` | POST | Clears conversation memory |
| `/end_interview` | POST | Generates feedback from conversation + job role |

---
## Tech Stack

### **Backend**
- **FastAPI** — API framework  
- **Uvicorn** — ASGI server  
- **LangChain 0.3.x** — RAG pipeline, retrievers, memory  
- **Google Gemini (via langchain-google-genai)** — LLM for interview questions & analysis  
- **FAISS (CPU)** — Vector store for document retrieval  
- **Sentence Transformers** — Embedding generation  
- **Whisper (Local)** — Speech-to-Text  
- **Edge-TTS** — Text-to-Speech  
- **PyPDF2** — PDF parsing for resumes  
- **dotenv** — Environment variable management  
- **Pydub, asyncio, aiofiles, httpx** — Audio & async utils

### **Frontend **
- **React (Vite)** — UI framework  
- **Axios** — API calls  
- **react-audio-recorder / react-media-recorder** — Microphone recording  
- **react-markdown + remark-gfm** — Render markdown output  
- **lucide-react** — Icons

### **Local Optional**
- **Ollama** — For local LLM support (fallback)
---

## Setup & Installation

### Backend

1. Clone the repository:

```bash
git clone https://github.com/Caspian4/Interview-Practice-Partner.git
cd backend
```
2. Create a virtual environment:

```
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```
3. Install dependencies:

```
pip install -r requirements.txt
```
4. Create a .env file

Inside the backend folder, create a file named .env and add your API key:
```
GOOGLE_API_KEY=your_api_key_here
```
5. Run the server:

```
uvicorn backend.server:app --reload
```
Server will start on http://localhost:8000.

### Frontend (Vite + React)

1. Navigate to frontend directory:

```
cd frontend
cd eightfold
```
2. Install dependencies:

```
npm install
```
⚠️ Note: This generates a package-lock.json file. Commit it to your repository to lock package versions and ensure consistency across environments.

3. Run the development server:

```
npm run dev
```
Frontend will start on the URL shown in the console, usually http://localhost:5173.

### FFmpeg Setup (Required for Whisper STT)

Whisper requires FFmpeg to handle audio input. Install it using one of the following methods:

#### Windows (Add to System PATH)
1. Download FFmpeg:  
   https://www.gyan.dev/ffmpeg/builds/
2. Extract the folder and place it in:  
   `C:\ffmpeg`
3. Add the following to your system PATH:  
   `C:\ffmpeg\bin`
4. Restart the terminal and verify installation:
 `ffmpeg -version`

#### Windows (Alternative: Add FFmpeg only inside the virtual environment)
If you prefer not to modify the system PATH:
1. Open your venv activation script:  
`backend/venv/Scripts/Activate.ps1`
2. Add this line at the end of the file:
`$env:PATH += ";C:\ffmpeg\bin"`
3. Reactivate the environment:
`venv\Scripts\activate`
`ffmpeg-version`

---
## Interview Workflow

1. **Start**
   - Run backend & frontend.
   - Upload resume or select role.  
   ![Step 1](https://github.com/user-attachments/assets/67c137ae-9037-45ca-a17f-16913069dc86)

2. **Greeting**
   - AI interviewer welcomes the user.  
   ![Step 2](https://github.com/user-attachments/assets/5c5f80fb-0cfb-4145-9204-57018257638f)

3. **User Response**
   - Answer questions; AI replies contextually.  
   ![Step 3](https://github.com/user-attachments/assets/cfc48f60-5aa1-41ee-91ab-0489146ca70c)

4. **Follow-ups**
   - AI asks follow-ups based on answers or resume.  
   ![Step 4](https://github.com/user-attachments/assets/95055bb0-d0a9-4b59-9a7a-3dc212edb094)

5. **Interaction Modes**
   - Toggle between **text** and **voice**.  
   ![Step 5](https://github.com/user-attachments/assets/4bfb41ad-bca3-44e1-8748-3f7b4507161f)

6. **Controls**
   - Side panel: **End Interview** / **End Session**.  
 <p align="center">
  <img src="https://github.com/user-attachments/assets/399dc906-797c-47c4-bdad-478a79ce5ac3" alt="Step 6" width="200"/>
 </p>

7. **Feedback**
   - Generated after at least **4 answers**.  
<div style="display: flex; justify-content: center; gap: 20px;">
  <img src="https://github.com/user-attachments/assets/54121491-70c9-4eb3-acfb-95134cdb7d40" alt="Step 7" width="500"/>
  <img src="https://github.com/user-attachments/assets/38bd198e-0393-400d-a28d-1b0c1ca18213" alt="Step 8" width="500"/>
</div>

8. **End Session**
   - Clears memory & returns to home page.

---
## Design Decisions

This section explains the reasoning behind the major technology and architecture choices in the AI Interview Practice Partner.

### 1. FAISS instead of Chroma
I initially attempted to use ChromaDB, but the LangChain ecosystem had compatibility and version conflicts, especially with `langchain-google-genai==2.0.10`.  
To avoid these issues, I switched to **FAISS**, which is lightweight, stable, and fast for local similarity search.

---

### 2. Whisper for Speech-to-Text (STT)
Whisper was chosen because:

- It can run **locally**.
- It is lightweight enough for this project.
- It provides strong accuracy compared to browser STT APIs.
- No external API dependency.

---

### 3. Edge-TTS instead of gTTS or ElevenLabs
I originally wanted a fully local TTS solution, but local models require significant memory.  
**Edge-TTS** was chosen because:

- It works using the cloud without high resource usage.
- It provides better quality than gTTS.
- It is free, unlike ElevenLabs.

---

### 4. RAG instead of a normal LLM chat
A plain Gemini API chat would only give generic interview questions.  
RAG was used to ensure:

- Role-specific, grounded interview questions.
- Consistent domain knowledge throughout the conversation.
- Ability to generate meaningful follow-up questions.

I created a custom knowledge base, applied text splitting, created embeddings, and retrieved context based on cosine similarity.

---

### 5. Compression Retriever
A compression retriever was used to:

- Remove irrelevant information from retrieved chunks.
- Reduce prompt noise.
- Improve accuracy and relevance of responses.

---

### 6. Conversation Buffer Memory
Conversation buffer memory helps maintain:

- Short-term dialogue history.
- Context for follow-up questions.
- Coherent responses combining retrieved knowledge + user history +job role.

---

### 7. Model Choice: Gemini + Local Ollama
Both Gemini and Ollama integrations were implemented.  
Gemini was selected as the default because:

- Faster responses.
- More reliable for structured, interviewer-style text.

---

### 8. Streamlit Prototype → React Final Build
The project began as a **Streamlit prototype** to quickly test:

- RAG pipeline flow
- Whisper STT integration
- TTS pipeline
- Interview question/answer logic

After validating the concept, it was migrated to **React (Vite)** to provide:

- A significantly better chat experience
- Cleaner, scalable UI/UX
- Component-level control
- Flexibility for future feature expansion

## Error Handling & Edge Cases

This agent includes robust error-handling for realistic user behavior:

- **Confused or off-topic user** → system gently redirects to the question.
- **User skips a question** → interviewer explains briefly and moves to the next.
- **No relevant documents retrieved** → fallback to generic role-based question set.
- **PDF upload failure** → client displays an error and prevents a crash.
- **User ends interview early** → validation enforces a minimum of 4 answered questions.
- **End session** → memory is cleared immediately and the user is returned to the homepage.

## Video Demo
https://www.youtube.com/watch?v=zq5oLkbPUy4

## License

This project is licensed under the **MIT License** © 2025 Ayushi Adhikari.


