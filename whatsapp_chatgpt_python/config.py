"""
Configuration and constants
"""

DEFAULT_MODEL = "gpt-4o"

GPT4_MODELS = [
    "gpt-4", "gpt-4-turbo", "gpt-4-turbo-preview",
    "gpt-4-1106-preview", "gpt-4-0125-preview", "gpt-4-32k"
]

GPT4O_MODELS = [
    "gpt-4o", "gpt-4o-mini", "gpt-4o-2024-05-13"
]

GPT35_MODELS = [
    "gpt-3.5-turbo", "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125"
]

O1_MODELS = [
    "o1", "o1-mini", "o1-preview"
]

IMAGE_CAPABLE_MODELS = [
    "gpt-4o", "gpt-4o-mini", "gpt-4-vision-preview",
    "gpt-4-turbo", "gpt-4-turbo-preview"
]

ALL_MODELS = GPT4_MODELS + GPT4O_MODELS + GPT35_MODELS + O1_MODELS

DEFAULT_REALTIME_MODEL = "gpt-realtime-2.1"
DEFAULT_REALTIME_VOICE = "marin"
DEFAULT_VOICE_GREETING = "Greet the caller briefly."
DEFAULT_MAX_CALL_SECONDS = 600
DEFAULT_RING_SECONDS = 60
DEFAULT_ANSWER_SECONDS = 60
DEFAULT_VAD_THRESHOLD = 0.5
DEFAULT_VAD_PREFIX_PADDING_MS = 400
DEFAULT_VAD_SILENCE_DURATION_MS = 800
DEFAULT_VAD_NOISE_REDUCTION = "near_field"
VOICE_CALL_LANGUAGE = "adaptive"
VOICE_THREAD_NAME = "voice-calls"
INCOMING_CALL_OFFER = "offer"
INCOMING_CALL_END_STATUSES = ("declined", "missed", "hungUp", "hangUp")
VOICE_MISSING_DEPENDENCIES = (
    "Voice calls need Python 3.11 or newer and the optional dependencies, install them with: "
    "pip install 'whatsapp-chatgpt-python[voice]'"
)


def is_image_capable_model(model: str) -> bool:
    return model in IMAGE_CAPABLE_MODELS
