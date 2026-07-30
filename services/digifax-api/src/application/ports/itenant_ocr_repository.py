"""
itenant_ocr_repository.py
Port interface for TenantOCRConfiguration persistence.
"""

from abc import ABC, abstractmethod
from src.domain.ocr_provider.entities import TenantOCRConfiguration


class ITenantOCRRepository(ABC):
    """
    Outbound Port interface decoupling OCR configuration database adapters from use cases.
    """

    @abstractmethod
    def save(self, config: TenantOCRConfiguration) -> None:
        """Saves or updates the configuration aggregate."""
        pass

    @abstractmethod
    def get_by_tenant_id(self, tenant_id: str) -> TenantOCRConfiguration | None:
        """Loads configuration scoped to a specific tenant ID."""
        pass
