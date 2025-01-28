import asyncio
from typing import Any, Callable, Dict, Type, TypeVar, Union

import polars as pl
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def to_response_format(response_model: Type[T]) -> dict:
    model_schema = response_model.model_json_schema()
    model_schema["additionalProperties"] = False
    return {
        "type": "json_schema",
        "json_schema": {
            "schema": model_schema,
            "name": response_model.__name__,
            "strict": True,
        },
    }


def ensure_expr(expr: Union[str, pl.Expr], str_fn: Callable[[str], pl.Expr]) -> pl.Expr:
    if isinstance(expr, str):
        return str_fn(expr)
    return expr


def to_polars_schema(schema: Union[Type[BaseModel], Dict[str, Any]]) -> pl.Struct:
    if isinstance(schema, type) and issubclass(schema, BaseModel):
        schema = schema.model_json_schema()

    def resolve_ref(ref: str, root_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a JSON schema reference against the root schema."""
        name = ref[len("#/$defs/") :]
        return root_schema["$defs"][name]

    def _convert_field(
        field_schema: Dict[str, Any], root_schema: Dict[str, Any]
    ) -> pl.DataType:
        # Handle references first
        if "$ref" in field_schema:
            field_schema = resolve_ref(field_schema["$ref"], root_schema)

        field_type = field_schema.get("type")
        if field_type == "string":
            return pl.String()
        elif field_type == "number":
            return pl.Float64()
        elif field_type == "integer":
            return pl.Int64()
        elif field_type == "boolean":
            return pl.Boolean()
        elif field_type == "array":
            items = field_schema.get("items", {})
            if isinstance(items, dict):
                return pl.List(_convert_field(items, root_schema))
            return pl.List(pl.Unknown())
        elif field_type == "object":
            properties = field_schema.get("properties", {})
            return pl.Struct(
                {
                    name: _convert_field(prop, root_schema)
                    for name, prop in properties.items()
                }
            )
        else:
            return pl.Unknown()

    if schema.get("type") != "object":
        raise ValueError("Top-level schema must be an object type")

    properties = schema.get("properties", {})
    return pl.Struct(
        {name: _convert_field(prop, schema) for name, prop in properties.items()}
    )


def parse_model_id(model_id: str, providers: dict) -> tuple[str, str]:
    provider, _, model = model_id.partition("/")
    if provider not in providers:
        raise ValueError(f"No provider registered for alias '{provider}'")
    if not model:
        raise ValueError("Model name is required in the format 'provider/model'")
    return provider, model


def get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop
