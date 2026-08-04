"""
itenant_branding_repository.py
Repository port interface for TenantBranding aggregate persistence.
"""

import abc
from src.domain.tenant_branding.entities import TenantBranding


class ITenantBrandingRepository(abc.ABC):
    """
    Outbound port interface decouple domain aggregates from physical storage database components.
    """

    @abc.abstractmethod
    def save(self, branding: TenantBranding) -> None:
        """Saves or updates a TenantBranding aggregate."""
        pass

    @abc.abstractmethod
    def get_by_tenant_id(self, tenant_id: str) -> TenantBranding | None:
        """Retrieves a TenantBranding aggregate matching the identifier key."""
        pass
