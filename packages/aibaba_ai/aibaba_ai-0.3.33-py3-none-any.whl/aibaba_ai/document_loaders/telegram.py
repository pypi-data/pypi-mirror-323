from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.document_loaders import (
        TelegramChatApiLoader,
        TelegramChatFileLoader,
    )
    from aibaba_ai_community.document_loaders.telegram import (
        concatenate_rows,
        text_to_docs,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "concatenate_rows": "aibaba_ai_community.document_loaders.telegram",
    "TelegramChatFileLoader": "aibaba_ai_community.document_loaders",
    "text_to_docs": "aibaba_ai_community.document_loaders.telegram",
    "TelegramChatApiLoader": "aibaba_ai_community.document_loaders",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "concatenate_rows",
    "TelegramChatFileLoader",
    "text_to_docs",
    "TelegramChatApiLoader",
]
