from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.utilities.vertexai import (
        create_retry_decorator,
        get_client_info,
        init_vertexai,
        raise_vertex_import_error,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "create_retry_decorator": "aibaba_ai_community.utilities.vertexai",
    "raise_vertex_import_error": "aibaba_ai_community.utilities.vertexai",
    "init_vertexai": "aibaba_ai_community.utilities.vertexai",
    "get_client_info": "aibaba_ai_community.utilities.vertexai",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "create_retry_decorator",
    "raise_vertex_import_error",
    "init_vertexai",
    "get_client_info",
]
