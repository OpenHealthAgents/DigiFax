"""
generate_text_extraction.py
Use Case managing tenant text extraction workflows using resolved AI provider configurations.
"""

from src.application.ports.itenant_ai_provider_repository import ITenantAIProviderRepository
from src.domain.ai_provider.entities import TenantAIProviderConfiguration
from src.domain.ai_provider.value_objects import (
    ModelParameters,
    RetryStrategy,
    PromptTemplates,
    Thresholds,
    ProviderConfig
)
from src.domain.ai_provider.domain_services import TenantAIRoutingService
from src.domain.ai_provider.iai_provider import IAIProvider


class GenerateTextExtractionUseCase:
    """
    Inbound Use Case executing LLM text extraction. Resolves fallbacks if unconfigured.
    """

    def __init__(self, repo: ITenantAIProviderRepository):
        self.repo = repo

    def execute(
        self,
        tenant_id: str,
        raw_prompt: str,
        prompt_key: str | None = None,
        system_instruction: str | None = None,
        provider_instances: dict[str, IAIProvider] = None
    ) -> str:
        """
        Loads settings, resolves prompts templates, and delegates queries to Routing Service.
        """
        config = self.repo.get_by_tenant_id(tenant_id)
        if not config:
            # Build Default Global AI configuration
            default_params = ModelParameters(
                temperature=0.2,
                max_tokens=1500,
                timeout_seconds=30
            )
            default_retry = RetryStrategy(
                max_retries=2,
                backoff_factor=1.5
            )
            default_prompts = PromptTemplates(
                templates={"default": "Analyze clinical text: {text}"}
            )
            default_thresh = Thresholds(
                confidence_threshold=0.85,
                human_review_threshold=0.70
            )
            default_providers = [
                ProviderConfig(provider_name="OpenAI", model_name="gpt-4o", priority=1),
                ProviderConfig(provider_name="Ollama", model_name="llama3", priority=2)
            ]
            config = TenantAIProviderConfiguration(
                tenant_id=tenant_id,
                preferred_provider="OpenAI",
                fallback_model="gpt-4o-mini",
                model_parameters=default_params,
                retry_strategy=default_retry,
                prompt_templates=default_prompts,
                thresholds=default_thresh,
                providers=default_providers
            )

        # Resolve prompt template if defined
        final_prompt = raw_prompt
        if prompt_key and prompt_key in config.prompt_templates.templates:
            template = config.prompt_templates.templates[prompt_key]
            if "{text}" in template:
                final_prompt = template.replace("{text}", raw_prompt)
            else:
                final_prompt = f"{template}\n\nInput Payload:\n{raw_prompt}"

        # Delegate execution to domain routing service
        return TenantAIRoutingService.execute_generation(
            tenant_config=config,
            prompt=final_prompt,
            system_instruction=system_instruction,
            provider_instances=provider_instances
        )
