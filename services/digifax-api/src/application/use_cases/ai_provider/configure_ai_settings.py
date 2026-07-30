"""
configure_ai_settings.py
Use Case configuring and saving TenantAIProviderConfiguration parameters.
"""

from src.application.ports.itenant_ai_provider_repository import ITenantAIProviderRepository
from src.domain.common.event_bus import IEventBus
from src.domain.ai_provider.entities import TenantAIProviderConfiguration
from src.domain.ai_provider.value_objects import (
    ModelParameters,
    RetryStrategy,
    PromptTemplates,
    Thresholds,
    ProviderConfig
)


class ConfigureAISettingsUseCase:
    """
    Inbound Use Case configuring AI settings and fallback rules for a Tenant.
    """

    def __init__(self, repo: ITenantAIProviderRepository, event_bus: IEventBus):
        self.repo = repo
        self.event_bus = event_bus

    def execute(
        self,
        tenant_id: str,
        preferred_provider: str,
        fallback_model: str,
        temperature: float,
        max_tokens: int,
        timeout_seconds: int,
        max_retries: int,
        backoff_factor: float,
        prompt_templates: dict[str, str],
        confidence_threshold: float,
        human_review_threshold: float,
        providers: list[dict]
    ) -> TenantAIProviderConfiguration:
        """
        Validates, modifies, and saves target AI configurations.
        """
        model_params = ModelParameters(
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds
        )
        retry_strat = RetryStrategy(
            max_retries=max_retries,
            backoff_factor=backoff_factor
        )
        prompts = PromptTemplates(templates=prompt_templates)
        thresh = Thresholds(
            confidence_threshold=confidence_threshold,
            human_review_threshold=human_review_threshold
        )
        
        provider_configs = [
            ProviderConfig(
                provider_name=p["provider_name"],
                model_name=p["model_name"],
                api_base_url=p.get("api_base_url"),
                api_key_obfuscated=p.get("api_key_obfuscated"),
                priority=p.get("priority", 1)
            ) for p in providers
        ]

        config = self.repo.get_by_tenant_id(tenant_id)
        if not config:
            config = TenantAIProviderConfiguration(
                tenant_id=tenant_id,
                preferred_provider=preferred_provider,
                fallback_model=fallback_model,
                model_parameters=model_params,
                retry_strategy=retry_strat,
                prompt_templates=prompts,
                thresholds=thresh,
                providers=provider_configs
            )
        else:
            config.update_configuration(
                preferred_provider=preferred_provider,
                fallback_model=fallback_model,
                model_parameters=model_params,
                retry_strategy=retry_strat,
                prompt_templates=prompts,
                thresholds=thresh,
                providers=provider_configs
            )

        self.repo.save(config)

        # Dispatch events
        for event in config._domain_events:
            self.event_bus.publish(event)
        config._domain_events.clear()

        return config
