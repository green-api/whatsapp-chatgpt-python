"""
Contact message handler
"""

import re
from whatsapp_chatbot_python import Notification
from .base import MessageHandler

class ContactMessageHandler(MessageHandler):
    def can_handle(self, notification: Notification) -> bool:
        """
        Check if this handler can process the message

        Args:
            notification: The notification object

        Returns:
            True if this is a contact message
        """
        message_type = self.get_message_type(notification)
        return message_type == "contactMessage"

    async def process_message(self, notification: Notification, *args, **kwargs) -> str:
        """
        Process the contact message

        Args:
            notification: The notification object

        Returns:
            A text description of the contact
        """
        message_data = notification.get_message_data()
        if not message_data or "contactMessageData" not in message_data:
            return "[The user shared a contact but I couldn't access it]"

        contact_data = message_data.get("contactMessageData", {})
        display_name = contact_data.get("displayName", "unknown")
        vcard = contact_data.get("vcard", "")

        phone_number = None
        if vcard:
            phone_match = re.search(r'TEL(?:;[^:]+)?:([+\d\s-]+)', vcard)
            phone_number = phone_match.group(1) if phone_match else None

        phone_text = f"\nPhone: {phone_number}" if phone_number else ""
        return f"[The user shared a contact: \"{display_name}\"{phone_text}]"
