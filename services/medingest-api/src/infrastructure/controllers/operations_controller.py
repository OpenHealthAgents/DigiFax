"""
operations_controller.py
FastAPI controller routing platform statuses and maintenance switches.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from src.application.use_cases.operations.toggle_maintenance_mode import ToggleMaintenanceModeUseCase
from src.application.use_cases.operations.update_platform_health import UpdatePlatformHealthUseCase
from src.infrastructure.persistence.in_memory_operations_repository import InMemoryOperationsRepository

router = APIRouter(prefix="/api/operations", tags=["Platform Operations Management"])

_operations_repo = InMemoryOperationsRepository()


# --- REQUEST & RESPONSE SCHEMAS ---

class ToggleMaintenanceRequest(BaseModel):
    enabled: bool = Field(..., description="Simulate global maintenance mode lock state")


class UpdateHealthRequest(BaseModel):
    component_name: str = Field(..., description="DATABASE, STORAGE, TEMPORAL, AI_PROVIDER, etc.")
    status: str = Field(..., description="HEALTHY, DEGRADED, DOWN")
    latency_ms: float = Field(..., description="Latency check in ms")


class UpdateFlagRequest(BaseModel):
    flag_name: str = Field(..., description="Toggle switch parameter key")
    enabled: bool = Field(..., description="New boolean value")


class HealthMetricResponse(BaseModel):
    component_name: str
    status: str
    latency_ms: float
    timestamp: str


class PlatformConfigResponse(BaseModel):
    tenant_id: str
    maintenance_mode_enabled: bool
    active_feature_flags: Dict[str, bool]
    health_metrics: Dict[str, HealthMetricResponse]


# --- ROUTERS ---

@router.post("/maintenance", response_model=PlatformConfigResponse, status_code=status.HTTP_200_OK)
def toggle_maintenance(
    req: ToggleMaintenanceRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Toggles global system-wide maintenance mode lock."""
    use_case = ToggleMaintenanceModeUseCase(_operations_repo)
    config = use_case.execute(x_tenant_id, req.enabled)
    return _build_response(config)


@router.post("/health", response_model=PlatformConfigResponse, status_code=status.HTTP_200_OK)
def log_health_metric(
    req: UpdateHealthRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Appends latency metrics checks for a platform component."""
    use_case = UpdatePlatformHealthUseCase(_operations_repo)
    try:
        config = use_case.execute_health_metric(
            tenant_id=x_tenant_id,
            component_name=req.component_name,
            status=req.status,
            latency_ms=req.latency_ms
        )
        return _build_response(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/flag", response_model=PlatformConfigResponse, status_code=status.HTTP_200_OK)
def update_feature_flag(
    req: UpdateFlagRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Modifies toggle values for a deployment feature flag."""
    use_case = UpdatePlatformHealthUseCase(_operations_repo)
    config = use_case.execute_feature_flag(x_tenant_id, req.flag_name, req.enabled)
    return _build_response(config)


@router.get("/status", response_model=PlatformConfigResponse, status_code=status.HTTP_200_OK)
def get_operations_status(
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Queries active operations, feature flags, and health check values."""
    config = _operations_repo.get_config(x_tenant_id)
    if not config:
        # Pre-seed defaults if config does not exist
        use_case = ToggleMaintenanceModeUseCase(_operations_repo)
        config = use_case.execute(x_tenant_id, False)

    return _build_response(config)


# --- HELPERS ---

def _build_response(config: Any) -> PlatformConfigResponse:
    metrics = {
        cname: HealthMetricResponse(
            component_name=m.component_name,
            status=m.status,
            latency_ms=m.latency_ms,
            timestamp=m.timestamp
        ) for cname, m in config.health_metrics.items()
    }
    return PlatformConfigResponse(
        tenant_id=config.tenant_id,
        maintenance_mode_enabled=config.maintenance_mode_enabled,
        active_feature_flags=config.active_feature_flags,
        health_metrics=metrics
    )
