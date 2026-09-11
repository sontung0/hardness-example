"""Unit tests for services.change_password — TDD red phase scaffolds."""

import importlib
import pytest

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skip(reason="Red phase: change_password not implemented yet"),
]


class TestChangePassword:
    """T-32, T-33, T-34, T-35: Service-level password change logic."""

    def test_change_password_success_hashes_new_password(self):
        """T-32: Valid current password → new password hashed and stored."""
        svc = importlib.import_module("services")
        svc.register_user("alice", "current123", "Alice")
        result = svc.change_password("alice", "current123", "newpass123")
        assert result is not None
        assert "message" in result

    def test_change_password_wrong_current_raises_value_error(self):
        """T-33: Wrong current password → ValueError raised."""
        svc = importlib.import_module("services")
        svc.register_user("bob", "correct123", "Bob")
        with pytest.raises(ValueError, match="Invalid credentials"):
            svc.change_password("bob", "wrongpass", "newpass123")

    def test_change_password_weak_new_password_raises_value_error(self):
        """T-34: New password < 8 chars → ValueError raised."""
        svc = importlib.import_module("services")
        svc.register_user("charlie", "current123", "Charlie")
        with pytest.raises(ValueError, match="at least 8 characters"):
            svc.change_password("charlie", "current123", "short")

    def test_change_password_unknown_user_raises_value_error(self):
        """T-35: Nonexistent user → ValueError raised."""
        svc = importlib.import_module("services")
        with pytest.raises(ValueError):
            svc.change_password("nobody", "pass123", "newpass123")
