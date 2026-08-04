"""
iusage_metering_repository.py
Outbound port repository interface for TenantUsageSummary aggregate persistence.
"""

from abc import ABC, abstractmethod
from src.domain.metering.entities import TenantUsageSummary


class IUsageMeteringRepository(ABC):
    """
    Interface for persistence of TenantUsageSummary configurations.
    """

    @abstractmethod
    def save_usage_summary(self, summary: TenantUsageSummary) -> None:
        """Saves usage summary statistics for a tenant."""
        pass

    @abstractmethod
    def get_usage_summary(self, tenant_id: str) -> TenantUsageSummary | None:
        """Loads usage summary statistics for a tenant."""
        pass
