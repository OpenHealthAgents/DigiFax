"""
entities.py
Domain Entities and Aggregate Root for AI Provider configuration.
"""

from src.domain.common.entity import Entity
from src.domain.ai_provider.value_objects import (
    ModelParameters,
    RetryStrategy,
    PromptTemplates,
    Thresholds,
    ProviderConfig
)


class TenantAIProviderConfiguration(Entity):
    """
    Aggregate Root managing a Tenant's AI model selections and priority routing settings.
    """

    def __init__(
        self,
        tenant_id: str,
        preferred_provider: str,
        fallback_model: str,
        model_parameters: ModelParameters,
        retry_strategy: RetryStrategy,
        prompt_templates: PromptTemplates,
        thresholds: Thresholds,
        providers: list[ProviderConfig],
        version: int = 1
    ):
        super().__init__(id=tenant_id)
        self.tenant_id = tenant_id
        self.preferred_provider = preferred_provider
        self.fallback_model = fallback_model
        self.model_parameters = model_parameters
        self.retry_strategy = retry_strategy
        self.prompt_templates = prompt_templates
        self.thresholds = thresholds
        self.providers = providers
        self.version = version
        self._domain_events = []

    def update_configuration(
        self,
        preferred_provider: str,
        fallback_model: str,
        model_parameters: ModelParameters,
        retry_strategy: RetryStrategy,
        prompt_templates: PromptTemplates,
        thresholds: Thresholds,
        providers: list[ProviderConfig]
    ) -> None:
        """Updates AI provider selection parameters."""
        self.preferred_provider = preferred_provider
        self.fallback_model = fallback_model
        self.model_parameters = model_parameters
        self.retry_strategy = retry_strategy
        self.prompt_templates = prompt_templates
        self.thresholds = thresholds
        self.providers = providers
        
        # Inject domain event if required for audits
        from src.domain.common.domain_event import DomainEvent
        from dataclasses import dataclass, field
        from datetime import datetime

        @dataclass(frozen=True)
        class AIProviderConfigUpdatedEvent(DomainEvent):
            tenant_id: str
            preferred_provider: str
            occurred_at: datetime = field(default_factory=datetime.utcnow)

        self._domain_events.append(
            AIProviderConfigUpdatedEvent(
                tenant_id=self.tenant_id,
                preferred_provider=preferred_provider
            )
        )
