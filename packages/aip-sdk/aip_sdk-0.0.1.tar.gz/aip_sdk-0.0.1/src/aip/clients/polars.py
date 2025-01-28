from typing import TypeVar

import polars as pl
from pydantic import BaseModel

from aip import utils
from aip._types import (
    ChatCompletionRequest,
    EmbeddingRequest,
)
from aip.proxy import ModelProxy
from aip.utils import to_response_format

DEFAULT_EMBEDDING_MODEL = "openai/text-embedding-3-small"
DEFAULT_CHAT_MODEL = "openai/gpt-4o-mini"

T = TypeVar("T", bound=BaseModel)


class PolarsClient:
    def __init__(self, proxy: ModelProxy):
        self.proxy = proxy

    def embed(self, expr: str | pl.Expr, model: str | None = None) -> pl.Expr:
        def _embed_series(series: pl.Series) -> pl.Series:
            requests = [
                EmbeddingRequest(
                    input=text,
                    model=model if model is not None else DEFAULT_EMBEDDING_MODEL,
                )
                for text in series
            ]
            responses = self.proxy.embed_iter(requests)
            return pl.Series([resp.data[0].embedding for resp in responses])

        expr = utils.ensure_expr(expr, str_fn=pl.col)
        return expr.map_batches(_embed_series).alias("embedding")

    def chat(
        self,
        system_prompt: str | pl.Expr,
        user_prompt: str | pl.Expr,
        response_model: type[T] | None = None,
        model: str | None = None,
    ) -> pl.Expr:
        system_prompt = utils.ensure_expr(system_prompt, str_fn=pl.lit).alias("system")
        user_prompt = utils.ensure_expr(user_prompt, str_fn=pl.lit).alias("user")
        struct = pl.struct(system_prompt, user_prompt)

        if response_model is not None:
            return_dtype = utils.to_polars_schema(response_model)
            params = {"response_format": to_response_format(response_model)}
            alias = response_model.__name__
        else:
            return_dtype = pl.String
            params = {}
            alias = "chat"

        def _chat_series(series: pl.Series) -> pl.Series:
            requests = [
                ChatCompletionRequest(
                    **{
                        "messages": [
                            {"role": "system", "content": s["system"]},
                            {"role": "user", "content": s["user"]},
                        ],
                        "model": model or DEFAULT_CHAT_MODEL,
                        "params": params,
                    }
                )
                for s in series
            ]
            responses = self.proxy.chat_iter(requests)
            if response_model is not None:
                return pl.Series(
                    [
                        response_model.model_validate_json(
                            resp.choices[0].message.content or "{}"
                        ).model_dump()
                        for resp in responses
                    ]
                )
            else:
                return pl.Series(
                    [resp.choices[0].message.content for resp in responses]
                )

        chat_expr = struct.map_batches(_chat_series, return_dtype)
        return chat_expr.alias(alias)

    def extract(
        self,
        expr: str | pl.Expr,
        response_model: type[T],
        model: str | None = None,
        system_prompt: str | pl.Expr | None = None,
    ) -> pl.Expr:
        # NOTE: No need to explicitly specify schema in system prompt, automatically
        #       injected before the system prompt server-side for structured generation.
        default_prompt = (
            "Extract data from the provided content according to the specified schema."
        )
        return self.chat(
            system_prompt=system_prompt or default_prompt,
            user_prompt=expr,
            response_model=response_model,
            model=model,
        )
