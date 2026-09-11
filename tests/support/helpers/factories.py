"""Faker-based data factory for test data generation."""

from __future__ import annotations

import random
import string


def random_username(prefix: str = "user") -> str:
    """Generate a random username like 'user_a3f8k'."""
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{suffix}"


def random_password(length: int = 12) -> str:
    """Generate a random password meeting typical complexity rules."""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return "".join(random.choices(chars, k=length))


def random_name() -> str:
    """Generate a random display name."""
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
    last_names = ["Smith", "Jones", "Brown", "Davis", "Wilson", "Taylor"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def registration_payload(
    username: str | None = None,
    password: str | None = None,
    name: str | None = None,
) -> dict[str, str]:
    """Build a registration payload with optional overrides."""
    return {
        "username": username or random_username(),
        "password": password or random_password(),
        "name": name or random_name(),
    }
