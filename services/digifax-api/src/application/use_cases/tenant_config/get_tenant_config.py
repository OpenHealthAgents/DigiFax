"""
get_tenant_config.py
Use Case returning active TenantConfiguration settings, resolving default fallback bounds.
"""

from src.application.ports.itenant_configuration_repository import ITenantConfigurationRepository
from src.domain.tenant_config.entities import TenantConfiguration
from src.domain.tenant_config.value_objects import LocaleSettings, ClinicalFormats, RetentionSettings


class GetTenantConfigUseCase:
    """
    Inbound Use Case resolving Tenant Configuration following fallback rules:
    Tenant-specific configuration -> Global Defaults.
    """

    def __init__(self, repo: ITenantConfigurationRepository):
        self.repo = repo

    def execute(self, tenant_id: str) -> TenantConfiguration:
        """
        Retrieves active configuration for a tenant. Falls back to Global Defaults if unconfigured.
        """
        config = self.repo.get_by_tenant_id(tenant_id)
        if not config:
            # Reconstitute Global Default configuration
            default_locale = LocaleSettings(
                date_format="YYYY-MM-DD",
                time_format="HH:mm:ss",
                timezone="UTC",
                language="en",
                currency="USD",
                locale="en-US",
                number_format="1,234.56"
            )
            default_clinical = ClinicalFormats(
                patient_id_format=r"PAT-\d{6}",
                medical_record_format=r"MRN-\d{8}",
                document_number_format=r"DOC-\d{10}"
            )
            default_retention = RetentionSettings(
                default_retention_days=365
            )
            config = TenantConfiguration(
                tenant_id=tenant_id,
                locale_settings=default_locale,
                clinical_formats=default_clinical,
                retention_settings=default_retention,
                version=1
            )
        return config
