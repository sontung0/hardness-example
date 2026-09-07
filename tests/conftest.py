import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _clear_store():
    """Clear in-memory store between tests to prevent cross-test pollution."""
    import store

    store.users.clear()
    yield
    store.users.clear()


@pytest.fixture
def client():
    """Fresh TestClient per test."""
    from main import app

    return TestClient(app)


@pytest.fixture
def registered_user(client):
    """Register a test user and return the response data (includes access_token)."""
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "password": "testpass123",
            "name": "Test User",
        },
    )
    return response.json()


@pytest.fixture
def auth_header(registered_user):
    """Return Authorization header dict for the registered user."""
    return {"Authorization": f"Bearer {registered_user['access_token']}"}


@pytest.fixture
def delete_user_from_store():
    """Helper to simulate user deletion from the in-memory store."""

    def _delete(username: str):
        import store

        store.users.pop(username, None)

    return _delete
