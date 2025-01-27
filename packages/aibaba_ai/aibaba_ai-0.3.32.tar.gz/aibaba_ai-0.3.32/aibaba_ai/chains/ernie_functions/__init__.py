from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.chains.ernie_functions.base import (
        convert_to_ernie_function,
        create_ernie_fn_chain,
        create_ernie_fn_runnable,
        create_structured_output_chain,
        create_structured_output_runnable,
        get_ernie_output_parser,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "convert_to_ernie_function": "aibaba_ai_community.chains.ernie_functions.base",
    "create_ernie_fn_chain": "aibaba_ai_community.chains.ernie_functions.base",
    "create_ernie_fn_runnable": "aibaba_ai_community.chains.ernie_functions.base",
    "create_structured_output_chain": "aibaba_ai_community.chains.ernie_functions.base",
    "create_structured_output_runnable": (
        "aibaba_ai_community.chains.ernie_functions.base"
    ),
    "get_ernie_output_parser": "aibaba_ai_community.chains.ernie_functions.base",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "convert_to_ernie_function",
    "create_structured_output_chain",
    "create_ernie_fn_chain",
    "create_structured_output_runnable",
    "create_ernie_fn_runnable",
    "get_ernie_output_parser",
]
