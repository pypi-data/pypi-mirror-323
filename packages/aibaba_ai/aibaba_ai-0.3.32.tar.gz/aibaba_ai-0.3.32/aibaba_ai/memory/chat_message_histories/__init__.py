from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aibaba_ai_community.chat_message_histories import (
        AstraDBChatMessageHistory,
        CassandraChatMessageHistory,
        ChatMessageHistory,
        CosmosDBChatMessageHistory,
        DynamoDBChatMessageHistory,
        ElasticsearchChatMessageHistory,
        FileChatMessageHistory,
        FirestoreChatMessageHistory,
        MomentoChatMessageHistory,
        MongoDBChatMessageHistory,
        Neo4jChatMessageHistory,
        PostgresChatMessageHistory,
        RedisChatMessageHistory,
        RocksetChatMessageHistory,
        SingleStoreDBChatMessageHistory,
        SQLChatMessageHistory,
        StreamlitChatMessageHistory,
        UpstashRedisChatMessageHistory,
        XataChatMessageHistory,
        ZepChatMessageHistory,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "AstraDBChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "CassandraChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "ChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "CosmosDBChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "DynamoDBChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "ElasticsearchChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "FileChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "FirestoreChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "MomentoChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "MongoDBChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "Neo4jChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "PostgresChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "RedisChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "RocksetChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "SQLChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "SingleStoreDBChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "StreamlitChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "UpstashRedisChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "XataChatMessageHistory": "aibaba_ai_community.chat_message_histories",
    "ZepChatMessageHistory": "aibaba_ai_community.chat_message_histories",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "AstraDBChatMessageHistory",
    "CassandraChatMessageHistory",
    "ChatMessageHistory",
    "CosmosDBChatMessageHistory",
    "DynamoDBChatMessageHistory",
    "ElasticsearchChatMessageHistory",
    "FileChatMessageHistory",
    "FirestoreChatMessageHistory",
    "MomentoChatMessageHistory",
    "MongoDBChatMessageHistory",
    "Neo4jChatMessageHistory",
    "PostgresChatMessageHistory",
    "RedisChatMessageHistory",
    "RocksetChatMessageHistory",
    "SingleStoreDBChatMessageHistory",
    "SQLChatMessageHistory",
    "StreamlitChatMessageHistory",
    "UpstashRedisChatMessageHistory",
    "XataChatMessageHistory",
    "ZepChatMessageHistory",
]
