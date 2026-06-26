"""
CygnussIA Plugin V2
Infrastructure - Ollama Exceptions
"""

from __future__ import annotations


class OllamaError(Exception):
    """Base exception for all Ollama-related errors."""


class OllamaConnectionError(OllamaError):
    """Raised when the client cannot connect to the Ollama server."""


class OllamaTimeoutError(OllamaError):
    """Raised when a request exceeds the configured timeout."""


class OllamaResponseError(OllamaError):
    """Raised when Ollama returns an unexpected HTTP response."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code


class OllamaModelNotFoundError(OllamaError):
    """Raised when the requested model does not exist."""

    def __init__(self, model: str) -> None:
        super().__init__(f"Model '{model}' was not found.")
        self.model = model


class OllamaStreamingError(OllamaError):
    """Raised when a streaming response fails."""


class OllamaCancelledError(OllamaError):
    """Raised when an operation is cancelled."""


class OllamaValidationError(OllamaError):
    """Raised when invalid data is passed to the client."""


class OllamaAuthenticationError(OllamaError):
    """Reserved for future authenticated deployments."""


class OllamaRateLimitError(OllamaError):
    """Raised when the provider rejects requests because of rate limiting."""


class OllamaServerError(OllamaError):
    """Raised when Ollama returns a 5xx response."""

    def __init__(
        self,
        status_code: int,
        message: str,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code