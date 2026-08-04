"""
configure_compliance.py
Use case for configuring tenant-level active regulations and retention schedules.
"""

from src.application.ports.icompliance_repository import IComplianceRepository
from src.domain.compliance.entities import TenantComplianceConfiguration
from src.domain.compliance.value_objects import ComplianceRegulation, RetentionRule


class ConfigureComplianceUseCase:
    """
    Usecase allowing tenant admins to activate privacy regulations and retention rules.
    """

    def __init__(self, repo: IComplianceRepository) -> None:
        self.repo = repo

    def execute(
        self,
        tenant_id: str,
        regulations: list[dict],
        retention_rules: list[dict]
    ) -> TenantComplianceConfiguration:
        """Saves compliance configuration settings for a tenant."""
        config = self.repo.get_configuration(tenant_id)
        if not config:
            config = TenantComplianceConfiguration(tenant_id=tenant_id)

        # Map regulations
        regs_list = []
        for r in regulations:
            regs_list.append(
                ComplianceRegulation(
                    name=r["name"],
                    description=r.get("description", ""),
                    region=r.get("region", "")
                )
            )
        config.enabled_regulations = regs_list

        # Map retention rules
        rules_list = []
        for rule in retention_rules:
            rules_list.append(
                RetentionRule(
                    resource_type=rule["resource_type"],
                    retention_days=rule["retention_days"],
                    expiration_action=rule["expiration_action"]
                )
            )
        config.retention_rules = rules_list

        self.repo.save_configuration(config)
        return config
