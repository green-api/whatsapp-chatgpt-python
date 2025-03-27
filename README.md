# WhatsApp GPT Bot Library for Python

- [Документация на русском языке](./README.ru.md)

A modern, state-based WhatsApp bot library with OpenAI GPT integration, built on top of whatsapp-chatbot-python and
GREEN-API.

## Features

- OpenAI GPT model integration for intelligent responses
- Support for multiple GPT models (GPT-3.5, GPT-4, GPT-4o, o1)
- Multimodal capabilities with image processing support
- Voice message transcription using Whisper API
- Comprehensive message handling for various WhatsApp media types
- Middleware architecture for customizing message and response processing
- Built-in conversation history management
- State-based conversation flow inherited from base library
- Python type hints and comprehensive docstrings

## Installation

```bash
pip install whatsapp-chatgpt-python
```

The dependencies (`openai`, `whatsapp-chatbot-python`, and `requests`) will be installed automatically.

### Prerequisites

Before using the bot, you'll need:

1. A registered account with [GREEN-API](https://green-api.com/)
2. An instance ID and API token from your GREEN-API account
3. An OpenAI API key for GPT access

## Quick Start

```python
from whatsapp_chatgpt_python import WhatsappGptBot

# Initialize the bot
bot = WhatsappGptBot(
    id_instance="your-instance-id",
    api_token_instance="your-api-token",
    openai_api_key="your-openai-api-key",
    model="gpt-4o",
    system_message="You are a helpful assistant."
)

# Start the bot
bot.run_forever()
```

## Core Components

### Bot Configuration

The bot inherits all configuration options from the base `GreenAPIBot` including the ability to customize GREEN-API
instance settings.

Complete configuration options for the WhatsappGptBot:

```python
bot = WhatsappGptBot(
    # Required parameters
    id_instance="your-instance-id",
    api_token_instance="your-api-token",
    openai_api_key="your-openai-api-key",

    # Optional GPT-specific parameters
    model="gpt-4o",  # Default model
    max_history_length=10,  # Maximum messages in conversation history
    system_message="You are a helpful assistant.",  # System message to set behavior
    temperature=0.5,  # Temperature for response generation
    error_message="Sorry, I couldn't process your request. Please try again.",
    session_timeout=1800,  # Session timeout in seconds (30 minutes)

    # Optional parameters from base bot
    bot_debug_mode=False,  # Enable debug logs
    debug_mode=False,  # Enable API debug mode
    raise_errors=True,  # Whether to raise API errors
    settings={  # GREEN-API instance settings
        "webhookUrl": "",  # Custom webhook URL
        "webhookUrlToken": "",  # Webhook security token
        "delaySendMessagesMilliseconds": 500,  # Delay between messages
        "markIncomingMessagesReaded": "yes",  # Mark messages as read
        "incomingWebhook": "yes",  # Enable incoming webhooks
        "keepOnlineStatus": "yes",  # Keep WhatsApp online status
        "pollMessageWebhook": "yes",  # Enable poll message webhooks
    }
)
```

### WhatsappGptBot

Main class for creating and managing your OpenAI-powered WhatsApp bot:

```python
from whatsapp_chatgpt_python import WhatsappGptBot

bot = WhatsappGptBot(
    id_instance="your-instance-id",
    api_token_instance="your-api-token",
    openai_api_key="your-openai-api-key",
    model="gpt-4o",
    system_message="You are a helpful assistant specializing in customer support.",
    max_history_length=15,
    temperature=0.7,
    settings={
        "webhookUrl": "",
        "markIncomingMessagesReaded": "yes",
        "keepOnlineStatus": "yes",
        "delaySendMessagesMilliseconds": 500,
    }
)

# Start the bot
bot.run_forever()
```

## Message Handling

The bot automatically handles different types of WhatsApp messages and converts them into a format understood by
OpenAI's models.

### Supported Message Types

- **Text**: Regular text messages
- **Image**: Photos with optional captions (supported in vision-capable models)
- **Audio**: Voice messages with automatic transcription
- **Video**: Video messages with captions
- **Document**: File attachments
- **Poll**: Poll messages and poll updates
- **Location**: Location sharing
- **Contact**: Contact sharing

### Message Handler Registry

The bot uses a registry of message handlers to process different message types:

```python
# Access the registry
registry = bot.message_handlers


# Create a custom message handler
class CustomMessageHandler(MessageHandler):
    def can_handle(self, notification):
        return notification.get_message_type() == "custom-type"

    async def process_message(self, notification, openai_client=None, model=None):
        # Process the message
        return "Processed content"


# Register the custom handler
bot.register_message_handler(CustomMessageHandler())

# Replace an existing handler
bot.replace_handler(TextMessageHandler, CustomTextHandler())
```

## Middleware System

The middleware system allows for customizing message processing before sending to GPT and response processing before
sending back to the user.

### Adding Message Middleware

```python
# Process messages before sending to GPT
def custom_message_middleware(notification, message_content, messages, session_data):
    # Add custom context to the conversation
    if notification.get_message_type() == "textMessage" and notification.chat.endswith("@c.us"):
        # Add context to the message
        enhanced_content = f"[User message] {message_content}"

        return {
            "message_content": enhanced_content,
            "messages": messages
        }

    return {
        "message_content": message_content,
        "messages": messages
    }


# Add the middleware
bot.add_message_middleware(custom_message_middleware)
```

### Adding Response Middleware

```python
# Process GPT responses before sending to user
def custom_response_middleware(response, messages, session_data):
    # Format or modify the response
    formatted_response = response.replace("GPT", "Assistant").strip()

    # You can also modify the messages that will be saved in history
    return {
        "response": formatted_response,
        "messages": messages
    }


# Add the middleware
bot.add_response_middleware(custom_response_middleware)
```

## Session Data

The GPT bot extends the base session data with conversation-specific information:

```python
@dataclass
class GPTSessionData:
    """Session data for GPT conversations"""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    last_activity: int = field(default_factory=lambda: int(time.time()))
    user_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
```

You can access and modify this data in your middleware:

```python
def message_middleware(notification, content, messages, session_data):
    # Set context variables
    if "variables" not in session_data.context:
        session_data.context["variables"] = {}

    session_data.context["variables"]["last_interaction"] = int(time.time())

    return {"message_content": content, "messages": messages}
```

## Utilities

The library provides several utility functions for common tasks:

### Media Handling

```python
from whatsapp_chatgpt_python import Utils

# Download media from a URL
temp_file = await Utils.download_media("https://example.com/image.jpg")

# Transcribe audio
from openai import OpenAI

openai_client = OpenAI(api_key="your-openai-api-key")
transcript = await Utils.transcribe_audio("/path/to/audio.ogg", openai_client)

# Clean up after processing
import os

os.unlink(temp_file)
```

### Conversation Management

```python
from whatsapp_chatgpt_python import Utils

# Trim conversation history
trimmed_messages = Utils.trim_conversation_history(
    messages,
    10,  # max messages
    True  # preserve system message
)

# Estimate token usage
estimated_tokens = Utils.estimate_tokens(messages)
```

## Supported OpenAI Models

The library supports a variety of OpenAI models:

### GPT-4 Models

- gpt-4
- gpt-4-turbo
- gpt-4-turbo-preview
- gpt-4-1106-preview
- gpt-4-0125-preview
- gpt-4-32k

### GPT-4o Models

- gpt-4o (default)
- gpt-4o-mini
- gpt-4o-2024-05-13

### GPT-3.5 Models

- gpt-3.5-turbo
- gpt-3.5-turbo-16k
- gpt-3.5-turbo-1106
- gpt-3.5-turbo-0125

### o1 Models

- o1
- o1-mini
- o1-preview

### Image-Capable Models

The following models can process images:

- gpt-4o
- gpt-4o-mini
- gpt-4-vision-preview
- gpt-4-turbo
- gpt-4-turbo-preview

## Advanced Configuration

### Custom Command Handling

Since the library is built on whatsapp-chatbot-python, you can use all the command/filter features of the base library:

```python
@bot.router.message(command="help")
def help_handler(notification):
    help_text = (
        "🤖 *WhatsApp GPT Bot* 🤖\n\n"
        "Available commands:\n"
        "• */help* - Show this help message\n"
        "• */clear* - Clear conversation history\n"
        "• */info* - Show bot information"
    )
    notification.answer(help_text)


# Clear conversation history command
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

    # Update session
    bot.update_session_data(chat_id, session_data)

    notification.answer("🗑️ Conversation history cleared! Let's start fresh.")
```

### Bypassing GPT for Certain Commands

You can create handlers that don't process with GPT:

```python
@bot.router.message(command="weather")
def weather_handler(notification):
    notification.answer(
        "🌤️ This is a placeholder weather response from a custom handler.\n\n"
        "In a real bot, this would fetch actual weather data from an API.\n\n"
        "This handler demonstrates skipping GPT processing."
    )
```

### Explicit GPT Processing

You can explicitly request GPT processing after handling a message:

```python
@bot.router.message(text_message="recommend")
def recommend_handler(notification):
    # Add a prefix message
    notification.answer("I'll give you a recommendation. Let me think...")
    # Request GPT processing as well
    notification.process_with_gpt()
```

You can also modify the message before sending it to GPT using the `custom_message` parameter:

```python
# Echo handler that forwards a modified message to GPT
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
```

This is useful when you want to preprocess the message before it's sent to GPT, such as removing command prefixes,
formatting the input, or adding context.

### Advanced Message Processing

```python
# Check if current model supports images
if bot.supports_images():
    # Handle image-based workflow
    pass
```

## Complete Example Bot

Here's a complete example of a WhatsApp GPT bot with custom handlers and middleware:

```python
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
ID_INSTANCE = os.environ.get("INSTANCE_ID")
API_TOKEN = os.environ.get("INSTANCE_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

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

        return text


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

    return {"response": formatted_response, "messages": messages}


# Add the middleware
bot.add_message_middleware(logging_middleware)
bot.add_response_middleware(formatting_middleware)


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

    # Update session
    bot.update_session_data(chat_id, session_data)

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
        "• */weather* - Example of a handler that skips GPT\n\n"
        "You can send text, images, audio, and more. I'll respond intelligently to your messages."
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


# Example weather handler that skips GPT processing
@bot.router.message(command="weather")
def weather_handler(notification):
    notification.answer(
        "🌤️ This is a placeholder weather response from a custom handler.\n\n"
        "In a real bot, this would fetch actual weather data from an API.\n\n"
        "This handler demonstrates skipping GPT processing."
    )


# Start the bot
if __name__ == "__main__":
    logger.info("Starting WhatsApp GPT Bot...")
    logger.info(f"Using model: {bot.get_model()}")
    bot.run_forever()
```

## License

MIT

## Technologies Used

This library is built on top of:

- [whatsapp-chatbot-python](https://github.com/green-api/whatsapp-chatbot-python) - The base WhatsApp bot library
- [GREEN-API](https://green-api.com/) - WhatsApp API service for bot integration
- [OpenAI API](https://openai.com/) - For GPT model integration
