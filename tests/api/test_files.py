import io
import uuid

from fastapi.testclient import TestClient

from app.main import create_app


def unique_email() -> str:
    return f"user-{uuid.uuid4()}@example.com"


def register_and_login(client: TestClient) -> tuple[str, int]:
    email = unique_email()
    password = "SuperSecret123!"

    register_response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return token, user_id


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_upload_and_list_files() -> None:
    client = TestClient(create_app())
    token, user_id = register_and_login(client)

    upload_response = client.post(
        "/files",
        headers=auth_headers(token),
        files={"file": ("sample.jpg", io.BytesIO(b"fake-image-bytes"), "image/jpeg")},
    )
    assert upload_response.status_code == 201
    uploaded = upload_response.json()

    assert uploaded["owner_id"] == user_id
    assert uploaded["original_filename"] == "sample.jpg"
    assert uploaded["content_type"] == "image/jpeg"
    assert uploaded["storage_key"].startswith("uploads/")
    assert uploaded["storage_uri"].startswith("file://")

    list_response = client.get("/files", headers=auth_headers(token))
    assert list_response.status_code == 200
    items = list_response.json()
    assert len(items) >= 1
    assert items[0]["owner_id"] == user_id


def test_non_image_upload_is_rejected() -> None:
    client = TestClient(create_app())
    token, _ = register_and_login(client)

    response = client.post(
        "/files",
        headers=auth_headers(token),
        files={"file": ("sample.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Only image uploads are supported."


def test_file_access_is_owner_scoped() -> None:
    client = TestClient(create_app())

    token_a, _ = register_and_login(client)
    token_b, _ = register_and_login(client)

    upload_response = client.post(
        "/files",
        headers=auth_headers(token_a),
        files={"file": ("a.jpg", io.BytesIO(b"fake-image-bytes"), "image/jpeg")},
    )
    assert upload_response.status_code == 201
    file_id = upload_response.json()["id"]

    get_as_other = client.get(f"/files/{file_id}", headers=auth_headers(token_b))
    assert get_as_other.status_code == 404

    delete_as_other = client.delete(f"/files/{file_id}", headers=auth_headers(token_b))
    assert delete_as_other.status_code == 404


def test_delete_file() -> None:
    client = TestClient(create_app())
    token, _ = register_and_login(client)

    upload_response = client.post(
        "/files",
        headers=auth_headers(token),
        files={"file": ("to-delete.jpg", io.BytesIO(b"fake-image-bytes"), "image/jpeg")},
    )
    assert upload_response.status_code == 201
    file_id = upload_response.json()["id"]

    delete_response = client.delete(f"/files/{file_id}", headers=auth_headers(token))
    assert delete_response.status_code == 204

    get_response = client.get(f"/files/{file_id}", headers=auth_headers(token))
    assert get_response.status_code == 404
