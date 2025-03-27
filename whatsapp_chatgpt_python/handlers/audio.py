"""
Audio message handler
"""

import logging
import os
import shutil

from whatsapp_chatbot_python import Notification
from .base import MessageHandler
from ..utils import Utils

logger = logging.getLogger('whatsapp_chatgpt_python.handlers.audio')


class AudioMessageHandler(MessageHandler):
    def can_handle(self, notification: Notification) -> bool:
        """
        Check if this handler can process the message

        Args:
            notification: The notification object

        Returns:
            True if this is an audio message
        """
        message_type = self.get_message_type(notification)
        return message_type == "audioMessage"

    async def process_message(self, notification: Notification, openai_client=None, *args, **kwargs) -> str:
        """
        Process the audio message by transcribing it

        Args:
            notification: The notification object
            openai_client: OpenAI client for transcription

        Returns:
            A string with the transcription or error message
        """
        try:
            message_data = notification.get_message_data()
            if not message_data or "fileMessageData" not in message_data:
                return "[The user sent an audio message but I couldn't access it]"

            file_data = message_data.get("fileMessageData", {})
            download_url = file_data.get("downloadUrl", "")
            mime_type = file_data.get("mimeType", "")

            if not download_url:
                return "[The user sent an audio message but I couldn't access it]"

            temp_file = await Utils.download_media(download_url)

            if not openai_client:
                os.unlink(temp_file)
                return "[The user sent an audio message but transcription is not available]"

            is_whatsapp_voice = mime_type == "audio/ogg; codecs=opus"
            if is_whatsapp_voice:
                ogg_file = temp_file + ".ogg"
                shutil.copy2(temp_file, ogg_file)

                try:
                    with open(ogg_file, "rb") as audio_file:
                        transcription = openai_client.audio.transcriptions.create(
                            file=audio_file,
                            model="whisper-1"
                        )

                    os.unlink(temp_file)
                    os.unlink(ogg_file)

                    return f"[The user sent an audio message. Transcription: \"{transcription.text}\"]"
                except Exception as e:
                    logger.warning(f"Failed to transcribe WhatsApp voice with .ogg extension: {e}")
                    os.unlink(ogg_file)

            transcription = await Utils.transcribe_audio(temp_file, openai_client)
            os.unlink(temp_file)
            return f"[The user sent an audio message. Transcription: \"{transcription}\"]"
        except Exception as e:
            logger.error(f"Error processing audio: {e}", exc_info=True)
            return "[The user sent an audio message that couldn't be transcribed]"
