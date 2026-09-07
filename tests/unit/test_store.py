"""Unit tests for the in-memory user store."""

import pytest

import store
from store import add_user, get_user, get_user_with_hash, user_exists


@pytest.mark.unit
class TestAddUser:
    def test_add_user_stores_data(self):
        add_user("alice", "hash123", "Alice")
        assert user_exists("alice")

    def test_add_user_overwrites_existing(self):
        add_user("bob", "hash1", "Bob")
        add_user("bob", "hash2", "Bobby")
        user = get_user("bob")
        assert user is not None
        assert user["name"] == "Bobby"


@pytest.mark.unit
class TestGetUser:
    def test_get_user_returns_username_and_name(self):
        add_user("charlie", "hash", "Charlie")
        user = get_user("charlie")
        assert user == {"username": "charlie", "name": "Charlie"}

    def test_get_user_returns_none_for_missing(self):
        assert get_user("nobody") is None

    def test_get_user_does_not_expose_hash(self):
        add_user("diana", "secret_hash", "Diana")
        user = get_user("diana")
        assert "password_hash" not in user


@pytest.mark.unit
class TestGetUserWithHash:
    def test_returns_full_record(self):
        add_user("eve", "hash99", "Eve")
        user = get_user_with_hash("eve")
        assert user["password_hash"] == "hash99"

    def test_returns_none_for_missing(self):
        assert get_user_with_hash("nobody") is None


@pytest.mark.unit
class TestUserExists:
    def test_exists_after_add(self):
        add_user("frank", "h", "Frank")
        assert user_exists("frank") is True

    def test_not_exists(self):
        assert user_exists("ghost") is False
