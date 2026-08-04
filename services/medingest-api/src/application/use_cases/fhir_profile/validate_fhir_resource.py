"""
validate_fhir_resource.py
Use case validating FHIR resource conformity payload against active profile targets.
"""

from typing import Any
from src.application.ports.ifhir_profile_repository import IFHIRProfileRepository
from src.domain.fhir_profile.domain_services import FHIRProfileValidationPipeline
from src.domain.fhir_profile.value_objects import FHIRValidationResult


class ValidateFHIRResourceUseCase:
    """
    Usecase orchestrating structural validation pipelines for clinical FHIR payloads.
    """

    def __init__(self, repo: IFHIRProfileRepository) -> None:
        self.repo = repo
        self.pipeline = FHIRProfileValidationPipeline()

    def execute(self, tenant_id: str, resource: dict[str, Any]) -> FHIRValidationResult:
        """Loads active profiles list and evaluates constraints."""
        # Load configuration
        config = self.repo.get_configuration(tenant_id)
        active_igs = config.active_igs if config else []

        # Load all structure definitions active for this tenant
        global_sds = self.repo.get_structure_definitions(tenant_id=None)
        tenant_sds = self.repo.get_structure_definitions(tenant_id=tenant_id)
        
        # Combine definitions (tenant specific overrides global)
        all_sds = {sd.url: sd for sd in global_sds}
        for sd in tenant_sds:
            all_sds[sd.url] = sd

        return self.pipeline.validate_resource(
            tenant_id=tenant_id,
            resource=resource,
            active_igs=active_igs,
            structure_definitions=list(all_sds.values())
        )
