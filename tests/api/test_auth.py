import uuid

from fastapi.testclient import TestClient

from app.main import create_app


def unique_email() -> str:
    return f"user-{uuid.uuid4()}@example.com"


def test_register_login_and_me_flow() -> None:
    client = TestClient(create_app())
    email = unique_email()
    password = "SuperSecret123!"

    register_response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201
    register_data = register_response.json()
    assert register_data["email"] == email
    assert register_data["is_active"] is True

    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == email


def test_register_duplicate_email_returns_409() -> None:
    client = TestClient(create_app())
    email = unique_email()
    password = "SuperSecret123!"

    first = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert first.status_code == 201

    second = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert second.status_code == 409


def test_login_with_wrong_password_returns_401() -> None:
    client = TestClient(create_app())
    email = unique_email()

    register_response = client.post(
        "/auth/register",
        json={"email": email, "password": "CorrectPassword123!"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": "WrongPassword123!"},
    )
    assert login_response.status_code == 401
