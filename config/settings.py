from dotenv import load_dotenv
import os   

load_dotenv()

ENV = os.getenv("ENVIRONMENT", "development")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")