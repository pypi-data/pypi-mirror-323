from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.utilities import ArceeWrapper
    from aibaba_ai_community.utilities.arcee import (
        ArceeDocument,
        ArceeDocumentAdapter,
        ArceeDocumentSource,
        ArceeRoute,
        DALMFilter,
        DALMFilterType,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "ArceeRoute": "aibaba_ai_community.utilities.arcee",
    "DALMFilterType": "aibaba_ai_community.utilities.arcee",
    "DALMFilter": "aibaba_ai_community.utilities.arcee",
    "ArceeDocumentSource": "aibaba_ai_community.utilities.arcee",
    "ArceeDocument": "aibaba_ai_community.utilities.arcee",
    "ArceeDocumentAdapter": "aibaba_ai_community.utilities.arcee",
    "ArceeWrapper": "aibaba_ai_community.utilities",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "ArceeRoute",
    "DALMFilterType",
    "DALMFilter",
    "ArceeDocumentSource",
    "ArceeDocument",
    "ArceeDocumentAdapter",
    "ArceeWrapper",
]
