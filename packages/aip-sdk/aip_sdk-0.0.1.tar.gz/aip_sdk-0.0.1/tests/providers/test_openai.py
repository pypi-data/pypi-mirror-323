import os

import aiohttp
import pytest
from aip._types import (
    ChatCompletionRequest,
    ChatCompletionRequestMessage,
    EmbeddingRequest,
)
from aip.providers.openai import OpenAIProvider, OpenAIProviderConfig


@pytest.fixture
def provider() -> OpenAIProvider:
    provider = OpenAIProvider(
        config=OpenAIProviderConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    )
    return provider


@pytest.mark.asyncio
async def test_chat_completion(provider: OpenAIProvider):
    request = ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=[ChatCompletionRequestMessage(role="user", content="Say hello!")],
    )

    async with aiohttp.ClientSession() as session:
        response = await provider.chat(request, session)

    assert response.choices is not None
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None
    assert response.usage is not None


@pytest.mark.asyncio
async def test_embedding(provider: OpenAIProvider):
    request = EmbeddingRequest(model="text-embedding-ada-002", input="Hello world")

    async with aiohttp.ClientSession() as session:
        response = await provider.embed(request, session)

    assert response.data is not None
    assert len(response.data) == 1
    assert len(response.data[0].embedding) > 0
    assert response.usage is not None
