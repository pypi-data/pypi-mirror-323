from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.graphs import NetworkxEntityGraph
    from aibaba_ai_community.graphs.networkx_graph import (
        KnowledgeTriple,
        get_entities,
        parse_triples,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "KnowledgeTriple": "aibaba_ai_community.graphs.networkx_graph",
    "parse_triples": "aibaba_ai_community.graphs.networkx_graph",
    "get_entities": "aibaba_ai_community.graphs.networkx_graph",
    "NetworkxEntityGraph": "aibaba_ai_community.graphs",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "KnowledgeTriple",
    "parse_triples",
    "get_entities",
    "NetworkxEntityGraph",
]
