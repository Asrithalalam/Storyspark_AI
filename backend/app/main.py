from contextlib import asynccontextmanager
from urllib.parse import urlparse
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routers import auth, health, stories


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


@app.middleware("http")
async def origin_csrf_validation_middleware(request: Request, call_next):
    """
    Strict Origin and Referer validation middleware for CSRF defense on cookie-based sessions.

    Policy:
    - Safe methods (GET, HEAD, OPTIONS) pass through without Origin validation.
    - CORS OPTIONS preflight requests are explicitly exempted.
    - For state-changing methods (POST, PUT, PATCH, DELETE):
        1. If 'Origin' is provided, it must exactly match one of settings.ALLOWED_ORIGINS.
        2. If 'Origin' is absent and 'Referer' is provided, the origin parsed from 'Referer' must exactly match settings.ALLOWED_ORIGINS.
        3. For authentication state-changing endpoints (/api/auth/*): if both 'Origin' and 'Referer' are absent,
           the request is rejected with 403 Forbidden.
           (Documented behavior: Non-browser clients without Origin/Referer headers are rejected.)
    """
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        origin = request.headers.get("origin")
        if origin:
            if origin not in settings.ALLOWED_ORIGINS:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Cross-origin request rejected: Untrusted Origin."},
                )
        else:
            referer = request.headers.get("referer")
            if referer:
                parsed = urlparse(referer)
                referer_origin = f"{parsed.scheme}://{parsed.netloc}"
                if referer_origin not in settings.ALLOWED_ORIGINS:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "Cross-origin request rejected: Untrusted Referer."},
                    )
            elif request.url.path.startswith(f"{settings.API_PREFIX}/auth"):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "State-changing request rejected: Missing Origin and Referer header."},
                )

    return await call_next(request)


# Include routers
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(stories.router, prefix=settings.API_PREFIX)
app.include_router(auth.router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    """Root endpoint for basic service discovery."""
    return {
        "project": "StorySpark AI",
        "description": "Where Ideas Become Stories",
        "health_check": f"{settings.API_PREFIX}/health",
        "stories": f"{settings.API_PREFIX}/stories",
        "auth": f"{settings.API_PREFIX}/auth",
    }
