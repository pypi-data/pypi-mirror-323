from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.tools import AINValueOps
    from aibaba_ai_community.tools.ainetwork.value import ValueSchema

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "ValueSchema": "aibaba_ai_community.tools.ainetwork.value",
    "AINValueOps": "aibaba_ai_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "ValueSchema",
    "AINValueOps",
]
