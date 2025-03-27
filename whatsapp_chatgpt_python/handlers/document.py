"""
Document message handler
"""

from whatsapp_chatbot_python import Notification
from .base import MessageHandler

class DocumentMessageHandler(MessageHandler):
    def can_handle(self, notification: Notification) -> bool:
        """
        Check if this handler can process the message

        Args:
            notification: The notification object

        Returns:
            True if this is a document message
        """
        message_type = self.get_message_type(notification)
        return message_type == "documentMessage"

    async def process_message(self, notification: Notification, *args, **kwargs) -> str:
        """
        Process the document message

        Args:
            notification: The notification object

        Returns:
            A text description of the document
        """
        message_data = notification.get_message_data()
        if not message_data or "fileMessageData" not in message_data:
            return "[The user sent a document but I couldn't access it]"

        file_data = message_data.get("fileMessageData", {})
        file_name = file_data.get("fileName", "unknown file")
        caption = file_data.get("caption", "")

        caption_text = f' with caption: "{caption}"' if caption else ""

        return f"[The user sent a document: \"{file_name}\"{caption_text}]"
