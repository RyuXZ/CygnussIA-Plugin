"""
CygnussIA Plugin V2
Infrastructure - Ollama Models
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class OllamaModel(BaseModel):
    """Installed Ollama model."""

    name: str
    digest: str | None = None
    size: int | None = None
    modified_at: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class GenerateOptions(BaseModel):
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    num_predict: int | None = None
    seed: int | None = None


class GenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: bool = False
    system: str | None = None
    template: str | None = None
    keep_alive: str = "30m"
    options: GenerateOptions = Field(default_factory=GenerateOptions)


class GenerateChunk(BaseModel):
    model: str
    response: str
    done: bool = False


class GenerateResponse(BaseModel):
    model: str
    response: str
    done: bool

    total_duration: int | None = None
    load_duration: int | None = None
    prompt_eval_count: int | None = None
    eval_count: int | None = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    stream: bool = False
    keep_alive: str = "30m"
    options: GenerateOptions = Field(default_factory=GenerateOptions)


class EmbeddingsRequest(BaseModel):
    model: str
    prompt: str


class EmbeddingsResponse(BaseModel):
    embedding: list[float]