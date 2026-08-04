"""
ioperations_repository.py
Outbound port repository interface for platform operations settings.
"""

from abc import ABC, abstractmethod
from src.domain.operations.entities import PlatformOperationsConfig


class IOperationsRepository(ABC):
    """
    Interface for persistence of Tenant PlatformOperationsConfigs.
    """

    @abstractmethod
    def save_config(self, config: PlatformOperationsConfig) -> None:
        """Saves operations config state."""
        pass

    @abstractmethod
    def get_config(self, tenant_id: str) -> PlatformOperationsConfig | None:
        """Loads operations config state."""
        pass
