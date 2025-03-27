"""
Extended notification class
"""

import logging
from whatsapp_chatbot_python import Notification as BaseNotification

logger = logging.getLogger('whatsapp_chatgpt_python')


class ExtendedNotification(BaseNotification):
    """
    Extended notification class with GPT processing capability

    This subclass adds a method to process a message with GPT
    after it's been handled by a handler.
    """

    def __init__(self, event, api, state_manager, gpt_bot=None):
        """
        Initialize an extended notification

        Args:
            event: The event data
            api: The GreenAPI instance
            state_manager: The state manager
            gpt_bot: Reference to the WhatsappGptBot instance
        """
        super().__init__(event, api, state_manager)
        self.gpt_bot = gpt_bot
        self._already_processed = False

    def process_with_gpt(self, custom_message=None) -> None:
        """
        Process this message with GPT

        Args:
            custom_message: Optional custom message to send to GPT instead of the original message
        """
        if not self.gpt_bot:
            logger.warning("Cannot process with GPT: No GPT bot reference available")
            return

        if self._already_processed:
            logger.debug("Skipping duplicate GPT processing")
            return

        logger.debug(f"Processing message from {self.sender} with GPT (handler requested)")
        self._already_processed = True

        if custom_message is not None:
            modified_event = self.event.copy()

            if 'messageData' in modified_event:
                if modified_event['messageData']['typeMessage'] == 'textMessage':
                    modified_event['messageData']['textMessageData']['textMessage'] = custom_message
                elif modified_event['messageData']['typeMessage'] in ['extendedTextMessage', 'quotedMessage']:
                    modified_event['messageData']['extendedTextMessageData']['text'] = custom_message

            custom_notification = BaseNotification(
                modified_event,
                self.api,
                self.state_manager
            )

            self.gpt_bot._process_with_gpt(custom_notification)
        else:
            self.gpt_bot._process_with_gpt(self)
