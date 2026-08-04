"""
value_objects.py
Domain Value Objects representing AI provider options and model parameters.
"""

from dataclasses import dataclass, field
from typing import Any
from src.domain.common.value_object import ValueObject


@dataclass(frozen=True)
class ModelParameters(ValueObject):
    """Immutable model hyperparameter selections."""
    temperature: float
    max_tokens: int
    timeout_seconds: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        if self.max_tokens < 1:
            raise ValueError("Max tokens must be at least 1")
        if self.timeout_seconds < 1:
            raise ValueError("Timeout must be at least 1 second")


@dataclass(frozen=True)
class RetryStrategy(ValueObject):
    """Immutable retry strategy configuration."""
    max_retries: int
    backoff_factor: float

    def __post_init__(self) -> None:
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")
        if self.backoff_factor <= 0.0:
            raise ValueError("Backoff factor must be positive")


@dataclass(frozen=True)
class PromptTemplates(ValueObject):
    """Immutable prompt template mapping."""
    templates: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Prompt layouts validations
        for k, v in self.templates.items():
            if not k.strip():
                raise ValueError("Prompt template key cannot be empty")


@dataclass(frozen=True)
class Thresholds(ValueObject):
    """Immutable confidence parameters mapping review gates."""
    confidence_threshold: float
    human_review_threshold: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
        if not 0.0 <= self.human_review_threshold <= 1.0:
            raise ValueError("Human review threshold must be between 0.0 and 1.0")


@dataclass(frozen=True)
class ProviderConfig(ValueObject):
    """Immutable provider-specific settings."""
    provider_name: str  # Ollama, vLLM, llama.cpp, OpenAI, LiteLLM, OpenRouter
    model_name: str
    api_base_url: str | None = None
    api_key_obfuscated: str | None = None
    priority: int = 1

    def __post_init__(self) -> None:
        if not self.provider_name.strip():
            raise ValueError("Provider name cannot be empty")
        if not self.model_name.strip():
            raise ValueError("Model name cannot be empty")
        if self.priority < 1:
            raise ValueError("Priority must be at least 1")
