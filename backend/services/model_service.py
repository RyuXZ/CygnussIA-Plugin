"""
CygnussIA Plugin v2

Model Service

Author: CygnussIA Project
License: MIT
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

from logger import get_logger
from ollama_client import ollama

logger = get_logger(__name__)


class ModelService:

    CACHE_SECONDS = 30

    def __init__(self):

        self._models: list[dict[str, Any]] = []

        self._last_update: datetime | None = None

        self._lock = asyncio.Lock()

    async def refresh(self, force: bool = False):

        async with self._lock:

            if (
                not force
                and self._last_update
                and datetime.utcnow() - self._last_update
                < timedelta(seconds=self.CACHE_SECONDS)
            ):
                return self._models

            logger.info("Refreshing model cache...")

            self._models = await ollama.list_models()

            self._last_update = datetime.utcnow()

            logger.info(
                "%s models detected.",
                len(self._models)
            )

            return self._models

    async def list(self):

        return await self.refresh()

    async def names(self):

        models = await self.refresh()

        return sorted(

            [m["name"] for m in models]

        )

    async def exists(self, model: str):

        models = await self.refresh()

        return any(

            m["name"] == model

            for m in models

        )

    async def get(self, model: str):

        models = await self.refresh()

        for item in models:

            if item["name"] == model:

                return item

        return None

    async def version(self):

        return await ollama.version()

    async def health(self):

        return await ollama.health()

    async def pull(self, model: str):

        logger.info("Downloading %s", model)

        result = await ollama.pull(model)

        await self.refresh(force=True)

        return result

    async def delete(self, model: str):

        logger.info("Deleting %s", model)

        result = await ollama.delete(model)

        await self.refresh(force=True)

        return result

    async def statistics(self):

        models = await self.refresh()

        total_size = 0

        for m in models:

            total_size += m.get("size", 0)

        return {

            "count": len(models),

            "total_size": total_size,

            "cached": self._last_update,

        }


model_service = ModelService()