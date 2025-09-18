# use OpenAI whisper for STT model (transcription)

from dataclasses import dataclass 


@dataclass 
class VoiceModelConfig:
    pass


@dataclass
class VoiceReturnFormat:
    transcription: str 
    time = None  # unix timestamp for the request
    model_config: VoiceModelConfig = None  # VoiceModelConfig used to generate transcription


class VoiceModel:
    def __init__(self, config: VoiceModelConfig):
        self.config = config 

    def transcribe(...) -> VoiceReturnFormat:
        # generate transcription and return 
        pass
