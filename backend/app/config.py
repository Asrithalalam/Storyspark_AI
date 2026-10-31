import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Settings:
    PROJECT_NAME: str = "StorySpark AI Backend"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # CORS origins
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

settings = Settings()
