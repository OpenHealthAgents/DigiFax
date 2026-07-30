"""
test_ai_provider.py
Unit tests verifying AI Provider Management tactical objects, routing, retries, and fallback behaviors.
"""

import pytest

from src.domain.ai_provider.entities import TenantAIProviderConfiguration
from src.domain.ai_provider.value_objects import (
    ModelParameters,
    RetryStrategy,
    PromptTemplates,
    Thresholds,
    ProviderConfig
)
from src.domain.ai_provider.domain_services import TenantAIRoutingService
from src.application.use_cases.ai_provider.configure_ai_settings import ConfigureAISettingsUseCase
from src.application.use_cases.ai_provider.generate_text_extraction import GenerateTextExtractionUseCase
from src.infrastructure.persistence.in_memory_tenant_ai_provider_repository import InMemoryTenantAIProviderRepository
from src.infrastructure.persistence.base_repository import ConcurrencyException
from src.infrastructure.ai_provider.ollama_adapter import OllamaProviderAdapter
from src.infrastructure.ai_provider.openai_adapter import OpenAIProviderAdapter
from src.infrastructure.ai_provider.vllm_adapter import VLLMProviderAdapter
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus


def test_model_parameter_validations() -> None:
    # 1. Valid params
    params = ModelParameters(0.7, 100, 30)
    assert params.temperature == 0.7

    # 2. Invalid temperature
    with pytest.raises(ValueError):
        ModelParameters(2.5, 100, 30)

    # 3. Invalid max tokens
    with pytest.raises(ValueError):
        ModelParameters(0.7, 0, 30)


def test_provider_config_validations() -> None:
    # 1. Valid config
    config = ProviderConfig("Ollama", "llama3", priority=1)
    assert config.provider_name == "Ollama"

    # 2. Invalid priority
    with pytest.raises(ValueError):
        ProviderConfig("Ollama", "llama3", priority=0)


def test_routing_service_fallback_loop() -> None:
    # Configure Ollama (priority 1, fails) and OpenAI (priority 2, succeeds)
    default_params = ModelParameters(0.7, 500, 10)
    default_retry = RetryStrategy(0, 0.5)  # 0 retries to speed up test
    default_prompts = PromptTemplates()
    default_thresh = Thresholds(0.8, 0.7)
    providers = [
        ProviderConfig("Ollama", "llama3", priority=1),
        ProviderConfig("OpenAI", "gpt-4o", priority=2)
    ]
    config = TenantAIProviderConfiguration(
        tenant_id="tenant-1",
        preferred_provider="Ollama",
        fallback_model="gpt-4o",
        model_parameters=default_params,
        retry_strategy=default_retry,
        prompt_templates=default_prompts,
        thresholds=default_thresh,
        providers=providers
    )

    # Mock Ollama (fails) and OpenAI (succeeds)
    instances = {
        "Ollama": OllamaProviderAdapter(should_fail=True),
        "OpenAI": OpenAIProviderAdapter(response_text="Succeeded OpenAI")
    }

    res = TenantAIRoutingService.execute_generation(
        tenant_config=config,
        prompt="Ingest secure report details.",
        provider_instances=instances
    )

    # Assert it falls back and returns OpenAI's mock output
    assert "Succeeded OpenAI" in res


def test_routing_service_retry_behavior(monkeypatch) -> None:
    # Track calls count
    call_count = 0

    class TrackingOllamaAdapter(OllamaProviderAdapter):
        def generate(self, *args, **kwargs) -> str:
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Connection refused")

    default_params = ModelParameters(0.7, 500, 10)
    default_retry = RetryStrategy(2, 0.01)  # 2 retries, 10ms backoff
    default_prompts = PromptTemplates()
    default_thresh = Thresholds(0.8, 0.7)
    providers = [
        ProviderConfig("Ollama", "llama3", priority=1)
    ]
    config = TenantAIProviderConfiguration(
        tenant_id="tenant-1",
        preferred_provider="Ollama",
        fallback_model="gpt-4o",
        model_parameters=default_params,
        retry_strategy=default_retry,
        prompt_templates=default_prompts,
        thresholds=default_thresh,
        providers=providers
    )

    instances = {
        "Ollama": TrackingOllamaAdapter()
    }

    # Should attempt generation and fail, raising RuntimeError after all retries
    with pytest.raises(RuntimeError) as exc:
        TenantAIRoutingService.execute_generation(
            tenant_config=config,
            prompt="Try call count",
            provider_instances=instances
        )

    # Assert call count is 3 (1 initial call + 2 retries)
    assert call_count == 3
    assert "AI Generation failed across all prioritize loops" in str(exc.value)


def test_generate_text_extraction_use_case_templates() -> None:
    repo = InMemoryTenantAIProviderRepository()
    use_case = GenerateTextExtractionUseCase(repo)

    # Pre-seed config with prompt templates
    params = ModelParameters(0.2, 1000, 30)
    retry = RetryStrategy(0, 0.5)
    prompts = PromptTemplates(templates={"phi_extractor": "Extract fields from clinical text: {text}"})
    thresh = Thresholds(0.8, 0.7)
    providers = [ProviderConfig("vLLM", "llama-70b", priority=1)]
    config = TenantAIProviderConfiguration(
        tenant_id="tenant-alice",
        preferred_provider="vLLM",
        fallback_model="gpt-4o",
        model_parameters=params,
        retry_strategy=retry,
        prompt_templates=prompts,
        thresholds=thresh,
        providers=providers
    )
    repo.save(config)

    instances = {
        "vLLM": VLLMProviderAdapter(response_text="Extracted Summary")
    }

    # Execute extraction using templates key
    res = use_case.execute(
        tenant_id="tenant-alice",
        raw_prompt="John Doe, 42 years old, HbA1c 7.2%",
        prompt_key="phi_extractor",
        provider_instances=instances
    )

    assert "prompt=Extract fields from " in res


def test_repository_concurrency() -> None:
    repo = InMemoryTenantAIProviderRepository()
    params = ModelParameters(0.7, 500, 10)
    retry = RetryStrategy(1, 0.5)
    prompts = PromptTemplates()
    thresh = Thresholds(0.8, 0.7)
    providers = [ProviderConfig("OpenAI", "gpt-4", priority=1)]
    config = TenantAIProviderConfiguration(
        tenant_id="tenant-bob",
        preferred_provider="OpenAI",
        fallback_model="gpt-4",
        model_parameters=params,
        retry_strategy=retry,
        prompt_templates=prompts,
        thresholds=thresh,
        providers=providers
    )

    repo.save(config)
    assert config.version == 1

    stale = repo.get_by_tenant_id("tenant-bob")

    config.fallback_model = "gpt-4o-mini"
    repo.save(config)
    assert config.version == 2

    with pytest.raises(ConcurrencyException):
        repo.save(stale)
