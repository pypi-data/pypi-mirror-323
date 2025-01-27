from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.chains.graph_qa.neptune_sparql import (
        INTERMEDIATE_STEPS_KEY,
        SPARQL_GENERATION_TEMPLATE,
        NeptuneSparqlQAChain,
        extract_sparql,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "INTERMEDIATE_STEPS_KEY": "aibaba_ai_community.chains.graph_qa.neptune_sparql",
    "NeptuneSparqlQAChain": "aibaba_ai_community.chains.graph_qa.neptune_sparql",
    "SPARQL_GENERATION_TEMPLATE": "aibaba_ai_community.chains.graph_qa.neptune_sparql",
    "extract_sparql": "aibaba_ai_community.chains.graph_qa.neptune_sparql",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "INTERMEDIATE_STEPS_KEY",
    "NeptuneSparqlQAChain",
    "SPARQL_GENERATION_TEMPLATE",
    "extract_sparql",
]
