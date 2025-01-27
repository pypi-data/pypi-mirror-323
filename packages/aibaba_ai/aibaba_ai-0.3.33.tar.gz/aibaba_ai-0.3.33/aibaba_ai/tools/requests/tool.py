from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.tools import (
        BaseRequestsTool,
        RequestsDeleteTool,
        RequestsGetTool,
        RequestsPatchTool,
        RequestsPostTool,
        RequestsPutTool,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "BaseRequestsTool": "aibaba_ai_community.tools",
    "RequestsGetTool": "aibaba_ai_community.tools",
    "RequestsPostTool": "aibaba_ai_community.tools",
    "RequestsPatchTool": "aibaba_ai_community.tools",
    "RequestsPutTool": "aibaba_ai_community.tools",
    "RequestsDeleteTool": "aibaba_ai_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "BaseRequestsTool",
    "RequestsGetTool",
    "RequestsPostTool",
    "RequestsPatchTool",
    "RequestsPutTool",
    "RequestsDeleteTool",
]
