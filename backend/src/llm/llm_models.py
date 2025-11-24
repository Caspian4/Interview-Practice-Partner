"""LLM Models"""
import os
from dotenv import load_dotenv

load_dotenv()

# ------------------------------
# Gemini LLM (official langchain-google-genai wrapper)
# ------------------------------
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

def init_gemini_llm(api_key: str = None, model: str = "gemini-2.0-flash", temperature: float = 0.3):
    if ChatGoogleGenerativeAI is None:
        raise RuntimeError("Install langchain_google_genai to use Gemini LLM.")
    api_key = api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GOOGLE_API_KEY in your environment.")
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=api_key,
    )


# ------------------------------
# Ollama LLM (official langchain-ollama wrapper)
# ------------------------------
try:
    from langchain_ollama import ChatOllama
except ImportError:
    ChatOllama = None
    raise RuntimeError("Install langchain-ollama to use Ollama LLM (pip install langchain-ollama).")

def init_ollama_llm(model: str = "llama2:latest", temperature: float = 0.3) -> ChatOllama:
    """Initialize Ollama LLM using the official ChatOllama wrapper."""
    if ChatOllama is None:
        raise RuntimeError("langchain-ollama is not installed.")
    return ChatOllama(model=model, temperature=temperature)