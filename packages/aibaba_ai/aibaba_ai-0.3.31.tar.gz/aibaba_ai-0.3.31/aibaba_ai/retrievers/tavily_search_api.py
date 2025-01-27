from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.retrievers import TavilySearchAPIRetriever
    from aibaba_ai_community.retrievers.tavily_search_api import SearchDepth

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "SearchDepth": "aibaba_ai_community.retrievers.tavily_search_api",
    "TavilySearchAPIRetriever": "aibaba_ai_community.retrievers",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "SearchDepth",
    "TavilySearchAPIRetriever",
]
