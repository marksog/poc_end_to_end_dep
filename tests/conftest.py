# tests/conftest.py

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes import _items


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    # Clear the in-memory store before each test
    _items.clear()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_item_payload():
    """Standard item payload for tests."""
    return {
        "name": "Test Widget",
        "description": "A widget for testing",
        "price": 29.99,
        "status": "active",
    }


@pytest.fixture
def created_item(client, sample_item_payload):
    """Create an item and return the response data."""
    response = client.post("/api/items", json=sample_item_payload)
    return response.json()