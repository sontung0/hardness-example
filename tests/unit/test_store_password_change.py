"""Unit tests for store.update_password — TDD red phase scaffolds."""

import importlib
import pytest

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skip(reason="Red phase: update_password not implemented yet"),
]


class TestUpdatePassword:
    """T-29, T-30, T-31: Store-level password update operations."""

    def test_update_password_overwrites_hash_keeps_username_and_name(self):
        """T-29: update_password replaces hash, preserves username and name."""
        store = importlib.import_module("store")
        store.add_user("alice", "old_hash_123", "Alice")
        store.update_password("alice", "new_hash_456")
        user = store.get_user_with_hash("alice")
        assert user is not None
        assert user["password_hash"] == "new_hash_456"
        assert user["username"] == "alice"
        assert user["name"] == "Alice"

    def test_update_password_nonexistent_user_is_noop(self):
        """T-30: update_password on unknown user does not raise or create user."""
        store = importlib.import_module("store")
        store.update_password("nobody", "some_hash")
        assert store.get_user("nobody") is None

    def test_get_user_after_update_returns_no_hash(self):
        """T-31: get_user (safe accessor) never exposes password_hash after update."""
        store = importlib.import_module("store")
        store.add_user("bob", "old_hash", "Bob")
        store.update_password("bob", "new_hash")
        user = store.get_user("bob")
        assert user is not None
        assert "password_hash" not in user
        assert user["username"] == "bob"
        assert user["name"] == "Bob"
