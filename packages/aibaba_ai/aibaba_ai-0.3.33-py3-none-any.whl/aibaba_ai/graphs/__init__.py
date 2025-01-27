"""**Graphs** provide a natural language interface to graph databases."""

from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.graphs import (
        ArangoGraph,
        FalkorDBGraph,
        HugeGraph,
        KuzuGraph,
        MemgraphGraph,
        NebulaGraph,
        Neo4jGraph,
        NeptuneGraph,
        NetworkxEntityGraph,
        RdfGraph,
    )


# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "MemgraphGraph": "aibaba_ai_community.graphs",
    "NetworkxEntityGraph": "aibaba_ai_community.graphs",
    "Neo4jGraph": "aibaba_ai_community.graphs",
    "NebulaGraph": "aibaba_ai_community.graphs",
    "NeptuneGraph": "aibaba_ai_community.graphs",
    "KuzuGraph": "aibaba_ai_community.graphs",
    "HugeGraph": "aibaba_ai_community.graphs",
    "RdfGraph": "aibaba_ai_community.graphs",
    "ArangoGraph": "aibaba_ai_community.graphs",
    "FalkorDBGraph": "aibaba_ai_community.graphs",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "MemgraphGraph",
    "NetworkxEntityGraph",
    "Neo4jGraph",
    "NebulaGraph",
    "NeptuneGraph",
    "KuzuGraph",
    "HugeGraph",
    "RdfGraph",
    "ArangoGraph",
    "FalkorDBGraph",
]
