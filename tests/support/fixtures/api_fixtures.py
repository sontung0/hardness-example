"""Shared test fixtures for API-level tests."""

import pytest


@pytest.fixture
def register_payload():
    """Default registration payload."""
    return {
        "username": "apiuser",
        "password": "securepass456",
        "name": "API User",
    }


@pytest.fixture
def login_payload():
    """Default login payload (user must be registered first)."""
    return {
        "username": "apiuser",
        "password": "securepass456",
    }
