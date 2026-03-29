"""Functional tests for auth endpoints."""


def test_login_success(client, admin_user):
    res = client.post(
        "/auth/login",
        json={
            "username": "testadmin",
            "password": "password123",
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["role"] == "admin"


def test_login_wrong_password(client, admin_user):
    res = client.post(
        "/auth/login",
        json={
            "username": "testadmin",
            "password": "wrongpassword",
        },
    )
    assert res.status_code == 401
    assert res.get_json()["success"] is False


def test_login_nonexistent_user(client):
    res = client.post(
        "/auth/login",
        json={
            "username": "nobody",
            "password": "password123",
        },
    )
    assert res.status_code == 401


def test_login_missing_fields(client):
    res = client.post("/auth/login", json={"username": "testadmin"})
    assert res.status_code == 400


def test_me_with_token(client, admin_token):
    res = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {admin_token}",
        },
    )
    assert res.status_code == 200
    assert res.get_json()["data"]["username"] == "testadmin"


def test_me_without_token(client):
    res = client.get("/auth/me")
    assert res.status_code == 401


def test_logout(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Logout
    res = client.post("/auth/logout", headers=headers)
    assert res.status_code == 200

    # Token should be blacklisted
    res = client.get("/auth/me", headers=headers)
    assert res.status_code == 401
