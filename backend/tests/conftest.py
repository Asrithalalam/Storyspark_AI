"""Pytest fixtures and configuration for StorySpark AI backend tests."""

import os
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory) -> str:
    """Create a temporary SQLite database file for isolation from development data."""
    tmp_dir = tmp_path_factory.mktemp("db")
    db_file = tmp_dir / "test_storyspark.db"
    return str(db_file)


@pytest.fixture(scope="session")
def test_engine(test_db_path: str):
    """Create a SQLAlchemy engine attached to the temporary test database."""
    engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Provide a transactional database session for each test function."""
    connection = test_engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection,
    )
    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with overridden get_db dependency."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
