"""
itenant_configuration_repository.py
Port interface for TenantConfiguration persistence.
"""

from abc import ABC, abstractmethod
from src.domain.tenant_config.entities import TenantConfiguration


class ITenantConfigurationRepository(ABC):
    """
    Outbound Port interface decoupling TenantConfiguration adapters from use cases.
    """

    @abstractmethod
    def save(self, config: TenantConfiguration) -> None:
        """Saves or updates the TenantConfiguration record."""
        pass

    @abstractmethod
    def get_by_tenant_id(self, tenant_id: str) -> TenantConfiguration | None:
        """Loads TenantConfiguration scoped to a specific tenant ID."""
        pass
