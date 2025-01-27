from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.tools import (
        BaseSQLDatabaseTool,
        InfoSQLDatabaseTool,
        ListSQLDatabaseTool,
        QuerySQLCheckerTool,
        QuerySQLDataBaseTool,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "BaseSQLDatabaseTool": "aibaba_ai_community.tools",
    "QuerySQLDataBaseTool": "aibaba_ai_community.tools",
    "InfoSQLDatabaseTool": "aibaba_ai_community.tools",
    "ListSQLDatabaseTool": "aibaba_ai_community.tools",
    "QuerySQLCheckerTool": "aibaba_ai_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "BaseSQLDatabaseTool",
    "QuerySQLDataBaseTool",
    "InfoSQLDatabaseTool",
    "ListSQLDatabaseTool",
    "QuerySQLCheckerTool",
]
