"""
compliance_controller.py
FastAPI controller routing compliance configuration settings, consents, and audits.
"""

from typing import Any, List
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from src.application.use_cases.compliance.configure_compliance import ConfigureComplianceUseCase
from src.application.use_cases.compliance.record_consent import RecordPatientConsentUseCase
from src.application.use_cases.compliance.set_legal_hold import SetLegalHoldUseCase, LegalHoldException
from src.application.use_cases.compliance.request_data_deletion import RequestDataDeletionUseCase
from src.application.use_cases.compliance.request_data_export import RequestDataExportUseCase
from src.application.use_cases.compliance.record_audit_log import RecordAuditLogUseCase
from src.infrastructure.persistence.in_memory_compliance_repository import InMemoryComplianceRepository

router = APIRouter(prefix="/api/compliance", tags=["Compliance Management"])
_compliance_repo = InMemoryComplianceRepository()


# --- REQUEST & RESPONSE SCHEMAS ---

class ComplianceRegulationRequest(BaseModel):
    name: str
    description: str = ""
    region: str = ""


class RetentionRuleRequest(BaseModel):
    resource_type: str
    retention_days: int
    expiration_action: str


class ConfigureComplianceRequest(BaseModel):
    regulations: List[ComplianceRegulationRequest]
    retention_rules: List[RetentionRuleRequest]


class ConsentPolicyRequest(BaseModel):
    patient_id: str
    consent_type: str
    scope: str
    signed_date: str


class LegalHoldRequest(BaseModel):
    patient_id: str
    active: bool


class RightToDeletionRequest(BaseModel):
    patient_id: str
    justification: str


class RightToExportRequest(BaseModel):
    patient_id: str
    justification: str


class RecordAuditRequest(BaseModel):
    user_id: str
    resource_id: str
    action: str
    justification: str


class AuditLogResponse(BaseModel):
    user_id: str
    resource_id: str
    action: str
    justification: str
    timestamp: str | None = None


# --- ROUTERS ---

@router.post("/config", status_code=status.HTTP_200_OK)
def configure_compliance(
    req: ConfigureComplianceRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Configures active privacy regulations and retention rules for the tenant."""
    use_case = ConfigureComplianceUseCase(_compliance_repo)
    config = use_case.execute(
        tenant_id=x_tenant_id,
        regulations=[r.dict() for r in req.regulations],
        retention_rules=[r.dict() for r in req.retention_rules]
    )
    return {
        "tenant_id": config.tenant_id,
        "enabled_regulations": [{"name": r.name} for r in config.enabled_regulations],
        "retention_rules": [{"resource_type": r.resource_type} for r in config.retention_rules]
    }


@router.post("/consent", status_code=status.HTTP_200_OK)
def record_consent(
    req: ConsentPolicyRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Registers patient consent opt-in scope policies."""
    use_case = RecordPatientConsentUseCase(_compliance_repo)
    consent = use_case.execute(
        tenant_id=x_tenant_id,
        patient_id=req.patient_id,
        consent_type=req.consent_type,
        scope=req.scope,
        signed_date=req.signed_date
    )
    return {
        "patient_id": consent.patient_id,
        "consent_policies": [{"scope": p.scope, "consent_type": p.consent_type} for p in consent.consent_policies]
    }


@router.post("/legal-hold", status_code=status.HTTP_200_OK)
def set_legal_hold(
    req: LegalHoldRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Toggles legal hold active locks on a patient profile."""
    use_case = SetLegalHoldUseCase(_compliance_repo)
    consent = use_case.execute(
        tenant_id=x_tenant_id,
        patient_id=req.patient_id,
        active=req.active
    )
    return {
        "patient_id": consent.patient_id,
        "legal_hold": consent.legal_hold
    }


@router.post("/delete", status_code=status.HTTP_200_OK)
def request_deletion(
    req: RightToDeletionRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Executes Right to Deletion requests unless blocked by legal hold."""
    use_case = RequestDataDeletionUseCase(_compliance_repo)
    try:
        use_case.execute(
            tenant_id=x_tenant_id,
            patient_id=req.patient_id,
            justification=req.justification
        )
        return {"status": "purged", "detail": "Patient resources successfully deleted from database"}
    except LegalHoldException as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/export", status_code=status.HTTP_200_OK)
def request_export(
    req: RightToExportRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Executes Right to Export requests, packing patient files."""
    use_case = RequestDataExportUseCase(_compliance_repo)
    bundle = use_case.execute(
        tenant_id=x_tenant_id,
        patient_id=req.patient_id,
        justification=req.justification
    )
    return bundle


@router.post("/audit", status_code=status.HTTP_201_CREATED, response_model=AuditLogResponse)
def record_audit(
    req: RecordAuditRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Manually records access entries logs."""
    use_case = RecordAuditLogUseCase(_compliance_repo)
    entry = use_case.execute(
        tenant_id=x_tenant_id,
        user_id=req.user_id,
        resource_id=req.resource_id,
        action=req.action,
        justification=req.justification
    )
    return AuditLogResponse(
        user_id=entry.user_id,
        resource_id=entry.resource_id,
        action=entry.action,
        justification=entry.justification,
        timestamp=entry.timestamp
    )


@router.get("/audit", response_model=List[AuditLogResponse])
def get_audits(
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Lists compliance access audit timelines."""
    entries = _compliance_repo.get_audit_entries(x_tenant_id)
    return [
        AuditLogResponse(
            user_id=e.user_id,
            resource_id=e.resource_id,
            action=e.action,
            justification=e.justification,
            timestamp=e.timestamp
        ) for e in entries
    ]
