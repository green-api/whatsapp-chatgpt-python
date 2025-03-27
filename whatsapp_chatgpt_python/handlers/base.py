"""
Base message handler class
"""

from abc import ABC, abstractmethod
from typing import Any
from whatsapp_chatbot_python import Notification

class MessageHandler(ABC):
    @abstractmethod
    def can_handle(self, notification: Notification) -> bool:
        """
        Check if this handler can process the message

        Args:
            notification: The notification object

        Returns:
            True if this handler can process the message, False otherwise
        """
        pass

    @staticmethod
    def get_message_type(notification: Notification) -> str:
        """
        Extract message type from notification

        Args:
            notification: The notification object

        Returns:
            Message type or empty string if not available
        """
        message_data = notification.get_message_data()
        if not message_data:
            return ""

        return message_data.get("typeMessage", "")

    @abstractmethod
    async def process_message(self, notification: Notification, openai_client=None, model=None) -> Any:
        """
        Process the message and return content for OpenAI

        Args:
            notification: The notification object
            openai_client: Optional OpenAI client instance
            model: Optional model name

        Returns:
            Processed message content for OpenAI
        """
        pass

class FallbackMessageHandler(MessageHandler):
    """Fallback handler for any message type not handled by other handlers"""

    def can_handle(self, notification: Notification) -> bool:
        return True

    async def process_message(self, notification: Notification, *args, **kwargs) -> str:
        message_type = self.get_message_type(notification)
        return f"[The user sent a {message_type or 'unknown'} message]"
