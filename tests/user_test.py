from tests.conftest import user_data


def test_create_user(client):
    response = client.post(
        "/user/",
        json={
            "first_name": "test",
            "last_name": "test",
            "email": "tests@example.com",
            "password": "sString123",
        },
    )
    assert response.status_code == 201
    result = response.json()
    result.pop("id")
    assert result == {
        "first_name": "Test",
        "last_name": "Test",
        "email": "tests@example.com",
    }


def test_login(client, user_data):
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"],
    }
    login_response = client.post("/auth/login/", data=login_data)
    assert login_response.status_code == 200
    assert login_response.json()["access_token"]
    assert login_response.json()["token_type"] == "bearer"


def test_user_get_by_id(client):
    response = client.get("/user/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "first_name": "Test",
        "last_name": "Test",
        "email": "tests@example.com",
    }


def test_user_get_all(client):
    response = client.get("/user/list/")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "first_name": "Test",
            "last_name": "Test",
            "email": "tests@example.com",
        }
    ]


def test_user_update(client, user_data):
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"],
    }
    login_response = client.post("/auth/login/", data=login_data)
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        "/user/1",
        json={
            "first_name": "Tests",
            "last_name": "Tests",
        },
        headers=headers,
    )
    assert response.status_code == 200, f"Update failed: {response.text}"
    assert response.json() == {
        "first_name": "Tests",
        "last_name": "Tests",
    }


def test_user_delete(client, user_data):
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"],
    }
    login_response = client.post("/auth/login/", data=login_data)

    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/user/1", headers=headers)
    assert response.status_code == 204, f"Failed to delete user: {response.text}"
