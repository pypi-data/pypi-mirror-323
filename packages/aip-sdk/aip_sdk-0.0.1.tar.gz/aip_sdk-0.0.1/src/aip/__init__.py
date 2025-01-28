# ruff: noqa: E402

# Patch asyncio to allow nested event loops
__import__("nest_asyncio").apply()

# Rest of __init__.py
import argparse as _argparse

from .clients import PolarsClient as _PolarsClient
from .providers.openai import OpenAIProvider as _OpenAIProvider
from .providers.openai import OpenAIProviderConfig as _OpenAIProviderConfig
from .proxy import ModelProxy as _ModelProxy

defaults = _argparse.Namespace()
defaults.openai = _OpenAIProvider(_OpenAIProviderConfig())

_default_proxy = _ModelProxy(
    providers={
        "openai": defaults.openai,
    }
)

_polars_client = _PolarsClient(proxy=_default_proxy)

chat = _polars_client.chat
embed = _polars_client.embed
extract = _polars_client.extract
# summarize = _polars_client.summarize
