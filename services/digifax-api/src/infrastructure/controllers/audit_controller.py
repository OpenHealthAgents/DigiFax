"""
audit_controller.py
FastAPI controller routing audit event additions, searches, and cryptographic verifications.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from src.application.use_cases.audit.log_audit_event import LogAuditEventUseCase
from src.application.use_cases.audit.verify_audit_integrity import VerifyAuditIntegrityUseCase
from src.infrastructure.persistence.in_memory_audit_repository import InMemoryAuditRepository

router = APIRouter(prefix="/api/audit", tags=["Audit & Governance Management"])

_audit_repo = InMemoryAuditRepository()


# --- REQUEST & RESPONSE SCHEMAS ---

class LogAuditEventRequest(BaseModel):
    user_id: str = Field(..., description="Unique ID initiator")
    role: str = Field(..., description="Role profile context")
    ip_address: str = Field(..., description="Client IP origin")
    action: str = Field(..., description="CREATE, READ, UPDATE, DELETE, etc.")
    entity_type: str = Field(..., description="Modified target entity configuration")
    entity_id: str = Field(..., description="Target database ID")
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None


class AuditActorResponse(BaseModel):
    user_id: str
    role: str
    ip_address: str


class AuditPayloadResponse(BaseModel):
    action: str
    entity_type: str
    entity_id: str
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None


class AuditEventResponse(BaseModel):
    event_id: str
    tenant_id: str
    timestamp: str
    actor: AuditActorResponse
    payload: AuditPayloadResponse
    log_hash: str


class VerifyIntegrityResponse(BaseModel):
    status: str  # SECURE, TAMPERED
    verified_count: int
    tampered_event_ids: List[str]
    message: str


# --- ROUTERS ---

@router.post("/log", response_model=AuditEventResponse, status_code=status.HTTP_201_CREATED)
def log_event(
    req: LogAuditEventRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Logs a signed audit log event into immutable chain memory."""
    use_case = LogAuditEventUseCase(_audit_repo)
    try:
        event = use_case.execute(
            tenant_id=x_tenant_id,
            user_id=req.user_id,
            role=req.role,
            ip_address=req.ip_address,
            action=req.action,
            entity_type=req.entity_type,
            entity_id=req.entity_id,
            before_state=req.before_state,
            after_state=req.after_state
        )
        return AuditEventResponse(
            event_id=event.event_id,
            tenant_id=event.tenant_id,
            timestamp=event.timestamp,
            actor=AuditActorResponse(
                user_id=event.actor.user_id,
                role=event.actor.role,
                ip_address=event.actor.ip_address
            ),
            payload=AuditPayloadResponse(
                action=event.payload.action,
                entity_type=event.payload.entity_type,
                entity_id=event.payload.entity_id,
                before_state=event.payload.before_state,
                after_state=event.payload.after_state
            ),
            log_hash=event.log_hash
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search", response_model=List[AuditEventResponse], status_code=status.HTTP_200_OK)
def search_events(
    actor_id: Optional[str] = None,
    action: Optional[str] = None,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Queries audit log events with optional action type or initiator search strings."""
    events = _audit_repo.list_events(x_tenant_id, actor_id=actor_id, action=action)
    return [
        AuditEventResponse(
            event_id=e.event_id,
            tenant_id=e.tenant_id,
            timestamp=e.timestamp,
            actor=AuditActorResponse(
                user_id=e.actor.user_id,
                role=e.actor.role,
                ip_address=e.actor.ip_address
            ),
            payload=AuditPayloadResponse(
                action=e.payload.action,
                entity_type=e.payload.entity_type,
                entity_id=e.payload.entity_id,
                before_state=e.payload.before_state,
                after_state=e.payload.after_state
            ),
            log_hash=e.log_hash
        ) for e in events
    ]


@router.post("/verify", response_model=VerifyIntegrityResponse, status_code=status.HTTP_200_OK)
def verify_integrity(
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Triggers sequential re-evaluation of logs hash keys to detect tampering."""
    use_case = VerifyAuditIntegrityUseCase(_audit_repo)
    result = use_case.execute(x_tenant_id)
    return VerifyIntegrityResponse(
        status=result["status"],
        verified_count=result["verified_count"],
        tampered_event_ids=result["tampered_event_ids"],
        message=result["message"]
    )
