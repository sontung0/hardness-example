"""In-memory user store. Module-level dict — data lost on restart by design (AD-3)."""

users: dict[str, dict] = {}


def add_user(username: str, password_hash: str, name: str) -> None:
    users[username] = {"username": username, "name": name, "password_hash": password_hash}


def get_user(username: str) -> dict | None:
    user = users.get(username)
    if user is None:
        return None
    return {"username": user["username"], "name": user["name"]}


def get_user_with_hash(username: str) -> dict | None:
    return users.get(username)


def user_exists(username: str) -> bool:
    return username in users
