"""Authentication service providing secure password hashing, JWT session tokens,
and user management.

Note on Logout Limitation:
Because JWT tokens are cryptographically self-contained and stateless, clearing the HttpOnly cookie
removes the session from the client browser. However, any previously copied token would remain technically
valid on the server until its expiration time (exp). For this application demo, a 7-day token expiration
is accepted.
"""

from datetime import datetime, timezone
import hashlib
import hmac
import logging
import secrets
import time
from typing import Any

import jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)

# PBKDF2 Parameters (OWASP recommended standards)
PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 600000
SALT_BYTES = 16

# Dummy hash for constant-time comparison against nonexistent users
DUMMY_SALT = b"\x00" * SALT_BYTES
DUMMY_HASH = f"pbkdf2_sha256${PBKDF2_ITERATIONS}${DUMMY_SALT.hex()}${'0' * 64}"


# Custom authentication exceptions
class AuthError(Exception):
    """Base exception for authentication service."""
    pass


class EmailAlreadyExistsError(AuthError):
    """Raised when registering an email that already exists."""
    pass


class InvalidCredentialsError(AuthError):
    """Raised when credentials (email/password) are incorrect."""
    pass


class AccountConflictError(AuthError):
    """Raised when an account already exists under a different auth provider."""
    pass


class InvalidSessionTokenError(AuthError):
    """Raised when a session JWT is invalid, expired, or malformed."""
    pass


# ============================================================================
# Password Hashing & Verification
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a plaintext password using PBKDF2-HMAC-SHA256 with a unique random salt.

    Returns:
        Formatted string: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
    """
    if not password:
        raise ValueError("Password cannot be empty.")

    salt = secrets.token_bytes(SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        hash_name=PBKDF2_ALGORITHM,
        password=password.encode("utf-8"),
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${derived.hex()}"


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    """
    Verify a plaintext password against a stored PBKDF2-HMAC-SHA256 hash
    using constant-time comparison to protect against timing attacks.
    """
    if not plain_password or not hashed_password or not isinstance(hashed_password, str):
        return False

    parts = hashed_password.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False

    try:
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hash = bytes.fromhex(parts[3])
    except (ValueError, TypeError):
        return False

    computed = hashlib.pbkdf2_hmac(
        hash_name=PBKDF2_ALGORITHM,
        password=plain_password.encode("utf-8"),
        salt=salt,
        iterations=iterations,
    )

    return hmac.compare_digest(computed, expected_hash)


# ============================================================================
# JWT Session Tokens
# ============================================================================

def create_session_token(user_id: int, email: str) -> str:
    """
    Create a signed session JWT using HS256 with required claims: sub, email, iat, exp.
    sub claim is strictly a string representation of the integer user ID.
    """
    now = int(time.time())
    exp = now + settings.COOKIE_MAX_AGE_SECONDS

    payload = {
        "sub": str(user_id),
        "email": email.strip().lower(),
        "iat": now,
        "exp": exp,
    }

    token = jwt.encode(
        payload=payload,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token


def verify_session_token(token: str | None) -> dict[str, Any]:
    """
    Verify and decode a session JWT.
    Strictly validates algorithm (HS256), signature, expiration, and presence of required claims.

    Raises:
        InvalidSessionTokenError: If token is missing, expired, invalid, or malformed.
    """
    if not token or not isinstance(token, str):
        raise InvalidSessionTokenError("Session token is missing.")

    try:
        claims = jwt.decode(
            jwt=token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["sub", "email", "iat", "exp"],
            },
        )
    except jwt.ExpiredSignatureError:
        raise InvalidSessionTokenError("Session token has expired.") from None
    except jwt.InvalidAlgorithmError:
        raise InvalidSessionTokenError("Unsupported token algorithm.") from None
    except jwt.InvalidTokenError as exc:
        raise InvalidSessionTokenError(f"Invalid session token: {exc}") from None
    except Exception as exc:
        raise InvalidSessionTokenError(f"Token verification error: {exc}") from None

    # Validate sub and email format
    sub = claims.get("sub")
    if not isinstance(sub, str) or not sub.strip():
        raise InvalidSessionTokenError("Token 'sub' claim must be a non-empty string.")

    email = claims.get("email")
    if not isinstance(email, str) or not email.strip():
        raise InvalidSessionTokenError("Token 'email' claim must be a non-empty string.")

    return claims


# ============================================================================
# Database Operations
# ============================================================================

def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Retrieve an active user by primary key ID."""
    user = db.get(User, user_id)
    if user and user.is_active:
        return user
    return None


def get_user_by_email(db: Session, email: str) -> User | None:
    """Retrieve an active user by email address."""
    clean_email = email.strip().lower()
    stmt = select(User).where(User.email == clean_email, User.is_active.is_(True))
    return db.scalars(stmt).first()


def register_local_user(db: Session, email: str, password: str, full_name: str | None = None) -> User:
    """
    Register a new local user with email and password.
    Normalizes email and safely handles concurrent duplicate registrations via IntegrityError rollback.
    """
    clean_email = email.strip().lower()

    # Pre-check email existence
    existing = get_user_by_email(db, clean_email)
    if existing:
        raise EmailAlreadyExistsError("An account with this email already exists.")

    password_hash = hash_password(password)

    new_user = User(
        email=clean_email,
        hashed_password=password_hash,
        full_name=full_name.strip() if full_name else None,
        auth_provider="local",
        is_active=True,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"Registered new local user (ID: {new_user.id}, email: {clean_email})")
        return new_user
    except IntegrityError:
        db.rollback()
        logger.warning(f"Concurrent registration collision for email: {clean_email}")
        raise EmailAlreadyExistsError("An account with this email already exists.") from None


def authenticate_local_user(db: Session, email: str, password: str) -> User:
    """
    Authenticate a user using email and password.
    Uses constant-time comparison even when user is not found to prevent timing-based user enumeration.

    Raises:
        InvalidCredentialsError: On incorrect email or password with uniform error message.
    """
    clean_email = email.strip().lower()
    user = get_user_by_email(db, clean_email)

    if not user or not user.hashed_password:
        # Run dummy verification to ensure constant-time response
        verify_password("dummy", DUMMY_HASH)
        raise InvalidCredentialsError("Invalid email or password.")

    if not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError("Invalid email or password.")

    return user
