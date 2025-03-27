"""
Location message handler
"""

from whatsapp_chatbot_python import Notification
from .base import MessageHandler

class LocationMessageHandler(MessageHandler):
    def can_handle(self, notification: Notification) -> bool:
        """
        Check if this handler can process the message

        Args:
            notification: The notification object

        Returns:
            True if this is a location message
        """
        message_type = self.get_message_type(notification)
        return message_type == "locationMessage"

    async def process_message(self, notification: Notification, *args, **kwargs) -> str:
        """
        Process the location message

        Args:
            notification: The notification object

        Returns:
            A text description of the location
        """
        message_data = notification.get_message_data()
        if not message_data or "locationMessageData" not in message_data:
            return "[The user shared a location but I couldn't access it]"

        location_data = message_data.get("locationMessageData", {})
        name = location_data.get("nameLocation", "unnamed location")
        address = location_data.get("address", "")
        latitude = location_data.get("latitude", 0)
        longitude = location_data.get("longitude", 0)

        address_text = f" ({address})" if address else ""
        coords = f"{latitude}, {longitude}"

        return f"[The user shared a location: \"{name}\"{address_text} at coordinates: {coords}]"
