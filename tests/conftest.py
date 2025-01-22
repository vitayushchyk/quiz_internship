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
        "username": "tests@example.com",
        "password": "sString123",
    }
