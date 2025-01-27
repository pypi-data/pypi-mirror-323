from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.llms import AzureMLOnlineEndpoint
    from aibaba_ai_community.llms.azureml_endpoint import (
        AzureMLEndpointClient,
        ContentFormatterBase,
        CustomOpenAIContentFormatter,
        DollyContentFormatter,
        GPT2ContentFormatter,
        HFContentFormatter,
        OSSContentFormatter,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "AzureMLEndpointClient": "aibaba_ai_community.llms.azureml_endpoint",
    "ContentFormatterBase": "aibaba_ai_community.llms.azureml_endpoint",
    "GPT2ContentFormatter": "aibaba_ai_community.llms.azureml_endpoint",
    "OSSContentFormatter": "aibaba_ai_community.llms.azureml_endpoint",
    "HFContentFormatter": "aibaba_ai_community.llms.azureml_endpoint",
    "DollyContentFormatter": "aibaba_ai_community.llms.azureml_endpoint",
    "CustomOpenAIContentFormatter": "aibaba_ai_community.llms.azureml_endpoint",
    "AzureMLOnlineEndpoint": "aibaba_ai_community.llms",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "AzureMLEndpointClient",
    "ContentFormatterBase",
    "GPT2ContentFormatter",
    "OSSContentFormatter",
    "HFContentFormatter",
    "DollyContentFormatter",
    "CustomOpenAIContentFormatter",
    "AzureMLOnlineEndpoint",
]
