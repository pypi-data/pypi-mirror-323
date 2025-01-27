"""Browser tools and toolkit."""

from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.tools import (
        ClickTool,
        CurrentWebPageTool,
        ExtractHyperlinksTool,
        ExtractTextTool,
        GetElementsTool,
        NavigateBackTool,
        NavigateTool,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "NavigateTool": "aibaba_ai_community.tools",
    "NavigateBackTool": "aibaba_ai_community.tools",
    "ExtractTextTool": "aibaba_ai_community.tools",
    "ExtractHyperlinksTool": "aibaba_ai_community.tools",
    "GetElementsTool": "aibaba_ai_community.tools",
    "ClickTool": "aibaba_ai_community.tools",
    "CurrentWebPageTool": "aibaba_ai_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "NavigateTool",
    "NavigateBackTool",
    "ExtractTextTool",
    "ExtractHyperlinksTool",
    "GetElementsTool",
    "ClickTool",
    "CurrentWebPageTool",
]
