from dotenv import load_dotenv
import os   

load_dotenv()

ENV = os.getenv("ENVIRONMENT", "development")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
APP_DIR = os.path.dirname(BASE_DIR)
DATA_PATH = os.getenv("DATA_PATH", os.path.join(APP_DIR, "data_db"))