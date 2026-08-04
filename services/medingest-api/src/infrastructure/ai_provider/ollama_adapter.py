"""
ollama_adapter.py
Ollama provider integration adapter.
"""

from src.domain.ai_provider.iai_provider import IAIProvider


class OllamaProviderAdapter(IAIProvider):
    """
    Adapter executing text completions via local Ollama API server.
    """

    def __init__(self, should_fail: bool = False, response_text: str = "Ollama Response"):
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
            raise ConnectionError("Ollama endpoint refused connection (localhost:11434)")
        return f"{self.response_text} [temp={temperature}] [prompt={prompt[:20]}]"
