def register(client, username: str, password: str):
    r = client.post("/auth/", json={"username": username, "password": password})
    assert r.status_code == 201

def login_token(client, username: str, password: str) -> str:
    r = client.post("/auth/token", json={"username": username, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]

def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

def test_create_ticket(client):
    register(client, "nedmac", "abc123")
    token = login_token(client, "nedmac", "abc123")

    r = client.post(
        "/api/tickets/",
        json={
                "title": "Computer problems",
                "description": "Computer turns off randomly after a few minutes",
                "priority": 4
            },
        headers=auth_headers(token)
    )

    assert r.status_code == 201