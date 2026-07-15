from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("COINGECKO_API")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")