import asyncio
from typing import Iterable, TypeVar

import aiohttp
from pydantic import BaseModel

from aip import utils

from ._types import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
)
from .providers import BaseProvider

T = TypeVar("T", bound=BaseModel)


class ModelProxy:
    def __init__(self, providers: dict[str, BaseProvider]):
        self.providers = providers

    async def chat(
        self,
        request: ChatCompletionRequest,
        session: aiohttp.ClientSession,
    ) -> ChatCompletionResponse:
        provider_key, model = utils.parse_model_id(request.model, self.providers)
        provider = self.providers[provider_key]
        request.model = model
        return await provider.chat(request=request, session=session)

    async def embed(
        self,
        request: EmbeddingRequest,
        session: aiohttp.ClientSession,
    ) -> EmbeddingResponse:
        provider_key, model = utils.parse_model_id(request.model, self.providers)
        provider = self.providers[provider_key]
        request.model = model
        return await provider.embed(request=request, session=session)

    def chat_iter(
        self, requests: Iterable[ChatCompletionRequest]
    ) -> list[ChatCompletionResponse]:
        async def _collect():
            async with aiohttp.ClientSession() as session:
                tasks = [self.chat(request, session) for request in requests]
                return await asyncio.gather(*tasks)

        return asyncio.get_event_loop().run_until_complete(_collect())

    def embed_iter(
        self, requests: Iterable[EmbeddingRequest]
    ) -> list[EmbeddingResponse]:
        async def _collect():
            async with aiohttp.ClientSession() as session:
                tasks = [self.embed(request, session) for request in requests]
                return await asyncio.gather(*tasks)

        return asyncio.get_event_loop().run_until_complete(_collect())
