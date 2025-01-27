from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.agent_toolkits.openapi.planner import (
        RequestsDeleteToolWithParsing,
        RequestsGetToolWithParsing,
        RequestsPatchToolWithParsing,
        RequestsPostToolWithParsing,
        RequestsPutToolWithParsing,
        create_openapi_agent,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "RequestsGetToolWithParsing": (
        "aibaba_ai_community.agent_toolkits.openapi.planner"
    ),
    "RequestsPostToolWithParsing": (
        "aibaba_ai_community.agent_toolkits.openapi.planner"
    ),
    "RequestsPatchToolWithParsing": (
        "aibaba_ai_community.agent_toolkits.openapi.planner"
    ),
    "RequestsPutToolWithParsing": (
        "aibaba_ai_community.agent_toolkits.openapi.planner"
    ),
    "RequestsDeleteToolWithParsing": (
        "aibaba_ai_community.agent_toolkits.openapi.planner"
    ),
    "create_openapi_agent": "aibaba_ai_community.agent_toolkits.openapi.planner",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "RequestsGetToolWithParsing",
    "RequestsPostToolWithParsing",
    "RequestsPatchToolWithParsing",
    "RequestsPutToolWithParsing",
    "RequestsDeleteToolWithParsing",
    "create_openapi_agent",
]
