from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.document_transformers import OpenAIMetadataTagger
    from aibaba_ai_community.document_transformers.openai_functions import (
        create_metadata_tagger,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "OpenAIMetadataTagger": "aibaba_ai_community.document_transformers",
    "create_metadata_tagger": (
        "aibaba_ai_community.document_transformers.openai_functions"
    ),
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "OpenAIMetadataTagger",
    "create_metadata_tagger",
]
