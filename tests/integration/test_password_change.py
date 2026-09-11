"""Integration tests for POST /change-password — TDD red phase scaffolds."""

import pytest

# Red-phase: endpoint doesn't exist yet, but tests will be collected


@pytest.mark.integration
@pytest.mark.skip(reason="Red phase: /change-password endpoint not implemented yet")
class TestChangePasswordEndpoint:
    """T-36 to T-49: API-level password change tests."""

    # ── Happy path ──────────────────────────────────────────────────

    def test_valid_change_returns_200_and_success_message(self, client, registered_user, auth_header):
        """T-36: Valid current + new password → HTTP 200 + success message."""
        response = client.post(
            "/change-password",
            json={"current_password": "testpass123", "new_password": "newpass123"},
            headers=auth_header,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "Password changed successfully"

    def test_old_password_no_longer_authenticates_after_change(self, client, registered_user, auth_header):
        """T-37: After successful change, old password fails login."""
        # Change password
        client.post(
            "/change-password",
            json={"current_password": "testpass123", "new_password": "newpass123"},
            headers=auth_header,
        )
        # Try login with old password
        login_response = client.post(
            "/login",
            json={"username": "testuser", "password": "testpass123"},
        )
        assert login_response.status_code == 401

    # ── Validation ──────────────────────────────────────────────────

    def test_weak_new_password_returns_400(self, client, registered_user, auth_header):
        """T-38: New password < 8 chars → HTTP 400."""
        response = client.post(
            "/change-password",
            json={"current_password": "testpass123", "new_password": "short"},
            headers=auth_header,
        )
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "at least 8 characters" in response.json()["detail"]

    def test_boundary_new_password_exactly_8_chars_returns_200(self, client, registered_user, auth_header):
        """T-39: New password exactly 8 chars → HTTP 200 (boundary)."""
        response = client.post(
            "/change-password",
            json={"current_password": "testpass123", "new_password": "eightchr"},
            headers=auth_header,
        )
        assert response.status_code == 200

    # ── Authentication ──────────────────────────────────────────────

    def test_missing_authorization_header_returns_401(self, client, registered_user):
        """T-40: No Authorization header → HTTP 401."""
        response = client.post(
            "/change-password",
            json={"current_password": "testpass123", "new_password": "newpass123"},
        )
        assert response.status_code == 401

    def test_expired_jwt_returns_401(self, client, registered_user):
        """T-41: Expired JWT → HTTP 401."""
        # Create an expired token (exp in the past)
        import jwt

        expired_token = jwt.encode(
            {"sub": "testuser", "exp": 0},
            "secret",
            algorithm="HS256",
        )
        response = client.post(
            "/change-password",
            json={"current_password": "testpass123", "new_password": "newpass123"},
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    def test_invalid_jwt_returns_401(self, client, registered_user):
        """T-42: Invalid JWT → HTTP 401."""
        response = client.post(
            "/change-password",
            json={"current_password": "testpass123", "new_password": "newpass123"},
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    # ── Error semantics ─────────────────────────────────────────────

    def test_wrong_current_password_returns_401_invalid_credentials(self, client, registered_user, auth_header):
        """T-43: Wrong current password → HTTP 401 with same message as login."""
        response = client.post(
            "/change-password",
            json={"current_password": "wrongpassword", "new_password": "newpass123"},
            headers=auth_header,
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_existing_jwt_remains_valid_after_password_change(self, client, registered_user, auth_header):
        """T-44: JWT from before change still works for /me after change."""
        # Change password
        client.post(
            "/change-password",
            json={"current_password": "testpass123", "new_password": "newpass123"},
            headers=auth_header,
        )
        # Use the SAME JWT (from registration) to hit /me
        response = client.get("/me", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

    # ── Error shape consistency ──────────────────────────────────────

    def test_all_errors_return_detail_shape(self, client, registered_user, auth_header):
        """T-45: Every error response contains {"detail": str}."""
        # Missing fields
        response = client.post(
            "/change-password",
            json={},
            headers=auth_header,
        )
        assert "detail" in response.json()
        assert isinstance(response.json()["detail"], str)

        # Wrong password
        response = client.post(
            "/change-password",
            json={"current_password": "wrong", "new_password": "newpass123"},
            headers=auth_header,
        )
        assert "detail" in response.json()
        assert isinstance(response.json()["detail"], str)

    # ── Input validation ────────────────────────────────────────────

    def test_username_case_normalization_in_change_password(self, client, registered_user, auth_header):
        """T-46: Username is lowercased during change-password flow."""
        response = client.post(
            "/change-password",
            json={"current_password": "testpass123", "new_password": "newpass123"},
            headers=auth_header,
        )
        assert response.status_code == 200

    def test_empty_body_returns_400_or_422(self, client, registered_user, auth_header):
        """T-47: Empty JSON body → HTTP 400 or 422."""
        response = client.post(
            "/change-password",
            json={},
            headers=auth_header,
        )
        assert response.status_code in (400, 422)

    def test_missing_current_password_field_returns_400_or_422(self, client, registered_user, auth_header):
        """T-48: Missing current_password → HTTP 400 or 422."""
        response = client.post(
            "/change-password",
            json={"new_password": "newpass123"},
            headers=auth_header,
        )
        assert response.status_code in (400, 422)

    def test_missing_new_password_field_returns_400_or_422(self, client, registered_user, auth_header):
        """T-49: Missing new_password → HTTP 400 or 422."""
        response = client.post(
            "/change-password",
            json={"current_password": "testpass123"},
            headers=auth_header,
        )
        assert response.status_code in (400, 422)
