"""
Media handling utilities
"""

import os
import tempfile
import requests


async def download_media(url: str) -> str:
    """
    Download media from URL to a temporary file

    Args:
        url: URL to download from

    Returns:
        Path to the downloaded file

    Raises:
        Exception: If download fails
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download: {response.status_code}")

    fd, temp_path = tempfile.mkstemp(suffix=".tmp")
    with os.fdopen(fd, 'wb') as f:
        f.write(response.content)

    return temp_path


async def transcribe_audio(file_path: str, openai_client) -> str:
    """
    Transcribe audio using OpenAI Whisper API

    Args:
        file_path: Path to the audio file
        openai_client: OpenAI client instance

    Returns:
        Transcribed text

    Raises:
        Exception: If transcription fails
    """
    with open(file_path, "rb") as audio_file:
        transcription = openai_client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1"
        )

    return transcription.text
