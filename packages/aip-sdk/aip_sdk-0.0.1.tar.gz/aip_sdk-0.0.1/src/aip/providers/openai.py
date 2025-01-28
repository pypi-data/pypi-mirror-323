import asyncio
import os
from typing import Any, TypeVar

import aiohttp
from pydantic import BaseModel

from .._types import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
)
from .base import BaseProvider, BaseProviderConfig, RateLimitStyle

T = TypeVar("T", bound=BaseModel)


class OpenAIProviderConfig(BaseProviderConfig):
    base_url: str = "https://api.openai.com/v1"
    api_key: str | None = None
    rate_limit_style: RateLimitStyle = "header_based"
    max_concurrent_chats: int = 40
    max_concurrent_embeddings: int = 40


class OpenAIProvider(BaseProvider[OpenAIProviderConfig]):
    def configure(self, config: OpenAIProviderConfig | dict[str, Any]):
        if isinstance(config, dict):
            config = OpenAIProviderConfig(**config)
        self.config = config
        self.api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self._chat_semaphore = asyncio.Semaphore(self.config.max_concurrent_chats)
        self._embed_semaphore = asyncio.Semaphore(self.config.max_concurrent_embeddings)

    async def chat(
        self,
        request: ChatCompletionRequest,
        session: aiohttp.ClientSession,
    ) -> ChatCompletionResponse:
        async with self._chat_semaphore:
            async with session.post(
                f"{self.config.base_url}/chat/completions",
                headers=self.headers,
                json=request.flatten_params(),
            ) as response:
                response.raise_for_status()
                response_data = await response.json()
                return ChatCompletionResponse.model_validate(response_data)

    async def embed(
        self,
        request: EmbeddingRequest,
        session: aiohttp.ClientSession,
    ) -> EmbeddingResponse:
        async with self._embed_semaphore:
            async with session.post(
                f"{self.config.base_url}/embeddings",
                headers=self.headers,
                json=request.model_dump(),
            ) as response:
                response.raise_for_status()
                response_data = await response.json()
                return EmbeddingResponse.model_validate(response_data)
