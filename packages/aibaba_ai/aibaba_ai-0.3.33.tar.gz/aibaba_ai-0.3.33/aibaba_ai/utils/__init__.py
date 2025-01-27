"""
**Utility functions** for Aibaba AI.

These functions do not depend on any other Aibaba AI module.
"""

from typing import TYPE_CHECKING, Any

from aibaba_ai_core.utils import (
    comma_list,
    get_from_dict_or_env,
    get_from_env,
    stringify_dict,
    stringify_value,
)
from aibaba_ai_core.utils.formatting import StrictFormatter, formatter
from aibaba_ai_core.utils.input import (
    get_bolded_text,
    get_color_mapping,
    get_colored_text,
    print_text,
)
from aibaba_ai_core.utils.utils import (
    check_package_version,
    convert_to_secret_str,
    get_pydantic_field_names,
    guard_import,
    mock_now,
    raise_for_status_with_text,
    xor_args,
)

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.utils.math import (
        cosine_similarity,
        cosine_similarity_top_k,
    )

# Not deprecated right now because we will likely need to move these functions
# back into langchain (as long as we're OK with the dependency on numpy).
_MODULE_LOOKUP = {
    "cosine_similarity": "aibaba_ai_community.utils.math",
    "cosine_similarity_top_k": "aibaba_ai_community.utils.math",
}

_import_attribute = create_importer(__package__, module_lookup=_MODULE_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "StrictFormatter",
    "check_package_version",
    "comma_list",
    "convert_to_secret_str",
    "cosine_similarity",
    "cosine_similarity_top_k",
    "get_bolded_text",
    "get_color_mapping",
    "get_colored_text",
    "get_from_dict_or_env",
    "get_from_env",
    "formatter",
    "get_pydantic_field_names",
    "guard_import",
    "mock_now",
    "print_text",
    "raise_for_status_with_text",
    "stringify_dict",
    "stringify_value",
    "xor_args",
]
