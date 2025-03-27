"""
Video message handler
"""

from whatsapp_chatbot_python import Notification
from .base import MessageHandler

class VideoMessageHandler(MessageHandler):
    def can_handle(self, notification: Notification) -> bool:
        """
        Check if this handler can process the message

        Args:
            notification: The notification object

        Returns:
            True if this is a video message
        """
        message_type = self.get_message_type(notification)
        return message_type == "videoMessage"

    async def process_message(self, notification: Notification, *args, **kwargs) -> str:
        """
        Process the video message

        Args:
            notification: The notification object

        Returns:
            A text description of the video
        """
        message_data = notification.get_message_data()
        if not message_data or "fileMessageData" not in message_data:
            return "[The user sent a video but I couldn't access it]"

        file_data = message_data.get("fileMessageData", {})
        file_name = file_data.get("fileName", "")
        caption = file_data.get("caption", "")

        caption_text = f' with caption: "{caption}"' if caption else ""
        file_text = f' ({file_name})' if file_name else ""

        return f"[The user sent a video{file_text}{caption_text}]"
