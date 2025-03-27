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

def is_image_capable_model(model: str) -> bool:
    return model in IMAGE_CAPABLE_MODELS
