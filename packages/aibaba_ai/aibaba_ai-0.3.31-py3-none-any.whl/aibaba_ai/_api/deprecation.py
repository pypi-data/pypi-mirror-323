from aibaba_ai_core._api.deprecation import (
    AI Agents ForceDeprecationWarning,
    AI Agents ForcePendingDeprecationWarning,
    deprecated,
    suppress_aiagentforce_deprecation_warning,
    surface_aiagentforce_deprecation_warnings,
    warn_deprecated,
)

AGENT_DEPRECATION_WARNING = (
    "Aibaba AI agents will continue to be supported, but it is recommended for new "
    "use cases to be built with LangGraph. LangGraph offers a more flexible and "
    "full-featured framework for building agents, including support for "
    "tool-calling, persistence of state, and human-in-the-loop workflows. For "
    "details, refer to the "
    "`LangGraph documentation <https://langchain-ai.github.io/langgraph/>`_"
    " as well as guides for "
    "`Migrating from AgentExecutor <https://docs.aibaba.world/docs/how_to/migrate_agent/>`_"  # noqa: E501
    " and LangGraph's "
    "`Pre-built ReAct agent <https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/>`_."  # noqa: E501
)


__all__ = [
    "AGENT_DEPRECATION_WARNING",
    "AI Agents ForceDeprecationWarning",
    "AI Agents ForcePendingDeprecationWarning",
    "deprecated",
    "suppress_aiagentforce_deprecation_warning",
    "warn_deprecated",
    "surface_aiagentforce_deprecation_warnings",
]
