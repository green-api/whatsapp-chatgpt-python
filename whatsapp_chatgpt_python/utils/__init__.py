"""
Utility functions for WhatsApp GPT Bot
"""

from .media import download_media, transcribe_audio
from .conversation import trim_conversation_history, estimate_tokens
from .router import setup_router_integration


class Utils:
    """Unified utility class providing access to all utility functions"""

    @staticmethod
    async def download_media(url):
        """Download media from URL to a temporary file"""
        return await download_media(url)

    @staticmethod
    async def transcribe_audio(file_path, openai_client):
        """Transcribe audio using OpenAI Whisper API"""
        return await transcribe_audio(file_path, openai_client)

    @staticmethod
    def trim_conversation_history(messages, max_messages, preserve_system=True):
        """Trim conversation history while preserving system message"""
        return trim_conversation_history(messages, max_messages, preserve_system)

    @staticmethod
    def estimate_tokens(messages):
        """Estimate the number of tokens in a message list"""
        return estimate_tokens(messages)
