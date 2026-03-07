from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import GEMINI_MODEL, GOOGLE_API_KEY


def get_llm():
    return ChatGoogleGenerativeAI(
        model = GEMINI_MODEL,
        google_api_key = GOOGLE_API_KEY
    )