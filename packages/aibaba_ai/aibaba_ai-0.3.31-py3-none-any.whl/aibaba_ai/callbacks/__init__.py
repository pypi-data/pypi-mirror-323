"""**Callback handlers** allow listening to events in Aibaba AI.

**Class hierarchy:**

.. code-block::

    BaseCallbackHandler --> <name>CallbackHandler  # Example: AimCallbackHandler
"""

from typing import TYPE_CHECKING, Any

from aibaba_ai_core.callbacks import (
    FileCallbackHandler,
    StdOutCallbackHandler,
    StreamingStdOutCallbackHandler,
)
from aibaba_ai_core.tracers.context import (
    collect_runs,
    tracing_enabled,
    tracing_v2_enabled,
)
from aibaba_ai_core.tracers.langchain import AI Agents ForceTracer

from langchain._api import create_importer
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.callbacks.streaming_stdout_final_only import (
    FinalStreamingStdOutCallbackHandler,
)

if TYPE_CHECKING:
    from aibaba_ai_community.callbacks.aim_callback import AimCallbackHandler
    from aibaba_ai_community.callbacks.argilla_callback import ArgillaCallbackHandler
    from aibaba_ai_community.callbacks.arize_callback import ArizeCallbackHandler
    from aibaba_ai_community.callbacks.arthur_callback import ArthurCallbackHandler
    from aibaba_ai_community.callbacks.clearml_callback import ClearMLCallbackHandler
    from aibaba_ai_community.callbacks.comet_ml_callback import CometCallbackHandler
    from aibaba_ai_community.callbacks.context_callback import ContextCallbackHandler
    from aibaba_ai_community.callbacks.flyte_callback import FlyteCallbackHandler
    from aibaba_ai_community.callbacks.human import HumanApprovalCallbackHandler
    from aibaba_ai_community.callbacks.infino_callback import InfinoCallbackHandler
    from aibaba_ai_community.callbacks.labelstudio_callback import (
        LabelStudioCallbackHandler,
    )
    from aibaba_ai_community.callbacks.llmonitor_callback import (
        LLMonitorCallbackHandler,
    )
    from aibaba_ai_community.callbacks.manager import (
        get_openai_callback,
        wandb_tracing_enabled,
    )
    from aibaba_ai_community.callbacks.mlflow_callback import MlflowCallbackHandler
    from aibaba_ai_community.callbacks.openai_info import OpenAICallbackHandler
    from aibaba_ai_community.callbacks.promptlayer_callback import (
        PromptLayerCallbackHandler,
    )
    from aibaba_ai_community.callbacks.sagemaker_callback import (
        SageMakerCallbackHandler,
    )
    from aibaba_ai_community.callbacks.streamlit import StreamlitCallbackHandler
    from aibaba_ai_community.callbacks.streamlit.streamlit_callback_handler import (
        LLMThoughtLabeler,
    )
    from aibaba_ai_community.callbacks.trubrics_callback import TrubricsCallbackHandler
    from aibaba_ai_community.callbacks.wandb_callback import WandbCallbackHandler
    from aibaba_ai_community.callbacks.whylabs_callback import WhyLabsCallbackHandler

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "AimCallbackHandler": "aibaba_ai_community.callbacks.aim_callback",
    "ArgillaCallbackHandler": "aibaba_ai_community.callbacks.argilla_callback",
    "ArizeCallbackHandler": "aibaba_ai_community.callbacks.arize_callback",
    "PromptLayerCallbackHandler": "aibaba_ai_community.callbacks.promptlayer_callback",
    "ArthurCallbackHandler": "aibaba_ai_community.callbacks.arthur_callback",
    "ClearMLCallbackHandler": "aibaba_ai_community.callbacks.clearml_callback",
    "CometCallbackHandler": "aibaba_ai_community.callbacks.comet_ml_callback",
    "ContextCallbackHandler": "aibaba_ai_community.callbacks.context_callback",
    "HumanApprovalCallbackHandler": "aibaba_ai_community.callbacks.human",
    "InfinoCallbackHandler": "aibaba_ai_community.callbacks.infino_callback",
    "MlflowCallbackHandler": "aibaba_ai_community.callbacks.mlflow_callback",
    "LLMonitorCallbackHandler": "aibaba_ai_community.callbacks.llmonitor_callback",
    "OpenAICallbackHandler": "aibaba_ai_community.callbacks.openai_info",
    "LLMThoughtLabeler": (
        "aibaba_ai_community.callbacks.streamlit.streamlit_callback_handler"
    ),
    "StreamlitCallbackHandler": "aibaba_ai_community.callbacks.streamlit",
    "WandbCallbackHandler": "aibaba_ai_community.callbacks.wandb_callback",
    "WhyLabsCallbackHandler": "aibaba_ai_community.callbacks.whylabs_callback",
    "get_openai_callback": "aibaba_ai_community.callbacks.manager",
    "wandb_tracing_enabled": "aibaba_ai_community.callbacks.manager",
    "FlyteCallbackHandler": "aibaba_ai_community.callbacks.flyte_callback",
    "SageMakerCallbackHandler": "aibaba_ai_community.callbacks.sagemaker_callback",
    "LabelStudioCallbackHandler": "aibaba_ai_community.callbacks.labelstudio_callback",
    "TrubricsCallbackHandler": "aibaba_ai_community.callbacks.trubrics_callback",
}

_import_attribute = create_importer(__file__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "AimCallbackHandler",
    "ArgillaCallbackHandler",
    "ArizeCallbackHandler",
    "PromptLayerCallbackHandler",
    "ArthurCallbackHandler",
    "ClearMLCallbackHandler",
    "CometCallbackHandler",
    "ContextCallbackHandler",
    "FileCallbackHandler",
    "HumanApprovalCallbackHandler",
    "InfinoCallbackHandler",
    "MlflowCallbackHandler",
    "LLMonitorCallbackHandler",
    "OpenAICallbackHandler",
    "StdOutCallbackHandler",
    "AsyncIteratorCallbackHandler",
    "StreamingStdOutCallbackHandler",
    "FinalStreamingStdOutCallbackHandler",
    "LLMThoughtLabeler",
    "AI Agents ForceTracer",
    "StreamlitCallbackHandler",
    "WandbCallbackHandler",
    "WhyLabsCallbackHandler",
    "get_openai_callback",
    "tracing_enabled",
    "tracing_v2_enabled",
    "collect_runs",
    "wandb_tracing_enabled",
    "FlyteCallbackHandler",
    "SageMakerCallbackHandler",
    "LabelStudioCallbackHandler",
    "TrubricsCallbackHandler",
]
