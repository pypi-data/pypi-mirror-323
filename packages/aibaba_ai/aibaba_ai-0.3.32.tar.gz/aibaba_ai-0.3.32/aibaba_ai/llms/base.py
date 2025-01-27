# Backwards compatibility.
from aibaba_ai_core.language_models import BaseLanguageModel
from aibaba_ai_core.language_models.llms import (
    LLM,
    BaseLLM,
)

__all__ = [
    "BaseLanguageModel",
    "BaseLLM",
    "LLM",
]
