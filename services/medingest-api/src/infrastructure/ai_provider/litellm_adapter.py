"""
litellm_adapter.py
LiteLLM provider integration adapter.
"""

from src.domain.ai_provider.iai_provider import IAIProvider


class LiteLLMProviderAdapter(IAIProvider):
    """
    Adapter executing text completions via LiteLLM proxy server router.
    """

    def __init__(self, should_fail: bool = False, response_text: str = "LiteLLM Response"):
        self.should_fail = should_fail
        self.response_text = response_text

    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        timeout_seconds: int = 30
    ) -> str:
        if self.should_fail:
            raise ConnectionError("LiteLLM router failed to resolve backend model")
        return f"{self.response_text} [temp={temperature}] [prompt={prompt[:20]}]"
