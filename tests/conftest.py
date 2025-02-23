import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def user_data():
    return {
        "username": "string@example.com",
        "password": "string123",
    }


@pytest.fixture
def test_user(client):
    user_data = {
        "first_name": "Test",
        "last_name": "Testivich",
        "email": "Testivich@example.com",
        "password": "password123",
    }

    response = client.post("/user/", json=user_data)

    if response.status_code == 409:
        return {"username": user_data["email"], "password": user_data["password"]}

    assert response.status_code == 201, f"Error: {response.text}"
    return {"username": user_data["email"], "password": user_data["password"]}


@pytest.fixture
def auth_headers(client, test_user):
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"],
    }
    login_response = client.post("/auth/login/", data=login_data)
    assert login_response.status_code == 200, f"Error: {login_response.text}"
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_company(client, auth_headers):
    company_data = {
        "name": "Test Company",
        "description": "This is a test company",
        "status": "visible",
        "owner_id": 1,
    }

    response = client.post("/company/", json=company_data, headers=auth_headers)
    assert response.status_code == 201, f"Company creation failed: {response.text}"

    return response.json()


@pytest.fixture
def not_owner_data():
    return {
        "first_name": "Not Owner",
        "last_name": "Not Owner",
        "email": "not_owner@example.com",
        "password": "password123",
    }


@pytest.fixture
def not_owner_auth_headers(client, not_owner_data):
    not_owner_response = client.post("/user/", json=not_owner_data)
    if not_owner_response.status_code == 409:
        login_data = {
            "username": not_owner_data["email"],
            "password": not_owner_data["password"],
        }
    else:
        assert (
            not_owner_response.status_code == 201
        ), f"Error: {not_owner_response.text}"
        login_data = {
            "username": not_owner_data["email"],
            "password": not_owner_data["password"],
        }

    login_response = client.post("/auth/login/", data=login_data)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def existing_company():
    return {"id": 1}
