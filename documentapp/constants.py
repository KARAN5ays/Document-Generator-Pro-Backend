"""
Application constants to avoid magic strings across the codebase.
"""


class DocumentStatus:
    """Document verification status values."""
    VALID = "valid"
    REVOKED = "revoked"


class UserRole:
    """User role choices (matches models.User.Role)."""
    ADMIN = "ADMIN"
    STAFF = "STAFF"
