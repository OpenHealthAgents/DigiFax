"""
ifhir_profile_repository.py
Outbound port repository interface for FHIR profile configurations and StructureDefinitions.
"""

from abc import ABC, abstractmethod
from src.domain.fhir_profile.entities import TenantFHIRProfileConfiguration, FHIRStructureDefinition


class IFHIRProfileRepository(ABC):
    """
    Interface for persistence of TenantFHIRProfileConfiguration and StructureDefinition rules.
    """

    @abstractmethod
    def save_configuration(self, config: TenantFHIRProfileConfiguration) -> None:
        """Saves configuration settings for a tenant."""
        pass

    @abstractmethod
    def get_configuration(self, tenant_id: str) -> TenantFHIRProfileConfiguration | None:
        """Loads configuration settings for a tenant."""
        pass

    @abstractmethod
    def save_structure_definition(self, sd: FHIRStructureDefinition) -> None:
        """Saves a StructureDefinition constraints profile."""
        pass

    @abstractmethod
    def get_structure_definitions(self, tenant_id: str | None = None) -> list[FHIRStructureDefinition]:
        """Lists StructureDefinitions active for the system or a specific tenant."""
        pass

    @abstractmethod
    def get_structure_definition_by_url(
        self,
        url: str,
        tenant_id: str | None = None
    ) -> FHIRStructureDefinition | None:
        """Finds a StructureDefinition matching a canonical URL profile."""
        pass
