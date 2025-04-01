"""Exceptions while using CosmosClient."""


class APIKeyMissingError(Exception):
    """Exception raised when an API key is missing."""

    def __init__(self) -> None:
        """Initialize the exception with a message."""
        message = "API Key for Cosmos is missing."
        super().__init__(message)


class InvalidInputError(Exception):
    """Exception raised when invalid input is provided."""

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message."""
        super().__init__(message)
