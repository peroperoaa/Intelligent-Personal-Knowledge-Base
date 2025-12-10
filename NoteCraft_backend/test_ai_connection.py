import os
import sys
import django
from dotenv import load_dotenv

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NoteCraft_backend.settings')
django.setup()

from NoteMaker.ai_module import query_ai, get_vector_db
from langchain_openai import ChatOpenAI

load_dotenv()

def test_openrouter_connection():
    print("Testing OpenRouter Connection...")
    api_key = os.getenv("OPEN_ROUTER_API_KEY")
    if not api_key:
        print("Error: OPEN_ROUTER_API_KEY not found.")
        return

    try:
        llm = ChatOpenAI(
            model_name="qwen/qwq-32b:free",
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0
        )
        response = llm.invoke("Hello, are you working?")
        print(f"OpenRouter Response: {response.content}")
        print("OpenRouter Connection Successful!")
    except Exception as e:
        print(f"OpenRouter Connection Failed: {e}")

def test_vector_db():
    print("\nTesting Vector DB...")
    try:
        vectordb = get_vector_db()
        print(f"Vector DB loaded. Collection count: {vectordb._collection.count()}")
    except Exception as e:
        print(f"Vector DB Error: {e}")

if __name__ == "__main__":
    test_vector_db()
    test_openrouter_connection()
