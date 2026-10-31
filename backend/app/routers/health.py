from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="", tags=["Health"])

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime

@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Health check endpoint to verify backend status."""
    return HealthResponse(
        status="ok",
        message="StorySpark AI backend is running",
        timestamp=datetime.now(timezone.utc),
    )
