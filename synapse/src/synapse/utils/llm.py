from crewai import LLM
from langchain_litellm import ChatLiteLLM
from dotenv import load_dotenv
from langchain_litellm import ChatLiteLLM
import os

load_dotenv()

def gemini_creative():
    return LLM(
        api_key=os.getenv("GEMINI_API_KEY"),
        model="gemini/gemini-2.5-flash",
        temperature = 0.7,
        top_p=0.8,
    )

def gemini():
    return LLM(
        api_key=os.getenv("GEMINI_API_KEY"),
        model="gemini/gemini-2.5-flash",
    )

llm = ChatLiteLLM(model="azure/gpt-5-mini")
