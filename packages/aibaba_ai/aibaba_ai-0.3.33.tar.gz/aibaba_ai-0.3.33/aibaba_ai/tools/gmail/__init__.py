"""Gmail tools."""

from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.tools import (
        GmailCreateDraft,
        GmailGetMessage,
        GmailGetThread,
        GmailSearch,
        GmailSendMessage,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "GmailCreateDraft": "aibaba_ai_community.tools",
    "GmailSendMessage": "aibaba_ai_community.tools",
    "GmailSearch": "aibaba_ai_community.tools",
    "GmailGetMessage": "aibaba_ai_community.tools",
    "GmailGetThread": "aibaba_ai_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "GmailCreateDraft",
    "GmailSendMessage",
    "GmailSearch",
    "GmailGetMessage",
    "GmailGetThread",
]
