"""
entities.py
Domain Entities and Aggregate Roots for FHIR Profile Configuration and StructureDefinitions.
"""

from src.domain.common.entity import Entity


class TenantFHIRProfileConfiguration(Entity):
    """
    Aggregate Root representing a tenant's active FHIR profile configuration.
    
    Manages selection of standard Implementation Guides (e.g. US Core, IPS)
    and lists custom profile StructureDefinitions URLs.
    """

    def __init__(
        self,
        tenant_id: str,
        active_igs: list[str] = None,
        custom_profiles: list[str] = None,
        version: int = 1
    ):
        super().__init__(id=tenant_id)
        self.tenant_id = tenant_id
        self.active_igs = active_igs or []
        self.custom_profiles = custom_profiles or []
        self.version = version

    def activate_ig(self, ig_url: str) -> None:
        """Enables a standard Implementation Guide constraint set."""
        if ig_url not in self.active_igs:
            self.active_igs.append(ig_url)

    def deactivate_ig(self, ig_url: str) -> None:
        """Disables an Implementation Guide constraint set."""
        if ig_url in self.active_igs:
            self.active_igs.remove(ig_url)


class FHIRStructureDefinition(Entity):
    """
    Entity representing a StructureDefinition detailing constraints and required paths
    for validating conforming FHIR resource instances.
    """

    def __init__(
        self,
        url: str,
        resource_type: str,
        tenant_id: str | None = None,
        required_paths: list[str] = None,
        version: int = 1
    ):
        super().__init__(id=f"{tenant_id or 'global'}:{url}")
        self.url = url
        self.resource_type = resource_type
        self.tenant_id = tenant_id
        self.required_paths = required_paths or []
        self.version = version
