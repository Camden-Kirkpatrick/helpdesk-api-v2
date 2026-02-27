from conftest import register, login_token
from starlette import status


def test_register(client):
    # Act
    r = register(client, "bob", "abc123")
    # Assert
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    assert "id" in data
    assert data["username"] == "bob"
    assert "password" not in data
    assert "hashed_password" not in data

def test_login_token(client):
    # Arrange
    r = register(client, "bob", "abc123")
    r = login_token(client, "bob", "abc123")
    # Assert
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["access_token"]


def test_create_ticket_success(auth_client):
    # Act
    r = auth_client.post(
        "/api/tickets/",
        json={
                "title": "Computer problems",
                "description": "Computer turns off randomly after a few minutes",
                "priority": 4
            }
    )
    # Assert
    assert r.status_code == status.HTTP_201_CREATED


def test_create_ticket_failure(auth_client):
    # Act
    r = auth_client.post(
        "/api/tickets/",
        json={}
    )
    # Assert
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_ticket_success(auth_client, ticket):
    # Act
    r = auth_client.patch(
        f"/api/tickets/{ticket['id']}",
        json={
                "status": "in_progress"
            }
    )
    # Assert
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["status"] == "in_progress"


def test_update_ticket_failure(auth_client, ticket):
    # Arrange
    invalid_id = 2
    # Act
    r = auth_client.patch(
        f"/api/tickets/{invalid_id}",
        json={
                "status": "in_progress"
            }
    )
    # Assert
    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert r.json()["detail"] == f"Ticket with ticket_id={invalid_id} does not exist"


def test_delete_ticket(auth_client, ticket):
    # Act
    r = auth_client.delete(
        f"/api/tickets/{ticket['id']}"
    )
    # Assert
    assert r.status_code == status.HTTP_200_OK
    # Get the ticket to see if it was deleted
    r = auth_client.get(f"/api/tickets/{ticket['id']}")
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_tickets(auth_client, ticket):
    # Act
    r = auth_client.get("/api/tickets/")
    # Assert
    assert r.status_code == status.HTTP_200_OK
    tickets = r.json()
    assert isinstance(tickets, list)
    assert len(tickets) == 1
    assert r.json()[0]["id"] == 1
    assert r.json()[0]["title"] == "Computer problems"
    assert r.json()[0]["description"] == "Computer turns off randomly after a few minutes"
    assert r.json()[0]["priority"] == 4
    assert r.json()[0]["status"] == "open"
    assert r.json()[0]["user_id"] == 1


def test_get_ticket_by_id_success(auth_client, ticket):
    # Act
    r = auth_client.get(f"/api/tickets/{ticket['id']}")
    # Assert
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data["id"] == ticket["id"]
    assert data["title"] == ticket["title"]
    assert data["description"] == ticket["description"]
    assert data["priority"] == ticket["priority"]
    assert data["status"] == ticket["status"]
    assert data["user_id"] == ticket["user_id"]


def test_get_ticket_by_id_failure(auth_client, ticket):
    # Arrange
    invalid_id = 2
    # Act
    r = auth_client.get(f"/api/tickets/{invalid_id}")
    # Assert
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_search_for_ticket_success(auth_client, ticket):
    # Arrange
    search_term = "computer"
    # Act
    r = auth_client.get(f"/api/tickets/search?title={search_term}")
    # Assert
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert data[0]["title"] == ticket["title"]


def test_search_for_ticket_no_results(auth_client, ticket):
    # Arrange
    search_term = "abc"
    # Act
    r = auth_client.get(f"/api/tickets/search?title={search_term}")
    # Assert
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    assert len(data) == 0


def test_create_ticket_requires_auth(client):
    # Act
    r = client.post(
        "/api/tickets/",
        json={
            "title": "Test",
            "description": "Test",
            "priority": 1
        }
    )
    # Assert
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

def test_multiple_users(client, two_users_headers):
    # Arrange
    bob = two_users_headers["bob"]
    sam = two_users_headers["sam"]

    # Act
    r1 = client.post(
        "/api/tickets/",
        json={
            "title": "Test1",
            "description": "Test1",
            "priority": 1
        },
        headers=bob
    )
    r2 = client.post(
        "/api/tickets/",
        json={
            "title": "Test2",
            "description": "Test2",
            "priority": 2
        },
        headers=sam
    )
    # Assert
    assert r1.status_code == status.HTTP_201_CREATED
    assert r2.status_code == status.HTTP_201_CREATED