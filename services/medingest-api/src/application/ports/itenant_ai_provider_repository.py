"""
itenant_ai_provider_repository.py
Port interface for TenantAIProviderConfiguration persistence.
"""

from abc import ABC, abstractmethod
from src.domain.ai_provider.entities import TenantAIProviderConfiguration


class ITenantAIProviderRepository(ABC):
    """
    Outbound Port interface decoupling AI configuration adapters from use cases.
    """

    @abstractmethod
    def save(self, config: TenantAIProviderConfiguration) -> None:
        """Saves or updates the configuration aggregate."""
        pass

    @abstractmethod
    def get_by_tenant_id(self, tenant_id: str) -> TenantAIProviderConfiguration | None:
        """Loads configuration scoped to a specific tenant ID."""
        pass
