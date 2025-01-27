from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.cache import (
        AstraDBCache,
        AstraDBSemanticCache,
        AzureCosmosDBSemanticCache,
        CassandraCache,
        CassandraSemanticCache,
        FullLLMCache,
        FullMd5LLMCache,
        GPTCache,
        InMemoryCache,
        MomentoCache,
        RedisCache,
        RedisSemanticCache,
        SQLAlchemyCache,
        SQLAlchemyMd5Cache,
        SQLiteCache,
        UpstashRedisCache,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "FullLLMCache": "aibaba_ai_community.cache",
    "SQLAlchemyCache": "aibaba_ai_community.cache",
    "SQLiteCache": "aibaba_ai_community.cache",
    "UpstashRedisCache": "aibaba_ai_community.cache",
    "RedisCache": "aibaba_ai_community.cache",
    "RedisSemanticCache": "aibaba_ai_community.cache",
    "GPTCache": "aibaba_ai_community.cache",
    "MomentoCache": "aibaba_ai_community.cache",
    "InMemoryCache": "aibaba_ai_community.cache",
    "CassandraCache": "aibaba_ai_community.cache",
    "CassandraSemanticCache": "aibaba_ai_community.cache",
    "FullMd5LLMCache": "aibaba_ai_community.cache",
    "SQLAlchemyMd5Cache": "aibaba_ai_community.cache",
    "AstraDBCache": "aibaba_ai_community.cache",
    "AstraDBSemanticCache": "aibaba_ai_community.cache",
    "AzureCosmosDBSemanticCache": "aibaba_ai_community.cache",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "FullLLMCache",
    "SQLAlchemyCache",
    "SQLiteCache",
    "UpstashRedisCache",
    "RedisCache",
    "RedisSemanticCache",
    "GPTCache",
    "MomentoCache",
    "InMemoryCache",
    "CassandraCache",
    "CassandraSemanticCache",
    "FullMd5LLMCache",
    "SQLAlchemyMd5Cache",
    "AstraDBCache",
    "AstraDBSemanticCache",
    "AzureCosmosDBSemanticCache",
]
