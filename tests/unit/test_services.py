"""Unit tests for business logic (services layer)."""

import pytest

import store
from services import authenticate_user, register_user


@pytest.mark.unit
class TestRegisterUser:
    def test_register_returns_username_and_name(self):
        result = register_user("alice", "secret123", "Alice")
        assert result["username"] == "alice"
        assert result["name"] == "Alice"

    def test_register_lowercases_username(self):
        result = register_user("BOB", "pass", "Bob")
        assert result["username"] == "bob"
        assert store.user_exists("bob")

    def test_register_duplicate_raises_value_error(self):
        register_user("charlie", "pass", "Charlie")
        with pytest.raises(ValueError, match="already exists"):
            register_user("charlie", "pass2", "Charlie 2")


@pytest.mark.unit
class TestAuthenticateUser:
    def test_authenticate_success(self):
        register_user("diana", "mypassword", "Diana")
        result = authenticate_user("diana", "mypassword")
        assert result["username"] == "diana"

    def test_authenticate_wrong_password(self):
        register_user("eve", "correct", "Eve")
        with pytest.raises(ValueError):
            authenticate_user("eve", "wrong")

    def test_authenticate_unknown_user(self):
        with pytest.raises(ValueError):
            authenticate_user("nobody", "pass")
