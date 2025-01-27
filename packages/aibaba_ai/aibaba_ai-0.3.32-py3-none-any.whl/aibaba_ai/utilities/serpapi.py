from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.utilities import SerpAPIWrapper
    from aibaba_ai_community.utilities.serpapi import HiddenPrints

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "HiddenPrints": "aibaba_ai_community.utilities.serpapi",
    "SerpAPIWrapper": "aibaba_ai_community.utilities",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "HiddenPrints",
    "SerpAPIWrapper",
]
