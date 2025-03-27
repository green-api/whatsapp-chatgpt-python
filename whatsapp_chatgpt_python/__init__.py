"""
WhatsApp GPT Bot
A Python library for creating WhatsApp bots integrated with OpenAI GPT models.
Built on top of whatsapp-chatbot-python and GREEN-API.
"""

from .bot import WhatsappGptBot
from .models import GPTSessionData
from .notification import ExtendedNotification
from .config import (
    DEFAULT_MODEL,
    GPT4_MODELS,
    GPT4O_MODELS,
    GPT35_MODELS,
    O1_MODELS,
    IMAGE_CAPABLE_MODELS,
    ALL_MODELS,
    is_image_capable_model
)
from .handlers import (
    MessageHandler,
    TextMessageHandler,
    ImageMessageHandler,
    AudioMessageHandler,
    VideoMessageHandler,
    DocumentMessageHandler,
    LocationMessageHandler,
    ContactMessageHandler,
    PollMessageHandler,
    FallbackMessageHandler
)
from .middleware import MiddlewareManager
from .utils import Utils

__version__ = "0.1.0"
