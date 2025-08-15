import os
from dotenv import load_dotenv

def load_environment():
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OpenAI API key is missing in the environment variables.")
    
    # MongoDB configuration (optional - will use default if not set)
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    
    return openai_key
