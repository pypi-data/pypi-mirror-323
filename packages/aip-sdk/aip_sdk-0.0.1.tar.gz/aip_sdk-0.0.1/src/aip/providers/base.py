from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, Literal, TypeVar

import aiohttp
from pydantic import BaseModel

from .._types import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
)

ConfigT = TypeVar("ConfigT", bound="BaseProviderConfig")


RateLimitStyle = Literal["header_based", "quota_based"] | None


class RateLimitInfo(BaseModel):
    style: RateLimitStyle
    limit_requests: int | None = None
    limit_tokens: int | None = None
    remaining_requests: int | None = None
    remaining_tokens: int | None = None
    reset_requests: datetime | None = None
    reset_tokens: datetime | None = None

    @property
    def is_rate_limited(self) -> bool:
        if self.style == "header_based":
            return (
                self.remaining_requests is not None and self.remaining_requests <= 0
            ) or (self.remaining_tokens is not None and self.remaining_tokens <= 0)
        return False  # For QUOTA_BASED, we rely on error responses instead


class BaseProviderConfig(BaseModel):
    rate_limit_style: RateLimitStyle = None
    max_concurrent_chats: int = -1
    max_concurrent_embeddings: int = -1


class BaseProvider(ABC, Generic[ConfigT]):
    config: ConfigT

    def __init__(self, config: ConfigT):
        self.configure(config)

    @abstractmethod
    def configure(self, config: ConfigT | dict[str, Any]): ...

    @abstractmethod
    async def chat(
        self, request: ChatCompletionRequest, session: aiohttp.ClientSession
    ) -> ChatCompletionResponse: ...

    @abstractmethod
    async def embed(
        self, request: EmbeddingRequest, session: aiohttp.ClientSession
    ) -> EmbeddingResponse: ...
