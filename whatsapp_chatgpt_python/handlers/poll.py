"""
Poll message handler
"""

from whatsapp_chatbot_python import Notification
from .base import MessageHandler

class PollMessageHandler(MessageHandler):
    def can_handle(self, notification: Notification) -> bool:
        """
        Check if this handler can process the message

        Args:
            notification: The notification object

        Returns:
            True if this is a poll message
        """
        message_type = self.get_message_type(notification)
        return message_type in ["pollMessage", "pollUpdateMessage"]

    async def process_message(self, notification: Notification, *args, **kwargs) -> str:
        """
        Process the poll message

        Args:
            notification: The notification object

        Returns:
            A text description of the poll
        """
        message_data = notification.get_message_data()
        if not message_data:
            return "[The user interacted with a poll but I couldn't access it]"

        message_type = message_data.get("typeMessage", "")

        if message_type == "pollMessage":
            poll_data = message_data.get("pollMessageData", {})
            if not poll_data:
                return "[The user created a poll but I couldn't access it]"

            name = poll_data.get("name", "unnamed poll")
            options = poll_data.get("options", [])
            option_names = [opt.get("optionName", "") for opt in options if "optionName" in opt]

            options_text = ", ".join(f'"{opt}"' for opt in option_names) if option_names else "no options"

            return f"[The user created a poll: \"{name}\" with options: {options_text}]"

        elif message_type == "pollUpdateMessage":
            poll_update_data = message_data.get("pollMessageData", {})
            if not poll_update_data:
                return "[The user voted in a poll but I couldn't access the details]"

            poll_name = poll_update_data.get("name", "unnamed poll")
            votes = poll_update_data.get("votes", [])

            vote_info = []
            for vote in votes:
                voters = len(vote.get("optionVoters", []))
                option_name = vote.get("optionName", "unknown option")
                vote_info.append(f'"{option_name}" ({voters} vote{"s" if voters != 1 else ""})')

            vote_text = ", ".join(vote_info) if vote_info else "no votes"

            return f"[The user voted in poll: \"{poll_name}\" with results: {vote_text}]"

        return "[The user interacted with a poll]"
