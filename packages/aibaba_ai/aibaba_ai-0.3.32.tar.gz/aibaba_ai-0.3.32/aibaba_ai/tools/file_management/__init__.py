"""File Management Tools."""

from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.tools import (
        CopyFileTool,
        DeleteFileTool,
        FileSearchTool,
        ListDirectoryTool,
        MoveFileTool,
        ReadFileTool,
        WriteFileTool,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "CopyFileTool": "aibaba_ai_community.tools",
    "DeleteFileTool": "aibaba_ai_community.tools",
    "FileSearchTool": "aibaba_ai_community.tools",
    "MoveFileTool": "aibaba_ai_community.tools",
    "ReadFileTool": "aibaba_ai_community.tools",
    "WriteFileTool": "aibaba_ai_community.tools",
    "ListDirectoryTool": "aibaba_ai_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "CopyFileTool",
    "DeleteFileTool",
    "FileSearchTool",
    "MoveFileTool",
    "ReadFileTool",
    "WriteFileTool",
    "ListDirectoryTool",
]
