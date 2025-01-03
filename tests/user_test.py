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


def test_login(client):
    response = client.post(
        "/auth/login/",
        json={
            "email": "tests@example.com",
            "password": "sString123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get("access_token") is not None
    assert data.get("token_type") == "bearer"


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


def test_user_update(client):
    response = client.put(
        "/user/1",
        json={
            "first_name": "Tests",
            "last_name": "Tests",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "first_name": "Tests",
        "last_name": "Tests",
    }


def test_user_delete(client):
    response = client.delete("/user/1")
    assert response.status_code == 204
