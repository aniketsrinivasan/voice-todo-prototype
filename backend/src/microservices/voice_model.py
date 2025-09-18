from __future__ import annotations

import time
from dataclasses import dataclass
from io import BytesIO
from typing import Optional


@dataclass
class VoiceModelConfig:
    model_id: str = "whisper-1"


@dataclass
class VoiceReturnFormat:
    transcription: str
    time: float
    model_config: VoiceModelConfig


class VoiceModel:
    """
    Speech-to-text transcription using OpenAI Whisper.
    """

    def __init__(self, config: VoiceModelConfig):
        self.config = config

    def transcribe(self, file_bytes: bytes, mime: str) -> VoiceReturnFormat:
        """
        Transcribe audio bytes into text.

        Args:
            file_bytes: Raw audio bytes.
            mime: MIME type, e.g. audio/mpeg.

        Returns:
            VoiceReturnFormat with transcription and timing info.
        """

        started = time.time()

        try:
            from openai import OpenAI  # type: ignore
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("openai package is required for transcription") from exc

        client = OpenAI()
        file_like = BytesIO(file_bytes)
        file_like.name = f"audio.{mime.split('/')[-1]}"

        result = client.audio.transcriptions.create(
            model=self.config.model_id,
            file=file_like,  # type: ignore[arg-type]
            response_format="text",
        )

        text: str = str(result)
        return VoiceReturnFormat(transcription=text, time=started, model_config=self.config)

