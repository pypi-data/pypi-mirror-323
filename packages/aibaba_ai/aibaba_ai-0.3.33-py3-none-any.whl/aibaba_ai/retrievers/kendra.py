from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.retrievers import AmazonKendraRetriever
    from aibaba_ai_community.retrievers.kendra import (
        AdditionalResultAttribute,
        AdditionalResultAttributeValue,
        DocumentAttribute,
        DocumentAttributeValue,
        Highlight,
        QueryResult,
        QueryResultItem,
        ResultItem,
        RetrieveResult,
        RetrieveResultItem,
        TextWithHighLights,
        clean_excerpt,
        combined_text,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "clean_excerpt": "aibaba_ai_community.retrievers.kendra",
    "combined_text": "aibaba_ai_community.retrievers.kendra",
    "Highlight": "aibaba_ai_community.retrievers.kendra",
    "TextWithHighLights": "aibaba_ai_community.retrievers.kendra",
    "AdditionalResultAttributeValue": "aibaba_ai_community.retrievers.kendra",
    "AdditionalResultAttribute": "aibaba_ai_community.retrievers.kendra",
    "DocumentAttributeValue": "aibaba_ai_community.retrievers.kendra",
    "DocumentAttribute": "aibaba_ai_community.retrievers.kendra",
    "ResultItem": "aibaba_ai_community.retrievers.kendra",
    "QueryResultItem": "aibaba_ai_community.retrievers.kendra",
    "RetrieveResultItem": "aibaba_ai_community.retrievers.kendra",
    "QueryResult": "aibaba_ai_community.retrievers.kendra",
    "RetrieveResult": "aibaba_ai_community.retrievers.kendra",
    "AmazonKendraRetriever": "aibaba_ai_community.retrievers",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "clean_excerpt",
    "combined_text",
    "Highlight",
    "TextWithHighLights",
    "AdditionalResultAttributeValue",
    "AdditionalResultAttribute",
    "DocumentAttributeValue",
    "DocumentAttribute",
    "ResultItem",
    "QueryResultItem",
    "RetrieveResultItem",
    "QueryResult",
    "RetrieveResult",
    "AmazonKendraRetriever",
]
