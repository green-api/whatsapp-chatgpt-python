"""
Conversation management utilities
"""

from typing import List, Dict, Any


def trim_conversation_history(
        messages: List[Dict[str, Any]],
        max_messages: int,
        preserve_system: bool = True
) -> List[Dict[str, Any]]:
    """
    Trim conversation history to the specified number of messages

    Args:
        messages: List of conversation messages
        max_messages: Maximum number of messages to keep
        preserve_system: Whether to preserve system message

    Returns:
        Trimmed list of messages
    """
    if len(messages) <= max_messages:
        return messages

    if preserve_system and messages and messages[0].get("role") == "system":
        return [messages[0]] + messages[-(max_messages - 1):]
    else:
        return messages[-max_messages:]


def estimate_tokens(messages: List[Dict[str, Any]]) -> int:
    """
    Estimate the number of tokens in a conversation (rough estimation)

    Args:
        messages: List of conversation messages

    Returns:
        Estimated token count
    """
    total = 0
    for message in messages:
        content = message.get("content", "")
        # Very rough estimation: 1 token ~= 4 characters
        if isinstance(content, str):
            total += len(content) // 4
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    total += len(item["text"]) // 4
                if isinstance(item, dict) and "image_url" in item:
                    total += 50  # Rough estimate for image presence

    return total
