import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app, database


@pytest.fixture
def client():
    database.clear()
    return TestClient(app)
