from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.adapters.openai import (
        Chat,
        ChatCompletion,
        ChatCompletionChunk,
        ChatCompletions,
        Choice,
        ChoiceChunk,
        Completions,
        IndexableBaseModel,
        chat,
        convert_dict_to_message,
        convert_message_to_dict,
        convert_messages_for_finetuning,
        convert_openai_messages,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
MODULE_LOOKUP = {
    "IndexableBaseModel": "aibaba_ai_community.adapters.openai",
    "Choice": "aibaba_ai_community.adapters.openai",
    "ChatCompletions": "aibaba_ai_community.adapters.openai",
    "ChoiceChunk": "aibaba_ai_community.adapters.openai",
    "ChatCompletionChunk": "aibaba_ai_community.adapters.openai",
    "convert_dict_to_message": "aibaba_ai_community.adapters.openai",
    "convert_message_to_dict": "aibaba_ai_community.adapters.openai",
    "convert_openai_messages": "aibaba_ai_community.adapters.openai",
    "ChatCompletion": "aibaba_ai_community.adapters.openai",
    "convert_messages_for_finetuning": "aibaba_ai_community.adapters.openai",
    "Completions": "aibaba_ai_community.adapters.openai",
    "Chat": "aibaba_ai_community.adapters.openai",
    "chat": "aibaba_ai_community.adapters.openai",
}

_import_attribute = create_importer(__file__, deprecated_lookups=MODULE_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "IndexableBaseModel",
    "Choice",
    "ChatCompletions",
    "ChoiceChunk",
    "ChatCompletionChunk",
    "convert_dict_to_message",
    "convert_message_to_dict",
    "convert_openai_messages",
    "ChatCompletion",
    "convert_messages_for_finetuning",
    "Completions",
    "Chat",
    "chat",
]
