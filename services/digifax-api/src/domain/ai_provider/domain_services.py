"""
domain_services.py
Domain Routing Service coordinating retries and priority fallbacks across AI providers.
"""

import time
import logging
from src.domain.ai_provider.entities import TenantAIProviderConfiguration
from src.domain.ai_provider.iai_provider import IAIProvider

logger = logging.getLogger(__name__)


class TenantAIRoutingService:
    """
    Domain Service routing queries across priority lists, implementing retries and fallbacks.
    """

    @staticmethod
    def execute_generation(
        tenant_config: TenantAIProviderConfiguration,
        prompt: str,
        system_instruction: str | None = None,
        provider_instances: dict[str, IAIProvider] = None
    ) -> str:
        """
        Executes text generation by iterating over prioritized providers.
        
        Applies:
            1. Priority-based sorting.
            2. Exponential retry loops.
            3. Graceful provider failover fallbacks.
        """
        if not provider_instances:
            raise ValueError("Provider instances mapping is required")

        # 1. Sort configured providers by priority index ascending
        sorted_providers = sorted(tenant_config.providers, key=lambda p: p.priority)

        last_error = None

        # 2. Iterate through fallback list
        for config in sorted_providers:
            provider_name = config.provider_name
            if provider_name not in provider_instances:
                logger.warning(f"Provider {provider_name} has no matching registered instance adapter. Skipping.")
                continue

            instance = provider_instances[provider_name]
            max_retries = tenant_config.retry_strategy.max_retries
            backoff = tenant_config.retry_strategy.backoff_factor

            # 3. Retry loop for current provider
            for attempt in range(max_retries + 1):
                try:
                    res = instance.generate(
                        prompt=prompt,
                        system_instruction=system_instruction,
                        temperature=tenant_config.model_parameters.temperature,
                        max_tokens=tenant_config.model_parameters.max_tokens,
                        timeout_seconds=tenant_config.model_parameters.timeout_seconds
                    )
                    return res
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Attempt {attempt + 1} failed for provider {provider_name} on model {config.model_name}: {str(e)}"
                    )
                    if attempt < max_retries:
                        time.sleep(backoff * (2 ** attempt))

            logger.error(f"All retries failed for provider {provider_name}. Falling back to next prioritized choice.")

        # 4. If all fail, check fallback_model using default fallback provider (or throw)
        if tenant_config.fallback_model and "OpenAI" in provider_instances:
            logger.warning(f"Triggering global fallback model check: {tenant_config.fallback_model}")
            try:
                fallback_instance = provider_instances["OpenAI"]
                return fallback_instance.generate(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=tenant_config.model_parameters.temperature,
                    max_tokens=tenant_config.model_parameters.max_tokens,
                    timeout_seconds=tenant_config.model_parameters.timeout_seconds
                )
            except Exception as e:
                raise RuntimeError(f"Fallback model execution failed: {str(e)}") from e

        raise RuntimeError(f"AI Generation failed across all prioritize loops. Last Error: {str(last_error)}")
