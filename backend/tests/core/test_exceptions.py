from fastapi import status
from app.core.exceptions import (
    ForesightException,
    EntityNotFoundException,
    BadRequestException,
    AuthenticationException,
    AuthorizationException
)

def test_base_exception() -> None:
    """Test the base exception class defaults."""
    exc = ForesightException()
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "An unexpected error occurred."

def test_entity_not_found_exception() -> None:
    """Test EntityNotFoundException formatting."""
    exc = EntityNotFoundException(entity_name="User", entity_id=123)
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert "User with ID 123 not found" in exc.detail

def test_bad_request_exception() -> None:
    """Test BadRequestException formatting."""
    exc = BadRequestException(detail="Invalid input")
    assert exc.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.detail == "Invalid input"

def test_authentication_exception() -> None:
    """Test AuthenticationException headers."""
    exc = AuthenticationException()
    assert exc.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.headers == {"WWW-Authenticate": "Bearer"}

def test_authorization_exception() -> None:
    """Test AuthorizationException status code."""
    exc = AuthorizationException()
    assert exc.status_code == status.HTTP_403_FORBIDDEN
