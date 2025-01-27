from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.callbacks.streamlit.streamlit_callback_handler import (
        LLMThought,
        LLMThoughtLabeler,
        LLMThoughtState,
        StreamlitCallbackHandler,
        ToolRecord,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "LLMThoughtState": (
        "aibaba_ai_community.callbacks.streamlit.streamlit_callback_handler"
    ),
    "ToolRecord": (
        "aibaba_ai_community.callbacks.streamlit.streamlit_callback_handler"
    ),
    "LLMThoughtLabeler": (
        "aibaba_ai_community.callbacks.streamlit.streamlit_callback_handler"
    ),
    "LLMThought": (
        "aibaba_ai_community.callbacks.streamlit.streamlit_callback_handler"
    ),
    "StreamlitCallbackHandler": (
        "aibaba_ai_community.callbacks.streamlit.streamlit_callback_handler"
    ),
}

_import_attribute = create_importer(__file__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "LLMThoughtState",
    "ToolRecord",
    "LLMThoughtLabeler",
    "LLMThought",
    "StreamlitCallbackHandler",
]
