from starlette import status
from conftest import register, login_token

"""
Fixture behavior used in this file:

client:
    Provides a fresh test client with a clean test database per test.

auth_client:
    Same as client, but with a default Authorization header already set
    (authenticated user).

ticket:
    Creates exactly one ticket in the database for the authenticated user
    and returns its JSON representation.

two_users_headers:
    Registers + logs in two users ("bob" and "sam") and returns their
    Authorization headers.
"""


def test_register_success(client):
    # Arrange
    username = "bob"
    password = "abc123"
    # Act
    r = register(client, username, password)
    # Assert
    # 201 means the user was created successfully.
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    # The response should include a generated primary key for the new user.
    assert "id" in data
    # The created user's username should match the one we sent.
    assert data["username"] == username
    # The API should never return plaintext passwords.
    assert "password" not in data
    # The API should also never return hashed passwords.
    assert "hashed_password" not in data


def test_register_failure(client):
    # Arrange
    # Not providing a password
    username = "bob"
    # Act
    r = register(client, username)
    # Assert
    # 422 means FastAPI rejected the request body because required fields are missing/invalid.
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_login_token_success(client):
    # Arrange
    reg_r = register(client, "bob", "abc123")
    # If registration failed, the login test would fail for the wrong reason.
    assert reg_r.status_code == status.HTTP_201_CREATED
    # Act
    log_r = login_token(client, "bob", "abc123")
    # Assert
    # 200 means credentials were accepted and a token was issued.
    assert log_r.status_code == status.HTTP_200_OK
    data = log_r.json()
    # Access token is required for authenticated requests.
    assert "access_token" in data
    # Token type is included so clients know how to format the Authorization header.
    assert "token_type" in data
    # OAuth2PasswordBearer expects "Authorization: Bearer <token>".
    assert data["token_type"] == "bearer"
    # Token should be a string (JWT is transmitted as text).
    assert isinstance(data["access_token"], str)
    # Token should not be empty.
    assert data["access_token"]


def test_login_token_unauthorized(client):
    # Arrange
    reg_r = register(client, "bob", "abc123")
    # Ensure the user exists before attempting a bad login.
    assert reg_r.status_code == status.HTTP_201_CREATED
    # Act
    # Logging in with the wrong password
    log_r = login_token(client, "bob", "abc1234")
    # Assert
    # 401 means the credentials were invalid.
    assert log_r.status_code == status.HTTP_401_UNAUTHORIZED


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
    # 201 means the ticket was created successfully.
    assert r.status_code == status.HTTP_201_CREATED


def test_create_ticket_empty(auth_client):
    # Act
    r = auth_client.post(
        "/api/tickets/",
        json={}
    )
    # Assert
    # 422 means required fields were missing (TicketCreate validation failed).
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_ticket_priority_out_of_range(auth_client):
    # Act
    r = auth_client.post(
        "/api/tickets/",
        json={
                "title": "Computer problems",
                "description": "Computer turns off randomly after a few minutes",
                "priority": 0
        }
    )
    # Assert
    # 422 means the request failed validation (priority is outside allowed range).
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_ticket_priority_invalid_type(auth_client):
    # Act
    r = auth_client.post(
        "/api/tickets/",
        json={
                "title": "Computer problems",
                "description": "Computer turns off randomly after a few minutes",
                "priority": "abc"
        }
    )
    # Assert
    # 422 means the request failed validation (priority must be an int).
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_ticket_success(auth_client, ticket):
    # Act
    r = auth_client.patch(
        f"/api/tickets/{ticket['id']}",
        json={"status": "in_progress"}
    )
    # Assert
    # 200 means the update succeeded.
    assert r.status_code == status.HTTP_200_OK
    # Confirm the server actually updated the stored value.
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
    # 404 means there is no ticket with that ID (or the API hides inaccessible tickets).
    assert r.status_code == status.HTTP_404_NOT_FOUND
    # Confirm the API returns the expected error message for debugging/contract consistency.
    assert r.json()["detail"] == f"Ticket with ticket_id={invalid_id} does not exist"


def test_delete_ticket_success(auth_client, ticket):
    # Arrange
    ticket_id = ticket["id"]

    # Act - delete the ticket
    r = auth_client.delete(f"/api/tickets/{ticket_id}")
    # Assert - deletion succeeded
    # 200 means the delete request was accepted and processed.
    assert r.status_code == status.HTTP_200_OK

    # Act - attempt to retrieve deleted ticket
    r = auth_client.get(f"/api/tickets/{ticket_id}")
    # Assert - ticket no longer exists
    # 404 confirms the ticket was actually removed.
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_delete_ticket_failure(auth_client, ticket):
    # Arrange
    invalid_id = 2

    # Act - delete the ticket
    r = auth_client.delete(f"/api/tickets/{invalid_id}")
    # Assert - ticket does not exist
    # 404 means you cannot delete a ticket that isn't there.
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_tickets_success(auth_client, ticket):
    # Act
    r = auth_client.get("/api/tickets/")
    # Assert
    # 200 means the list endpoint returned successfully.
    assert r.status_code == status.HTTP_200_OK
    tickets = r.json()
    # Expect exactly one ticket, and it should match the one created by the fixture.
    # This checks both list length (1 item) and exact ticket contents.
    assert tickets == [ticket]


def test_get_all_tickets_unauthorized(client):
    # Act
    r = client.get("/api/tickets/")
    # Assert
    # 401 means the endpoint requires authentication and no valid token was provided.
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_ticket_by_id_success(auth_client, ticket):
    # Arrange
    ticket_id = ticket["id"]

    # Act
    r = auth_client.get(f"/api/tickets/{ticket_id}")
    # Assert
    # 200 means the ticket was found and returned.
    assert r.status_code == status.HTTP_200_OK
    # Exact match ensures no fields are missing/extra and values are correct.
    assert r.json() == ticket


def test_get_ticket_by_id_failure(auth_client, ticket):
    # Arrange
    invalid_id = 2

    # Act
    r = auth_client.get(f"/api/tickets/{invalid_id}")
    # Assert
    # 404 means there is no ticket with that ID (or the API hides inaccessible tickets).
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_get_ticket_by_id_unauthorized(client):
    # Act
    r = client.get(f"/api/tickets/1")
    # Assert
    # 401 means requests without a valid Authorization header are rejected.
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_search_for_ticket_success(auth_client, ticket):
    # Arrange
    search_term = "computer"

    # Act
    r = auth_client.get(f"/api/tickets/search?title={search_term}")
    # Assert
    # 200 means the search endpoint returned successfully.
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    # Confirm the first result matches the ticket created by the fixture.
    assert data[0]["title"] == ticket["title"]


def test_search_for_ticket_no_results(auth_client, ticket):
    # Arrange
    search_term = "abc"

    # Act
    r = auth_client.get(f"/api/tickets/search?title={search_term}")
    # Assert
    # 200 means the request succeeded even if there are no matches.
    assert r.status_code == status.HTTP_200_OK
    data = r.json()
    # No matches should return an empty list (not an error).
    assert len(data) == 0


def test_create_ticket_unauthorized(client):
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
    # 401 means you must be logged in to create a ticket.
    assert r.status_code == status.HTTP_401_UNAUTHORIZED

def test_multiple_users(client, two_users_headers):
    # Arrange
    bob = two_users_headers["bob"]
    sam = two_users_headers["sam"]

    # Act - Bob creates a ticket
    r1 = client.post(
        "/api/tickets/",
        json={
            "title": "Test1",
            "description": "Test1",
            "priority": 1
        },
        headers=bob
    )

    # Assert - Bob's ticket created successfully
    assert r1.status_code == status.HTTP_201_CREATED
    bob_ticket = r1.json()

    # Act - Sam creates a ticket
    r2 = client.post(
        "/api/tickets/",
        json={
            "title": "Test2",
            "description": "Test2",
            "priority": 2
        },
        headers=sam
    )

    # Assert - Sam's ticket created successfully
    assert r2.status_code == status.HTTP_201_CREATED
    sam_ticket = r2.json()

    # Act - Bob lists tickets
    rb = client.get("/api/tickets/", headers=bob)
    # Assert - Bob only sees his tickets
    assert rb.status_code == status.HTTP_200_OK
    bob_list = rb.json()
    # All Bob's tickets should have the same user_id
    # all(...) ensures EVERY returned ticket belongs to Bob.
    assert all(t["user_id"] == bob_ticket["user_id"] for t in bob_list)
    # Bob should be able to see their own ticket
    # any(...) ensures at least one returned ticket is Bob's created ticket.
    assert any(t["id"] == bob_ticket["id"] for t in bob_list)
    # Bob does not see Sam's ticket
    # Ensures no ticket in Bob's list matches Sam's ticket ID.
    assert all(t["id"] != sam_ticket["id"] for t in bob_list)

    # Act - Sam lists tickets
    rs = client.get("/api/tickets/", headers=sam)

    # Assert - Sam only sees his tickets
    assert rs.status_code == status.HTTP_200_OK
    sam_list = rs.json()
    # All Sam's tickets should have the same user_id
    # all(...) ensures EVERY returned ticket belongs to Sam.
    assert all(t["user_id"] == sam_ticket["user_id"] for t in sam_list)
    # Sam should be able to see their own ticket
    # any(...) ensures at least one returned ticket is Sam's created ticket.
    assert any(t["id"] == sam_ticket["id"] for t in sam_list)
    # Sam does not see Bob's ticket
    # Ensures no ticket in Sam's list matches Bob's ticket ID.
    assert all(t["id"] != bob_ticket["id"] for t in sam_list)


    # Act - Bob tries to access Sam's ticket directly
    rb_failure = client.get(f"/api/tickets/{sam_ticket['id']}", headers=bob)
    # Assert - API does not expose other users' tickets (returns 404)
    # 404 here means Bob cannot retrieve Sam's ticket by ID.
    assert rb_failure.status_code == status.HTTP_404_NOT_FOUND

    # Act - Sam tries to access Bob's ticket directly
    rs_failure = client.get(f"/api/tickets/{bob_ticket['id']}", headers=sam)
    # Assert - API does not expose other users' tickets (returns 404)
    # 404 here means Sam cannot retrieve Bob's ticket by ID.
    assert rs_failure.status_code == status.HTTP_404_NOT_FOUND


def test_update_ticket_ownership_enforced(client, two_users_headers):
    # Arrange
    bob = two_users_headers["bob"]
    sam = two_users_headers["sam"]

    # Bob creates ticket
    bob_r = client.post(
        "/api/tickets/",
        json={"title": "Bob", "description": "Bob", "priority": 1},
        headers=bob
    )
    assert bob_r.status_code == status.HTTP_201_CREATED
    bob_ticket = bob_r.json()

    # Sam creates ticket
    sam_r = client.post(
        "/api/tickets/",
        json={"title": "Sam", "description": "Sam", "priority": 2},
        headers=sam
    )
    assert sam_r.status_code == status.HTTP_201_CREATED
    sam_ticket = sam_r.json()

    # Act - Bob tries to update Sam's ticket
    r = client.patch(
        f"/api/tickets/{sam_ticket['id']}",
        json={"status": "closed"},
        headers=bob
    )

    # Assert - API does not expose other users' tickets (returns 404)
    # 404 here means Bob cannot update Sam's ticket.
    assert r.status_code == status.HTTP_404_NOT_FOUND

    # Act - Sam tries to update Bob's ticket
    r = client.patch(
        f"/api/tickets/{bob_ticket['id']}",
        json={"status": "closed"},
        headers=sam
    )

   # Assert - API does not expose other users' tickets (returns 404)
    # 404 here means Sam cannot update Bob's ticket.
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_delete_ticket_ownership_enforced(client, two_users_headers):
    # Arrange
    bob = two_users_headers["bob"]
    sam = two_users_headers["sam"]

    # Bob creates ticket
    bob_r = client.post(
        "/api/tickets/",
        json={"title": "Bob", "description": "Bob", "priority": 1},
        headers=bob
    )
    assert bob_r.status_code == status.HTTP_201_CREATED
    bob_ticket = bob_r.json()

    # Sam creates ticket
    sam_r = client.post(
        "/api/tickets/",
        json={"title": "Sam", "description": "Sam", "priority": 2},
        headers=sam
    )
    assert sam_r.status_code == status.HTTP_201_CREATED
    sam_ticket = sam_r.json()

    # Act - Bob tries to delete Sam's ticket
    r = client.delete(f"/api/tickets/{sam_ticket['id']}", headers=bob)

    # Assert - API does not expose other users' tickets (returns 404)
    # 404 here means Bob cannot delete Sam's ticket.
    assert r.status_code == status.HTTP_404_NOT_FOUND

    # Act - Sam tries to delete Bob's ticket
    r = client.delete(f"/api/tickets/{bob_ticket['id']}", headers=sam)

    # Assert - API does not expose other users' tickets (returns 404)
    # 404 here means Sam cannot delete Bob's ticket.
    assert r.status_code == status.HTTP_404_NOT_FOUND

    # Assert tickets still exist for their owners
    rb = client.get(f"/api/tickets/{bob_ticket['id']}", headers=bob)
    # Owner can still retrieve their own ticket after the other user's delete attempt.
    assert rb.status_code == status.HTTP_200_OK

    rs = client.get(f"/api/tickets/{sam_ticket['id']}", headers=sam)
    # Owner can still retrieve their own ticket after the other user's delete attempt.
    assert rs.status_code == status.HTTP_200_OK