from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.agent_toolkits.github.toolkit import (
        BranchName,
        CommentOnIssue,
        CreateFile,
        CreatePR,
        CreateReviewRequest,
        DeleteFile,
        DirectoryPath,
        GetIssue,
        GetPR,
        GitHubToolkit,
        NoInput,
        ReadFile,
        SearchCode,
        SearchIssuesAndPRs,
        UpdateFile,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "NoInput": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "GetIssue": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "CommentOnIssue": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "GetPR": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "CreatePR": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "CreateFile": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "ReadFile": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "UpdateFile": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "DeleteFile": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "DirectoryPath": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "BranchName": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "SearchCode": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "CreateReviewRequest": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "SearchIssuesAndPRs": "aibaba_ai_community.agent_toolkits.github.toolkit",
    "GitHubToolkit": "aibaba_ai_community.agent_toolkits.github.toolkit",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "NoInput",
    "GetIssue",
    "CommentOnIssue",
    "GetPR",
    "CreatePR",
    "CreateFile",
    "ReadFile",
    "UpdateFile",
    "DeleteFile",
    "DirectoryPath",
    "BranchName",
    "SearchCode",
    "CreateReviewRequest",
    "SearchIssuesAndPRs",
    "GitHubToolkit",
]
