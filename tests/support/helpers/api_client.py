"""Shared test helpers — API client wrappers and data utilities."""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient


class APIClient:
    """Thin wrapper around TestClient with auth convenience methods."""

    def __init__(self, client: TestClient) -> None:
        self._client = client
        self._token: str | None = None

    def register(
        self, username: str = "helperuser", password: str = "helperpass", name: str = "Helper User"
    ) -> dict[str, Any]:
        """Register a user and store the token."""
        resp = self._client.post(
            "/register",
            json={"username": username, "password": password, "name": name},
        )
        data = resp.json()
        self._token = data.get("access_token")
        return data

    def login(self, username: str, password: str) -> dict[str, Any]:
        """Login and store the token."""
        resp = self._client.post(
            "/login",
            json={"username": username, "password": password},
        )
        data = resp.json()
        self._token = data.get("access_token")
        return data

    @property
    def auth_headers(self) -> dict[str, str]:
        """Return Authorization header dict."""
        if not self._token:
            raise RuntimeError("No token — call register() or login() first")
        return {"Authorization": f"Bearer {self._token}"}

    def get_current_user(self) -> dict[str, Any]:
        """Call GET /me with stored auth."""
        resp = self._client.get("/me", headers=self.auth_headers)
        return resp.json()
