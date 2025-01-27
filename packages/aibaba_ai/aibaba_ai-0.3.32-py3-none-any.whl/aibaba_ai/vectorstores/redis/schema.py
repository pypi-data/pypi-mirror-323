from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.vectorstores.redis.schema import (
        FlatVectorField,
        HNSWVectorField,
        NumericFieldSchema,
        RedisDistanceMetric,
        RedisField,
        RedisModel,
        RedisVectorField,
        TagFieldSchema,
        TextFieldSchema,
        read_schema,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "RedisDistanceMetric": "aibaba_ai_community.vectorstores.redis.schema",
    "RedisField": "aibaba_ai_community.vectorstores.redis.schema",
    "TextFieldSchema": "aibaba_ai_community.vectorstores.redis.schema",
    "TagFieldSchema": "aibaba_ai_community.vectorstores.redis.schema",
    "NumericFieldSchema": "aibaba_ai_community.vectorstores.redis.schema",
    "RedisVectorField": "aibaba_ai_community.vectorstores.redis.schema",
    "FlatVectorField": "aibaba_ai_community.vectorstores.redis.schema",
    "HNSWVectorField": "aibaba_ai_community.vectorstores.redis.schema",
    "RedisModel": "aibaba_ai_community.vectorstores.redis.schema",
    "read_schema": "aibaba_ai_community.vectorstores.redis.schema",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "RedisDistanceMetric",
    "RedisField",
    "TextFieldSchema",
    "TagFieldSchema",
    "NumericFieldSchema",
    "RedisVectorField",
    "FlatVectorField",
    "HNSWVectorField",
    "RedisModel",
    "read_schema",
]
