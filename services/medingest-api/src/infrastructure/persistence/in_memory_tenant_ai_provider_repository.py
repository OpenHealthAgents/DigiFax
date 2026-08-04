"""
in_memory_tenant_ai_provider_repository.py
In-memory persistence adapter for TenantAIProviderConfiguration aggregate.
"""

from typing import Any
from src.application.ports.itenant_ai_provider_repository import ITenantAIProviderRepository
from src.domain.ai_provider.entities import TenantAIProviderConfiguration
from src.domain.ai_provider.value_objects import (
    ModelParameters,
    RetryStrategy,
    PromptTemplates,
    Thresholds,
    ProviderConfig
)
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryTenantAIProviderRepository(BaseInMemoryRepository, ITenantAIProviderRepository):
    """
    Thread-safe in-memory adapter storing TenantAIProviderConfiguration records.
    """

    def __init__(self) -> None:
        super().__init__()

    def save(self, config: TenantAIProviderConfiguration) -> None:
        """Saves configuration with version validation (OCC)."""
        record_data = {
            "id": config.tenant_id,
            "tenant_id": config.tenant_id,
            "preferred_provider": config.preferred_provider,
            "fallback_model": config.fallback_model,
            "model_parameters": {
                "temperature": config.model_parameters.temperature,
                "max_tokens": config.model_parameters.max_tokens,
                "timeout_seconds": config.model_parameters.timeout_seconds
            },
            "retry_strategy": {
                "max_retries": config.retry_strategy.max_retries,
                "backoff_factor": config.retry_strategy.backoff_factor
            },
            "prompt_templates": {
                "templates": config.prompt_templates.templates
            },
            "thresholds": {
                "confidence_threshold": config.thresholds.confidence_threshold,
                "human_review_threshold": config.thresholds.human_review_threshold
            },
            "providers": [
                {
                    "provider_name": p.provider_name,
                    "model_name": p.model_name,
                    "api_base_url": p.api_base_url,
                    "api_key_obfuscated": p.api_key_obfuscated,
                    "priority": p.priority
                } for p in config.providers
            ],
            "version": getattr(config, "version", 1)
        }

        self._save_record(config.tenant_id, record_data)
        saved = self._records[config.tenant_id]
        config.version = saved["version"]

    def get_by_tenant_id(self, tenant_id: str) -> TenantAIProviderConfiguration | None:
        """Retrieves and reconstitutes TenantAIProviderConfiguration scoped to a tenant."""
        record = self._get_record_by_id(tenant_id, tenant_id)
        if not record:
            return None

        model_params = ModelParameters(
            temperature=record["model_parameters"]["temperature"],
            max_tokens=record["model_parameters"]["max_tokens"],
            timeout_seconds=record["model_parameters"]["timeout_seconds"]
        )
        retry_strat = RetryStrategy(
            max_retries=record["retry_strategy"]["max_retries"],
            backoff_factor=record["retry_strategy"]["backoff_factor"]
        )
        prompts = PromptTemplates(
            templates=record["prompt_templates"]["templates"]
        )
        thresh = Thresholds(
            confidence_threshold=record["thresholds"]["confidence_threshold"],
            human_review_threshold=record["thresholds"]["human_review_threshold"]
        )
        providers = [
            ProviderConfig(
                provider_name=p["provider_name"],
                model_name=p["model_name"],
                api_base_url=p["api_base_url"],
                api_key_obfuscated=p["api_key_obfuscated"],
                priority=p["priority"]
            ) for p in record["providers"]
        ]

        return TenantAIProviderConfiguration(
            tenant_id=record["tenant_id"],
            preferred_provider=record["preferred_provider"],
            fallback_model=record["fallback_model"],
            model_parameters=model_params,
            retry_strategy=retry_strat,
            prompt_templates=prompts,
            thresholds=thresh,
            providers=providers,
            version=record["version"]
        )
