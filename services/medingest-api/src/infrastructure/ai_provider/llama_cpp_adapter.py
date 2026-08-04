"""
llama_cpp_adapter.py
llama.cpp provider integration adapter.
"""

from src.domain.ai_provider.iai_provider import IAIProvider


class LlamaCppProviderAdapter(IAIProvider):
    """
    Adapter executing text completions via llama.cpp server.
    """

    def __init__(self, should_fail: bool = False, response_text: str = "llama.cpp Response"):
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
            raise ConnectionError("llama.cpp socket timeout")
        return f"{self.response_text} [temp={temperature}] [prompt={prompt[:20]}]"
