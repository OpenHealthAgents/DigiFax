"""
iterminology_repository.py
Port interface for TenantConceptMap and TenantValueSetOverride persistence.
"""

from abc import ABC, abstractmethod
from src.domain.terminology.entities import TenantConceptMap, TenantValueSetOverride


class ITerminologyRepository(ABC):
    """
    Outbound Port interface decoupling Terminology and mapping storages from use cases.
    """

    @abstractmethod
    def save_concept_map(self, concept_map: TenantConceptMap) -> None:
        """Saves or updates a concept map."""
        pass

    @abstractmethod
    def get_concept_map(self, tenant_id: str, mapping_key: str) -> TenantConceptMap | None:
        """Loads a concept map for a specific tenant and key."""
        pass

    @abstractmethod
    def save_valueset_override(self, override: TenantValueSetOverride) -> None:
        """Saves valueset overriding configurations."""
        pass

    @abstractmethod
    def get_valueset_override(self, tenant_id: str, system_url: str) -> TenantValueSetOverride | None:
        """Loads customized overrides settings."""
        pass
