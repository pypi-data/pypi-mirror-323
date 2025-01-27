import json
import os
import httpx
from jay_ai.cli_types import (
    STT,
    TTS,
    VAD,
    STTProvider,
    SessionConfig,
    TTSProvider,
    VADProvider,
)
from jay_ai.utils import fetch_site_url, fetch_headers


async def generate_token(session_config: SessionConfig, agent_api_url: str) -> str:
    # Convert to dict so we can remove fields easily
    tts_kwargs_dict = session_config.tts.model_dump()
    tts_provider = None
    tts_credentials = None

    if isinstance(session_config.tts, TTS.ElevenLabs):
        tts_provider = TTSProvider.ELEVENLABS.value.label
        # ElevenLabs uses `api_key`
        tts_credentials = tts_kwargs_dict["api_key"]
        del tts_kwargs_dict["api_key"]
    elif isinstance(session_config.tts, TTS.OpenAI):
        tts_provider = TTSProvider.OPENAI.value.label
        # OpenAI uses `api_key`
        tts_credentials = tts_kwargs_dict["api_key"]
        del tts_kwargs_dict["api_key"]
    elif isinstance(session_config.tts, TTS.Google):
        tts_provider = TTSProvider.GOOGLE.value.label
        # Google uses `credentials` (dict) -> JSON string
        creds_dict = tts_kwargs_dict["credentials"]
        tts_credentials = json.dumps(creds_dict)
        del tts_kwargs_dict["credentials"]
    elif isinstance(session_config.tts, TTS.Azure):
        tts_provider = TTSProvider.AZURE.value.label
        # Azure uses `api_key`
        tts_credentials = tts_kwargs_dict["api_key"]
        del tts_kwargs_dict["api_key"]
    elif isinstance(session_config.tts, TTS.Deepgram):
        tts_provider = TTSProvider.DEEPGRAM.value.label
        # Deepgram TTS also uses `api_key`
        tts_credentials = tts_kwargs_dict["api_key"]
        del tts_kwargs_dict["api_key"]
    elif isinstance(session_config.tts, TTS.Cartesia):
        tts_provider = TTSProvider.CARTESIA.value.label
        # Cartesia uses `api_key`
        tts_credentials = tts_kwargs_dict["api_key"]
        del tts_kwargs_dict["api_key"]
    else:
        raise Exception(f"Unknown TTS provider: {session_config.tts}")

    # Convert back to JSON (for the payload)
    tts_kwargs = json.dumps(tts_kwargs_dict)

    # Do the same for STT
    stt_kwargs_dict = session_config.stt.model_dump()
    stt_provider = None
    stt_credentials = None

    if isinstance(session_config.stt, STT.OpenAI):
        stt_provider = STTProvider.OPENAI.value.label
        stt_credentials = stt_kwargs_dict["api_key"]
        del stt_kwargs_dict["api_key"]
    elif isinstance(session_config.stt, STT.Azure):
        stt_provider = STTProvider.AZURE.value.label
        stt_credentials = stt_kwargs_dict["api_key"]
        del stt_kwargs_dict["api_key"]
    elif isinstance(session_config.stt, STT.Deepgram):
        stt_provider = STTProvider.DEEPGRAM.value.label
        stt_credentials = stt_kwargs_dict["api_key"]
        del stt_kwargs_dict["api_key"]
    else:
        raise Exception(f"Unknown STT provider: {session_config.stt}")

    stt_kwargs = json.dumps(stt_kwargs_dict)

    # VAD
    vad_kwargs = session_config.vad.model_dump_json()
    vad_provider = None
    if isinstance(session_config.vad, VAD.Silero):
        vad_provider = VADProvider.SILERO.value.label
    else:
        raise Exception(f"Unknown VAD provider: {session_config.vad}")

    payload = {
        "messages": session_config.initial_messages,
        "tts_provider": tts_provider,
        "tts_kwargs": tts_kwargs,
        "tts_credentials": tts_credentials,
        "stt_provider": stt_provider,
        "stt_kwargs": stt_kwargs,
        "stt_credentials": stt_credentials,
        "vad_provider": vad_provider,
        "vad_kwargs": vad_kwargs,
        "session_data": session_config.session_data,
        "first_message": session_config.first_message,
        "allow_interruptions": session_config.allow_interruptions,
        "interrupt_time_threshold": session_config.interrupt_time_threshold,
        "interrupt_word_threshold": session_config.interrupt_word_threshold,
        "min_endpointing_delay": session_config.min_endpointing_delay,
        "max_nested_function_calls": session_config.max_nested_function_calls,
        "agent_api_url": agent_api_url,
    }
    endpoint = f"{fetch_site_url()}/api/generateToken"
    headers = fetch_headers(os.getenv("JAY_INTERNAL__AGENT_API_KEY"))

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                endpoint, json=payload, timeout=30.0, headers=headers
            )
            response.raise_for_status()
            response_json = response.json()
            token = response_json.get("token")
            if not token:
                raise ValueError(
                    "Token not found in the response from jay API. This should never happen."
                )

            return token

        except httpx.HTTPStatusError as http_err:
            raise Exception(
                f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.text}"
            ) from http_err

        except httpx.RequestError as req_err:
            raise Exception(f"Request error occurred: {req_err}") from req_err

        except ValueError as val_err:
            raise Exception(f"Value error: {val_err}") from val_err
