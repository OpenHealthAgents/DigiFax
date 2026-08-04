"""
in_memory_tenant_config_repository.py
In-memory persistence adapter for TenantConfiguration aggregate.
"""

from typing import Any
from src.application.ports.itenant_configuration_repository import ITenantConfigurationRepository
from src.domain.tenant_config.entities import TenantConfiguration
from src.domain.tenant_config.value_objects import LocaleSettings, ClinicalFormats, RetentionSettings
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryTenantConfigurationRepository(BaseInMemoryRepository, ITenantConfigurationRepository):
    """
    Thread-safe in-memory adapter storing TenantConfiguration records.
    """

    def __init__(self) -> None:
        super().__init__()

    def save(self, config: TenantConfiguration) -> None:
        """Saves configuration with version validation (OCC)."""
        record_data = {
            "id": config.tenant_id,
            "tenant_id": config.tenant_id,
            "locale_settings": {
                "date_format": config.locale_settings.date_format,
                "time_format": config.locale_settings.time_format,
                "timezone": config.locale_settings.timezone,
                "language": config.locale_settings.language,
                "currency": config.locale_settings.currency,
                "locale": config.locale_settings.locale,
                "number_format": config.locale_settings.number_format
            },
            "clinical_formats": {
                "patient_id_format": config.clinical_formats.patient_id_format,
                "medical_record_format": config.clinical_formats.medical_record_format,
                "document_number_format": config.clinical_formats.document_number_format
            },
            "retention_settings": {
                "default_retention_days": config.retention_settings.default_retention_days
            },
            "version": getattr(config, "version", 1)
        }

        self._save_record(config.tenant_id, record_data)
        saved = self._records[config.tenant_id]
        config.version = saved["version"]

    def get_by_tenant_id(self, tenant_id: str) -> TenantConfiguration | None:
        """Retrieves and reconstitutes TenantConfiguration scoped to a tenant."""
        record = self._get_record_by_id(tenant_id, tenant_id)
        if not record:
            return None

        locale = LocaleSettings(
            date_format=record["locale_settings"]["date_format"],
            time_format=record["locale_settings"]["time_format"],
            timezone=record["locale_settings"]["timezone"],
            language=record["locale_settings"]["language"],
            currency=record["locale_settings"]["currency"],
            locale=record["locale_settings"]["locale"],
            number_format=record["locale_settings"]["number_format"]
        )
        clinical = ClinicalFormats(
            patient_id_format=record["clinical_formats"]["patient_id_format"],
            medical_record_format=record["clinical_formats"]["medical_record_format"],
            document_number_format=record["clinical_formats"]["document_number_format"]
        )
        retention = RetentionSettings(
            default_retention_days=record["retention_settings"]["default_retention_days"]
        )

        return TenantConfiguration(
            tenant_id=record["tenant_id"],
            locale_settings=locale,
            clinical_formats=clinical,
            retention_settings=retention,
            version=record["version"]
        )
