"""Unit tests for JWT creation, decoding, and FastAPI dependency (auth.py).

Covers all branches in auth.py (P0 gap):
  - create_access_token: token shape, sub claim, expiry, algorithm
  - decode_token: valid, expired, wrong-secret, malformed, tampered
  - get_current_user: valid bearer, None, bearer-only, empty, non-bearer,
                      expired, invalid, missing-sub
"""

import time

import jwt
import pytest
from fastapi import HTTPException

from auth import (
    ALGORITHM,
    SECRET_KEY,
    TOKEN_EXPIRY_HOURS,
    create_access_token,
    decode_token,
    get_current_user,
)


@pytest.mark.unit
class TestCreateAccessToken:
    def test_returns_string(self):
        token = create_access_token("alice")
        assert isinstance(token, str)

    def test_sub_claim_is_lowercased(self):
        token = create_access_token("Alice")
        payload = decode_token(token)
        assert payload["sub"] == "alice"

    def test_expiry_is_24h_from_now(self):
        before = time.time()
        token = create_access_token("user1")
        after = time.time()
        payload = decode_token(token)

        expected_min = before + (TOKEN_EXPIRY_HOURS * 3600) - 5
        expected_max = after + (TOKEN_EXPIRY_HOURS * 3600) + 5
        assert expected_min <= payload["exp"] <= expected_max

    def test_sub_claim_matches_username(self):
        token = create_access_token("bob")
        payload = decode_token(token)
        assert payload["sub"] == "bob"

    def test_token_encodes_with_correct_algorithm(self):
        """T-AUTH-05: Token uses HS256 algorithm."""
        token = create_access_token("carol")
        header = jwt.get_unverified_header(token)
        assert header["alg"] == "HS256"


@pytest.mark.unit
class TestDecodeToken:
    def test_valid_token_decodes(self):
        token = create_access_token("charlie")
        payload = decode_token(token)
        assert payload["sub"] == "charlie"
        assert "exp" in payload

    def test_expired_token_raises(self):
        token = jwt.encode(
            {"sub": "diana", "exp": int(time.time()) - 3600},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_token(token)

    def test_wrong_secret_raises(self):
        token = jwt.encode(
            {"sub": "eve", "exp": int(time.time()) + 3600},
            "wrong-secret",
            algorithm=ALGORITHM,
        )
        with pytest.raises(jwt.InvalidTokenError):
            decode_token(token)

    def test_malformed_token_raises(self):
        with pytest.raises(jwt.InvalidTokenError):
            decode_token("not-a-valid-jwt")

    def test_tampered_signature_raises(self):
        """T-AUTH-10: Tampered signature byte raises InvalidTokenError."""
        token = create_access_token("fay")
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        with pytest.raises(jwt.InvalidTokenError):
            decode_token(tampered)


@pytest.mark.unit
class TestGetCurrentUser:
    """T-AUTH-11 to T-AUTH-18 — all branches in get_current_user."""

    def test_valid_token_returns_username(self):
        token = create_access_token("frank")
        result = get_current_user(authorization=f"Bearer {token}")
        assert result == "frank"

    def test_no_header_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization=None)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"

    def test_bearer_only_no_token_raises_401(self):
        """T-AUTH-13: 'Bearer' with no token part → 401."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization="Bearer")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"

    def test_empty_string_raises_401(self):
        """T-AUTH-14: Empty string authorization → 401."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization="")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"

    def test_non_bearer_scheme_raises_401(self):
        token = create_access_token("grace")
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization=f"Token {token}")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"

    def test_expired_token_raises_401_token_expired(self):
        """T-AUTH-16: Expired Bearer token → 401 'Token has expired'."""
        token = jwt.encode(
            {"sub": "hank", "exp": int(time.time()) - 3600},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization=f"Bearer {token}")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token has expired"

    def test_invalid_token_raises_401_invalid_token(self):
        """T-AUTH-17: Garbage Bearer token → 401 'Invalid token'."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization="Bearer garbage-token-value")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"

    def test_missing_sub_claim_raises_401(self):
        """T-AUTH-18: Valid JWT without 'sub' → 401 'Invalid token'."""
        token = jwt.encode(
            {"exp": int(time.time()) + 3600},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization=f"Bearer {token}")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"
