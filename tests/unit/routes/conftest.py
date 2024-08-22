import pytest
from fastapi.testclient import TestClient

from routes import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    client = TestClient(app)
    return client
