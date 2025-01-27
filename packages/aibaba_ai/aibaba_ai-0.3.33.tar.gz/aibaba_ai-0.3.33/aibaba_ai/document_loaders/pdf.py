from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.document_loaders import (
        AmazonTextractPDFLoader,
        MathpixPDFLoader,
        OnlinePDFLoader,
        PagedPDFSplitter,
        PDFMinerLoader,
        PDFMinerPDFasHTMLLoader,
        PDFPlumberLoader,
        PyMuPDFLoader,
        PyPDFDirectoryLoader,
        PyPDFium2Loader,
        UnstructuredPDFLoader,
    )
    from aibaba_ai_community.document_loaders.pdf import (
        BasePDFLoader,
        DocumentIntelligenceLoader,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "UnstructuredPDFLoader": "aibaba_ai_community.document_loaders",
    "BasePDFLoader": "aibaba_ai_community.document_loaders.pdf",
    "OnlinePDFLoader": "aibaba_ai_community.document_loaders",
    "PagedPDFSplitter": "aibaba_ai_community.document_loaders",
    "PyPDFium2Loader": "aibaba_ai_community.document_loaders",
    "PyPDFDirectoryLoader": "aibaba_ai_community.document_loaders",
    "PDFMinerLoader": "aibaba_ai_community.document_loaders",
    "PDFMinerPDFasHTMLLoader": "aibaba_ai_community.document_loaders",
    "PyMuPDFLoader": "aibaba_ai_community.document_loaders",
    "MathpixPDFLoader": "aibaba_ai_community.document_loaders",
    "PDFPlumberLoader": "aibaba_ai_community.document_loaders",
    "AmazonTextractPDFLoader": "aibaba_ai_community.document_loaders",
    "DocumentIntelligenceLoader": "aibaba_ai_community.document_loaders.pdf",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "UnstructuredPDFLoader",
    "BasePDFLoader",
    "OnlinePDFLoader",
    "PagedPDFSplitter",
    "PyPDFium2Loader",
    "PyPDFDirectoryLoader",
    "PDFMinerLoader",
    "PDFMinerPDFasHTMLLoader",
    "PyMuPDFLoader",
    "MathpixPDFLoader",
    "PDFPlumberLoader",
    "AmazonTextractPDFLoader",
    "DocumentIntelligenceLoader",
]
