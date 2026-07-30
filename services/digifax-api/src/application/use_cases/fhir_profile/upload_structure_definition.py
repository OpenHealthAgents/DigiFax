"""
upload_structure_definition.py
Use case registering custom structure definition profiles.
"""

from src.application.ports.ifhir_profile_repository import IFHIRProfileRepository
from src.domain.fhir_profile.entities import FHIRStructureDefinition


class UploadStructureDefinitionUseCase:
    """
    Usecase registering or updating custom structure definition clinical constraints.
    """

    def __init__(self, repo: IFHIRProfileRepository) -> None:
        self.repo = repo

    def execute(
        self,
        tenant_id: str,
        url: str,
        resource_type: str,
        required_paths: list[str]
    ) -> FHIRStructureDefinition:
        """Saves custom StructureDefinition to repository."""
        if not url.strip():
            raise ValueError("StructureDefinition canonical URL cannot be empty")
        if not resource_type.strip():
            raise ValueError("ResourceType cannot be empty")

        sd = FHIRStructureDefinition(
            url=url,
            resource_type=resource_type,
            tenant_id=tenant_id,
            required_paths=required_paths
        )
        self.repo.save_structure_definition(sd)

        # Update tenant configuration to include custom profile reference URL
        config = self.repo.get_configuration(tenant_id)
        if not config:
            from src.domain.fhir_profile.entities import TenantFHIRProfileConfiguration
            config = TenantFHIRProfileConfiguration(tenant_id=tenant_id)
        
        if url not in config.custom_profiles:
            config.custom_profiles.append(url)
            self.repo.save_configuration(config)

        return sd
