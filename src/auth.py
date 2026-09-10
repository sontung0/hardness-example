"""JWT creation, verification, and FastAPI dependency."""

import os
import time

import jwt
from fastapi import Header, HTTPException

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super-secret-key-do-not-commit")
ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24


def create_access_token(username: str) -> str:
    exp = int(time.time()) + (TOKEN_EXPIRY_HOURS * 3600)
    return jwt.encode({"sub": username.lower(), "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def get_current_user(authorization: str = Header(None)) -> str:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(parts[1])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return username
