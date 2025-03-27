"""
Text message handler
"""

from whatsapp_chatbot_python import Notification
from .base import MessageHandler

class TextMessageHandler(MessageHandler):
    def can_handle(self, notification: Notification) -> bool:
        """
        Check if this handler can process the message

        Args:
            notification: The notification object

        Returns:
            True if this is a text or extended text message
        """
        message_type = self.get_message_type(notification)
        return message_type in ["textMessage", "extendedTextMessage"]

    async def process_message(self, notification: Notification, *args, **kwargs) -> str:
        """
        Process the message and return the text content

        Args:
            notification: The notification object

        Returns:
            The message text or "Empty message" if none
        """
        return notification.message_text or "Empty message"
