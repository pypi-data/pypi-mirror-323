from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.vectorstores.redis.filters import (
        RedisFilter,
        RedisFilterExpression,
        RedisFilterField,
        RedisFilterOperator,
        RedisNum,
        RedisTag,
        RedisText,
        check_operator_misuse,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "RedisFilterOperator": "aibaba_ai_community.vectorstores.redis.filters",
    "RedisFilter": "aibaba_ai_community.vectorstores.redis.filters",
    "RedisFilterField": "aibaba_ai_community.vectorstores.redis.filters",
    "check_operator_misuse": "aibaba_ai_community.vectorstores.redis.filters",
    "RedisTag": "aibaba_ai_community.vectorstores.redis.filters",
    "RedisNum": "aibaba_ai_community.vectorstores.redis.filters",
    "RedisText": "aibaba_ai_community.vectorstores.redis.filters",
    "RedisFilterExpression": "aibaba_ai_community.vectorstores.redis.filters",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "RedisFilterOperator",
    "RedisFilter",
    "RedisFilterField",
    "check_operator_misuse",
    "RedisTag",
    "RedisNum",
    "RedisText",
    "RedisFilterExpression",
]
