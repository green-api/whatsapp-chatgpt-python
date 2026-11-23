"""
Voice calls with an OpenAI Realtime model
"""
import asyncio
import importlib.util
import logging
import sys
import threading
from dataclasses import dataclass, field
from time import monotonic, time
from typing import Optional

from .config import (
    DEFAULT_ANSWER_SECONDS,
    DEFAULT_MAX_CALL_SECONDS,
    DEFAULT_REALTIME_MODEL,
    DEFAULT_REALTIME_VOICE,
    DEFAULT_RING_SECONDS,
    DEFAULT_VAD_NOISE_REDUCTION,
    DEFAULT_VAD_PREFIX_PADDING_MS,
    DEFAULT_VAD_SILENCE_DURATION_MS,
    DEFAULT_VAD_THRESHOLD,
    DEFAULT_VOICE_GREETING,
    VOICE_CALL_LANGUAGE,
    VOICE_MISSING_DEPENDENCIES,
    VOICE_THREAD_NAME,
)

logger = logging.getLogger('whatsapp_chatgpt_python')


@dataclass
class VoiceActivityConfig:
    """
    Detection of the caller's speech

    Attributes:
        threshold: Speech threshold from 0 to 1, higher needs louder speech
        prefix_padding_ms: Audio kept before the detected speech, in milliseconds
        silence_duration_ms: Silence that ends the caller's turn, in milliseconds
        noise_reduction: Noise reduction of the caller's audio: near_field, far_field or None
    """
    threshold: float = DEFAULT_VAD_THRESHOLD
    prefix_padding_ms: int = DEFAULT_VAD_PREFIX_PADDING_MS
    silence_duration_ms: int = DEFAULT_VAD_SILENCE_DURATION_MS
    noise_reduction: Optional[str] = DEFAULT_VAD_NOISE_REDUCTION


@dataclass
class VoiceCallsConfig:
    """
    Voice calls handled by an OpenAI Realtime model

    Attributes:
        model: Realtime model
        voice: Voice of the model, for example marin, cedar, alloy, ash, coral, sage, shimmer, verse
        instructions: Instructions for the voice conversation, the bot's system_message by default
        greeting: What the model is asked to say first when the call connects
        answer_incoming: Whether to answer incoming calls with the model
        max_call_seconds: Longest conversation in seconds, the bot hangs up after it
        ring_seconds: How long an outgoing call rings before the bot gives up
        vad: Detection of the caller's speech
    """
    model: str = DEFAULT_REALTIME_MODEL
    voice: str = DEFAULT_REALTIME_VOICE
    instructions: Optional[str] = None
    greeting: str = DEFAULT_VOICE_GREETING
    answer_incoming: bool = True
    max_call_seconds: float = DEFAULT_MAX_CALL_SECONDS
    ring_seconds: float = DEFAULT_RING_SECONDS
    vad: VoiceActivityConfig = field(default_factory=VoiceActivityConfig)


class VoiceCalls:
    """
    Runs one voice call at a time on its own thread, so the bot keeps handling messages during a call.
    The call itself is run by the calls engine of whatsapp-chatbot-python.
    """

    def __init__(
            self,
            api_url: str,
            id_instance: str,
            api_token_instance: str,
            openai_api_key: str,
            config: VoiceCallsConfig,
            instructions: Optional[str],
    ):
        if sys.version_info < (3, 11) or importlib.util.find_spec("aiortc") is None:
            raise RuntimeError(VOICE_MISSING_DEPENDENCIES)

        from whatsapp_chatbot_python.calls import (
            CallOptions,
            CallStateMachine,
            RecordingOptions,
            VadOptions,
            WhatsAppCallService,
        )

        self._config = config
        self._service = WhatsAppCallService(
            api_url=api_url,
            id_instance=id_instance,
            api_token_instance=api_token_instance,
            openai_api_key=openai_api_key,
            realtime_model=config.model,
            realtime_voice=config.voice,
            instructions=config.instructions or instructions or None,
            options=CallOptions(
                ring_seconds=config.ring_seconds,
                talk_seconds=config.max_call_seconds,
                recording=RecordingOptions(enabled=False),
                vad=VadOptions(
                    threshold=config.vad.threshold,
                    prefix_padding_ms=config.vad.prefix_padding_ms,
                    silence_duration_ms=config.vad.silence_duration_ms,
                    noise_reduction=config.vad.noise_reduction,
                ),
            ),
        )
        self._fsm = CallStateMachine()
        self._lock = threading.Lock()
        self._session = None
        self._loop = asyncio.new_event_loop()
        threading.Thread(target=self._loop.run_forever, name=VOICE_THREAD_NAME, daemon=True).start()

    @property
    def busy(self) -> bool:
        """Whether a voice call is running now"""
        return self._session is not None

    def call(self, chat_id: str) -> None:
        """Calls a chat and talks with the person through the model when they answer"""
        from whatsapp_chatbot_python.calls import CallSession

        self._start(CallSession(chat_id, chat_id, VOICE_CALL_LANGUAGE, prompt=self._config.greeting))

    def answer(self, sender: str, call_id: str, timestamp: Optional[float]) -> bool:
        """Answers an incoming call that is still ringing"""
        from whatsapp_chatbot_python.calls import CallSession

        remaining = DEFAULT_ANSWER_SECONDS - max(0.0, time() - (timestamp or time()))
        if remaining <= 0:
            return False

        self._start(CallSession.incoming(
            sender_id=sender,
            call_id=call_id,
            language=VOICE_CALL_LANGUAGE,
            incoming_deadline=monotonic() + remaining,
            prompt=self._config.greeting,
        ))
        return True

    def caller_left(self, call_id: str) -> None:
        """Tells the running call that the caller hung up before the call was answered"""
        self._loop.call_soon_threadsafe(self._service.notify_incoming_ended, call_id)

    def stop(self) -> None:
        """Ends the running call and stops taking new ones"""
        self._loop.call_soon_threadsafe(self._service.request_stop)

    def _start(self, session) -> None:
        from whatsapp_chatbot_python.calls import CallEvent

        with self._lock:
            if self._session is not None:
                raise RuntimeError("A voice call is already running")
            self._session = session

        self._fsm.apply(session, CallEvent.ENQUEUED)
        self._fsm.apply(session, CallEvent.DEQUEUED)
        asyncio.run_coroutine_threadsafe(self._run(session), self._loop)

    async def _run(self, session) -> None:
        try:
            result = await self._service.execute(session, self._fsm.apply)
            with result:
                logger.info(
                    f"Voice call with {session.chat_id} ended: {session.state.value}"
                    + (f" ({session.error_code})" if session.error_code else "")
                )
        except Exception as e:
            logger.error(f"Voice call failed: {e}", exc_info=True)
        finally:
            with self._lock:
                self._session = None
