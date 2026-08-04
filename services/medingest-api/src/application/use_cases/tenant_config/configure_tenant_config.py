"""
configure_tenant_config.py
Use Case configuring and saving TenantConfiguration parameters.
"""

from src.application.ports.itenant_configuration_repository import ITenantConfigurationRepository
from src.domain.common.event_bus import IEventBus
from src.domain.tenant_config.entities import TenantConfiguration
from src.domain.tenant_config.value_objects import LocaleSettings, ClinicalFormats, RetentionSettings


class ConfigureTenantConfigUseCase:
    """
    Inbound Use Case updating configuration options for a Tenant.
    """

    def __init__(self, repo: ITenantConfigurationRepository, event_bus: IEventBus):
        self.repo = repo
        self.event_bus = event_bus

    def execute(
        self,
        tenant_id: str,
        date_format: str,
        time_format: str,
        timezone: str,
        language: str,
        currency: str,
        locale: str,
        number_format: str,
        patient_id_format: str,
        medical_record_format: str,
        document_number_format: str,
        default_retention_days: int
    ) -> TenantConfiguration:
        """
        Validates, modifies, and saves target configurations.
        """
        locale_settings = LocaleSettings(
            date_format=date_format,
            time_format=time_format,
            timezone=timezone,
            language=language,
            currency=currency,
            locale=locale,
            number_format=number_format
        )
        clinical_formats = ClinicalFormats(
            patient_id_format=patient_id_format,
            medical_record_format=medical_record_format,
            document_number_format=document_number_format
        )
        retention_settings = RetentionSettings(
            default_retention_days=default_retention_days
        )

        config = self.repo.get_by_tenant_id(tenant_id)
        if not config:
            config = TenantConfiguration(
                tenant_id=tenant_id,
                locale_settings=locale_settings,
                clinical_formats=clinical_formats,
                retention_settings=retention_settings
            )
            # Dispatch event for initial creation
            from src.domain.tenant_config.events import TenantConfigurationUpdatedEvent
            config._domain_events.append(
                TenantConfigurationUpdatedEvent(
                    tenant_id=tenant_id,
                    changes={
                        "locale": locale,
                        "timezone": timezone,
                        "patient_id_format": patient_id_format,
                        "retention_days": default_retention_days
                    }
                )
            )
        else:
            config.update_configuration(
                locale_settings=locale_settings,
                clinical_formats=clinical_formats,
                retention_settings=retention_settings
            )

        self.repo.save(config)

        # Dispatch events
        for event in config._domain_events:
            self.event_bus.publish(event)
        config._domain_events.clear()

        return config
