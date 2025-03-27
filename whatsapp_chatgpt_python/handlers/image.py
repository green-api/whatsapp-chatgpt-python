"""
Image message handler
"""

import logging
import os
from typing import Union, List, Dict, Any
from whatsapp_chatbot_python import Notification
from .base import MessageHandler
from ..config import is_image_capable_model

logger = logging.getLogger('whatsapp_chatgpt_python.handlers.image')


class ImageMessageHandler(MessageHandler):
    SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'gif', 'webp']

    def can_handle(self, notification: Notification) -> bool:
        """
        Check if this handler can process the message

        Args:
            notification: The notification object

        Returns:
            True if this is an image message
        """
        message_type = self.get_message_type(notification)
        logger.debug(f"ImageMessageHandler checking message type: '{message_type}'")
        return message_type == "imageMessage"

    def _is_supported_format(self, file_name: str, mime_type: str) -> bool:
        if file_name:
            extension = os.path.splitext(file_name)[1].lower().lstrip('.')
            if extension not in self.SUPPORTED_FORMATS:
                return False

        if mime_type:
            mime_parts = mime_type.lower().split('/')
            if len(mime_parts) == 2:
                if mime_parts[0] == 'image':
                    sub_type = mime_parts[1]
                    if sub_type in self.SUPPORTED_FORMATS or sub_type == 'jpg':
                        return True

        if not file_name and mime_type:
            return True

        if file_name:
            extension = os.path.splitext(file_name)[1].lower().lstrip('.')
            return extension in self.SUPPORTED_FORMATS

        return False

    async def process_message(
            self,
            notification: Notification,
            openai_client=None,
            model=None
    ) -> Union[str, List[Dict[str, Any]]]:
        """
        Process the image message with format validation

        Args:
            notification: The notification object
            openai_client: OpenAI client instance
            model: Model name to check image capability

        Returns:
            For vision-capable models: A list of content items (text + image) if format is supported
            For other models or unsupported formats: A text description of the image
        """
        supports_images = is_image_capable_model(model) if model else False
        logger.debug(f"Processing image with model {model}, supports images: {supports_images}")

        message_data = notification.get_message_data()
        logger.debug(f"Image message data: {message_data and 'fileMessageData' in message_data}")

        if not message_data or "fileMessageData" not in message_data:
            return "[The user sent an image but I couldn't access it]"

        file_data = message_data.get("fileMessageData", {})
        download_url = file_data.get("downloadUrl", "")
        caption = file_data.get("caption", "")
        file_name = file_data.get("fileName", "")
        mime_type = file_data.get("mimeType", "")

        logger.debug(
            f"Image details - URL: {bool(download_url)}, Caption: '{caption}', File: '{file_name}', MIME: '{mime_type}'")

        if not download_url:
            return "[The user sent an image but I couldn't access it]"

        is_supported = self._is_supported_format(file_name, mime_type)
        logger.debug(f"Image format supported by OpenAI: {is_supported}")

        if not supports_images or not is_supported:
            reason = ""
            if supports_images and not is_supported:
                reason = " (unsupported format for AI analysis)"

            caption_text = f' with caption: "{caption}"' if caption else ""
            file_text = f' ({file_name})' if file_name else ""

            return f"[The user sent an image{file_text}{caption_text}{reason}]"

        logger.debug("Returning multimodal content for vision model")
        return [
            {"type": "text", "text": caption if caption else "Analyzing this image"},
            {"type": "image_url", "image_url": {"url": download_url}}
        ]
