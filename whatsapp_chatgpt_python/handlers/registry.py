"""
Message handler registry
"""

import logging
import asyncio
from typing import List, Any, Type
from whatsapp_chatbot_python import Notification

from .base import MessageHandler, FallbackMessageHandler
from .text import TextMessageHandler
from .image import ImageMessageHandler
from .audio import AudioMessageHandler
from .video import VideoMessageHandler
from .document import DocumentMessageHandler
from .location import LocationMessageHandler
from .contact import ContactMessageHandler
from .poll import PollMessageHandler

logger = logging.getLogger('whatsapp_chatgpt_python.handlers')

class MessageHandlerRegistry:
    def __init__(self, openai_client, model):
        """
        Initialize the message handler registry

        Args:
            openai_client: OpenAI client instance
            model: Model name
        """
        self.handlers: List[MessageHandler] = []
        self.openai_client = openai_client
        self.model = model
        self.register_default_handlers()

    def register_default_handlers(self):
        """Register the default set of message handlers"""
        self.handlers = [
            TextMessageHandler(),
            ImageMessageHandler(),
            AudioMessageHandler(),
            VideoMessageHandler(),
            DocumentMessageHandler(),
            LocationMessageHandler(),
            ContactMessageHandler(),
            PollMessageHandler(),
            FallbackMessageHandler()
        ]

    def register_handler(self, handler: MessageHandler, index: int = None):
        """
        Register a custom message handler

        Args:
            handler: The handler to register
            index: Optional position to insert the handler (default: before fallback)
        """
        if index is not None:
            self.handlers.insert(index, handler)
        else:
            self.handlers.insert(len(self.handlers) - 1, handler)

    def replace_handler(self, handler_type: Type[MessageHandler], new_handler: MessageHandler) -> bool:
        """
        Replace a handler of a specific type with a new handler

        Args:
            handler_type: The handler class to replace
            new_handler: The new handler instance

        Returns:
            True if replacement succeeded, False otherwise
        """
        for i, handler in enumerate(self.handlers):
            if isinstance(handler, handler_type):
                self.handlers[i] = new_handler
                return True
        return False

    async def process_message(self, notification: Notification) -> Any:
        """
        Process a message using the appropriate handler (async version)

        Args:
            notification: The notification object

        Returns:
            Processed message content
        """
        message_type = ""
        for handler in self.handlers:
            try:
                message_type = handler.get_message_type(notification)
                if handler.can_handle(notification):
                    logger.debug(f"Using handler {handler.__class__.__name__} for message type {message_type}")

                    if isinstance(handler, ImageMessageHandler):
                        return await handler.process_message(notification, self.openai_client, self.model)

                    return await handler.process_message(notification, self.openai_client)
            except Exception as e:
                logger.error(f"Error in handler {handler.__class__.__name__}: {e}", exc_info=True)
                continue

        logger.warning(f"No handler matched message type '{message_type}', using fallback")

        fallback = self.handlers[-1]
        return await fallback.process_message(notification, self.openai_client)

    def process_message_sync(self, notification: Notification) -> Any:
        """
        Process a message using the appropriate handler (sync version)

        Args:
            notification: The notification object

        Returns:
            Processed message content
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.process_message(notification))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error in process_message_sync: {e}", exc_info=True)
            return "[Error processing message]"
