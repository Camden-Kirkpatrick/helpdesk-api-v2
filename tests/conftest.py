import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from app.main import app
from app.db import get_session
from starlette import status

def register(client, username: str, password: str):
    return client.post("/auth/", json={"username": username, "password": password})

def login_token(client, username: str, password: str):
    return client.post("/auth/token", json={"username": username, "password": password})


TEST_DB_URL = "sqlite:///test_database.db"

@pytest.fixture
def client():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})

    # Delete all tables and create them all again for a fresh database
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    # Create a session with the new database
    def override_get_session():
        with Session(engine) as session:
            yield session
    
    # Use "override_get_session" instead of "get_session"
    app.dependency_overrides[get_session] = override_get_session

    # Pass the test client to the test
    with TestClient(app) as c:
        yield c

    # Remove all test dependency overrides so they don't affect other tests
    app.dependency_overrides.clear()

@pytest.fixture
def token(client) -> str:
    username = "bob"
    password = "abc123"
    register(client, username, password)

    r = login_token(client, username, password)
    return r.json()["access_token"]

@pytest.fixture
def auth_headers(token) -> dict:
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_client(client, auth_headers):
    client.headers.update(auth_headers)
    return client

@pytest.fixture
def ticket(auth_client):
    r = auth_client.post(
        "/api/tickets/",
        json={
                "title": "Computer problems",
                "description": "Computer turns off randomly after a few minutes",
                "priority": 4
        }
    )
    assert r.status_code == status.HTTP_201_CREATED
    return r.json()