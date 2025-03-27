"""
Router integration utilities
"""

import logging
from whatsapp_chatbot_python import Notification as BaseNotification

logger = logging.getLogger('whatsapp_chatgpt_python')
_logger_configured = False

def setup_router_integration(bot):
    """
    Set up router integration for the WhatsappGptBot

    This function adds tracking of handler execution and implements
    GPT processing based on whether handlers matched.

    Logic:
    1. If no handler handles a message, process with GPT
    2. If a handler handles a message, don't process with GPT by default
    3. A handler can explicitly request GPT processing by calling process_with_gpt()

    Args:
        bot: The WhatsappGptBot instance
    """
    from ..notification import ExtendedNotification

    global _logger_configured
    if not _logger_configured:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        _logger_configured = True

    original_propagate_event = bot.router.message.propagate_event

    handled_messages = {}
    processed_messages = {}

    def notification_process_with_gpt(self, custom_message=None):
        """
        Request GPT processing for this notification

        Args:
            custom_message: Optional custom message to process instead of the original
        """
        if not hasattr(self, 'sender'):
            logger.warning("Cannot process with GPT: notification has no sender attribute")
            return

        if self.sender in processed_messages:
            processed_messages[self.sender] = True

        if custom_message is not None:
            if not hasattr(bot, 'process_chat_sync'):
                logger.warning("Cannot process with GPT: bot has no process_chat_sync method")
                return

            modified_notification = BaseNotification(
                self.event.copy(),  # Make a copy to avoid modifying the original
                self.api,
                self.state_manager
            )

            bot._process_with_gpt(modified_notification)
        else:
            bot._process_with_gpt(self)

    original_process_with_gpt = getattr(BaseNotification, "process_with_gpt", None)

    if not hasattr(BaseNotification, "process_with_gpt"):
        BaseNotification.process_with_gpt = notification_process_with_gpt

    def propagate_event_wrapper():
        chat_id = None
        if bot.router.message.event and 'senderData' in bot.router.message.event:
            chat_id = bot.router.message.event['senderData'].get('chatId')

        if chat_id:
            handled_messages[chat_id] = False
            processed_messages[chat_id] = False

        from whatsapp_chatbot_python.manager.handler import Handler
        original_execute_handler = Handler.execute_handler

        def execute_handler_wrapper(self, observer):
            notification = BaseNotification(
                observer.event, observer.router.api, observer.state_manager
            )

            should_handle = self.check_event(notification)
            if not should_handle:
                logger.debug("Event does not match filters.")
                return False

            ext_notification = ExtendedNotification(
                observer.event, observer.router.api, observer.state_manager,
                gpt_bot=bot
            )

            if notification.chat and notification.chat in handled_messages:
                handled_messages[notification.chat] = True

            logger.debug("Event matches filters. Handling event.")

            try:
                self.handler(ext_notification)

                if notification.chat and notification.chat in processed_messages:
                    if hasattr(ext_notification, '_already_processed'):
                        processed_messages[notification.chat] = ext_notification._already_processed
            except Exception as e:
                logger.error(f"Error in handler: {e}", exc_info=True)

            return True

        for handler in bot.router.message.handlers:
            handler.__class__.execute_handler = execute_handler_wrapper

        original_propagate_event()

        for handler in bot.router.message.handlers:
            handler.__class__.execute_handler = original_execute_handler

        if chat_id:
            was_handled = handled_messages.get(chat_id, False)
            already_processed = processed_messages.get(chat_id, False)

            if not was_handled and not already_processed:
                logger.debug(f"Processing unhandled message from {chat_id} with GPT")

                try:
                    notification = BaseNotification(
                        bot.router.message.event,
                        bot.router.api,
                        bot.router.message.state_manager
                    )

                    bot._process_with_gpt(notification)
                except Exception as e:
                    logger.error(f"Error processing message with GPT: {e}", exc_info=True)

            if chat_id in handled_messages:
                del handled_messages[chat_id]
            if chat_id in processed_messages:
                del processed_messages[chat_id]

    bot.router.message.propagate_event = propagate_event_wrapper

    def cleanup():
        bot.router.message.propagate_event = original_propagate_event

        if original_process_with_gpt:
            BaseNotification.process_with_gpt = original_process_with_gpt
        elif hasattr(BaseNotification, "process_with_gpt"):
            delattr(BaseNotification, "process_with_gpt")

    bot._cleanup_router = cleanup

    logger.info("GPT router integration setup completed")
