"""**Retriever** class returns Documents given a text **query**.

It is more general than a vector store. A retriever does not need to be able to
store documents, only to return (or retrieve) it. Vector stores can be used as
the backbone of a retriever, but there are other types of retrievers as well.

**Class hierarchy:**

.. code-block::

    BaseRetriever --> <name>Retriever  # Examples: ArxivRetriever, MergerRetriever

**Main helpers:**

.. code-block::

    Document, Serializable, Callbacks,
    CallbackManagerForRetrieverRun, AsyncCallbackManagerForRetrieverRun
"""

from typing import TYPE_CHECKING, Any

from langchain._api.module_import import create_importer
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.ensemble import EnsembleRetriever
from langchain.retrievers.merger_retriever import MergerRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.retrievers.parent_document_retriever import ParentDocumentRetriever
from langchain.retrievers.re_phraser import RePhraseQueryRetriever
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.retrievers.time_weighted_retriever import (
    TimeWeightedVectorStoreRetriever,
)

if TYPE_CHECKING:
    from aibaba_ai_community.retrievers import (
        AmazonKendraRetriever,
        AmazonKnowledgeBasesRetriever,
        ArceeRetriever,
        ArxivRetriever,
        AzureAISearchRetriever,
        AzureCognitiveSearchRetriever,
        BM25Retriever,
        ChaindeskRetriever,
        ChatGPTPluginRetriever,
        CohereRagRetriever,
        DocArrayRetriever,
        DriaRetriever,
        ElasticSearchBM25Retriever,
        EmbedchainRetriever,
        GoogleCloudEnterpriseSearchRetriever,
        GoogleDocumentAIWarehouseRetriever,
        GoogleVertexAIMultiTurnSearchRetriever,
        GoogleVertexAISearchRetriever,
        KayAiRetriever,
        KNNRetriever,
        LlamaIndexGraphRetriever,
        LlamaIndexRetriever,
        MetalRetriever,
        MilvusRetriever,
        NeuralDBRetriever,
        OutlineRetriever,
        PineconeHybridSearchRetriever,
        PubMedRetriever,
        RemoteAI Agents ForceRetriever,
        SVMRetriever,
        TavilySearchAPIRetriever,
        TFIDFRetriever,
        VespaRetriever,
        WeaviateHybridSearchRetriever,
        WebResearchRetriever,
        WikipediaRetriever,
        ZepRetriever,
        ZillizRetriever,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "AmazonKendraRetriever": "aibaba_ai_community.retrievers",
    "AmazonKnowledgeBasesRetriever": "aibaba_ai_community.retrievers",
    "ArceeRetriever": "aibaba_ai_community.retrievers",
    "ArxivRetriever": "aibaba_ai_community.retrievers",
    "AzureAISearchRetriever": "aibaba_ai_community.retrievers",
    "AzureCognitiveSearchRetriever": "aibaba_ai_community.retrievers",
    "ChatGPTPluginRetriever": "aibaba_ai_community.retrievers",
    "ChaindeskRetriever": "aibaba_ai_community.retrievers",
    "CohereRagRetriever": "aibaba_ai_community.retrievers",
    "ElasticSearchBM25Retriever": "aibaba_ai_community.retrievers",
    "EmbedchainRetriever": "aibaba_ai_community.retrievers",
    "GoogleDocumentAIWarehouseRetriever": "aibaba_ai_community.retrievers",
    "GoogleCloudEnterpriseSearchRetriever": "aibaba_ai_community.retrievers",
    "GoogleVertexAIMultiTurnSearchRetriever": "aibaba_ai_community.retrievers",
    "GoogleVertexAISearchRetriever": "aibaba_ai_community.retrievers",
    "KayAiRetriever": "aibaba_ai_community.retrievers",
    "KNNRetriever": "aibaba_ai_community.retrievers",
    "LlamaIndexGraphRetriever": "aibaba_ai_community.retrievers",
    "LlamaIndexRetriever": "aibaba_ai_community.retrievers",
    "MetalRetriever": "aibaba_ai_community.retrievers",
    "MilvusRetriever": "aibaba_ai_community.retrievers",
    "OutlineRetriever": "aibaba_ai_community.retrievers",
    "PineconeHybridSearchRetriever": "aibaba_ai_community.retrievers",
    "PubMedRetriever": "aibaba_ai_community.retrievers",
    "RemoteAI Agents ForceRetriever": "aibaba_ai_community.retrievers",
    "SVMRetriever": "aibaba_ai_community.retrievers",
    "TavilySearchAPIRetriever": "aibaba_ai_community.retrievers",
    "BM25Retriever": "aibaba_ai_community.retrievers",
    "DriaRetriever": "aibaba_ai_community.retrievers",
    "NeuralDBRetriever": "aibaba_ai_community.retrievers",
    "TFIDFRetriever": "aibaba_ai_community.retrievers",
    "VespaRetriever": "aibaba_ai_community.retrievers",
    "WeaviateHybridSearchRetriever": "aibaba_ai_community.retrievers",
    "WebResearchRetriever": "aibaba_ai_community.retrievers",
    "WikipediaRetriever": "aibaba_ai_community.retrievers",
    "ZepRetriever": "aibaba_ai_community.retrievers",
    "ZillizRetriever": "aibaba_ai_community.retrievers",
    "DocArrayRetriever": "aibaba_ai_community.retrievers",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "AmazonKendraRetriever",
    "AmazonKnowledgeBasesRetriever",
    "ArceeRetriever",
    "ArxivRetriever",
    "AzureAISearchRetriever",
    "AzureCognitiveSearchRetriever",
    "BM25Retriever",
    "ChaindeskRetriever",
    "ChatGPTPluginRetriever",
    "CohereRagRetriever",
    "ContextualCompressionRetriever",
    "DocArrayRetriever",
    "DriaRetriever",
    "ElasticSearchBM25Retriever",
    "EmbedchainRetriever",
    "EnsembleRetriever",
    "GoogleCloudEnterpriseSearchRetriever",
    "GoogleDocumentAIWarehouseRetriever",
    "GoogleVertexAIMultiTurnSearchRetriever",
    "GoogleVertexAISearchRetriever",
    "KayAiRetriever",
    "KNNRetriever",
    "LlamaIndexGraphRetriever",
    "LlamaIndexRetriever",
    "MergerRetriever",
    "MetalRetriever",
    "MilvusRetriever",
    "MultiQueryRetriever",
    "MultiVectorRetriever",
    "OutlineRetriever",
    "ParentDocumentRetriever",
    "PineconeHybridSearchRetriever",
    "PubMedRetriever",
    "RemoteAI Agents ForceRetriever",
    "RePhraseQueryRetriever",
    "SelfQueryRetriever",
    "SVMRetriever",
    "TavilySearchAPIRetriever",
    "TFIDFRetriever",
    "TimeWeightedVectorStoreRetriever",
    "VespaRetriever",
    "WeaviateHybridSearchRetriever",
    "WebResearchRetriever",
    "WikipediaRetriever",
    "ZepRetriever",
    "NeuralDBRetriever",
    "ZillizRetriever",
]
