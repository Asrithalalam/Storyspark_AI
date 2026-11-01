"""FastAPI endpoints for authentication, registration, session management, and logout."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    UserResponse,
)
from app.services import auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# Cookie Helpers
# ============================================================================

def set_session_cookie(response: Response, token: str) -> None:
    """Attach the signed session JWT as an HttpOnly, SameSite=Lax cookie."""
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        max_age=settings.COOKIE_MAX_AGE_SECONDS,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
    )


def clear_session_cookie(response: Response) -> None:
    """Clear the session cookie by setting its max-age to 0."""
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
    )


# ============================================================================
# FastAPI Dependencies
# ============================================================================

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency yielding the authenticated User entity from the session cookie.

    Raises:
        HTTPException(401): If the session cookie is missing, expired, or invalid.
    """
    token = request.cookies.get(settings.COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )

    try:
        claims = auth_service.verify_session_token(token)
    except auth_service.InvalidSessionTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from None

    try:
        user_id = int(claims["sub"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed user identifier in session token.",
        ) from None

    user = auth_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account is inactive.",
        )

    return user


# ============================================================================
# Authentication Endpoints
# ============================================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new local user with email and password",
)
def register(
    req: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Register a new user, issue an HttpOnly session cookie, and return the user profile."""
    try:
        user = auth_service.register_local_user(
            db=db,
            email=req.email,
            password=req.password,
            full_name=req.full_name,
        )
    except auth_service.EmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from None

    # Issue session cookie
    token = auth_service.create_session_token(user_id=user.id, email=user.email)
    set_session_cookie(response=response, token=token)

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign in with email and password",
)
def login(
    req: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Authenticate email and password, issue an HttpOnly session cookie, and return user profile."""
    try:
        user = auth_service.authenticate_local_user(
            db=db,
            email=req.email,
            password=req.password,
        )
    except auth_service.InvalidCredentialsError:
        # Uniform, timing-safe error response
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        ) from None

    # Issue session cookie
    token = auth_service.create_session_token(user_id=user.id, email=user.email)
    set_session_cookie(response=response, token=token)

    return UserResponse.model_validate(user)


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign out and clear session cookie",
)
def logout(response: Response) -> MessageResponse:
    """Clear the session cookie from the client browser."""
    clear_session_cookie(response=response)
    return MessageResponse(message="Logged out successfully.")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get currently authenticated user profile",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the profile of the user currently authenticated via session cookie."""
    return UserResponse.model_validate(current_user)
