"""
Main WhatsApp GPT Bot class
"""
import logging
import time
from typing import Dict, Type, Callable
import openai
from whatsapp_chatbot_python import GreenAPIBot, Notification

from .config import DEFAULT_MODEL, ALL_MODELS, is_image_capable_model
from .models import GPTSessionData
from .middleware import MiddlewareManager
from .handlers import MessageHandler, MessageHandlerRegistry
from .utils.router import setup_router_integration

logger = logging.getLogger('whatsapp_chatgpt_python')


class WhatsappGptBot(GreenAPIBot):
    """WhatsApp bot with GPT integration"""

    def __init__(
            self,
            id_instance: str,
            api_token_instance: str,
            openai_api_key: str,
            model: str = DEFAULT_MODEL,
            max_history_length: int = 10,
            system_message: str = "",
            temperature: float = 0.5,
            error_message: str = "Sorry, I encountered an error processing your message. Please try again.",
            session_timeout: int = 1800,  # 30 minutes
            **kwargs
    ):
        """
        Initialize the WhatsApp GPT bot

        Args:
            id_instance: GREEN-API instance ID
            api_token_instance: GREEN-API instance token
            openai_api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4o)
            max_history_length: Maximum number of messages to keep in history
            system_message: System message to set assistant behavior
            temperature: Temperature for response generation
            error_message: Message to send when an error occurs
            session_timeout: Timeout for inactive sessions in seconds
            **kwargs: Additional arguments to pass to GreenAPIBot
        """
        super().__init__(id_instance, api_token_instance, **kwargs)

        if model not in ALL_MODELS:
            logger.warning(f"Model {model} not in known models list. Using anyway, but may not work as expected.")

        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.max_history_length = max_history_length
        self.model = model
        self.temperature = temperature
        self.system_message = system_message
        self.error_message = error_message
        self.session_timeout = session_timeout
        self.middleware = MiddlewareManager()
        self.message_handlers = MessageHandlerRegistry(self.openai_client, self.model)
        self.sessions: Dict[str, GPTSessionData] = {}
        self._handled_messages = {}

        setup_router_integration(self)

        logger.info(f"WhatsApp GPT Bot initialized with model {model}")

    def process_chat_sync(self, notification: Notification) -> None:
        """
        Synchronous wrapper for _process_chat to avoid issues with event loops
        """
        chat_id = notification.chat

        try:
            session_data = self.get_session_data(chat_id)
            message_content = self.message_handlers.process_message_sync(notification)

            if message_content is None:
                logger.warning("No message content to process")
                return

            for middleware in self.middleware.message_middlewares:
                try:
                    middleware_result = middleware(
                        notification, message_content, session_data.messages, session_data
                    )
                    if middleware_result:
                        message_content = middleware_result.get("message_content", message_content)
                        session_data.messages = middleware_result.get("messages", session_data.messages)
                except Exception as e:
                    logger.error(f"Error in message middleware: {e}", exc_info=True)

            if isinstance(message_content, str):
                user_message = {
                    "role": "user",
                    "content": message_content
                }
            elif isinstance(message_content, list):
                user_message = {
                    "role": "user",
                    "content": message_content
                }
            else:
                logger.warning(f"Unsupported message content type: {type(message_content)}")
                notification.answer(self.error_message)
                return

            messages = session_data.messages.copy()
            messages.append(user_message)

            from .utils import Utils
            messages = Utils.trim_conversation_history(
                messages,
                self.max_history_length,
                preserve_system=True
            )

            session_data.messages = messages

            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )

            response_text = response.choices[0].message.content

            messages.append({
                "role": "assistant",
                "content": response_text
            })

            # Run response middleware synchronously (no asyncio.run)
            for middleware in self.middleware.response_middlewares:
                try:
                    middleware_result = middleware(
                        response_text, messages, session_data
                    )
                    if middleware_result:
                        response_text = middleware_result.get("response", response_text)
                except Exception as e:
                    logger.error(f"Error in response middleware: {e}", exc_info=True)

            self.update_session_data(chat_id, session_data)

            notification.answer(response_text)

        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            notification.answer(self.error_message)

    def _process_with_gpt(self, notification: Notification) -> None:
        """
        Process a message with GPT (sync)
        """
        try:
            message_type = ""
            message_data = notification.get_message_data()
            if message_data:
                message_type = message_data.get("typeMessage", "unknown")

            logger.debug(f"Processing {message_type} message with GPT")

            self.process_chat_sync(notification)
        except Exception as e:
            logger.error(f"Error in _process_with_gpt: {e}", exc_info=True)
            try:
                notification.answer(self.error_message)
            except Exception:
                logger.error("Failed to send error message", exc_info=True)

    def add_message_middleware(self, middleware: Callable) -> 'WhatsappGptBot':
        """
        Add middleware to process messages before sending to OpenAI

        Args:
            middleware: The middleware function

        Returns:
            Self for method chaining
        """
        self.middleware.add_message_middleware(middleware)
        return self

    def add_response_middleware(self, middleware: Callable) -> 'WhatsappGptBot':
        """
        Add middleware to process responses before sending to the user

        Args:
            middleware: The middleware function

        Returns:
            Self for method chaining
        """
        self.middleware.add_response_middleware(middleware)
        return self

    def register_message_handler(self, handler: MessageHandler, index: int = None) -> 'WhatsappGptBot':
        """
        Register a custom message handler

        Args:
            handler: The handler to register
            index: Optional position to insert the handler

        Returns:
            Self for method chaining
        """
        self.message_handlers.register_handler(handler, index)
        return self

    def replace_handler(self, handler_class: Type[MessageHandler], new_handler: MessageHandler) -> 'WhatsappGptBot':
        """
        Replace a handler with a new one

        Args:
            handler_class: The class of handler to replace
            new_handler: The new handler instance

        Returns:
            Self for method chaining
        """
        self.message_handlers.replace_handler(handler_class, new_handler)
        return self

    def get_session_data(self, chat_id: str) -> GPTSessionData:
        """
        Get session data for a chat

        Args:
            chat_id: Chat ID

        Returns:
            Session data
        """
        if chat_id not in self.sessions:
            self.sessions[chat_id] = GPTSessionData()

            if self.system_message:
                self.sessions[chat_id].messages.append({
                    "role": "system",
                    "content": self.system_message
                })

        self.sessions[chat_id].update_activity()
        return self.sessions[chat_id]

    def update_session_data(self, chat_id: str, session_data: GPTSessionData) -> None:
        """
        Update session data for a chat

        Args:
            chat_id: Chat ID
            session_data: New session data
        """
        self.sessions[chat_id] = session_data

    def cleanup_sessions(self) -> None:
        """
        Remove expired sessions
        """
        current_time = int(time.time())
        expired_chats = []

        for chat_id, session in self.sessions.items():
            if current_time - session.last_activity > self.session_timeout:
                expired_chats.append(chat_id)

        for chat_id in expired_chats:
            logger.info(f"Removing expired session for chat {chat_id}")
            del self.sessions[chat_id]

    def get_model(self) -> str:
        """
        Get the current OpenAI model

        Returns:
            Model name
        """
        return self.model

    def supports_images(self) -> bool:
        """
        Check if the current model supports image processing

        Returns:
            True if the model supports images
        """
        return is_image_capable_model(self.model)
