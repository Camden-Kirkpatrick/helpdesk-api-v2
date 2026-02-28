import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from app.main import app
from app.db import get_session
from starlette import status

def register(client, username: str | None = None, password: str | None = None):
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

    reg_r = register(client, username, password)
    assert reg_r.status_code == status.HTTP_201_CREATED

    log_r = login_token(client, username, password)
    assert log_r.status_code == status.HTTP_200_OK

    return log_r.json()["access_token"]


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


@pytest.fixture
def two_users_headers(client) -> dict:
    reg1 = register(client, "bob", "abc123")
    reg2 = register(client, "sam", "def456")
    assert reg1.status_code == status.HTTP_201_CREATED
    assert reg2.status_code == status.HTTP_201_CREATED

    log1 = login_token(client, "bob", "abc123")
    log2 = login_token(client, "sam", "def456")
    assert log1.status_code == status.HTTP_200_OK
    assert log2.status_code == status.HTTP_200_OK

    token1 = log1.json()["access_token"]
    token2 = log2.json()["access_token"]

    header1 = {"Authorization": f"Bearer {token1}"}
    header2 = {"Authorization": f"Bearer {token2}"}

    return {"bob": header1, "sam": header2}