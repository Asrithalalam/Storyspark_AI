"""Tests for Stage 3: Story Ownership and Authorization."""

from fastapi import status
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.config import settings
from app.models.story import Story
from app.models.user import User
from app.services.auth_service import create_session_token


VALID_ORIGIN = "http://localhost:5173"

SAMPLE_STORY_DATA = {
    "title": "User A Chronicles",
    "content": "A wondrous adventure written exclusively by User A.",
    "prompt": "User A's creative concept.",
    "genre": "Fantasy",
    "mood": "Mysterious",
    "length": "Short",
}


@pytest.fixture
def user_a(db_session: Session) -> User:
    """Create User A."""
    u = User(
        email="user_a@storyspark.ai",
        hashed_password="mock_hash_a",
        full_name="User Alpha",
        auth_provider="local",
        is_active=True,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture
def user_b(db_session: Session) -> User:
    """Create User B."""
    u = User(
        email="user_b@storyspark.ai",
        hashed_password="mock_hash_b",
        full_name="User Beta",
        auth_provider="local",
        is_active=True,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture
def client_a(client: TestClient, user_a: User) -> TestClient:
    """Client authenticated as User A."""
    token = create_session_token(user_id=user_a.id, email=user_a.email)
    c = TestClient(
        client.app,
        headers={"Origin": VALID_ORIGIN},
        cookies={settings.COOKIE_NAME: token},
    )
    return c


@pytest.fixture
def client_b(client: TestClient, user_b: User) -> TestClient:
    """Client authenticated as User B."""
    token = create_session_token(user_id=user_b.id, email=user_b.email)
    c = TestClient(
        client.app,
        headers={"Origin": VALID_ORIGIN},
        cookies={settings.COOKIE_NAME: token},
    )
    return c


@pytest.fixture
def unauth_client(client: TestClient) -> TestClient:
    """Unauthenticated client with no session cookie."""
    c = TestClient(
        client.app,
        headers={"Origin": VALID_ORIGIN},
        cookies={},
    )
    return c


# ============================================================================
# Story Ownership & Cross-User Isolation Tests
# ============================================================================

def test_user_a_creates_and_retrieves_own_story(client_a: TestClient, user_a: User):
    """Verify User A creates a story, receives correct user_id, and can retrieve it."""
    res = client_a.post("/api/stories", json=SAMPLE_STORY_DATA)
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["title"] == SAMPLE_STORY_DATA["title"]
    assert data["user_id"] == user_a.id
    story_id = data["id"]

    # User A retrieves own story
    get_res = client_a.get(f"/api/stories/{story_id}")
    assert get_res.status_code == status.HTTP_200_OK
    assert get_res.json()["id"] == story_id
    assert get_res.json()["user_id"] == user_a.id


def test_user_b_cannot_retrieve_user_a_story(client_a: TestClient, client_b: TestClient):
    """Verify User B receives a 404 when attempting to access User A's story."""
    res = client_a.post("/api/stories", json=SAMPLE_STORY_DATA)
    assert res.status_code == status.HTTP_201_CREATED
    story_id = res.json()["id"]

    # User B attempts to access User A's story
    get_res = client_b.get(f"/api/stories/{story_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in get_res.json()["detail"].lower()


def test_user_b_cannot_delete_user_a_story(client_a: TestClient, client_b: TestClient):
    """Verify User B receives 404 when attempting to delete User A's story."""
    res = client_a.post("/api/stories", json=SAMPLE_STORY_DATA)
    assert res.status_code == status.HTTP_201_CREATED
    story_id = res.json()["id"]

    # User B attempts to delete User A's story
    del_res = client_b.delete(f"/api/stories/{story_id}")
    assert del_res.status_code == status.HTTP_404_NOT_FOUND

    # Verify story still exists for User A
    get_res = client_a.get(f"/api/stories/{story_id}")
    assert get_res.status_code == status.HTTP_200_OK


def test_each_user_sees_only_their_own_stories(
    client_a: TestClient, client_b: TestClient, user_a: User, user_b: User
):
    """Verify the My Stories list endpoint returns only stories owned by the requester."""
    # User A creates 2 stories
    client_a.post("/api/stories", json={**SAMPLE_STORY_DATA, "title": "A Story 1"})
    client_a.post("/api/stories", json={**SAMPLE_STORY_DATA, "title": "A Story 2"})

    # User B creates 1 story
    client_b.post("/api/stories", json={**SAMPLE_STORY_DATA, "title": "B Story 1"})

    # User A lists stories
    list_a = client_a.get("/api/stories")
    assert list_a.status_code == status.HTTP_200_OK
    titles_a = [s["title"] for s in list_a.json()]
    assert "A Story 1" in titles_a
    assert "A Story 2" in titles_a
    assert "B Story 1" not in titles_a

    # User B lists stories
    list_b = client_b.get("/api/stories")
    assert list_b.status_code == status.HTTP_200_OK
    titles_b = [s["title"] for s in list_b.json()]
    assert "B Story 1" in titles_b
    assert "A Story 1" not in titles_b
    assert "A Story 2" not in titles_b


def test_user_b_bulk_delete_ignores_user_a_stories(client_a: TestClient, client_b: TestClient):
    """Verify bulk-delete only deletes stories owned by the calling user."""
    res_a = client_a.post("/api/stories", json={**SAMPLE_STORY_DATA, "title": "A Keep Story"})
    story_a_id = res_a.json()["id"]

    res_b = client_b.post("/api/stories", json={**SAMPLE_STORY_DATA, "title": "B Target Story"})
    story_b_id = res_b.json()["id"]

    # User B attempts to bulk delete both IDs
    bulk_res = client_b.post("/api/stories/bulk-delete", json={"story_ids": [story_a_id, story_b_id]})
    assert bulk_res.status_code == status.HTTP_200_OK
    assert bulk_res.json()["deleted_count"] == 1
    assert bulk_res.json()["deleted_ids"] == [story_b_id]

    # User A's story still exists
    assert client_a.get(f"/api/stories/{story_a_id}").status_code == status.HTTP_200_OK


def test_clear_all_only_deletes_current_user_stories(client_a: TestClient, client_b: TestClient):
    """Verify clear-all deletes only the requesting user's stories."""
    client_a.post("/api/stories", json={**SAMPLE_STORY_DATA, "title": "A Preserved Story"})
    client_b.post("/api/stories", json={**SAMPLE_STORY_DATA, "title": "B Story To Clear"})

    clear_res = client_b.post("/api/stories/clear-all")
    assert clear_res.status_code == status.HTTP_200_OK
    assert clear_res.json()["deleted_count"] == 1

    # User B has no stories
    assert len(client_b.get("/api/stories").json()) == 0

    # User A's story remains
    assert len(client_a.get("/api/stories").json()) == 1


# ============================================================================
# Legacy NULL-Owner Stories Tests
# ============================================================================

def test_legacy_null_owner_stories_remain_hidden_and_preserved(
    db_session: Session, client_a: TestClient
):
    """Verify legacy stories with user_id=None are not returned and cannot be modified by users."""
    legacy_story = Story(
        title="Legacy Unowned Chronicle",
        content="Ancient scroll from before user registration.",
        genre="Fantasy",
        mood="Mysterious",
        length="Short",
        user_id=None,
    )
    db_session.add(legacy_story)
    db_session.commit()
    db_session.refresh(legacy_story)
    legacy_id = legacy_story.id

    # User A lists stories &rarr; legacy story is NOT returned
    list_res = client_a.get("/api/stories")
    assert list_res.status_code == status.HTTP_200_OK
    legacy_titles = [s["title"] for s in list_res.json()]
    assert "Legacy Unowned Chronicle" not in legacy_titles

    # User A attempts to get legacy story by ID &rarr; 404
    assert client_a.get(f"/api/stories/{legacy_id}").status_code == status.HTTP_404_NOT_FOUND

    # User A attempts to delete legacy story &rarr; 404
    assert client_a.delete(f"/api/stories/{legacy_id}").status_code == status.HTTP_404_NOT_FOUND

    # User A clear-all &rarr; legacy story remains in database
    client_a.post("/api/stories/clear-all")
    raw_story = db_session.get(Story, legacy_id)
    assert raw_story is not None
    assert raw_story.title == "Legacy Unowned Chronicle"


# ============================================================================
# Unauthenticated Requests Rejection Tests
# ============================================================================

def test_unauthenticated_requests_cannot_access_story_endpoints(unauth_client: TestClient):
    """Verify unauthenticated requests to story endpoints return 401 Unauthorized."""
    # List
    assert unauth_client.get("/api/stories").status_code == status.HTTP_401_UNAUTHORIZED

    # Get by ID
    assert unauth_client.get("/api/stories/1").status_code == status.HTTP_401_UNAUTHORIZED

    # Create
    assert unauth_client.post("/api/stories", json=SAMPLE_STORY_DATA).status_code == status.HTTP_401_UNAUTHORIZED

    # Generate
    gen_payload = {"prompt": "Test prompt", "genre": "Fantasy", "mood": "Mysterious", "length": "Short"}
    assert unauth_client.post("/api/stories/generate", json=gen_payload).status_code == status.HTTP_401_UNAUTHORIZED

    # Delete
    assert unauth_client.delete("/api/stories/1").status_code == status.HTTP_401_UNAUTHORIZED

    # Bulk delete
    assert unauth_client.post("/api/stories/bulk-delete", json={"story_ids": [1]}).status_code == status.HTTP_401_UNAUTHORIZED

    # Clear all
    assert unauth_client.post("/api/stories/clear-all").status_code == status.HTTP_401_UNAUTHORIZED
