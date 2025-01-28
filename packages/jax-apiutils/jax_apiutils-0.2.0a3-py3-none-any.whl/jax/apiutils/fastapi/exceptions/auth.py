"""Exceptions for the API Auth(Z/N) Errors."""

from fastapi import HTTPException

__all__ = [
    "Auth0UnauthenticatedException",
    "Auth0UnauthorizedException",
    "AuthenticationMismatch",
    "UnauthorizedException",
]


class Auth0UnauthenticatedException(HTTPException):
    """Exception for unauthenticated requests."""

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the exception."""
        super().__init__(401, **kwargs)


class AuthenticationMismatch(HTTPException):
    """Exception for mismatched authentication."""

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the exception."""
        super().__init__(401, **kwargs)


class Auth0UnauthorizedException(HTTPException):
    """Exception for unauthorized requests."""

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the exception."""
        super().__init__(403, **kwargs)


class UnauthorizedException(HTTPException):
    """Exception for unauthorized requests."""

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the exception."""
        super().__init__(403, **kwargs)
