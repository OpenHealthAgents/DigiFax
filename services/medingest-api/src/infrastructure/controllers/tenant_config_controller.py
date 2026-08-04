"""
tenant_config_controller.py
FastAPI REST API controller governing Tenant Configuration custom settings.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.application.common.tenant_context import TenantContext
from src.application.use_cases.tenant_config.configure_tenant_config import ConfigureTenantConfigUseCase
from src.application.use_cases.tenant_config.get_tenant_config import GetTenantConfigUseCase
from src.infrastructure.controllers.api_guard import require_permissions
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
from src.infrastructure.persistence.in_memory_tenant_config_repository import InMemoryTenantConfigurationRepository

router = APIRouter(prefix="/api/tenant/config", tags=["Tenant Configuration"])

# Module-level singletons for memory persistence context
_repo = InMemoryTenantConfigurationRepository()
_event_bus = InMemoryEventBus()


class ConfigureTenantConfigRequest(BaseModel):
    """Pydantic model representing styling custom settings request payload."""
    date_format: str = Field(..., description="Date formatting template")
    time_format: str = Field(..., description="Time formatting template")
    timezone: str = Field(..., description="Timezone setting")
    language: str = Field(..., description="Language identifier")
    currency: str = Field(..., description="Currency identifier")
    locale: str = Field(..., description="Locale identifier")
    number_format: str = Field(..., description="Number format schema")
    patient_id_format: str = Field(..., description="Regex validation layout for Patient ID")
    medical_record_format: str = Field(..., description="Regex validation layout for MRN")
    document_number_format: str = Field(..., description="Regex validation layout for Document ID")
    default_retention_days: int = Field(..., description="Document retention default days")


def get_get_config_use_case() -> GetTenantConfigUseCase:
    """Provides GetTenantConfigUseCase handler."""
    return GetTenantConfigUseCase(_repo)


def get_configure_config_use_case() -> ConfigureTenantConfigUseCase:
    """Provides ConfigureTenantConfigUseCase handler."""
    return ConfigureTenantConfigUseCase(_repo, _event_bus)


@router.get(
    "",
    summary="Retrieve active Tenant configurations",
    dependencies=[Depends(require_permissions("document:read"))]
)
def get_tenant_config(
    context: TenantContext = Depends(require_permissions("document:read")),
    use_case: GetTenantConfigUseCase = Depends(get_get_config_use_case)
):
    """
    Returns active settings configured by tenant or defaults to global presets.
    """
    config = use_case.execute(context.tenant_id)
    return {
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
        "version": config.version
    }


@router.post(
    "",
    summary="Update Tenant configuration parameters",
    dependencies=[Depends(require_permissions("document:write"))]
)
def update_tenant_config(
    payload: ConfigureTenantConfigRequest,
    context: TenantContext = Depends(require_permissions("document:write")),
    use_case: ConfigureTenantConfigUseCase = Depends(get_configure_config_use_case)
):
    """
    Creates or updates the tenant settings configuration.
    """
    try:
        config = use_case.execute(
            tenant_id=context.tenant_id,
            date_format=payload.date_format,
            time_format=payload.time_format,
            timezone=payload.timezone,
            language=payload.language,
            currency=payload.currency,
            locale=payload.locale,
            number_format=payload.number_format,
            patient_id_format=payload.patient_id_format,
            medical_record_format=payload.medical_record_format,
            document_number_format=payload.document_number_format,
            default_retention_days=payload.default_retention_days
        )
        return {
            "status": "success",
            "message": "Configuration updated successfully",
            "version": config.version
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
