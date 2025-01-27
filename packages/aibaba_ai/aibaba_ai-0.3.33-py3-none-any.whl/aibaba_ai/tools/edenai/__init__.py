"""Edenai Tools."""

from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.tools import (
        EdenAiExplicitImageTool,
        EdenAiObjectDetectionTool,
        EdenAiParsingIDTool,
        EdenAiParsingInvoiceTool,
        EdenAiSpeechToTextTool,
        EdenAiTextModerationTool,
        EdenAiTextToSpeechTool,
        EdenaiTool,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "EdenAiExplicitImageTool": "aibaba_ai_community.tools",
    "EdenAiObjectDetectionTool": "aibaba_ai_community.tools",
    "EdenAiParsingIDTool": "aibaba_ai_community.tools",
    "EdenAiParsingInvoiceTool": "aibaba_ai_community.tools",
    "EdenAiTextToSpeechTool": "aibaba_ai_community.tools",
    "EdenAiSpeechToTextTool": "aibaba_ai_community.tools",
    "EdenAiTextModerationTool": "aibaba_ai_community.tools",
    "EdenaiTool": "aibaba_ai_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "EdenAiExplicitImageTool",
    "EdenAiObjectDetectionTool",
    "EdenAiParsingIDTool",
    "EdenAiParsingInvoiceTool",
    "EdenAiTextToSpeechTool",
    "EdenAiSpeechToTextTool",
    "EdenAiTextModerationTool",
    "EdenaiTool",
]
