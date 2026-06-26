"""
CygnussIA Plugin V2
Professional Ollama Client

Author: CygnussIA Project
License: MIT
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx
import orjson

from backend.config import config
from backend.infrastructure.ollama.exceptions import (
    OllamaConnectionError,
    OllamaResponseError,
    OllamaServerError,
    OllamaTimeoutError,
)
from backend.infrastructure.ollama.models import (
    ChatRequest,
    EmbeddingsRequest,
    GenerateRequest,
    OllamaModel,
)

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Professional asynchronous client for Ollama.

    Features
    --------
    • HTTP Connection Pool
    • Keep Alive
    • Automatic Retries
    • Exponential Backoff
    • Streaming
    • Async
    • Typed Responses
    """

    DEFAULT_TIMEOUT = 300.0
    DEFAULT_RETRIES = 3

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        retries: int | None = None,
    ) -> None:

        self.base_url = (
            base_url
            or config.get(
                "ollama_url",
                "http://127.0.0.1:11434",
            )
        ).rstrip("/")

        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.retries = retries or self.DEFAULT_RETRIES

        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        """
        Initializes the HTTP client.
        """

        if self._client is not None:
            return

        limits = httpx.Limits(
            max_connections=50,
            max_keepalive_connections=20,
            keepalive_expiry=60,
        )

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            limits=limits,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "CygnussIA/2.0",
            },
        )

        logger.info("Ollama client initialized")

    async def close(self) -> None:
        """
        Closes the HTTP client.
        """

        if self._client is None:
            return

        await self._client.aclose()

        self._client = None

        logger.info("Ollama client closed")

    @property
    def connected(self) -> bool:
        return self._client is not None

    async def _ensure_client(self) -> httpx.AsyncClient:

        if self._client is None:
            await self.start()

        return self._client

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Performs an HTTP request with retries.
        """

        client = await self._ensure_client()

        last_exception: Exception | None = None

        for attempt in range(self.retries):

            try:

                response = await client.request(
                    method,
                    endpoint,
                    **kwargs,
                )

                if response.status_code >= 500:
                    raise OllamaServerError(
                        response.status_code,
                        response.text,
                    )

                response.raise_for_status()

                return response

            except httpx.TimeoutException as exc:

                last_exception = exc

                logger.warning(
                    "Timeout (%d/%d)",
                    attempt + 1,
                    self.retries,
                )

            except httpx.ConnectError as exc:

                last_exception = exc

                logger.warning(
                    "Connection failed (%d/%d)",
                    attempt + 1,
                    self.retries,
                )

            except httpx.HTTPStatusError as exc:

                raise OllamaResponseError(
                    message=exc.response.text,
                    status_code=exc.response.status_code,
                ) from exc

            await asyncio.sleep(2**attempt)

        if isinstance(last_exception, httpx.TimeoutException):
            raise OllamaTimeoutError from last_exception

        raise OllamaConnectionError from last_exception

    async def _get(
        self,
        endpoint: str,
    ) -> Any:

        response = await self._request(
            "GET",
            endpoint,
        )

        return response.json()

    async def _delete(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> Any:

        response = await self._request(
            "DELETE",
            endpoint,
            json=payload,
        )

        return response.json()

    async def _post(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> Any:

        response = await self._request(
            "POST",
            endpoint,
            json=payload,
        )

        return response.json()

    async def _stream(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Generic streaming helper.
        """

        client = await self._ensure_client()

        async with client.stream(
            "POST",
            endpoint,
            json=payload,
        ) as response:

            response.raise_for_status()

            async for line in response.aiter_lines():

                if not line:
                    continue

                yield orjson.loads(line)

        # ==========================================================
    # Health
    # ==========================================================

    async def health(self) -> bool:
        """
        Returns True if Ollama is reachable.
        """

        try:

            await self._get("/api/tags")

            return True

        except Exception:

            logger.exception("Unable to connect to Ollama")

            return False

    # ==========================================================
    # Version
    # ==========================================================

    async def version(self) -> dict[str, Any]:
        """
        Returns Ollama version.
        """

        return await self._get("/api/version")

    # ==========================================================
    # Installed Models
    # ==========================================================

    async def list_models(self) -> list[OllamaModel]:
        """
        Returns every installed model.
        """

        data = await self._get("/api/tags")

        models: list[OllamaModel] = []

        for item in data.get("models", []):

            models.append(
                OllamaModel.model_validate(item)
            )

        return models

    # ==========================================================
    # Model Exists
    # ==========================================================

    async def model_exists(
        self,
        model: str,
    ) -> bool:

        models = await self.list_models()

        return any(
            m.name == model
            for m in models
        )

    # ==========================================================
    # Show Model
    # ==========================================================

    async def show(
        self,
        model: str,
    ) -> dict[str, Any]:
        """
        Returns detailed information about a model.
        """

        return await self._post(

            "/api/show",

            {

                "model": model,

            },

        )

    # ==========================================================
    # Generate
    # ==========================================================

    async def generate(
        self,
        request: GenerateRequest,
    ) -> dict[str, Any]:
        """
        Generates a response.

        Streaming must be disabled.
        """

        payload = request.model_dump(
            exclude_none=True
        )

        payload["stream"] = False

        return await self._post(

            "/api/generate",

            payload,

        )

    # ==========================================================
    # Generate Stream
    # ==========================================================

    async def generate_stream(
        self,
        request: GenerateRequest,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Streams generated tokens.
        """

        payload = request.model_dump(
            exclude_none=True
        )

        payload["stream"] = True

        async for chunk in self._stream(

            "/api/generate",

            payload,

        ):

            yield chunk

    # ==========================================================
    # Chat
    # ==========================================================

    async def chat(
        self,
        request: ChatRequest,
    ) -> dict[str, Any]:

        payload = request.model_dump(
            exclude_none=True
        )

        payload["stream"] = False

        return await self._post(

            "/api/chat",

            payload,

        )

    # ==========================================================
    # Chat Stream
    # ==========================================================

    async def chat_stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[dict[str, Any]]:

        payload = request.model_dump(
            exclude_none=True
        )

        payload["stream"] = True

        async for chunk in self._stream(

            "/api/chat",

            payload,

        ):

            yield chunk