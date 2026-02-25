from conftest import register, login_token
from starlette import status


def test_register(client):
    # Act
   r = register(client, "bob", "abc123")
   # Assert
   assert r.status_code == status.HTTP_201_CREATED

def test_login_token(client):
    # Arrange
    r = register(client, "bob", "abc123")
    r = login_token(client, "bob", "abc123")
    # Act
    token = r.json()["access_token"]
    # Assert
    assert isinstance(token, str)
    assert token


def test_create_ticket(auth_client):
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

def test_update_ticket(auth_client, ticket):
    # Act
    r = auth_client.patch(
        f"/api/tickets/{ticket['id']}",
        json={
                "status": "in_progress"
            }
    )
    # Assert
    assert r.json()["status"] == "in_progress"
    assert r.status_code == status.HTTP_200_OK

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