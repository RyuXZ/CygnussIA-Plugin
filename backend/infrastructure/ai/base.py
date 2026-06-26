"""
CygnussIA Plugin V2
------------------

Abstract interface for AI providers.

This module defines the contract that every AI backend must implement.

Current implementations:
    - Ollama

Future implementations:
    - LM Studio
    - vLLM
    - OpenAI Compatible APIs
    - ComfyUI
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from pydantic import BaseModel


# ============================================================
# Models
# ============================================================


class AIModel(BaseModel):
    """Information about an installed model."""

    name: str
    size: int | None = None
    digest: str | None = None
    modified_at: str | None = None
    family: str | None = None
    parameter_size: str | None = None
    quantization_level: str | None = None


class GenerationChunk(BaseModel):
    """
    Streaming chunk returned while generating text.
    """

    response: str

    done: bool = False


class GenerationResponse(BaseModel):
    """
    Final generation result.
    """

    model: str

    response: str

    done: bool = True

    total_duration: int | None = None

    load_duration: int | None = None

    prompt_eval_count: int | None = None

    eval_count: int | None = None


# ============================================================
# Base Provider
# ============================================================


class AIProvider(ABC):
    """
    Abstract AI provider.

    Every backend (Ollama, LM Studio, etc.)
    must inherit from this class.
    """

    @abstractmethod
    async def health(self) -> bool:
        """Returns True if provider is online."""
        raise NotImplementedError

    @abstractmethod
    async def version(self) -> dict[str, Any]:
        """Returns provider version."""
        raise NotImplementedError

    @abstractmethod
    async def list_models(self) -> list[AIModel]:
        """Returns installed models."""
        raise NotImplementedError

    @abstractmethod
    async def model_exists(self, model: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def generate(
        self,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> GenerationResponse:
        """
        Generate a complete response.
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_stream(
        self,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> AsyncIterator[GenerationChunk]:
        """
        Stream tokens while generating.
        """
        raise NotImplementedError

    @abstractmethod
    async def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> GenerationResponse:
        raise NotImplementedError

    @abstractmethod
    async def embeddings(
        self,
        model: str,
        prompt: str,
    ) -> list[float]:
        raise NotImplementedError

    @abstractmethod
    async def pull(
        self,
        model: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        model: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Close HTTP connections."""
        raise NotImplementedError