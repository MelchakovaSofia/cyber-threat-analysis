import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest
from fastapi.testclient import TestClient

from app.database.session import Base, engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    # For tests, use create_all for simplicity
    # For production, use Alembic migrations
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def admin_token(client):
    client.post(
        "/api/auth/register",
        json={
            "login": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "role": "admin",
        },
    )
    response = client.post("/api/auth/login", json={"login": "admin", "password": "admin123"})
    return response.json()["access_token"]
