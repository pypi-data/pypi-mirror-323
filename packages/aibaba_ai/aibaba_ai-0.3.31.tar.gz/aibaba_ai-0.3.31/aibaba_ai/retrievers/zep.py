from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.retrievers import ZepRetriever
    from aibaba_ai_community.retrievers.zep import SearchScope, SearchType

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "SearchScope": "aibaba_ai_community.retrievers.zep",
    "SearchType": "aibaba_ai_community.retrievers.zep",
    "ZepRetriever": "aibaba_ai_community.retrievers",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "SearchScope",
    "SearchType",
    "ZepRetriever",
]
