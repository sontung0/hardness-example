"""Unit tests for business logic (services layer)."""

import threading

import pytest

import store
from services import authenticate_user, get_current_user_profile, register_user


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

    def test_register_oversized_password_raises_value_error(self):
        with pytest.raises(ValueError, match="Password must be at most 72 bytes"):
            register_user("oversized", "a" * 73, "Oversized")
        assert not store.user_exists("oversized")

    def test_register_boundary_72_byte_password_succeeds(self):
        result = register_user("boundary", "a" * 72, "Boundary")
        assert result["username"] == "boundary"
        assert store.user_exists("boundary")

    def test_concurrent_register_same_username_only_one_succeeds(self):
        """Two threads racing register_user for the same new username must not
        both succeed (overwrite) and must not both fail: exactly one wins."""
        username = "concurrent_register_user"
        results: list[dict] = []
        errors: list[Exception] = []
        barrier = threading.Barrier(2)

        def worker():
            barrier.wait()
            try:
                results.append(register_user(username, "password123", "Concurrent"))
            except ValueError as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 1
        assert len(errors) == 1
        assert "already exists" in str(errors[0])
        assert store.user_exists(username)


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

    def test_authenticate_oversized_password_raises_value_error(self):
        register_user("frank", "mypassword", "Frank")
        with pytest.raises(ValueError, match="Password must be at most 72 bytes"):
            authenticate_user("frank", "a" * 73)

    def test_authenticate_boundary_72_byte_password(self):
        register_user("gina", "a" * 72, "Gina")
        result = authenticate_user("gina", "a" * 72)
        assert result["username"] == "gina"


@pytest.mark.unit
class TestGetCurrentUserProfile:
    def test_profile_success(self):
        register_user("george", "pass", "George")
        result = get_current_user_profile("george")
        assert result["username"] == "george"
        assert result["name"] == "George"

    def test_profile_not_found_raises(self):
        with pytest.raises(ValueError, match="User not found"):
            get_current_user_profile("nobody")
