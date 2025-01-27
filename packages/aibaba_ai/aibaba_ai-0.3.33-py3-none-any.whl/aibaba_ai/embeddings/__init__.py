"""**Embedding models**  are wrappers around embedding models
from different APIs and services.

**Embedding models** can be LLMs or not.

**Class hierarchy:**

.. code-block::

    Embeddings --> <name>Embeddings  # Examples: OpenAIEmbeddings, HuggingFaceEmbeddings
"""

import logging
from typing import TYPE_CHECKING, Any

from langchain._api import create_importer
from langchain.embeddings.base import init_embeddings
from langchain.embeddings.cache import CacheBackedEmbeddings

if TYPE_CHECKING:
    from aibaba_ai_community.embeddings import (
        AlephAlphaAsymmetricSemanticEmbedding,
        AlephAlphaSymmetricSemanticEmbedding,
        AwaEmbeddings,
        AzureOpenAIEmbeddings,
        BedrockEmbeddings,
        BookendEmbeddings,
        ClarifaiEmbeddings,
        CohereEmbeddings,
        DashScopeEmbeddings,
        DatabricksEmbeddings,
        DeepInfraEmbeddings,
        DeterministicFakeEmbedding,
        EdenAiEmbeddings,
        ElasticsearchEmbeddings,
        EmbaasEmbeddings,
        ErnieEmbeddings,
        FakeEmbeddings,
        FastEmbedEmbeddings,
        GooglePalmEmbeddings,
        GPT4AllEmbeddings,
        GradientEmbeddings,
        HuggingFaceBgeEmbeddings,
        HuggingFaceEmbeddings,
        HuggingFaceHubEmbeddings,
        HuggingFaceInferenceAPIEmbeddings,
        HuggingFaceInstructEmbeddings,
        InfinityEmbeddings,
        JavelinAIGatewayEmbeddings,
        JinaEmbeddings,
        JohnSnowLabsEmbeddings,
        LlamaCppEmbeddings,
        LocalAIEmbeddings,
        MiniMaxEmbeddings,
        MlflowAIGatewayEmbeddings,
        MlflowEmbeddings,
        ModelScopeEmbeddings,
        MosaicMLInstructorEmbeddings,
        NLPCloudEmbeddings,
        OctoAIEmbeddings,
        OllamaEmbeddings,
        OpenAIEmbeddings,
        OpenVINOEmbeddings,
        QianfanEmbeddingsEndpoint,
        SagemakerEndpointEmbeddings,
        SelfHostedEmbeddings,
        SelfHostedHuggingFaceEmbeddings,
        SelfHostedHuggingFaceInstructEmbeddings,
        SentenceTransformerEmbeddings,
        SpacyEmbeddings,
        TensorflowHubEmbeddings,
        VertexAIEmbeddings,
        VoyageEmbeddings,
        XinferenceEmbeddings,
    )


logger = logging.getLogger(__name__)


# TODO: this is in here to maintain backwards compatibility
class HypotheticalDocumentEmbedder:
    def __init__(self, *args: Any, **kwargs: Any):
        logger.warning(
            "Using a deprecated class. Please use "
            "`from langchain.chains import HypotheticalDocumentEmbedder` instead"
        )
        from langchain.chains.hyde.base import HypotheticalDocumentEmbedder as H

        return H(*args, **kwargs)  # type: ignore

    @classmethod
    def from_llm(cls, *args: Any, **kwargs: Any) -> Any:
        logger.warning(
            "Using a deprecated class. Please use "
            "`from langchain.chains import HypotheticalDocumentEmbedder` instead"
        )
        from langchain.chains.hyde.base import HypotheticalDocumentEmbedder as H

        return H.from_llm(*args, **kwargs)


# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "AlephAlphaAsymmetricSemanticEmbedding": "aibaba_ai_community.embeddings",
    "AlephAlphaSymmetricSemanticEmbedding": "aibaba_ai_community.embeddings",
    "AwaEmbeddings": "aibaba_ai_community.embeddings",
    "AzureOpenAIEmbeddings": "aibaba_ai_community.embeddings",
    "BedrockEmbeddings": "aibaba_ai_community.embeddings",
    "BookendEmbeddings": "aibaba_ai_community.embeddings",
    "ClarifaiEmbeddings": "aibaba_ai_community.embeddings",
    "CohereEmbeddings": "aibaba_ai_community.embeddings",
    "DashScopeEmbeddings": "aibaba_ai_community.embeddings",
    "DatabricksEmbeddings": "aibaba_ai_community.embeddings",
    "DeepInfraEmbeddings": "aibaba_ai_community.embeddings",
    "DeterministicFakeEmbedding": "aibaba_ai_community.embeddings",
    "EdenAiEmbeddings": "aibaba_ai_community.embeddings",
    "ElasticsearchEmbeddings": "aibaba_ai_community.embeddings",
    "EmbaasEmbeddings": "aibaba_ai_community.embeddings",
    "ErnieEmbeddings": "aibaba_ai_community.embeddings",
    "FakeEmbeddings": "aibaba_ai_community.embeddings",
    "FastEmbedEmbeddings": "aibaba_ai_community.embeddings",
    "GooglePalmEmbeddings": "aibaba_ai_community.embeddings",
    "GPT4AllEmbeddings": "aibaba_ai_community.embeddings",
    "GradientEmbeddings": "aibaba_ai_community.embeddings",
    "HuggingFaceBgeEmbeddings": "aibaba_ai_community.embeddings",
    "HuggingFaceEmbeddings": "aibaba_ai_community.embeddings",
    "HuggingFaceHubEmbeddings": "aibaba_ai_community.embeddings",
    "HuggingFaceInferenceAPIEmbeddings": "aibaba_ai_community.embeddings",
    "HuggingFaceInstructEmbeddings": "aibaba_ai_community.embeddings",
    "InfinityEmbeddings": "aibaba_ai_community.embeddings",
    "JavelinAIGatewayEmbeddings": "aibaba_ai_community.embeddings",
    "JinaEmbeddings": "aibaba_ai_community.embeddings",
    "JohnSnowLabsEmbeddings": "aibaba_ai_community.embeddings",
    "LlamaCppEmbeddings": "aibaba_ai_community.embeddings",
    "LocalAIEmbeddings": "aibaba_ai_community.embeddings",
    "MiniMaxEmbeddings": "aibaba_ai_community.embeddings",
    "MlflowAIGatewayEmbeddings": "aibaba_ai_community.embeddings",
    "MlflowEmbeddings": "aibaba_ai_community.embeddings",
    "ModelScopeEmbeddings": "aibaba_ai_community.embeddings",
    "MosaicMLInstructorEmbeddings": "aibaba_ai_community.embeddings",
    "NLPCloudEmbeddings": "aibaba_ai_community.embeddings",
    "OctoAIEmbeddings": "aibaba_ai_community.embeddings",
    "OllamaEmbeddings": "aibaba_ai_community.embeddings",
    "OpenAIEmbeddings": "aibaba_ai_community.embeddings",
    "OpenVINOEmbeddings": "aibaba_ai_community.embeddings",
    "QianfanEmbeddingsEndpoint": "aibaba_ai_community.embeddings",
    "SagemakerEndpointEmbeddings": "aibaba_ai_community.embeddings",
    "SelfHostedEmbeddings": "aibaba_ai_community.embeddings",
    "SelfHostedHuggingFaceEmbeddings": "aibaba_ai_community.embeddings",
    "SelfHostedHuggingFaceInstructEmbeddings": "aibaba_ai_community.embeddings",
    "SentenceTransformerEmbeddings": "aibaba_ai_community.embeddings",
    "SpacyEmbeddings": "aibaba_ai_community.embeddings",
    "TensorflowHubEmbeddings": "aibaba_ai_community.embeddings",
    "VertexAIEmbeddings": "aibaba_ai_community.embeddings",
    "VoyageEmbeddings": "aibaba_ai_community.embeddings",
    "XinferenceEmbeddings": "aibaba_ai_community.embeddings",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "AlephAlphaAsymmetricSemanticEmbedding",
    "AlephAlphaSymmetricSemanticEmbedding",
    "AwaEmbeddings",
    "AzureOpenAIEmbeddings",
    "BedrockEmbeddings",
    "BookendEmbeddings",
    "CacheBackedEmbeddings",
    "ClarifaiEmbeddings",
    "CohereEmbeddings",
    "DashScopeEmbeddings",
    "DatabricksEmbeddings",
    "DeepInfraEmbeddings",
    "DeterministicFakeEmbedding",
    "EdenAiEmbeddings",
    "ElasticsearchEmbeddings",
    "EmbaasEmbeddings",
    "ErnieEmbeddings",
    "FakeEmbeddings",
    "FastEmbedEmbeddings",
    "GooglePalmEmbeddings",
    "GPT4AllEmbeddings",
    "GradientEmbeddings",
    "HuggingFaceBgeEmbeddings",
    "HuggingFaceEmbeddings",
    "HuggingFaceHubEmbeddings",
    "HuggingFaceInferenceAPIEmbeddings",
    "HuggingFaceInstructEmbeddings",
    "InfinityEmbeddings",
    "JavelinAIGatewayEmbeddings",
    "JinaEmbeddings",
    "JohnSnowLabsEmbeddings",
    "LlamaCppEmbeddings",
    "LocalAIEmbeddings",
    "MiniMaxEmbeddings",
    "MlflowAIGatewayEmbeddings",
    "MlflowEmbeddings",
    "ModelScopeEmbeddings",
    "MosaicMLInstructorEmbeddings",
    "NLPCloudEmbeddings",
    "OctoAIEmbeddings",
    "OllamaEmbeddings",
    "OpenAIEmbeddings",
    "OpenVINOEmbeddings",
    "QianfanEmbeddingsEndpoint",
    "SagemakerEndpointEmbeddings",
    "SelfHostedEmbeddings",
    "SelfHostedHuggingFaceEmbeddings",
    "SelfHostedHuggingFaceInstructEmbeddings",
    "SentenceTransformerEmbeddings",
    "SpacyEmbeddings",
    "TensorflowHubEmbeddings",
    "VertexAIEmbeddings",
    "VoyageEmbeddings",
    "XinferenceEmbeddings",
    "init_embeddings",
]
