"""
iai_provider.py
Domain interface (port) defining AI provider abstraction.
"""

from abc import ABC, abstractmethod


class IAIProvider(ABC):
    """
    Abstractions for AI models (Ollama, vLLM, OpenAI, llama.cpp, LiteLLM, OpenRouter).
    
    Business Context:
        Decouples OCR text extraction pipelines from any specific LLM provider API.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        timeout_seconds: int = 30
    ) -> str:
        """
        Executes text generation request against target LLM backend.
        """
        pass
