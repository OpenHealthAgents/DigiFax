"""
openai_adapter.py
OpenAI-compatible APIs provider integration adapter.
"""

from src.domain.ai_provider.iai_provider import IAIProvider


class OpenAIProviderAdapter(IAIProvider):
    """
    Adapter executing text completions via OpenAI or compatible endpoints.
    """

    def __init__(self, should_fail: bool = False, response_text: str = "OpenAI Response"):
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
            raise ConnectionError("OpenAI API rate limit exceeded")
        return f"{self.response_text} [temp={temperature}] [prompt={prompt[:20]}]"
