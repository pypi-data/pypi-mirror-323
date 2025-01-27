from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.document_loaders.parsers.audio import OpenAIWhisperParser
    from aibaba_ai_community.document_loaders.parsers.docai import DocAIParser
    from aibaba_ai_community.document_loaders.parsers.grobid import GrobidParser
    from aibaba_ai_community.document_loaders.parsers.html.bs4 import BS4HTMLParser
    from aibaba_ai_community.document_loaders.parsers.language.language_parser import (
        LanguageParser,
    )
    from aibaba_ai_community.document_loaders.parsers.pdf import (
        PDFMinerParser,
        PDFPlumberParser,
        PyMuPDFParser,
        PyPDFium2Parser,
        PyPDFParser,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "BS4HTMLParser": "aibaba_ai_community.document_loaders.parsers.html.bs4",
    "DocAIParser": "aibaba_ai_community.document_loaders.parsers.docai",
    "GrobidParser": "aibaba_ai_community.document_loaders.parsers.grobid",
    "LanguageParser": (
        "aibaba_ai_community.document_loaders.parsers.language.language_parser"
    ),
    "OpenAIWhisperParser": "aibaba_ai_community.document_loaders.parsers.audio",
    "PDFMinerParser": "aibaba_ai_community.document_loaders.parsers.pdf",
    "PDFPlumberParser": "aibaba_ai_community.document_loaders.parsers.pdf",
    "PyMuPDFParser": "aibaba_ai_community.document_loaders.parsers.pdf",
    "PyPDFium2Parser": "aibaba_ai_community.document_loaders.parsers.pdf",
    "PyPDFParser": "aibaba_ai_community.document_loaders.parsers.pdf",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "BS4HTMLParser",
    "DocAIParser",
    "GrobidParser",
    "LanguageParser",
    "OpenAIWhisperParser",
    "PDFMinerParser",
    "PDFPlumberParser",
    "PyMuPDFParser",
    "PyPDFium2Parser",
    "PyPDFParser",
]
