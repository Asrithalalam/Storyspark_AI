import os
from pathlib import Path
from dotenv import load_dotenv

# Base backend directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if present
load_dotenv(BASE_DIR / ".env")


class Settings:
    PROJECT_NAME: str = "StorySpark AI Backend"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # CORS origins
    ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]

    # Dedicated data directories
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOADS_DIR: Path = DATA_DIR / "uploads"

    # Image upload constraints
    MAX_IMAGE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_IMAGE_MIME_TYPES: set[str] = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    # Gemma / Gemini AI Settings
    @property
    def GEMINI_API_KEY(self) -> str | None:
        key = os.getenv("GEMINI_API_KEY")
        if key and key.strip():
            return key.strip()
        return None

    @property
    def GEMMA_MODEL_ID(self) -> str:
        return os.getenv("GEMMA_MODEL_ID", "gemma-4-26b-a4b-it").strip()

    @property
    def DATABASE_URL(self) -> str:
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            # If user provided relative sqlite URL like sqlite:///./data/...
            if env_url.startswith("sqlite:///./"):
                rel_path = env_url.replace("sqlite:///./", "", 1)
                abs_path = (BASE_DIR / rel_path).resolve()
                return f"sqlite:///{abs_path}"
            return env_url
        return f"sqlite:///{self.DATA_DIR / 'storyspark.db'}"


settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
