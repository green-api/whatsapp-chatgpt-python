"""
Middleware manager
"""

import logging
from typing import List, Dict, Any

from whatsapp_chatbot_python import Notification
from .base import ProcessMessageMiddleware, ProcessResponseMiddleware
from ..models import GPTSessionData

logger = logging.getLogger('whatsapp_chatgpt_python.middleware')


class MiddlewareManager:
    def __init__(self):
        self.message_middlewares: List[ProcessMessageMiddleware] = []
        self.response_middlewares: List[ProcessResponseMiddleware] = []

    def add_message_middleware(self, middleware: ProcessMessageMiddleware) -> None:
        """
        Add middleware to process messages before sending to OpenAI

        Args:
            middleware: The middleware function to add
        """
        self.message_middlewares.append(middleware)

    def add_response_middleware(self, middleware: ProcessResponseMiddleware) -> None:
        """
        Add middleware to process responses before sending to the user

        Args:
            middleware: The middleware function to add
        """
        self.response_middlewares.append(middleware)

    def process_message(
            self,
            notification: Notification,
            message_content: Any,
            messages: List[Dict[str, Any]],
            session_data: GPTSessionData
    ) -> Dict[str, Any]:
        """
        Process a message through all message middlewares

        Args:
            notification: The notification object
            message_content: The initial message content
            messages: The current conversation history
            session_data: The session data

        Returns:
            Dict with processed message_content and messages
        """
        result = {
            "message_content": message_content,
            "messages": messages.copy()  # Copy to avoid modifying the original
        }

        for middleware in self.message_middlewares:
            try:
                middleware_result = middleware(
                    notification,
                    result["message_content"],
                    result["messages"],
                    session_data
                )
                if middleware_result:
                    result = middleware_result
            except Exception as e:
                logger.error(f"Error in message middleware: {e}", exc_info=True)

        return result

    def process_response(
            self,
            response: str,
            messages: List[Dict[str, Any]],
            session_data: GPTSessionData
    ) -> Dict[str, Any]:
        """
        Process a response through all response middlewares

        Args:
            response: The initial response from OpenAI
            messages: The current conversation history
            session_data: The session data

        Returns:
            Dict with processed response and messages
        """
        result = {
            "response": response,
            "messages": messages.copy()  # Copy to avoid modifying the original
        }

        for middleware in self.response_middlewares:
            try:
                middleware_result = middleware(
                    result["response"],
                    result["messages"],
                    session_data
                )
                if middleware_result:
                    result = middleware_result
            except Exception as e:
                logger.error(f"Error in response middleware: {e}", exc_info=True)

        return result
