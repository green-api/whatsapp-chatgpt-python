"""
Message handlers for WhatsApp GPT Bot
"""

from .base import MessageHandler
from .text import TextMessageHandler
from .image import ImageMessageHandler
from .audio import AudioMessageHandler
from .video import VideoMessageHandler
from .document import DocumentMessageHandler
from .location import LocationMessageHandler
from .contact import ContactMessageHandler
from .poll import PollMessageHandler
from .base import FallbackMessageHandler
from .registry import MessageHandlerRegistry
