def test_health(client):
    response = client.get("/health").json()
    assert response["status"] == "ok"
    assert "environment" in response


def test_login_and_me(client, admin_token):
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["login"] == "admin"


def test_login_with_wrong_password(client, admin_token):
    response = client.post("/api/auth/login", json={"login": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_protected_endpoint_requires_token(client):
    assert client.get("/api/logs").status_code == 401
