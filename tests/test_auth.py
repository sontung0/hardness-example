"""
Acceptance tests for Simple REST API — Auth
Generated from test-design (ATDD red phase)

Test IDs map to coverage matrix in test-design-qa.md:
  T-01 to T-08:  FR-1 — Registration
  T-09 to T-13:  FR-2 — Login
  T-14 to T-19:  FR-3 — Get current user
  T-20 to T-25:  NFR scenarios
  T-26 to T-28:  Risk-driven scenarios
"""
import time

import jwt
import pytest

from tests.support.constants import (
    ERR_USER_NOT_FOUND,
    TEST_NAME,
    TEST_USERNAME,
)
from tests.support.helpers.factories import registration_payload

# ---------------------------------------------------------------------------
# FR-1: User Registration
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestRegister:
    """T-01 to T-08"""

    def test_register_success_returns_201_and_jwt(self, client):
        """T-01: Valid input → 201 + access_token"""
        response = client.post(
            "/register",
            json=registration_payload(username="alice", password="secret123", name="Alice"),
        )
        assert response.status_code == 201
        body = response.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_register_missing_username_returns_400(self, client):
        """T-02: Missing username → 400"""
        response = client.post(
            "/register",
            json={"password": "secret123", "name": "Alice"},
        )
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_register_missing_password_returns_400(self, client):
        """T-03: Missing password → 400"""
        response = client.post(
            "/register",
            json={"username": "alice", "name": "Alice"},
        )
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_register_missing_name_returns_400(self, client):
        """T-04: Missing name → 400"""
        response = client.post(
            "/register",
            json={"username": "alice", "password": "secret123"},
        )
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_register_duplicate_username_returns_409(self, client):
        """T-05: Duplicate username → 409"""
        client.post(
            "/register",
            json=registration_payload(username="alice", password="pass1", name="Alice"),
        )
        response = client.post(
            "/register",
            json=registration_payload(username="alice", password="pass2", name="Alice Again"),
        )
        assert response.status_code == 409
        assert "detail" in response.json()

    def test_register_username_case_normalization(self, client):
        """T-06: 'Bob' and 'bob' resolve to the same user"""
        client.post(
            "/register",
            json=registration_payload(username="Bob", password="pass1", name="Bob First"),
        )
        response = client.post(
            "/register",
            json=registration_payload(username="bob", password="pass2", name="Bob Second"),
        )
        assert response.status_code == 409

    def test_register_password_hashed_with_bcrypt(self, client):
        """T-07: Password stored as bcrypt hash, not plaintext"""
        import bcrypt

        client.post(
            "/register",
            json=registration_payload(username="hashcheck", password="mypassword", name="HC"),
        )
        # Verify via the store directly
        from store import users

        stored = users.get("hashcheck")
        assert stored is not None
        assert stored["password_hash"] != "mypassword"
        assert bcrypt.checkpw(
            b"mypassword",
            stored["password_hash"].encode("utf-8"),
        )

    def test_register_password_not_in_response(self, client):
        """T-08: password_hash never appears in response body"""
        response = client.post(
            "/register",
            json=registration_payload(username="secure", password="secret123", name="Secure"),
        )
        body = response.json()
        assert "password_hash" not in body
        assert "password" not in body

    def test_register_extra_fields_ignored(self, client):
        """Extra fields in request body are silently ignored"""
        response = client.post(
            "/register",
            json={
                **registration_payload(username="extra", password="pass", name="Extra"),
                "age": 30,
                "role": "admin",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert "access_token" in body


# ---------------------------------------------------------------------------
# FR-2: User Login
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestLogin:
    """T-09 to T-13"""

    def test_login_success_returns_200_and_jwt(self, client):
        """T-09: Valid credentials → 200 + JWT"""
        client.post(
            "/register",
            json=registration_payload(username="loginuser", password="pass123", name="Login User"),
        )
        response = client.post(
            "/login",
            json={"username": "loginuser", "password": "pass123"},
        )
        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_login_wrong_password_returns_401(self, client):
        """T-10: Wrong password → 401"""
        client.post(
            "/register",
            json=registration_payload(username="wrongpw", password="correct", name="WP"),
        )
        response = client.post(
            "/login",
            json={"username": "wrongpw", "password": "incorrect"},
        )
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_login_nonexistent_user_returns_401(self, client):
        """T-11: Nonexistent user → 401"""
        response = client.post(
            "/login",
            json={"username": "nobody", "password": "pass"},
        )
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_login_missing_username_returns_400(self, client):
        """T-12: Missing username → 400"""
        response = client.post(
            "/login",
            json={"password": "pass"},
        )
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_login_missing_password_returns_400(self, client):
        """T-13: Missing password → 400"""
        response = client.post(
            "/login",
            json={"username": "someuser"},
        )
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_login_extra_fields_ignored(self, client):
        """Extra fields in login request are silently ignored"""
        client.post(
            "/register",
            json=registration_payload(username="extra1", password="pass", name="Extra"),
        )
        response = client.post(
            "/login",
            json={"username": "extra1", "password": "pass", "extra": "ignored"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()


# ---------------------------------------------------------------------------
# FR-3: Get Current User
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestGetCurrentUser:
    """T-14 to T-19"""

    def test_me_valid_jwt_returns_200_and_profile(self, client, registered_user, auth_header):
        """T-14: Valid JWT → 200 + profile"""
        response = client.get("/me", headers=auth_header)
        assert response.status_code == 200
        body = response.json()
        assert body["username"] == TEST_USERNAME
        assert body["name"] == TEST_NAME
        assert "password_hash" not in body

    def test_me_no_token_returns_401(self, client):
        """T-15: No token → 401"""
        response = client.get("/me")
        assert response.status_code == 401

    def test_me_expired_token_returns_401(self, client):
        """T-16: Expired token → 401"""
        client.post(
            "/register",
            json=registration_payload(username="expired", password="pass", name="Exp"),
        )
        # Create an expired token
        from auth import SECRET_KEY

        expired_token = jwt.encode(
            {"sub": "expired", "exp": time.time() - 3600},
            SECRET_KEY,
            algorithm="HS256",
        )
        response = client.get(
            "/me", headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401

    def test_me_malformed_token_returns_401(self, client):
        """T-17: Malformed token → 401"""
        response = client.get(
            "/me", headers={"Authorization": "Bearer not-a-jwt-token"}
        )
        assert response.status_code == 401

    def test_me_user_deleted_after_registration(self, client, delete_user_from_store):
        """Token valid but user no longer in store → 401"""
        # Register a separate user for this test
        reg = client.post(
            "/register",
            json=registration_payload(username="ephemeral", password="pass", name="Eph"),
        )
        token = reg.json()["access_token"]

        # Remove user from store via fixture
        delete_user_from_store("ephemeral")

        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
        assert response.json()["detail"] == ERR_USER_NOT_FOUND

    def test_me_tampered_payload_returns_401(self, client):
        """T-18: Tampered payload → 401"""
        client.post(
            "/register",
            json=registration_payload(username="tamper", password="pass", name="Tamper"),
        )
        from auth import SECRET_KEY

        # Create a valid token then tamper with it
        token = jwt.encode(
            {"sub": "tamper", "exp": time.time() + 86400},
            SECRET_KEY,
            algorithm="HS256",
        )
        # Tamper: flip a character in the payload
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        response = client.get(
            "/me", headers={"Authorization": f"Bearer {tampered}"}
        )
        assert response.status_code == 401

    def test_me_wrong_secret_returns_401(self, client):
        """T-19: Token signed with wrong secret → 401"""
        wrong_secret_token = jwt.encode(
            {"sub": "anyone", "exp": time.time() + 86400},
            "wrong-secret-key",
            algorithm="HS256",
        )
        response = client.get(
            "/me", headers={"Authorization": f"Bearer {wrong_secret_token}"}
        )
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# NFR Scenarios
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestNFR:
    """T-20 to T-25"""

    def test_password_hash_never_in_any_response(self, client):
        """T-20: password_hash never appears in any response"""
        # Register
        reg = client.post(
            "/register",
            json=registration_payload(username="nfr20", password="pass", name="NFR20"),
        )
        assert "password_hash" not in reg.json()
        assert "password" not in reg.json()

        # Login
        login = client.post(
            "/login",
            json={"username": "nfr20", "password": "pass"},
        )
        assert "password_hash" not in login.json()

        # Get /me
        token = login.json()["access_token"]
        me = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert "password_hash" not in me.json()

    def test_error_shape_always_detail_string(self, client):
        """T-21: All error responses have {"detail": str}"""
        # 400 — missing fields
        r1 = client.post("/register", json={})
        assert r1.status_code == 400
        body1 = r1.json()
        assert "detail" in body1
        assert isinstance(body1["detail"], str)

        # 401 — wrong credentials
        r2 = client.post("/login", json={"username": "x", "password": "y"})
        assert r2.status_code == 401
        body2 = r2.json()
        assert "detail" in body2
        assert isinstance(body2["detail"], str)

        # 401 — no token
        r3 = client.get("/me")
        assert r3.status_code == 401
        body3 = r3.json()
        assert "detail" in body3
        assert isinstance(body3["detail"], str)

    def test_validation_error_returns_400_with_detail(self, client):
        """T-22: Invalid JSON body → 400 with {"detail": str} (422 overridden per AD-5)"""
        response = client.post(
            "/register",
            content="not-json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400
        body = response.json()
        assert "detail" in body
        assert isinstance(body["detail"], str)

    def test_store_returns_only_username_and_name(self, client):
        """T-23: store.get_user() returns only username + name, never password_hash"""
        client.post(
            "/register",
            json=registration_payload(username="store23", password="pass", name="S23"),
        )
        from store import get_user

        user = get_user("store23")
        assert user is not None
        assert "username" in user
        assert "name" in user
        assert "password_hash" not in user

    def test_jwt_sub_claim_is_lowercased_username(self, client):
        """T-24: JWT sub claim = lowercased username"""
        client.post(
            "/register",
            json=registration_payload(username="Alice", password="pass", name="Alice"),
        )
        from auth import SECRET_KEY

        login = client.post(
            "/login", json={"username": "alice", "password": "pass"}
        )
        token = login.json()["access_token"]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        assert payload["sub"] == "alice"

    def test_jwt_exp_is_24h_from_issuance(self, client):
        """T-25: JWT exp claim = 24h from issuance"""
        before = time.time()
        client.post(
            "/register",
            json=registration_payload(username="expcheck", password="pass", name="EC"),
        )
        login = client.post(
            "/login", json={"username": "expcheck", "password": "pass"}
        )
        after = time.time()
        from auth import SECRET_KEY

        token = login.json()["access_token"]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        expected_exp_min = before + 86400 - 5  # 24h minus 5s tolerance
        expected_exp_max = after + 86400 + 5
        assert expected_exp_min <= payload["exp"] <= expected_exp_max


# ---------------------------------------------------------------------------
# Risk-Driven Scenarios
# ---------------------------------------------------------------------------

@pytest.mark.api
class TestRiskDriven:
    """T-26 to T-28"""

    def test_full_auth_lifecycle(self, client):
        """T-26: Register → Login → Get /me end-to-end"""
        # Register
        reg = client.post(
            "/register",
            json=registration_payload(username="lifecycle", password="pass", name="LC"),
        )
        assert reg.status_code == 201

        # Login
        login = client.post(
            "/login", json={"username": "lifecycle", "password": "pass"}
        )
        assert login.status_code == 200
        token = login.json()["access_token"]

        # Get /me
        me = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["username"] == "lifecycle"
        assert me.json()["name"] == "LC"

    def test_concurrent_registrations_same_username(self, client):
        """T-27: Two registrations with same username → one 201, one 409"""
        client.post(
            "/register",
            json=registration_payload(username="race", password="pass1", name="R1"),
        )
        response = client.post(
            "/register",
            json=registration_payload(username="race", password="pass2", name="R2"),
        )
        assert response.status_code == 409

    def test_password_never_in_error_messages(self, client):
        """T-28: Password never leaked in any error response"""
        password = "supersecret123"
        response = client.post(
            "/login",
            json={"username": "anyone", "password": password},
        )
        body_text = response.text
        assert password not in body_text

        # Also check register error responses
        response2 = client.post(
            "/register",
            json={"username": "anyone"},  # missing password
        )
        assert password not in response2.text


# ---------------------------------------------------------------------------
