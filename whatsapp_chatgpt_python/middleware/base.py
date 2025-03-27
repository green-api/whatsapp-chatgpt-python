"""
Base middleware types
"""

from typing import Protocol, Dict, List, Any, TypeVar
from whatsapp_chatbot_python import Notification
from ..models import GPTSessionData

MessageContent = Any
Messages = List[Dict[str, Any]]
T = TypeVar('T')


class ProcessMessageMiddleware(Protocol):
    """
    Protocol for message processing middleware

    Args:
        notification (Notification): The notification object
        message_content (Any): The processed message content
        messages (List[Dict[str, Any]]): The current conversation history
        session_data (GPTSessionData): The session data

    Returns:
        Dict[str, Any]: Dict with updated message_content and messages
    """

    def __call__(
            self,
            notification: Notification,
            message_content: MessageContent,
            messages: Messages,
            session_data: GPTSessionData
    ) -> Dict[str, Any]: ...


class ProcessResponseMiddleware(Protocol):
    """
    Protocol for response processing middleware

    Args:
        response: The response text from OpenAI
        messages: The current conversation history
        session_data: The session data

    Returns:
        Dict with updated response and messages
    """

    def __call__(
            self,
            response: str,
            messages: Messages,
            session_data: GPTSessionData
    ) -> Dict[str, Any]: ...
