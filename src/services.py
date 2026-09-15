"""Business logic for registration, login, user retrieval, and password change."""

import bcrypt

from store import add_user, get_user, get_user_with_hash, update_password, user_exists


def register_user(username: str, password: str, name: str) -> dict:
    username_lower = username.lower()

    if user_exists(username_lower):
        raise ValueError("Username already exists")

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    add_user(username_lower, password_hash, name)
    return {"username": username_lower, "name": name}


def authenticate_user(username: str, password: str) -> dict:
    username_lower = username.lower()
    user = get_user_with_hash(username_lower)
    if user is None:
        raise ValueError("Invalid credentials")

    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        raise ValueError("Invalid credentials")

    return {"username": username_lower, "name": user["name"]}


def get_current_user_profile(username: str) -> dict:
    user = get_user(username)
    if user is None:
        raise ValueError("User not found")
    return user


def change_password(username: str, current_password: str, new_password: str) -> dict:
    username_lower = username.lower()
    user = get_user_with_hash(username_lower)
    if user is None:
        raise ValueError("Invalid credentials")

    if not bcrypt.checkpw(current_password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        raise ValueError("Invalid credentials")

    if len(new_password) < 8:
        raise ValueError("Password must be at least 8 characters")

    new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    update_password(username_lower, new_hash)
    return {"message": "Password changed successfully"}
