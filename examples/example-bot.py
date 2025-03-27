"""
Example WhatsApp GPT Bot implementation
"""

import os
import time
import logging
from whatsapp_chatgpt_python import (
    WhatsappGptBot,
    ImageMessageHandler,
    TextMessageHandler
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('whatsapp_chatgpt_python')

# Get environment variables
ID_INSTANCE = os.environ.get("INSTANCE_ID", "your_instance_id")
API_TOKEN = os.environ.get("INSTANCE_TOKEN", "your_instance_token")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_openai_api_key")

# Initialize the bot
bot = WhatsappGptBot(
    id_instance=ID_INSTANCE,
    api_token_instance=API_TOKEN,
    openai_api_key=OPENAI_API_KEY,
    model="gpt-4o",  # Uses the GPT-4o model (which supports images)
    system_message="You are a helpful assistant. Be concise and friendly in your replies.",
    max_history_length=15,  # Keep last 15 messages in conversation history
    temperature=0.7,  # Slightly more creative responses
    session_timeout=1800,  # Sessions expire after 30 minutes of inactivity
    error_message="Sorry, your message could not be processed.",  # Custom error message
)


# Custom image handler that provides enhanced instructions for images
class EnhancedImageHandler(ImageMessageHandler):
    async def process_message(self, notification, openai_client=None, model=None):
        # Call the parent class method to get the base result
        result = await super().process_message(notification, openai_client, model)

        # For text-only responses (non-vision models)
        if isinstance(result, str):
            return result.replace(
                "[The user sent an image",
                "[The user sent an image. Analyze what might be in it based on any caption"
            )

        # For vision-capable models, enhance the text instruction
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            if result[0].get('type') == 'text':
                text = result[0].get('text', '')
                if text == "Analyzing this image":
                    result[0]['text'] = "Describe this image in detail and what you see in it."

        return result


# Example of a custom text handler
class EnhancedTextHandler(TextMessageHandler):
    async def process_message(self, notification, *args, **kwargs):
        # Get the text message using the parent method
        text = await super().process_message(notification, *args, **kwargs)

        if not text:
            return text

        lower_text = text.lower()

        if any(term in lower_text for term in ['code', 'function', 'script', 'program']):
            return f"🧑‍💻 CODE REQUEST: {text}\n\n[I'll format my code response with proper syntax highlighting]"

        elif text.endswith('?') or text.lower().startswith(
                ('what', 'why', 'how', 'when', 'where', 'who', 'can', 'could')):
            return f"❓ QUESTION: {text}\n\n[I'll provide a clear and comprehensive answer]"

        elif 'translate' in lower_text or 'in spanish' in lower_text or 'in french' in lower_text:
            return f"🌐 TRANSLATION REQUEST: {text}\n\n[I'll translate this accurately with proper context]"

        elif any(greeting in lower_text.split() for greeting in ['hi', 'hello', 'hey', 'greetings']):
            return f"👋 GREETING: {text}\n\n[Responding with a friendly welcome]"

        else:
            return f"💬 MESSAGE: {text}\n\n[Enhanced text processing activated]"

# Replace the default handlers with our enhanced versions
bot.replace_handler(ImageMessageHandler, EnhancedImageHandler())
bot.replace_handler(TextMessageHandler, EnhancedTextHandler())


# Middleware to log all messages and add tracking information
def logging_middleware(notification, message_content, messages, session_data):
    user_id = notification.sender
    if isinstance(message_content, str):
        content_display = message_content[:100] + "..." if len(message_content) > 100 else message_content
    else:
        content_display = "complex content (likely contains media)"

    logger.info(f"Message from {user_id}: {content_display}")

    # Add tracking information to session context
    if not session_data.context.get("variables"):
        session_data.context["variables"] = {}

    session_data.context["variables"].update({
        "last_interaction": int(time.time()),
        "message_count": session_data.context.get("variables", {}).get("message_count", 0) + 1
    })

    # Return unchanged content and messages
    return {"message_content": message_content, "messages": messages}


# Middleware to format responses before sending to user
def formatting_middleware(response, messages, session_data):
    # Format response by adding a signature at the end of longer messages
    formatted_response = response.strip()

    # Don't add signature to short responses
    if len(formatted_response) > 100 and not formatted_response.endswith("_"):
        message_count = session_data.context.get("variables", {}).get("message_count", 0)
        formatted_response += f"\n\n_Message #{message_count} • Powered by GPT_"

    # For code blocks, make sure they're properly formatted
    # (This is redundant as OpenAI usually formats code correctly, but as an example)
    if "```" in formatted_response:
        # Make sure code blocks are properly spaced
        formatted_response = formatted_response.replace("```\n", "```\n\n")
        formatted_response = formatted_response.replace("\n```", "\n\n```")

    return {"response": formatted_response, "messages": messages}


# Add the middleware
bot.add_response_middleware(formatting_middleware)
bot.add_message_middleware(logging_middleware)


# Command handler for /clear to reset conversation history
@bot.router.message(command="clear")
def clear_history_handler(notification):
    chat_id = notification.chat

    # Get session data
    session_data = bot.get_session_data(chat_id)

    # Find system message if it exists
    system_message = None
    for msg in session_data.messages:
        if msg.get("role") == "system":
            system_message = msg
            break

    # Reset messages but keep system message
    if system_message:
        session_data.messages = [system_message]
    else:
        session_data.messages = []

    # Keep tracking variables
    context_vars = session_data.context.get("variables", {})

    # Update session
    bot.update_session_data(chat_id, session_data)

    # Restore tracking variables after update
    if "variables" not in session_data.context:
        session_data.context["variables"] = {}
    session_data.context["variables"].update(context_vars)

    notification.answer("🗑️ Conversation history cleared! Let's start fresh.")


# Command handler for /help to show available commands
@bot.router.message(command="help")
def help_handler(notification):
    help_text = (
        "🤖 *WhatsApp GPT Bot* 🤖\n\n"
        "Available commands:\n"
        "• */help* - Show this help message\n"
        "• */clear* - Clear conversation history\n"
        "• */info* - Show bot information\n"
        "• */echo* - Echo back your message with GPT assistance\n"
        "• */weather* - Example of a handler that skips GPT\n\n"
        "You can send text, images, audio, and more. I'll respond intelligently to your messages.\n\n"
        "Try asking me to:\n"
        "- Write creative content\n"
        "- Analyze images you send\n"
        "- Answer questions about any topic\n"
        "- Help with coding problems\n"
        "- Translate languages\n"
        "- Create summaries"
    )
    notification.answer(help_text)


# Add an info command
@bot.router.message(command="info")
def info_handler(notification):
    chat_id = notification.chat
    session_data = bot.get_session_data(chat_id)

    # Get session statistics
    message_count = len(session_data.messages) - 1  # Subtract system message
    if message_count < 0:
        message_count = 0

    vision_capable = "Yes" if bot.supports_images() else "No"

    info_text = (
        "📊 *Bot Information* 📊\n\n"
        f"Model: {bot.get_model()}\n"
        f"Vision capable: {vision_capable}\n"
        f"Messages in current session: {message_count}\n"
        f"Max history length: {bot.max_history_length}\n"
        f"Session timeout: {bot.session_timeout} seconds\n\n"
        "To clear the current conversation, use */clear*"
    )
    notification.answer(info_text)


# Echo handler that just forwards the message to GPT
@bot.router.message(command="echo")
def echo_handler(notification):
    # Get the rest of the message after the command
    message_text = notification.message_text
    command_parts = message_text.split(maxsplit=1)

    if len(command_parts) > 1:
        echo_text = command_parts[1]
        notification.answer(f"You said: {echo_text}\n\nI'll ask GPT for more insights...")

        # Process with GPT, but pass only the actual message (without the command)
        notification.process_with_gpt(custom_message=echo_text)
    else:
        notification.answer("Please provide text after the /echo command.")


# Example weather handler that skips GPT processing
@bot.router.message(command="weather")
def weather_handler(notification):
    notification.answer(
        "🌤️ This is a placeholder weather response from a custom handler.\n\n"
        "In a real bot, this would fetch actual weather data from an API.\n\n"
        "This handler demonstrates skipping GPT processing."
    )


# Example text message handler, which handles 'recommend' messages and adds context before GPT processing
@bot.router.message(text_message="recommend")
def recommend_handler(notification):
    # Add a prefix message
    notification.answer("I'll give you a recommendation. Let me think...")
    # Request GPT processing as well
    notification.process_with_gpt()


# Start the bot
if __name__ == "__main__":
    logger.info("Starting WhatsApp GPT Bot...")
    logger.info(f"Using model: {bot.get_model()}")
    bot.run_forever()
