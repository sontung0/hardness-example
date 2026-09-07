"""Custom exception types for domain-level error handling."""


class NotFoundError(ValueError):
    """Raised when a requested resource does not exist."""


class ConflictError(ValueError):
    """Raised when a resource already exists (e.g., duplicate username)."""
