"""
configure_active_igs.py
Use case allowing tenants to toggle active Implementation Guides.
"""

from src.application.ports.ifhir_profile_repository import IFHIRProfileRepository
from src.domain.fhir_profile.entities import TenantFHIRProfileConfiguration


class ConfigureActiveIGsUseCase:
    """
    Usecase configuring which standard implementation guides are active for a tenant.
    """

    def __init__(self, repo: IFHIRProfileRepository) -> None:
        self.repo = repo

    def execute(self, tenant_id: str, active_igs: list[str]) -> TenantFHIRProfileConfiguration:
        """Saves configuration with active IGs lists."""
        config = self.repo.get_configuration(tenant_id)
        if not config:
            config = TenantFHIRProfileConfiguration(tenant_id=tenant_id)

        config.active_igs = list(active_igs)
        self.repo.save_configuration(config)
        return config
