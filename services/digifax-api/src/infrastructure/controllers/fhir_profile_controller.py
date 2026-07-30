"""
fhir_profile_controller.py
FastAPI controller routing FHIR profile configurations and validate checks.
"""

from typing import Any, List
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from src.application.use_cases.fhir_profile.configure_active_igs import ConfigureActiveIGsUseCase
from src.application.use_cases.fhir_profile.upload_structure_definition import UploadStructureDefinitionUseCase
from src.application.use_cases.fhir_profile.validate_fhir_resource import ValidateFHIRResourceUseCase
from src.infrastructure.persistence.in_memory_fhir_profile_repository import InMemoryFHIRProfileRepository

router = APIRouter(prefix="/api/fhir/profile", tags=["FHIR Profile Management"])
_profile_repo = InMemoryFHIRProfileRepository()


# --- REQUEST & RESPONSE SCHEMAS ---

class ConfigureActiveIGsRequest(BaseModel):
    active_igs: List[str] = Field(..., description="Canonical URIs of active FHIR Implementation Guides")


class UploadStructureDefinitionRequest(BaseModel):
    url: str = Field(..., description="Canonical URL of custom profile")
    resource_type: str = Field(..., description="Resource type targets (e.g. Patient, Observation)")
    required_paths: List[str] = Field(..., description="List of required elements schema paths")


class ValidationResponse(BaseModel):
    valid: bool
    errors: List[str]
    profile_url: str | None = None


# --- ROUTERS ---

@router.post("/config", status_code=status.HTTP_200_OK)
def configure_active_igs(
    req: ConfigureActiveIGsRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Configures which Implementation Guides are enabled for this tenant."""
    use_case = ConfigureActiveIGsUseCase(_profile_repo)
    config = use_case.execute(tenant_id=x_tenant_id, active_igs=req.active_igs)
    return {
        "tenant_id": config.tenant_id,
        "active_igs": config.active_igs,
        "custom_profiles": config.custom_profiles
    }


@router.post("/structure-definition", status_code=status.HTTP_201_CREATED)
def upload_structure_definition(
    req: UploadStructureDefinitionRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Uploads a tenant-custom StructureDefinition profile."""
    use_case = UploadStructureDefinitionUseCase(_profile_repo)
    try:
        sd = use_case.execute(
            tenant_id=x_tenant_id,
            url=req.url,
            resource_type=req.resource_type,
            required_paths=req.required_paths
        )
        return {
            "url": sd.url,
            "resource_type": sd.resource_type,
            "tenant_id": sd.tenant_id,
            "required_paths": sd.required_paths
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate", response_model=ValidationResponse)
def validate_fhir_resource(
    resource: dict,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Evaluates FHIR resource payload conformances against active profiles."""
    use_case = ValidateFHIRResourceUseCase(_profile_repo)
    result = use_case.execute(tenant_id=x_tenant_id, resource=resource)
    return ValidationResponse(
        valid=result.valid,
        errors=result.errors,
        profile_url=result.profile_url
    )
