# underlying language model 


from dataclasses import dataclass 


@dataclass
class LLMConfig:
    model_id: str
    temperature: float = 0.2


class LLM:
    def __init__(self, config: LLMConfig):
        self.config = config 

    def get_language_model() -> LiteLLMModel:
        # get the underlying LiteLLMModel wrapper; only OpenAI support is sufficient for now
        pass

