"""
CygnussIA Plugin v2
Ollama Client

Author: CygnussIA Project
License: MIT
"""

from __future__ import annotations

from typing import Any

import httpx

from config import config
from logger import get_logger

logger = get_logger(__name__)


class OllamaClientError(Exception):
    """Excepción base del cliente Ollama."""


class OllamaConnectionError(OllamaClientError):
    """No fue posible conectar con Ollama."""


class OllamaClient:

    def __init__(self):

        self.base_url = config.get(
            "ollama_url",
            "http://127.0.0.1:11434"
        ).rstrip("/")

        self.timeout = config.get(
            "timeout",
            300
        )

        self.client = httpx.AsyncClient(

            base_url=self.base_url,

            timeout=self.timeout

        )

    async def close(self):

        await self.client.aclose()

    async def health(self) -> bool:

        """
        Comprueba si Ollama está disponible.
        """

        try:

            response = await self.client.get("/api/tags")

            return response.status_code == 200

        except Exception as e:

            logger.error(e)

            return False

    async def version(self) -> dict:

        """
        Devuelve la versión de Ollama.
        """

        response = await self.client.get("/api/version")

        response.raise_for_status()

        return response.json()

    async def list_models(self):

        """
        Obtiene todos los modelos instalados.
        """

        response = await self.client.get("/api/tags")

        response.raise_for_status()

        data = response.json()

        return data.get("models", [])

    async def model_exists(self, model: str) -> bool:

        models = await self.list_models()

        for item in models:

            if item["name"] == model:

                return True

        return False

    async def generate(

        self,

        model: str,

        prompt: str,

        stream: bool = False,

        **kwargs

    ) -> dict[str, Any]:

        payload = {

            "model": model,

            "prompt": prompt,

            "stream": stream

        }

        payload.update(kwargs)

        logger.info(
            "Generating with model %s",
            model
        )

        response = await self.client.post(

            "/api/generate",

            json=payload

        )

        response.raise_for_status()

        return response.json()

    async def chat(

        self,

        model: str,

        messages,

        stream=False,

        **kwargs

    ):

        payload = {

            "model": model,

            "messages": messages,

            "stream": stream

        }

        payload.update(kwargs)

        response = await self.client.post(

            "/api/chat",

            json=payload

        )

        response.raise_for_status()

        return response.json()

    async def embeddings(

        self,

        model: str,

        prompt: str

    ):

        response = await self.client.post(

            "/api/embeddings",

            json={

                "model": model,

                "prompt": prompt

            }

        )

        response.raise_for_status()

        return response.json()

    async def pull(

        self,

        model: str

    ):

        response = await self.client.post(

            "/api/pull",

            json={

                "name": model,

                "stream": False

            }

        )

        response.raise_for_status()

        return response.json()

    async def delete(

        self,

        model: str

    ):

        response = await self.client.delete(

            "/api/delete",

            json={

                "name": model

            }

        )

        response.raise_for_status()

        return response.json()


ollama = OllamaClient()