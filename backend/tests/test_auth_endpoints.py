"""Integration and security tests for Stage 2 Authentication Services, Endpoints, and Middleware."""

import time
from unittest.mock import patch
from fastapi import status
from fastapi.testclient import TestClient
import jwt
import pytest
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.services import auth_service


# Sample test credentials
TEST_EMAIL = "author@storyspark.ai"
TEST_PASSWORD = "SuperSecretPassword123!"
VALID_ORIGIN = "http://localhost:5173"


# ============================================================================
# Registration & Login Tests
# ============================================================================

def test_register_success(client: TestClient):
    """Test successful local user registration returns safe profile and Set-Cookie."""
    payload = {
        "email": "new_author@storyspark.ai",
        "password": "Password123!",
        "full_name": "New Author",
    }
    response = client.post("/api/auth/register", json=payload, headers={"Origin": VALID_ORIGIN})
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["email"] == "new_author@storyspark.ai"
    assert data["full_name"] == "New Author"
    assert data["auth_provider"] == "local"
    assert "hashed_password" not in data
    assert "password" not in data

    # Verify session cookie was set
    assert settings.COOKIE_NAME in response.cookies
    cookie = response.cookies[settings.COOKIE_NAME]
    assert len(cookie) > 20


def test_register_duplicate_email_rejected(client: TestClient):
    """Test registering with an existing email returns 409 Conflict."""
    payload = {
        "email": "duplicate@storyspark.ai",
        "password": "Password123!",
        "full_name": "Author One",
    }
    resp1 = client.post("/api/auth/register", json=payload, headers={"Origin": VALID_ORIGIN})
    assert resp1.status_code == status.HTTP_201_CREATED

    # Second attempt with same email
    resp2 = client.post("/api/auth/register", json=payload, headers={"Origin": VALID_ORIGIN})
    assert resp2.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in resp2.json()["detail"].lower()


def test_register_email_normalization(client: TestClient):
    """Test email is normalized to lowercase and whitespace stripped."""
    payload = {
        "email": "  CasedEmail@StorySpark.AI  ",
        "password": "Password123!",
        "full_name": "Cased Author",
    }
    resp = client.post("/api/auth/register", json=payload, headers={"Origin": VALID_ORIGIN})
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["email"] == "casedemail@storyspark.ai"

    # Login with lowercase version succeeds
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "casedemail@storyspark.ai", "password": "Password123!"},
        headers={"Origin": VALID_ORIGIN},
    )
    assert login_resp.status_code == status.HTTP_200_OK


def test_register_invalid_inputs(client: TestClient):
    """Test validation errors for invalid email or short password."""
    # Short password
    r1 = client.post(
        "/api/auth/register",
        json={"email": "test@storyspark.ai", "password": "short"},
        headers={"Origin": VALID_ORIGIN},
    )
    assert r1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Invalid email format
    r2 = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "ValidPassword123!"},
        headers={"Origin": VALID_ORIGIN},
    )
    assert r2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_success(client: TestClient):
    """Test successful password login sets session cookie."""
    # Register first
    client.post(
        "/api/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD, "full_name": "Spark Author"},
        headers={"Origin": VALID_ORIGIN},
    )

    # Login
    resp = client.post(
        "/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        headers={"Origin": VALID_ORIGIN},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["email"] == TEST_EMAIL
    assert settings.COOKIE_NAME in resp.cookies


def test_login_invalid_credentials_uniform_error(client: TestClient):
    """Verify wrong password and unknown email return identical generic 401 error."""
    client.post(
        "/api/auth/register",
        json={"email": "user_exists@storyspark.ai", "password": "Password123!"},
        headers={"Origin": VALID_ORIGIN},
    )

    # Wrong password for existing user
    resp_wrong_pw = client.post(
        "/api/auth/login",
        json={"email": "user_exists@storyspark.ai", "password": "WrongPassword!"},
        headers={"Origin": VALID_ORIGIN},
    )
    assert resp_wrong_pw.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp_wrong_pw.json()["detail"] == "Invalid email or password."

    # Nonexistent user
    resp_unknown_user = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@storyspark.ai", "password": "WrongPassword!"},
        headers={"Origin": VALID_ORIGIN},
    )
    assert resp_unknown_user.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp_unknown_user.json()["detail"] == "Invalid email or password."


# ============================================================================
# Session & Logout Tests
# ============================================================================

def test_get_me_authenticated(client: TestClient):
    """Test /api/auth/me returns current user when valid cookie is provided."""
    reg = client.post(
        "/api/auth/register",
        json={"email": "me_test@storyspark.ai", "password": "Password123!", "full_name": "Me Test"},
        headers={"Origin": VALID_ORIGIN},
    )
    assert reg.status_code == status.HTTP_201_CREATED

    # Session cookie is automatically retained in client session
    me_resp = client.get("/api/auth/me")
    assert me_resp.status_code == status.HTTP_200_OK
    assert me_resp.json()["email"] == "me_test@storyspark.ai"
    assert me_resp.json()["full_name"] == "Me Test"


def test_get_me_unauthenticated(client: TestClient):
    """Test /api/auth/me returns 401 Unauthorized when no cookie is sent."""
    # Use clean client without cookies
    clean_client = TestClient(client.app, cookies={}, headers={"Origin": VALID_ORIGIN})
    resp = clean_client.get("/api/auth/me")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "not authenticated" in resp.json()["detail"].lower()


def test_logout_clears_cookie(client: TestClient):
    """Test /api/auth/logout clears the session cookie."""
    client.cookies.clear()
    reg = client.post(
        "/api/auth/register",
        json={"email": "logout_test@storyspark.ai", "password": "Password123!"},
        headers={"Origin": VALID_ORIGIN},
    )
    assert settings.COOKIE_NAME in reg.cookies

    # Logout
    logout_resp = client.post("/api/auth/logout", headers={"Origin": VALID_ORIGIN})
    assert logout_resp.status_code == status.HTTP_200_OK
    assert logout_resp.json()["message"] == "Logged out successfully."

    # Subsequent call to /me should fail
    me_resp = client.get("/api/auth/me")
    assert me_resp.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# JWT Security & Validation Tests
# ============================================================================

def test_jwt_expired_token_rejected(client: TestClient):
    """Test expired JWT token is rejected with 401 Unauthorized."""
    past_time = int(time.time()) - 3600
    expired_payload = {
        "sub": "1",
        "email": "expired@storyspark.ai",
        "iat": past_time - 7200,
        "exp": past_time,
    }
    expired_token = jwt.encode(expired_payload, settings.JWT_SECRET_KEY, algorithm="HS256")

    client.cookies.set(settings.COOKIE_NAME, expired_token)
    resp = client.get("/api/auth/me")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "expired" in resp.json()["detail"].lower()


def test_jwt_malformed_token_rejected(client: TestClient):
    """Test malformed JWT token string is rejected."""
    client.cookies.set(settings.COOKIE_NAME, "not.a.valid.jwt.token")
    resp = client.get("/api/auth/me")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_jwt_unexpected_algorithm_rejected(client: TestClient):
    """Test token signed with unexpected algorithm (e.g. none or HS384) is rejected."""
    # Attempt algorithm confusion with 'none'
    now = int(time.time())
    payload = {"sub": "1", "email": "test@storyspark.ai", "iat": now, "exp": now + 3600}

    # Construct unsigned token with alg: none
    unsigned_token = jwt.encode(payload, key="", algorithm="none")
    client.cookies.set(settings.COOKIE_NAME, unsigned_token)
    resp = client.get("/api/auth/me")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_jwt_missing_required_claims_rejected(client: TestClient):
    """Test token missing required 'sub' or 'email' claims is rejected."""
    now = int(time.time())
    # Missing sub claim
    bad_payload = {"email": "test@storyspark.ai", "iat": now, "exp": now + 3600}
    bad_token = jwt.encode(bad_payload, settings.JWT_SECRET_KEY, algorithm="HS256")

    client.cookies.set(settings.COOKIE_NAME, bad_token)
    resp = client.get("/api/auth/me")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_insecure_jwt_secret_placeholder_rejected():
    """Verify system rejects insecure default/placeholder JWT secrets."""
    with patch.dict("os.environ", {"JWT_SECRET_KEY": "your_jwt_secret_key_here"}):
        from app.config import Settings
        s = Settings()
        with pytest.raises(ValueError, match="insecure placeholder"):
            _ = s.JWT_SECRET_KEY


# ============================================================================
# Origin & CSRF Validation Tests
# ============================================================================

def test_origin_validation_exact_match(client: TestClient):
    """Test state-changing requests with exact allowed Origin succeed."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "any@storyspark.ai", "password": "pw"},
        headers={"Origin": "http://localhost:5173"},
    )
    # Origin check passed (fails with 401 credentials rather than 403 Forbidden)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_referer_validation_when_origin_missing(client: TestClient):
    """Test state-changing requests with missing Origin but valid Referer succeed."""
    naked_client = TestClient(client.app, headers={})
    resp = naked_client.post(
        "/api/auth/login",
        json={"email": "any@storyspark.ai", "password": "pw"},
        headers={"Referer": "http://localhost:5173/login"},
    )
    # Referer check passed
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_untrusted_origin_rejected(client: TestClient):
    """Test state-changing requests with untrusted Origin return 403 Forbidden."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "any@storyspark.ai", "password": "pw"},
        headers={"Origin": "http://malicious-attacker.com"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert "rejected" in resp.json()["detail"].lower()


def test_untrusted_referer_rejected(client: TestClient):
    """Test state-changing requests with untrusted Referer and no Origin return 403 Forbidden."""
    naked_client = TestClient(client.app, headers={})
    resp = naked_client.post(
        "/api/auth/login",
        json={"email": "any@storyspark.ai", "password": "pw"},
        headers={"Referer": "http://malicious-attacker.com/page"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_missing_origin_and_referer_rejected(client: TestClient):
    """Test non-browser state-changing requests without Origin or Referer are rejected."""
    naked_client = TestClient(client.app, headers={})
    resp = naked_client.post(
        "/api/auth/login",
        json={"email": "any@storyspark.ai", "password": "pw"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert "missing origin and referer" in resp.json()["detail"].lower()


def test_cors_options_preflight_exempt_from_origin_rejection(client: TestClient):
    """Test CORS OPTIONS preflight request without Origin is NOT rejected with 403."""
    naked_client = TestClient(client.app, headers={})
    resp = naked_client.options("/api/auth/login")
    assert resp.status_code != status.HTTP_403_FORBIDDEN


# ============================================================================
# Concurrency & Race Condition Tests
# ============================================================================

def test_concurrent_duplicate_local_registration_handles_integrity_error(db_session: Session):
    """Verify concurrent registration collision rolls back and raises EmailAlreadyExistsError."""
    # First user succeeds
    auth_service.register_local_user(
        db=db_session,
        email="concurrent@storyspark.ai",
        password="Password123!",
    )

    # Second concurrent insert directly triggers IntegrityError
    from sqlalchemy.exc import IntegrityError
    with patch.object(db_session, "commit", side_effect=IntegrityError("UNIQUE constraint failed", {}, None)):
        with pytest.raises(auth_service.EmailAlreadyExistsError):
            auth_service.register_local_user(
                db=db_session,
                email="concurrent_race@storyspark.ai",
                password="Password123!",
            )
