import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "trackbuddy-vintage-secret-key-2026")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(BASE_DIR, "trackbuddy.db")
    
    # Weather Provider
    WEATHER_PROVIDER = os.getenv("WEATHER_PROVIDER", "open-meteo")
    
    # Routing Provider
    ROUTING_PROVIDER = os.getenv("ROUTING_PROVIDER", "osrm")
    ORS_API_KEY = os.getenv("ORS_API_KEY", "")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    
    # AI Assistant
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma2:2b")
    
    # Demo flag
    DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
