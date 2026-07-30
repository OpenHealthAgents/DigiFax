"""
ikey_ring_repository.py
Outbound port repository interface for TenantKeyRing aggregate persistence.
"""

from abc import ABC, abstractmethod
from src.domain.encryption.entities import TenantKeyRing


class IKeyRingRepository(ABC):
    """
    Interface for persistence of TenantKeyRings.
    """

    @abstractmethod
    def save_key_ring(self, key_ring: TenantKeyRing) -> None:
        """Saves a tenant's KeyRing configuration."""
        pass

    @abstractmethod
    def get_key_ring(self, tenant_id: str) -> TenantKeyRing | None:
        """Loads a tenant's KeyRing configuration."""
        pass
