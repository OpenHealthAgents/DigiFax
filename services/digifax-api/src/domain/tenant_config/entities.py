"""
entities.py
Domain Entities and Aggregate Root for Tenant Configuration.
"""

from typing import Any
from src.domain.common.entity import Entity
from src.domain.tenant_config.value_objects import LocaleSettings, ClinicalFormats, RetentionSettings
from src.domain.tenant_config.events import TenantConfigurationUpdatedEvent


class TenantConfiguration(Entity):
    """
    Aggregate Root representing localized system settings and metadata mapping templates.
    """

    def __init__(
        self,
        tenant_id: str,
        locale_settings: LocaleSettings,
        clinical_formats: ClinicalFormats,
        retention_settings: RetentionSettings,
        version: int = 1
    ):
        super().__init__(id=tenant_id)
        self.tenant_id = tenant_id
        self.locale_settings = locale_settings
        self.clinical_formats = clinical_formats
        self.retention_settings = retention_settings
        self.version = version
        self._domain_events = []

    def update_configuration(
        self,
        locale_settings: LocaleSettings,
        clinical_formats: ClinicalFormats,
        retention_settings: RetentionSettings
    ) -> None:
        """Updates formatting details, locale, numbering layouts, and lifecycle policies."""
        self.locale_settings = locale_settings
        self.clinical_formats = clinical_formats
        self.retention_settings = retention_settings
        
        event = TenantConfigurationUpdatedEvent(
            tenant_id=self.tenant_id,
            changes={
                "locale": locale_settings.locale,
                "timezone": locale_settings.timezone,
                "patient_id_format": clinical_formats.patient_id_format,
                "retention_days": retention_settings.default_retention_days
            }
        )
        self._domain_events.append(event)
