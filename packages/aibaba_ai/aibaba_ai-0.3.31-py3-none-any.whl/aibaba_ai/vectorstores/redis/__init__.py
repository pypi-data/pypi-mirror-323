from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.vectorstores import Redis
    from aibaba_ai_community.vectorstores.redis.base import RedisVectorStoreRetriever
    from aibaba_ai_community.vectorstores.redis.filters import (
        RedisFilter,
        RedisNum,
        RedisTag,
        RedisText,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "Redis": "aibaba_ai_community.vectorstores",
    "RedisFilter": "aibaba_ai_community.vectorstores.redis.filters",
    "RedisTag": "aibaba_ai_community.vectorstores.redis.filters",
    "RedisText": "aibaba_ai_community.vectorstores.redis.filters",
    "RedisNum": "aibaba_ai_community.vectorstores.redis.filters",
    "RedisVectorStoreRetriever": "aibaba_ai_community.vectorstores.redis.base",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "Redis",
    "RedisFilter",
    "RedisTag",
    "RedisText",
    "RedisNum",
    "RedisVectorStoreRetriever",
]
