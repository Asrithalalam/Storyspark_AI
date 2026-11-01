import os
from pathlib import Path
from dotenv import load_dotenv

# Base backend directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if present
load_dotenv(BASE_DIR / ".env")

INSECURE_PLACEHOLDER_SECRETS = {
    "your_jwt_secret_key_here",
    "replace_with_a_secure_random_64_character_hex_key",
    "secret",
    "changeme",
    "your-secret-key",
    "default_secret",
}


class Settings:
    PROJECT_NAME: str = "StorySpark AI Backend"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # CORS origins
    ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
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
            if env_url.startswith("sqlite:///./"):
                rel_path = env_url.replace("sqlite:///./", "", 1)
                abs_path = (BASE_DIR / rel_path).resolve()
                return f"sqlite:///{abs_path}"
            return env_url
        return f"sqlite:///{self.DATA_DIR / 'storyspark.db'}"

    # Authentication & Session Settings
    JWT_ALGORITHM: str = "HS256"

    @property
    def JWT_SECRET_KEY(self) -> str:
        key = os.getenv("JWT_SECRET_KEY", "").strip()
        if not key or key in INSECURE_PLACEHOLDER_SECRETS:
            raise ValueError(
                "JWT_SECRET_KEY is missing or contains an insecure placeholder. "
                "Please configure a valid, secure JWT_SECRET_KEY in backend/.env."
            )
        if len(key) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long for secure HS256 signing.")
        return key

    @property
    def COOKIE_NAME(self) -> str:
        return os.getenv("COOKIE_NAME", "storyspark_session").strip()

    @property
    def COOKIE_SECURE(self) -> bool:
        return os.getenv("COOKIE_SECURE", "False").strip().lower() in ("true", "1", "yes")

    @property
    def COOKIE_MAX_AGE_SECONDS(self) -> int:
        try:
            return int(os.getenv("COOKIE_MAX_AGE_SECONDS", "604800").strip())
        except ValueError:
            return 604800


settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
