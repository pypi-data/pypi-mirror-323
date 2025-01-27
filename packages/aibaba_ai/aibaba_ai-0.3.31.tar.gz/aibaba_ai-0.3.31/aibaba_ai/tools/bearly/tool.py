from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.tools import BearlyInterpreterTool
    from aibaba_ai_community.tools.bearly.tool import (
        BearlyInterpreterToolArguments,
        FileInfo,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "BearlyInterpreterToolArguments": "aibaba_ai_community.tools.bearly.tool",
    "FileInfo": "aibaba_ai_community.tools.bearly.tool",
    "BearlyInterpreterTool": "aibaba_ai_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "BearlyInterpreterToolArguments",
    "FileInfo",
    "BearlyInterpreterTool",
]
