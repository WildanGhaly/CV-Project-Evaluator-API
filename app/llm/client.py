from app.config import settings

# Placeholder for future real LLM calls via OpenAI SDK
# Implemented later: deterministic baseline makes the app run without secrets.

class LLMClient:
    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.enabled = bool(self.api_key)

    def available(self) -> bool:
        return self.enabled

    def eval_json(self, prompt: str, system: str = "") -> dict:
        """Return JSON from the model. (Not used in v1 baseline)"""
        raise NotImplementedError