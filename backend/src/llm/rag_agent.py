"""RAG agent"""
from src.llm.llm_models import init_gemini_llm, init_ollama_llm
from langchain.prompts import ChatPromptTemplate
import os
def init_llm():
    LLM_TYPE = os.getenv("LLM_TYPE", "gemini")  # 'gemini' or 'ollama'

    if LLM_TYPE == "gemini":
        llm = init_gemini_llm()
    elif LLM_TYPE == "ollama":
        llm = init_ollama_llm()
    else:
        raise RuntimeError(f"Unknown LLM_TYPE: {LLM_TYPE}")
    return llm


def get_prompt_template() -> ChatPromptTemplate:
    """Prompt template for RAG agent"""

    template = """
    You are an AI interviewer helping users prepare for interviews.
    Use the user's resume and chat context. Ask user for self-introduction and then ask them questions.
    Ask technical questions one at a time and after user answers respond with follow-up questions.
    Detected Job Role: {job_role}

    Use ONLY:
    Context from documents / resume:
    {context}

    Chat History:
    {chat_history} but don't repeat the question already asked even if not responded.

    User Question (if any):
    {question}

    Guidelines:
    - Provide hints only if requested
    - Do not repeat any previously asked questions from chat history
    - Ask the follow questions instead
    - Respond in English, concise and conversational
    - If empty response give answer and ask another question
    - If user give vague answer start with claryling question and user understanding

    Final Answer:
    """
    return ChatPromptTemplate.from_template(template)
