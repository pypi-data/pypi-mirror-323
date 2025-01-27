from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.utilities.clickup import (
        ClickupAPIWrapper,
        Component,
        CUList,
        Member,
        Space,
        Task,
        Team,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "Component": "aibaba_ai_community.utilities.clickup",
    "Task": "aibaba_ai_community.utilities.clickup",
    "CUList": "aibaba_ai_community.utilities.clickup",
    "Member": "aibaba_ai_community.utilities.clickup",
    "Team": "aibaba_ai_community.utilities.clickup",
    "Space": "aibaba_ai_community.utilities.clickup",
    "ClickupAPIWrapper": "aibaba_ai_community.utilities.clickup",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "Component",
    "Task",
    "CUList",
    "Member",
    "Team",
    "Space",
    "ClickupAPIWrapper",
]
