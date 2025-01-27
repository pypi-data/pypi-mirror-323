from typing import Union, Optional
from pydantic import BaseModel, model_validator, root_validator
from typing_extensions import Literal

class ProsodyConfig(BaseModel):
    """
    Prosody configuration for Azure TTS.

    Args:
        rate: Speaking rate. Can be one of "x-slow", "slow", "medium", "fast", "x-fast", or a float. A float value of 1.0 represents normal speed.
        volume: Speaking volume. Can be one of "silent", "x-soft", "soft", "medium", "loud", "x-loud", or a float. A float value of 100 (x-loud) represents the highest volume and it's the default pitch.
        pitch: Speaking pitch. Can be one of "x-low", "low", "medium", "high", "x-high". The default pitch is "medium".
    """

    rate: Literal["x-slow", "slow", "medium", "fast", "x-fast"] | float | None = None
    volume: (
        Literal["silent", "x-soft", "soft", "medium", "loud", "x-loud"] | float | None
    ) = None
    pitch: Literal["x-low", "low", "medium", "high", "x-high"] | None = None


    @model_validator(mode="after")
    def validate_prosody(cls, instance: "ProsodyConfig") -> "ProsodyConfig":
        if instance.rate:
            if isinstance(instance.rate, float) and not 0.5 <= instance.rate <= 2:
                raise ValueError("Prosody rate must be between 0.5 and 2")
            if isinstance(instance.rate, str) and instance.rate not in [
                "x-slow",
                "slow",
                "medium",
                "fast",
                "x-fast",
            ]:
                raise ValueError(
                    "Prosody rate must be one of 'x-slow', 'slow', 'medium', 'fast', 'x-fast'"
                )
        if instance.volume:
            if isinstance(instance.volume, float) and not 0 <= instance.volume <= 100:
                raise ValueError("Prosody volume must be between 0 and 100")
            if isinstance(instance.volume, str) and instance.volume not in [
                "silent",
                "x-soft",
                "soft",
                "medium",
                "loud",
                "x-loud",
            ]:
                raise ValueError(
                    "Prosody volume must be one of 'silent', 'x-soft', 'soft', 'medium', 'loud', 'x-loud'"
                )

        if instance.pitch and instance.pitch not in [
            "x-low",
            "low",
            "medium",
            "high",
            "x-high",
        ]:
            raise ValueError(
                "Prosody pitch must be one of 'x-low', 'low', 'medium', 'high', 'x-high'"
            )

        return instance
