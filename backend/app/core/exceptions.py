from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class ForesightException(HTTPException):
    """Base exception class for all ForesightAI specific exceptions."""
    def __init__(
        self, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = "An unexpected error occurred.",
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class EntityNotFoundException(ForesightException):
    """Raised when a requested database entity is not found."""
    def __init__(self, entity_name: str, entity_id: Any) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} with ID {entity_id} not found."
        )


class BadRequestException(ForesightException):
    """Raised when the client sends a malformed request."""
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class AuthenticationException(ForesightException):
    """Raised when authentication fails."""
    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationException(ForesightException):
    """Raised when the user does not have required permissions."""
    def __init__(self, detail: str = "Not enough permissions") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )
