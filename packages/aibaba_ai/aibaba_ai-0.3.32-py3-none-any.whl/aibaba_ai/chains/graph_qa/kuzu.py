from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.chains.graph_qa.kuzu import (
        KuzuQAChain,
        extract_cypher,
        remove_prefix,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "KuzuQAChain": "aibaba_ai_community.chains.graph_qa.kuzu",
    "extract_cypher": "aibaba_ai_community.chains.graph_qa.kuzu",
    "remove_prefix": "aibaba_ai_community.chains.graph_qa.kuzu",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = ["KuzuQAChain", "extract_cypher", "remove_prefix"]
