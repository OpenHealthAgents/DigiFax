"""
terminology_controller.py
FastAPI controller routing medical terminology translation, overrides, and rollback workflows.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field

from src.infrastructure.persistence.in_memory_terminology_repository import InMemoryTerminologyRepository
from src.application.use_cases.terminology.propose_local_mapping import ProposeLocalMappingUseCase
from src.application.use_cases.terminology.approve_concept_mapping import ApproveConceptMappingUseCase
from src.application.use_cases.terminology.rollback_concept_map import RollbackConceptMapUseCase
from src.application.use_cases.terminology.get_concept_mapping import GetConceptMappingUseCase

router = APIRouter(prefix="/api/terminology", tags=["terminology"])

# Global Repo reference for routing setup
_terminology_repo = InMemoryTerminologyRepository()


# --- REQUEST/RESPONSE SCHEMAS ---
class ProposeMappingRequest(BaseModel):
    mapping_key: str = Field(..., description="Unique mapping key name")
    source_system: str = Field(..., description="Local system layout")
    source_code: str = Field(..., description="Local code")
    target_system: str = Field(..., description="Standard target system (e.g. LOINC URI)")
    target_code: str = Field(..., description="Standard code")
    preferred_display: str | None = Field(None, description="Preferred display label")


class ApproveMappingRequest(BaseModel):
    mapping_key: str
    source_system: str
    source_code: str
    target_system: str
    target_code: str


class RollbackMappingRequest(BaseModel):
    mapping_key: str
    target_version: int


# --- CONTROLLER ROUTER ENDPOINTS ---

@router.post("/mapping/propose", status_code=status.HTTP_201_CREATED)
def propose_mapping(
    req: ProposeMappingRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Proposes a new terminology map rule."""
    use_case = ProposeLocalMappingUseCase(_terminology_repo)
    try:
        res = use_case.execute(
            tenant_id=x_tenant_id,
            mapping_key=req.mapping_key,
            source_system=req.source_system,
            source_code=req.source_code,
            target_system=req.target_system,
            target_code=req.target_code,
            preferred_display=req.preferred_display
        )
        return {
            "tenant_id": res.tenant_id,
            "mapping_key": res.mapping_key,
            "version": res.version,
            "rules_count": len(res.rules)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mapping/approve")
def approve_mapping(
    req: ApproveMappingRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Approves a proposed mapping rules state."""
    use_case = ApproveConceptMappingUseCase(_terminology_repo)
    try:
        res = use_case.execute(
            tenant_id=x_tenant_id,
            mapping_key=req.mapping_key,
            source_system=req.source_system,
            source_code=req.source_code,
            target_system=req.target_system,
            target_code=req.target_code
        )
        return {
            "tenant_id": res.tenant_id,
            "mapping_key": res.mapping_key,
            "version": res.version,
            "status": "APPROVED"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mapping/rollback")
def rollback_mapping(
    req: RollbackMappingRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Restores mapping rules list back to target version index."""
    use_case = RollbackConceptMapUseCase(_terminology_repo)
    try:
        res = use_case.execute(
            tenant_id=x_tenant_id,
            mapping_key=req.mapping_key,
            target_version=req.target_version
        )
        return {
            "tenant_id": res.tenant_id,
            "mapping_key": res.mapping_key,
            "version": res.version,
            "comment": f"Rolled back to v{req.target_version}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/translate")
def translate_concept(
    mapping_key: str,
    source_system: str,
    source_code: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Resolves local source_code mapping to standard FHIRCoding format."""
    use_case = GetConceptMappingUseCase(_terminology_repo)
    coding = use_case.execute(
        tenant_id=x_tenant_id,
        mapping_key=mapping_key,
        source_system=source_system,
        source_code=source_code
    )
    if not coding:
        raise HTTPException(status_code=404, detail="No active translation mapping rule found")
    return {
        "system": coding.system,
        "code": coding.code,
        "display": coding.display
    }
