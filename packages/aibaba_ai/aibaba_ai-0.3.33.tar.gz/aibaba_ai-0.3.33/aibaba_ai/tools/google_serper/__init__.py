from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.tools import GoogleSerperResults, GoogleSerperRun

"""Google Serper API Toolkit."""
"""Tool for the Serer.dev Google Search API."""

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "GoogleSerperRun": "aibaba_ai_community.tools",
    "GoogleSerperResults": "aibaba_ai_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "GoogleSerperRun",
    "GoogleSerperResults",
]
