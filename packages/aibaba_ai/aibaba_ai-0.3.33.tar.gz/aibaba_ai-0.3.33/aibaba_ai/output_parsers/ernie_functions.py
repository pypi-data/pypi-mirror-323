from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.output_parsers.ernie_functions import (
        JsonKeyOutputFunctionsParser,
        JsonOutputFunctionsParser,
        OutputFunctionsParser,
        PydanticAttrOutputFunctionsParser,
        PydanticOutputFunctionsParser,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "JsonKeyOutputFunctionsParser": (
        "aibaba_ai_community.output_parsers.ernie_functions"
    ),
    "JsonOutputFunctionsParser": "aibaba_ai_community.output_parsers.ernie_functions",
    "OutputFunctionsParser": "aibaba_ai_community.output_parsers.ernie_functions",
    "PydanticAttrOutputFunctionsParser": (
        "aibaba_ai_community.output_parsers.ernie_functions"
    ),
    "PydanticOutputFunctionsParser": (
        "aibaba_ai_community.output_parsers.ernie_functions"
    ),
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "JsonKeyOutputFunctionsParser",
    "JsonOutputFunctionsParser",
    "OutputFunctionsParser",
    "PydanticAttrOutputFunctionsParser",
    "PydanticOutputFunctionsParser",
]
