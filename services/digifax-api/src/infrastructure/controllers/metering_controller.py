"""
metering_controller.py
FastAPI controller routing tenant usage events logging and billing summaries.
"""

from typing import Any, Dict
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from src.application.use_cases.metering.record_usage_event import RecordUsageEventUseCase
from src.application.use_cases.metering.get_usage_summary import GetUsageSummaryUseCase
from src.application.use_cases.metering.reset_billing_period import ResetBillingPeriodUseCase
from src.infrastructure.persistence.in_memory_usage_repository import InMemoryUsageRepository

router = APIRouter(prefix="/api/metering", tags=["Usage Metering"])
_usage_repo = InMemoryUsageRepository()


# --- REQUEST & RESPONSE SCHEMAS ---

class RecordEventRequest(BaseModel):
    metric_name: str = Field(..., description="The usage metric to track")
    quantity: float = Field(..., description="Quantity accrued (e.g. upload count, size in bytes)")


class ResetBillingRequest(BaseModel):
    new_start: str
    new_end: str


class UsageSummaryResponse(BaseModel):
    tenant_id: str
    billing_period_start: str
    billing_period_end: str
    metrics: Dict[str, float]
    raw_events_count: int


# --- ROUTERS ---

@router.post("/event", response_model=UsageSummaryResponse, status_code=status.HTTP_200_OK)
def record_usage_event(
    req: RecordEventRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Logs a usage event, incrementing tenant summary totals."""
    use_case = RecordUsageEventUseCase(_usage_repo)
    try:
        summary = use_case.execute(
            tenant_id=x_tenant_id,
            metric_name=req.metric_name,
            quantity=req.quantity
        )
        return UsageSummaryResponse(
            tenant_id=summary.tenant_id,
            billing_period_start=summary.billing_period_start,
            billing_period_end=summary.billing_period_end,
            metrics=summary.metrics,
            raw_events_count=len(summary.raw_events)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/summary", response_model=UsageSummaryResponse, status_code=status.HTTP_200_OK)
def get_usage_summary(
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Resolves accrued usage totals accrued during active billing schedule cycles."""
    use_case = GetUsageSummaryUseCase(_usage_repo)
    summary = use_case.execute(tenant_id=x_tenant_id)
    return UsageSummaryResponse(
        tenant_id=summary.tenant_id,
        billing_period_start=summary.billing_period_start,
        billing_period_end=summary.billing_period_end,
        metrics=summary.metrics,
        raw_events_count=len(summary.raw_events)
    )


@router.post("/reset", response_model=UsageSummaryResponse, status_code=status.HTTP_200_OK)
def reset_billing_period(
    req: ResetBillingRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Resets tenant accrued metrics for a new cycle."""
    use_case = ResetBillingPeriodUseCase(_usage_repo)
    summary = use_case.execute(
        tenant_id=x_tenant_id,
        new_start=req.new_start,
        new_end=req.new_end
    )
    return UsageSummaryResponse(
        tenant_id=summary.tenant_id,
        billing_period_start=summary.billing_period_start,
        billing_period_end=summary.billing_period_end,
        metrics=summary.metrics,
        raw_events_count=len(summary.raw_events)
    )
