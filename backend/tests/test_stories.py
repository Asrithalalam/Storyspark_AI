"""Tests for Phase 3 Story Storage and SQLite integration."""

import os
import tempfile
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.story import Story


SAMPLE_STORY_PAYLOAD = {
    "title": "The Whispering Pines",
    "content": "Deep in the enchanted woods, the ancient pine trees murmured secrets to travelers who listened with an open heart. A lone wanderer discovered an ancient stone lantern that flickered without oil.",
    "prompt": "A magical tale about whispering trees and a lost traveler.",
    "image_filename": "forest_lantern.png",
    "genre": "Fantasy",
    "mood": "Mysterious",
    "length": "Medium",
}


def test_1_database_is_created_successfully(test_engine):
    """Requirement 1: Verify the SQLite database and 'stories' table are created successfully."""
    inspector = inspect(test_engine)
    table_names = inspector.get_table_names()
    assert "stories" in table_names

    columns = {col["name"]: col for col in inspector.get_columns("stories")}
    required_cols = [
        "id", "title", "content", "prompt", "image_filename",
        "genre", "mood", "length", "created_at"
    ]
    for col in required_cols:
        assert col in columns, f"Column '{col}' must exist in 'stories' table"

    # Verify primary key
    pk = inspector.get_pk_constraint("stories")
    assert pk["constrained_columns"] == ["id"]


def test_2_sample_story_can_be_saved(client: TestClient):
    """Requirement 2: Verify a sample story can be created via POST /api/stories."""
    response = client.post("/api/stories", json=SAMPLE_STORY_PAYLOAD)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["title"] == SAMPLE_STORY_PAYLOAD["title"]
    assert data["content"] == SAMPLE_STORY_PAYLOAD["content"]
    assert data["prompt"] == SAMPLE_STORY_PAYLOAD["prompt"]
    assert data["image_filename"] == SAMPLE_STORY_PAYLOAD["image_filename"]
    assert data["genre"] == SAMPLE_STORY_PAYLOAD["genre"]
    assert data["mood"] == SAMPLE_STORY_PAYLOAD["mood"]
    assert data["length"] == SAMPLE_STORY_PAYLOAD["length"]
    assert "id" in data
    assert "created_at" in data


def test_3_saved_story_receives_unique_id(client: TestClient):
    """Requirement 3: Verify each saved story receives a unique identifier."""
    story1_payload = {**SAMPLE_STORY_PAYLOAD, "title": "First Unique Tale"}
    story2_payload = {**SAMPLE_STORY_PAYLOAD, "title": "Second Unique Tale"}

    res1 = client.post("/api/stories", json=story1_payload)
    res2 = client.post("/api/stories", json=story2_payload)

    assert res1.status_code == status.HTTP_201_CREATED
    assert res2.status_code == status.HTTP_201_CREATED

    id1 = res1.json()["id"]
    id2 = res2.json()["id"]

    assert isinstance(id1, int)
    assert isinstance(id2, int)
    assert id1 != id2


def test_4_all_stories_can_be_listed(client: TestClient):
    """Requirement 4: Verify stories can be listed with history sidebar fields, newest first."""
    # Create two stories to list
    res1 = client.post("/api/stories", json={**SAMPLE_STORY_PAYLOAD, "title": "Older Story"})
    assert res1.status_code == status.HTTP_201_CREATED
    res2 = client.post("/api/stories", json={**SAMPLE_STORY_PAYLOAD, "title": "Newer Story"})
    assert res2.status_code == status.HTTP_201_CREATED

    res_list = client.get("/api/stories")
    assert res_list.status_code == status.HTTP_200_OK

    stories = res_list.json()
    assert isinstance(stories, list)
    assert len(stories) >= 2

    # Verify history sidebar required fields on each story item
    first_item = stories[0]
    required_keys = ["id", "title", "genre", "mood", "length", "content", "content_preview", "created_at"]
    for key in required_keys:
        assert key in first_item, f"Expected key '{key}' in story list item"

    # Verify newest first sorting (res2 title is "Newer Story")
    assert stories[0]["title"] == "Newer Story"
    assert stories[1]["title"] == "Older Story"


def test_5_single_story_can_be_retrieved(client: TestClient):
    """Requirement 5: Verify a single story can be retrieved by ID."""
    # First create a story
    create_res = client.post("/api/stories", json=SAMPLE_STORY_PAYLOAD)
    assert create_res.status_code == status.HTTP_201_CREATED
    story_id = create_res.json()["id"]

    # Retrieve the story
    get_res = client.get(f"/api/stories/{story_id}")
    assert get_res.status_code == status.HTTP_200_OK
    story_data = get_res.json()
    assert story_data["id"] == story_id
    assert story_data["title"] == SAMPLE_STORY_PAYLOAD["title"]
    assert story_data["content"] == SAMPLE_STORY_PAYLOAD["content"]


def test_6_story_can_be_deleted(client: TestClient):
    """Requirement 6: Verify a story can be deleted by ID."""
    # Create story to delete
    create_res = client.post("/api/stories", json=SAMPLE_STORY_PAYLOAD)
    story_id = create_res.json()["id"]

    # Delete story
    del_res = client.delete(f"/api/stories/{story_id}")
    assert del_res.status_code == status.HTTP_200_OK
    del_data = del_res.json()
    assert del_data["id"] == story_id
    assert "deleted" in del_data["message"].lower()

    # Verify it can no longer be retrieved
    get_res = client.get(f"/api/stories/{story_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND


def test_7_retrieving_nonexistent_story_returns_404(client: TestClient):
    """Requirement 7: Verify requesting a nonexistent ID returns HTTP 404."""
    response = client.get("/api/stories/99999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_8_deleting_nonexistent_story_returns_404(client: TestClient):
    """Requirement 8: Verify deleting a nonexistent ID returns HTTP 404."""
    response = client.delete("/api/stories/99999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_9_stories_remain_available_after_restarting_backend():
    """Requirement 9: Verify stories persist to SQLite file across backend shutdown and restart."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        tmp_db_path = tmp_file.name

    try:
        db_url = f"sqlite:///{tmp_db_path}"

        # --- SESSION 1: Startup backend, create tables, save a story ---
        engine1 = create_engine(db_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine1)
        Session1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)

        def get_db_1():
            db = Session1()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = get_db_1
        with TestClient(app) as client1:
            post_res = client1.post("/api/stories", json={
                **SAMPLE_STORY_PAYLOAD,
                "title": "Story That Survives Server Restart",
            })
            assert post_res.status_code == status.HTTP_201_CREATED
            persisted_id = post_res.json()["id"]

        # --- SIMULATE RESTART: Disconnect engine1, clear overrides ---
        engine1.dispose()
        app.dependency_overrides.clear()

        # --- SESSION 2: Brand new startup, reconnect to exact same SQLite file ---
        engine2 = create_engine(db_url, connect_args={"check_same_thread": False})
        Session2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)

        def get_db_2():
            db = Session2()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = get_db_2
        with TestClient(app) as client2:
            get_res = client2.get(f"/api/stories/{persisted_id}")
            assert get_res.status_code == status.HTTP_200_OK
            retrieved_data = get_res.json()
            assert retrieved_data["id"] == persisted_id
            assert retrieved_data["title"] == "Story That Survives Server Restart"

        engine2.dispose()
        app.dependency_overrides.clear()
    finally:
        if os.path.exists(tmp_db_path):
            os.remove(tmp_db_path)


def test_10_existing_health_endpoint_still_works(client: TestClient):
    """Requirement 10: Verify the Phase 2 /api/health endpoint still functions properly."""
    response = client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert "StorySpark AI backend is running" in data["message"]
    assert "timestamp" in data


def test_11_input_validation_rejects_empty_and_missing_fields(client: TestClient):
    """Verify input validation: whitespace-only fields or missing required fields return 422."""
    # Missing required 'content'
    res_missing = client.post("/api/stories", json={
        "title": "A Title Without Content",
        "genre": "Fantasy",
        "mood": "Calm",
        "length": "Short",
    })
    assert res_missing.status_code == 422

    # Whitespace-only title
    res_whitespace = client.post("/api/stories", json={
        **SAMPLE_STORY_PAYLOAD,
        "title": "   ",
    })
    assert res_whitespace.status_code == 422
