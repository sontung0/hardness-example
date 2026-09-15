"""
API acceptance tests for POST /change-password.

Test IDs map to coverage matrix for Epic 2 — Password Management:
  T-50: Valid change → 200 + success message
  T-51: Login with old password after change → 401
  T-52: Weak new password (< 8 chars) → 400
  T-53: Wrong current password → 401
  T-54: Missing Authorization → 401
  T-55: Expired JWT → 401
  T-56: Boundary: new password exactly 8 chars → 200
  T-57: Oversized current password (> 72 bytes) → 400
"""
import time

import jwt
import pytest

from tests.support.constants import (
    ERR_NOT_AUTHENTICATED,
    TEST_NAME,
    TEST_PASSWORD,
    TEST_USERNAME,
)
from tests.support.helpers.factories import registration_payload


# ---------------------------------------------------------------------------
# FR-4 / FR-5 / FR-6 / FR-7: Change Password
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestChangePassword:
    """T-50 to T-57"""

    def test_change_password_valid_returns_200_and_success_message(
        self, client, registered_user, auth_header
    ):
        """T-50: Valid current password + valid new password → 200 + message"""
        response = client.post(
            "/change-password",
            json={
                "current_password": TEST_PASSWORD,
                "new_password": "NewSecure123",
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "Password changed successfully"
        assert "password_hash" not in body

    def test_change_password_old_password_no_longer_works(
        self, client, registered_user, auth_header
    ):
        """T-51: After password change, login with old password → 401"""
        # Change the password
        client.post(
            "/change-password",
            json={
                "current_password": TEST_PASSWORD,
                "new_password": "NewSecure123",
            },
            headers=auth_header,
        )
        # Try logging in with the old password
        response = client.post(
            "/login",
            json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
        )
        assert response.status_code == 401

    def test_change_password_weak_new_password_returns_400(
        self, client, registered_user, auth_header
    ):
        """T-52: New password shorter than 8 chars → 400"""
        response = client.post(
            "/change-password",
            json={
                "current_password": TEST_PASSWORD,
                "new_password": "short",
            },
            headers=auth_header,
        )
        assert response.status_code == 400
        body = response.json()
        assert "detail" in body
        assert "8 characters" in body["detail"]

    def test_change_password_wrong_current_password_returns_401(
        self, client, registered_user, auth_header
    ):
        """T-53: Wrong current password → 401 with generic error"""
        response = client.post(
            "/change-password",
            json={
                "current_password": "wrongpassword",
                "new_password": "NewSecure123",
            },
            headers=auth_header,
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_change_password_missing_auth_returns_401(self, client):
        """T-54: No Authorization header → 401"""
        response = client.post(
            "/change-password",
            json={
                "current_password": TEST_PASSWORD,
                "new_password": "NewSecure123",
            },
        )
        assert response.status_code == 401
        assert response.json()["detail"] == ERR_NOT_AUTHENTICATED

    def test_change_password_expired_jwt_returns_401(self, client):
        """T-55: Expired JWT → 401"""
        # Register a user for this test
        client.post(
            "/register",
            json=registration_payload(
                username="chgpwexp", password="pass1234", name="Exp User"
            ),
        )
        # Create an expired token
        from auth import SECRET_KEY

        expired_token = jwt.encode(
            {"sub": "chgpwexp", "exp": time.time() - 3600},
            SECRET_KEY,
            algorithm="HS256",
        )
        response = client.post(
            "/change-password",
            json={
                "current_password": "pass1234",
                "new_password": "NewSecure123",
            },
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    def test_change_password_exactly_8_chars_returns_200(
        self, client, registered_user, auth_header
    ):
        """T-56: New password exactly 8 chars → 200 (boundary test)"""
        response = client.post(
            "/change-password",
            json={
                "current_password": TEST_PASSWORD,
                "new_password": "12345678",
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"

    def test_change_password_oversized_current_password_returns_400(
        self, client, registered_user, auth_header
    ):
        """T-57: Current password exceeding 72 bytes → 400"""
        response = client.post(
            "/change-password",
            json={
                "current_password": "a" * 73,
                "new_password": "NewSecure123",
            },
            headers=auth_header,
        )
        assert response.status_code == 400
        body = response.json()
        assert "detail" in body
        assert "72 bytes" in body["detail"]
