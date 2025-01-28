from typing import Any, Dict, Literal

from pydantic import BaseModel


class ClientConfig(BaseModel):
    default_chat_model: str = "openai/gpt-4o-mini"
    default_embedding_model: str = "openai/text-embedding-3-small"


# Chat Completions


class ChatCompletionRequestMessage(BaseModel):
    content: str
    role: Literal["system", "user", "assistant"]


class ChatCompletionRequestParams(BaseModel):
    frequency_penalty: float | None = None
    logprobs: bool | None = None
    max_completion_tokens: int | None = None
    max_tokens: int | None = None
    presence_penalty: float | None = None
    response_format: Dict[str, Any] | None = None
    seed: int | None = None
    service_tier: Literal["auto", "default"] | None = None
    stop: str | list[str] | None = None
    store: bool | None = None
    temperature: float | None = None
    top_logprobs: int | None = None
    top_p: float | None = None


class ChatCompletionRequest(BaseModel):
    messages: list[ChatCompletionRequestMessage]
    model: str
    params: ChatCompletionRequestParams | None = None

    def flatten_params(self) -> dict[str, Any]:
        params = self.params.model_dump() if self.params else {}
        return self.model_dump(exclude={"params"}) | params


class TopLogprob(BaseModel):
    token: str
    bytes: list[int] | None = None
    logprob: float


class ChatCompletionTokenLogprob(BaseModel):
    token: str
    bytes: list[int] | None = None
    logprob: float
    top_logprobs: list[TopLogprob]


class CompletionTokensDetails(BaseModel):
    accepted_prediction_tokens: int | None = None
    audio_tokens: int | None = None
    reasoning_tokens: int | None = None
    rejected_prediction_tokens: int | None = None


class PromptTokensDetails(BaseModel):
    audio_tokens: int | None = None
    cached_tokens: int | None = None


class CompletionUsage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    completion_tokens_details: CompletionTokensDetails | None = None
    prompt_tokens_details: PromptTokensDetails | None = None


class ChatCompletionMessage(BaseModel):
    content: str | None = None
    refusal: str | None = None
    role: Literal["assistant"]


class ChoiceLogprobs(BaseModel):
    content: list[ChatCompletionTokenLogprob] | None = None
    refusal: list[ChatCompletionTokenLogprob] | None = None


class Choice(BaseModel):
    finish_reason: Literal[
        "stop", "length", "tool_calls", "content_filter", "function_call"
    ]
    index: int
    logprobs: ChoiceLogprobs | None = None
    message: ChatCompletionMessage


class ChatCompletionResponse(BaseModel):
    id: str
    choices: list[Choice]
    created: int
    model: str
    object: Literal["chat.completion"]  # delete maybe?
    service_tier: Literal["scale", "default"] | None = None
    system_fingerprint: str | None = None
    usage: CompletionUsage | None = None


# Embeddings


class EmbeddingRequest(BaseModel):
    input: str
    model: str


class Embedding(BaseModel):
    embedding: list[float]
    index: int
    object: Literal["embedding"]  # delete maybe?


class Usage(BaseModel):
    prompt_tokens: int
    total_tokens: int


class EmbeddingResponse(BaseModel):
    data: list[Embedding]
    model: str
    object: Literal["list"]  # delete maybe?
    usage: Usage
