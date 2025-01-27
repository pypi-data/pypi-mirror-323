"""**Messages** are objects used in prompts and chat conversations.

**Class hierarchy:**

.. code-block::

    BaseMessage --> SystemMessage, AIMessage, HumanMessage, ChatMessage, FunctionMessage, ToolMessage
                --> BaseMessageChunk --> SystemMessageChunk, AIMessageChunk, HumanMessageChunk, ChatMessageChunk, FunctionMessageChunk, ToolMessageChunk

**Main helpers:**

.. code-block::

    ChatPromptTemplate

"""  # noqa: E501

from aibaba_ai_core.messages.ai import (
    AIMessage,
    AIMessageChunk,
)
from aibaba_ai_core.messages.base import (
    BaseMessage,
    BaseMessageChunk,
    merge_content,
    message_to_dict,
    messages_to_dict,
)
from aibaba_ai_core.messages.chat import ChatMessage, ChatMessageChunk
from aibaba_ai_core.messages.function import FunctionMessage, FunctionMessageChunk
from aibaba_ai_core.messages.human import HumanMessage, HumanMessageChunk
from aibaba_ai_core.messages.modifier import RemoveMessage
from aibaba_ai_core.messages.system import SystemMessage, SystemMessageChunk
from aibaba_ai_core.messages.tool import (
    InvalidToolCall,
    ToolCall,
    ToolCallChunk,
    ToolMessage,
    ToolMessageChunk,
)
from aibaba_ai_core.messages.utils import (
    AnyMessage,
    MessageLikeRepresentation,
    _message_from_dict,
    convert_to_messages,
    convert_to_openai_messages,
    filter_messages,
    get_buffer_string,
    merge_message_runs,
    message_chunk_to_message,
    messages_from_dict,
    trim_messages,
)

__all__ = [
    "AIMessage",
    "AIMessageChunk",
    "AnyMessage",
    "BaseMessage",
    "BaseMessageChunk",
    "ChatMessage",
    "ChatMessageChunk",
    "FunctionMessage",
    "FunctionMessageChunk",
    "HumanMessage",
    "HumanMessageChunk",
    "InvalidToolCall",
    "MessageLikeRepresentation",
    "SystemMessage",
    "SystemMessageChunk",
    "ToolCall",
    "ToolCallChunk",
    "ToolMessage",
    "ToolMessageChunk",
    "RemoveMessage",
    "_message_from_dict",
    "convert_to_messages",
    "get_buffer_string",
    "merge_content",
    "message_chunk_to_message",
    "message_to_dict",
    "messages_from_dict",
    "messages_to_dict",
    "filter_messages",
    "merge_message_runs",
    "trim_messages",
    "convert_to_openai_messages",
]
