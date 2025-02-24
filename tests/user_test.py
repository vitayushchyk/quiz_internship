def test_create_user(client):
    response = client.post(
        "/user/",
        json={
            "first_name": "test_create",
            "last_name": "user",
            "email": "create_user@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201, f"Error: {response.text}"
    result = response.json()
    result.pop("id")
    assert result == {
        "first_name": "test_create",
        "last_name": "user",
        "email": "create_user@example.com",
    }


def test_login(client):
    response = client.post(
        "/user/",
        json={
            "first_name": "login",
            "last_name": "user",
            "email": "login_user@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201, f"Error: {response.text}"

    login_data = {
        "username": "login_user@example.com",
        "password": "password123",
    }
    login_response = client.post("/auth/login/", data=login_data)
    assert login_response.status_code == 200, f"Error: {login_response.text}"
    assert login_response.json()["access_token"]
    assert login_response.json()["token_type"] == "bearer"


def test_user_get_by_id(client):
    response = client.post(
        "/user/",
        json={
            "first_name": "get_by_id",
            "last_name": "user",
            "email": "get_user@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201, f"Error: {response.text}"
    user_id = response.json()["id"]

    response = client.get(f"/user/{user_id}")
    assert response.status_code == 200, f"Error: {response.text}"
    assert response.json() == {
        "id": user_id,
        "first_name": "get_by_id",
        "last_name": "user",
        "email": "get_user@example.com",
    }


def test_user_get_all(client):
    for email in ["user1@example.com", "user2@example.com"]:
        response = client.post(
            "/user/",
            json={
                "first_name": "all_users",
                "last_name": "user",
                "email": email,
                "password": "password123",
            },
        )
        assert response.status_code == 201, f"Error: {response.text}"

    response = client.get("/user/")
    assert response.status_code == 200, f"Error: {response.text}"
    users = response.json()
    assert len(users) >= 2
    emails = [user["email"] for user in users]
    assert "user1@example.com" in emails
    assert "user2@example.com" in emails


def test_user_update(client):
    response = client.post(
        "/user/",
        json={
            "first_name": "old_first_name",
            "last_name": "old_last_name",
            "email": "update_user@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201, f"Error: {response.text}"
    user_id = response.json()["id"]

    login_data = {
        "username": "update_user@example.com",
        "password": "password123",
    }
    login_response = client.post("/auth/login/", data=login_data)
    assert login_response.status_code == 200, f"Error: {login_response.text}"
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        f"/user/{user_id}",
        json={
            "first_name": "Name",
            "last_name": "Name",
        },
        headers=headers,
    )
    assert response.status_code == 200, f"Update failed: {response.text}"
    assert response.json() == {
        "first_name": "Name",
        "last_name": "Name",
    }


def test_user_delete(client):
    response = client.post(
        "/user/",
        json={
            "first_name": "delete",
            "last_name": "user",
            "email": "delete_user@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201, f"Error: {response.text}"
    user_id = response.json()["id"]
    login_data = {
        "username": "delete_user@example.com",
        "password": "password123",
    }
    login_response = client.post("/auth/login/", data=login_data)
    assert login_response.status_code == 200, f"Error: {login_response.text}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(f"/user/{user_id}", headers=headers)
    assert response.status_code == 204
