from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import health, stories


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI: initializes database tables upon startup."""
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for StorySpark AI — Where Ideas Become Stories.",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(stories.router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    """Root endpoint for basic service discovery."""
    return {
        "project": "StorySpark AI",
        "description": "Where Ideas Become Stories",
        "health_check": f"{settings.API_PREFIX}/health",
        "stories": f"{settings.API_PREFIX}/stories",
    }
