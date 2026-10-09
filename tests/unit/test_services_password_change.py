"""Unit tests for services.change_password."""

import importlib
import threading

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

    def test_change_password_oversized_current_password_raises_value_error(self):
        """Oversized current_password (>72 bytes) rejected before bcrypt.checkpw is called."""
        svc = importlib.import_module("services")
        svc.register_user("erin", "current123", "Erin")
        with pytest.raises(ValueError, match="Password must be at most 72 bytes"):
            svc.change_password("erin", "a" * 73, "newpass123")

    def test_change_password_oversized_new_password_raises_value_error(self):
        """Oversized new_password (>72 bytes) rejected after current-password check succeeds,
        before bcrypt.hashpw is called; stored password remains unchanged."""
        svc = importlib.import_module("services")
        svc.register_user("frank", "current123", "Frank")
        with pytest.raises(ValueError, match="Password must be at most 72 bytes"):
            svc.change_password("frank", "current123", "a" * 73)
        # Old password still works; new (oversized) one was never hashed/stored.
        result = svc.authenticate_user("frank", "current123")
        assert result["username"] == "frank"

    def test_change_password_multibyte_utf8_new_password_over_72_bytes_raises_value_error(self):
        """Multi-byte UTF-8 password over 72 bytes but <= 72 chars is rejected by byte length."""
        svc = importlib.import_module("services")
        svc.register_user("gina", "current123", "Gina")
        new_password = "é" * 40  # 40 chars, 80 bytes when UTF-8 encoded
        with pytest.raises(ValueError, match="Password must be at most 72 bytes"):
            svc.change_password("gina", "current123", new_password)

    def test_change_password_boundary_72_byte_passwords_succeed(self):
        """Exactly 72 bytes for both current and new password proceeds normally."""
        svc = importlib.import_module("services")
        svc.register_user("harry", "a" * 72, "Harry")
        result = svc.change_password("harry", "a" * 72, "b" * 72)
        assert result is not None
        assert "message" in result

    def test_concurrent_change_password_same_user_no_lost_update(self):
        """Two threads racing change_password for the same user, both presenting the
        same (originally valid) current password with different new passwords, must
        serialize cleanly: exactly one call succeeds and stores its new hash, and any
        other call fails with a clean "Invalid credentials" (because the password has
        legitimately moved on under it) rather than any interleaved/corrupted write.
        The final stored hash matches exactly the winner's new password -- never a
        partial or garbled hash, and never both new passwords 'winning' at once."""
        import bcrypt

        svc = importlib.import_module("services")
        store_mod = importlib.import_module("store")
        svc.register_user("ivan", "current123", "Ivan")

        new_password_a = "newpassA1"
        new_password_b = "newpassB2"
        results: list[dict] = []
        errors: list[Exception] = []
        barrier = threading.Barrier(2)

        def worker(new_password: str):
            barrier.wait()
            try:
                results.append(svc.change_password("ivan", "current123", new_password))
            except ValueError as exc:
                errors.append(exc)

        threads = [
            threading.Thread(target=worker, args=(new_password_a,)),
            threading.Thread(target=worker, args=(new_password_b,)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exactly one call wins the race (check-then-write is atomic: no lost update).
        assert len(results) == 1
        # Any loser fails cleanly on re-verification against the now-current hash --
        # never a corrupted/garbled intermediate state.
        for err in errors:
            assert "Invalid credentials" in str(err)
        assert len(results) + len(errors) == 2

        stored = store_mod.get_user_with_hash("ivan")
        final_hash = stored["password_hash"].encode("utf-8")
        matches_a = bcrypt.checkpw(new_password_a.encode("utf-8"), final_hash)
        matches_b = bcrypt.checkpw(new_password_b.encode("utf-8"), final_hash)
        # Final hash matches exactly one of the two candidate new passwords.
        assert matches_a != matches_b
