from enum import Enum
from typing import Dict, List, Any, Literal, Optional, Tuple, Union
from typing_extensions import TypedDict
from pydantic import BaseModel
from typing import List
from jay_ai.plugins import azure, elevenlabs, openai, google, cartesia, deepgram


class ProviderEnvVarKey(BaseModel):
    env_var_key: str
    is_json: bool


class ProviderInfo(BaseModel):
    label: str
    display_label: str
    injection: str | None
    env_var_keys: list[ProviderEnvVarKey]


class TTSProvider(Enum):
    ELEVENLABS = ProviderInfo(
        display_label="ElevenLabs",
        label="elevenlabs",
        injection='TTS.ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])',
        env_var_keys=[
            ProviderEnvVarKey(env_var_key="ELEVENLABS_API_KEY", is_json=False)
        ],
    )
    GOOGLE = ProviderInfo(
        display_label="Google",
        label="google",
        injection='TTS.Google(credentials=json.loads(os.environ["GOOGLE_CREDENTIALS"]))',
        env_var_keys=[
            ProviderEnvVarKey(env_var_key="GOOGLE_CREDENTIALS", is_json=True)
        ],
    )
    OPENAI = ProviderInfo(
        display_label="OpenAI",
        label="openai",
        injection='TTS.OpenAI(api_key=os.environ["OPENAI_API_KEY"])',
        env_var_keys=[ProviderEnvVarKey(env_var_key="OPENAI_API_KEY", is_json=False)],
    )
    AZURE = ProviderInfo(
        display_label="Azure",
        label="azure",
        injection='TTS.Azure(api_key=os.environ["AZURE_API_KEY"], region=os.environ["AZURE_REGION"])',
        env_var_keys=[
            ProviderEnvVarKey(env_var_key="AZURE_API_KEY", is_json=False),
            ProviderEnvVarKey(env_var_key="AZURE_REGION", is_json=False),
        ],
    )
    CARTESIA = ProviderInfo(
        display_label="Cartesia",
        label="cartesia",
        injection='TTS.Cartesia(api_key=os.environ["CARTESIA_API_KEY"])',
        env_var_keys=[ProviderEnvVarKey(env_var_key="CARTESIA_API_KEY", is_json=False)],
    )
    DEEPGRAM = ProviderInfo(
        display_label="Deepgram",
        label="deepgram",
        injection='TTS.Deepgram(api_key=os.environ["DEEPGRAM_API_KEY"])',
        env_var_keys=[ProviderEnvVarKey(env_var_key="DEEPGRAM_API_KEY", is_json=False)],
    )


class STTProvider(Enum):
    DEEPGRAM = ProviderInfo(
        display_label="Deepgram",
        label="deepgram",
        injection='STT.Deepgram(api_key=os.environ["DEEPGRAM_API_KEY"])',
        env_var_keys=[ProviderEnvVarKey(env_var_key="DEEPGRAM_API_KEY", is_json=False)],
    )
    OPENAI = ProviderInfo(
        display_label="OpenAI",
        label="openai",
        injection='STT.OpenAI(api_key=os.environ["OPENAI_API_KEY"])',
        env_var_keys=[ProviderEnvVarKey(env_var_key="OPENAI_API_KEY", is_json=False)],
    )
    AZURE = ProviderInfo(
        display_label="Azure",
        label="azure",
        injection='STT.Azure(api_key=os.environ["AZURE_API_KEY"], region=os.environ["AZURE_REGION"])',
        env_var_keys=[
            ProviderEnvVarKey(env_var_key="AZURE_API_KEY", is_json=False),
            ProviderEnvVarKey(env_var_key="AZURE_REGION", is_json=False),
        ],
    )


class VADProvider(Enum):
    SILERO = ProviderInfo(
        display_label="Silero", label="silero", injection=None, env_var_keys=[]
    )


class LLMProvider(Enum):
    OPENAI = ProviderInfo(
        display_label="OpenAI",
        label="openai",
        injection='AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])',
        env_var_keys=[ProviderEnvVarKey(env_var_key="OPENAI_API_KEY", is_json=False)],
    )
    OPENAI_COMPATIBLE = ProviderInfo(
        display_label="OpenAI Compatible",
        label="openai_compatible",
        injection='AsyncOpenAI(api_key=os.environ["OPENAI_COMPATIBLE_API_KEY"])',
        env_var_keys=[
            ProviderEnvVarKey(env_var_key="OPENAI_COMPATIBLE_API_KEY", is_json=False)
        ],
    )


class Message(TypedDict):
    content: str
    role: Literal["system", "user", "assistant", "tool"]
    name: str | None = None
    tool_call_id: str | None = None


class TTS:
    class ElevenLabs(BaseModel):
        api_key: str
        voice: elevenlabs.Voice = elevenlabs.DEFAULT_VOICE
        model: elevenlabs.TTSModels | str = "eleven_turbo_v2_5"
        encoding: elevenlabs.TTSEncoding = "mp3_22050_32"
        enable_ssml_parsing: bool = False
        chunk_length_schedule: list[int] = [80, 120, 200, 260]  # range is [50, 500]

    class OpenAI(BaseModel):
        api_key: str
        model: openai.TTSModels | str = "tts-1"
        voice: openai.TTSVoices | str = "alloy"
        speed: float = 1.0

    class Google(BaseModel):
        credentials: dict
        language: google.SpeechLanguages | str = "en-US"
        gender: google.Gender | str = "neutral"
        voice_name: str = ""  # Not required
        encoding: google.AudioEncoding | str = "linear16"
        sample_rate: int = 24000
        pitch: int = 0
        effects_profile_id: str = ""
        speaking_rate: float = 1.0

    class Azure(BaseModel):
        api_key: str
        region: str
        sample_rate: int = 24000
        voice: str | None = None
        language: str | None = None
        prosody: azure.ProsodyConfig | None = None
        endpoint_id: str | None = None

    class Deepgram(BaseModel):
        api_key: str
        model: str = "aura-asteria-en"
        encoding: str = "linear16"
        sample_rate: int = 24000

    class Cartesia(BaseModel):
        api_key: str
        model: cartesia.TTSModels | str = "sonic-english"
        language: cartesia.TTSLanguages | str = "en"
        encoding: cartesia.TTSEncoding = "pcm_s16le"
        voice: str | list[float] = cartesia.TTSDefaultVoiceId
        speed: cartesia.TTSVoiceSpeed | float | None = None
        emotion: list[cartesia.TTSVoiceEmotion | str] | None = None
        sample_rate: int = 24000


class STT:
    class Deepgram(BaseModel):
        api_key: str
        model: deepgram.DeepgramModels = "nova-2-general"
        language: deepgram.DeepgramLanguages = "en-US"
        interim_results: bool = True
        punctuate: bool = True
        smart_format: bool = True
        sample_rate: int = 16000
        no_delay: bool = True
        endpointing_ms: int = 25
        # enable filler words by default to improve turn detector accuracy
        filler_words: bool = True
        keywords: list[Tuple[str, float]] = []
        profanity_filter: bool = False

    class Azure(BaseModel):
        api_key: str
        region: str
        sample_rate: int = 16000
        num_channels: int = 1
        # Azure handles multiple languages and can auto-detect the language used. It requires the candidate set to be set.
        languages: list[str] = ["en-US"]

    class OpenAI(BaseModel):
        api_key: str
        language: str = "en"
        model: openai.WhisperModels | str = "whisper-1"


class VAD:
    class Silero(BaseModel):
        min_speech_duration: float = 0.05
        min_silence_duration: float = 0.55
        prefix_padding_duration: float = 0.5
        max_buffered_speech: float = 60.0
        activation_threshold: float = 0.5
        sample_rate: Literal[8000, 16000] = 16000


class SessionConfig(BaseModel):
    initial_messages: List[Message]
    vad: VAD.Silero
    stt: Union[STT.OpenAI, STT.Azure, STT.Deepgram]
    tts: Union[
        TTS.OpenAI,
        TTS.ElevenLabs,
        TTS.Google,
        TTS.Azure,
        TTS.Deepgram,
        TTS.Cartesia,
    ]
    session_data: dict[str, Any] = {}
    first_message: str | None = None
    allow_interruptions: bool = True
    interrupt_time_threshold: float = 0.5
    interrupt_word_threshold: int = 0
    min_endpointing_delay: float = 0.5
    max_nested_function_calls: int = 1


class Function(TypedDict):
    arguments: str
    name: Optional[str]


class FunctionCallInput(TypedDict):
    id: str
    function: Function
    type: Literal["function"]


class FunctionCallResult(TypedDict):
    content: str
    role: Literal["tool"]
    function: Function
    tool_call_id: str


class ConfigureSessionInput(TypedDict):
    custom_data: dict


class LLMResponseToolCall(TypedDict):
    index: int
    id: Optional[str]
    type: Optional[str]
    function: Optional[Function]


class LLMResponseDelta(TypedDict):
    role: Optional[str]
    content: Optional[str]
    tool_calls: Optional[List[LLMResponseToolCall]]


class LLMResponseHandlerInput(TypedDict):
    messages: List[Message]
    session_data: dict[str, Any]


class LLMResponseChoiceItem(TypedDict):
    index: int
    delta: LLMResponseDelta
    finish_reason: Optional[str]


class LLMResponseUsage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMResponse(TypedDict):
    id: str
    object: Literal["chat.completion.chunk"]
    created: int
    model: str
    choices: List[LLMResponseChoiceItem]
    usage: Optional[LLMResponseUsage]


class OnUserStartedSpeakingInput(TypedDict):
    session_data: dict[str, Any]


class OnUserStoppedSpeakingInput(TypedDict):
    session_data: dict[str, Any]


class OnAgentStartedSpeakingInput(TypedDict):
    session_data: dict[str, Any]


class OnAgentStoppedSpeakingInput(TypedDict):
    session_data: dict[str, Any]


class OnUserMessageAddedInput(TypedDict):
    message: Message
    session_data: dict[str, Any]


class OnAgentMessageAddedInput(TypedDict):
    message: Message
    session_data: dict[str, Any]


class OnAgentInterruptedInput(TypedDict):
    message: Message
    session_data: dict[str, Any]


class OnFunctionCallsCollectedInput(TypedDict):
    function_calls: List[FunctionCallInput]
    session_data: dict[str, Any]


class OnFunctionCallsExecutedInput(TypedDict):
    results: List[FunctionCallResult]
    session_data: dict[str, Any]


class LLMResponseHandlerPayload(BaseModel):
    session_data: dict[str, Any]
    messages: List[Dict[str, Any]]


class ConfigureSessionPayload(BaseModel):
    custom_data: dict[str, Any]
    agent_api_url: str


class OnUserStartedSpeakingPayload(BaseModel):
    session_data: dict[str, Any]


class OnUserStoppedSpeakingPayload(BaseModel):
    session_data: dict[str, Any]


class OnAgentStartedSpeakingPayload(BaseModel):
    session_data: dict[str, Any]


class OnAgentStoppedSpeakingPayload(BaseModel):
    session_data: dict[str, Any]


class OnUserMessageAddedPayload(BaseModel):
    session_data: dict[str, Any]
    message: Message


class OnAgentMessageAddedPayload(BaseModel):
    session_data: dict[str, Any]
    message: Message


class OnAgentInterruptedPayload(BaseModel):
    session_data: dict[str, Any]
    message: Message


class OnFunctionCallsCollectedPayload(BaseModel):
    session_data: dict[str, Any]
    function_calls: List[FunctionCallInput]


class OnFunctionCallsExecutedPayload(BaseModel):
    session_data: dict[str, Any]
    results: List[FunctionCallResult]


class ToolCallPayload(BaseModel):
    function_arguments: dict[str, Any]
