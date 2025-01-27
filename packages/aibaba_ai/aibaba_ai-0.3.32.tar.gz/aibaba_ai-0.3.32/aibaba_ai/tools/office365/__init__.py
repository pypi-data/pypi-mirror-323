"""O365 tools."""

from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.tools import (
        O365CreateDraftMessage,
        O365SearchEmails,
        O365SearchEvents,
        O365SendEvent,
        O365SendMessage,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "O365SearchEmails": "aibaba_ai_community.tools",
    "O365SearchEvents": "aibaba_ai_community.tools",
    "O365CreateDraftMessage": "aibaba_ai_community.tools",
    "O365SendMessage": "aibaba_ai_community.tools",
    "O365SendEvent": "aibaba_ai_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "O365SearchEmails",
    "O365SearchEvents",
    "O365CreateDraftMessage",
    "O365SendMessage",
    "O365SendEvent",
]
