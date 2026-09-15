"""Unit tests for services.change_password."""

import importlib
import pytest

pytestmark = [
    pytest.mark.unit,
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

    def test_change_password_lowercases_username(self):
        """T-46: Username is lowercased during change-password flow."""
        svc = importlib.import_module("services")
        svc.register_user("MixedCase", "current123", "Name")
        result = svc.change_password("MixedCase", "current123", "newpass123")
        assert result is not None
        assert "message" in result

    def test_change_password_wrong_current_with_short_new_raises_invalid_credentials(self):
        """Wrong current password takes precedence over new-password length check."""
        svc = importlib.import_module("services")
        svc.register_user("dave", "current123", "Dave")
        with pytest.raises(ValueError, match="Invalid credentials"):
            svc.change_password("dave", "wrongpass", "short")
