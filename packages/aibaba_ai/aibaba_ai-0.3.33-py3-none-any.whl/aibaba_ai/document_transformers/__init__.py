"""**Document Transformers** are classes to transform Documents.

**Document Transformers** usually used to transform a lot of Documents in a single run.

**Class hierarchy:**

.. code-block::

    BaseDocumentTransformer --> <name>  # Examples: DoctranQATransformer, DoctranTextTranslator

**Main helpers:**

.. code-block::

    Document
"""  # noqa: E501

from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.document_transformers import (
        BeautifulSoupTransformer,
        DoctranPropertyExtractor,
        DoctranQATransformer,
        DoctranTextTranslator,
        EmbeddingsClusteringFilter,
        EmbeddingsRedundantFilter,
        GoogleTranslateTransformer,
        Html2TextTransformer,
        LongContextReorder,
        NucliaTextTransformer,
        OpenAIMetadataTagger,
        get_stateful_documents,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "BeautifulSoupTransformer": "aibaba_ai_community.document_transformers",
    "DoctranQATransformer": "aibaba_ai_community.document_transformers",
    "DoctranTextTranslator": "aibaba_ai_community.document_transformers",
    "DoctranPropertyExtractor": "aibaba_ai_community.document_transformers",
    "EmbeddingsClusteringFilter": "aibaba_ai_community.document_transformers",
    "EmbeddingsRedundantFilter": "aibaba_ai_community.document_transformers",
    "GoogleTranslateTransformer": "aibaba_ai_community.document_transformers",
    "get_stateful_documents": "aibaba_ai_community.document_transformers",
    "LongContextReorder": "aibaba_ai_community.document_transformers",
    "NucliaTextTransformer": "aibaba_ai_community.document_transformers",
    "OpenAIMetadataTagger": "aibaba_ai_community.document_transformers",
    "Html2TextTransformer": "aibaba_ai_community.document_transformers",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "BeautifulSoupTransformer",
    "DoctranQATransformer",
    "DoctranTextTranslator",
    "DoctranPropertyExtractor",
    "EmbeddingsClusteringFilter",
    "EmbeddingsRedundantFilter",
    "GoogleTranslateTransformer",
    "get_stateful_documents",
    "LongContextReorder",
    "NucliaTextTransformer",
    "OpenAIMetadataTagger",
    "Html2TextTransformer",
]
