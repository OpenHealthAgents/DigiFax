"""
reporting_controller.py
FastAPI controller routing scheduled report configurations and instant file generations.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from src.application.use_cases.reporting.configure_report_schedule import ConfigureReportScheduleUseCase
from src.application.use_cases.reporting.generate_report import GenerateReportUseCase
from src.infrastructure.persistence.in_memory_report_repository import InMemoryReportRepository
from src.infrastructure.delivery.local_email_mailer import LocalEmailMailer

router = APIRouter(prefix="/api/reporting", tags=["Reporting Management"])

_report_repo = InMemoryReportRepository()
_email_mailer = LocalEmailMailer()


# --- REQUEST & RESPONSE SCHEMAS ---

class ScheduleReportRequest(BaseModel):
    report_id: str = Field(..., description="Unique ID reference to set up or modify scheduling rules")
    report_type: str = Field(..., description="OCR_ACCURACY, AI_ACCURACY, FHIR_VALIDATION, PRODUCTIVITY, etc.")
    cron_expression: str = Field(..., description="Cron scheduling expression, e.g. '0 9 * * 1' for weekly Monday reports")
    recipient_email: str = Field(..., description="Email address where PDF/Excel/CSV links will be delivered")
    file_format: str = Field(..., description="CSV, EXCEL, PDF")
    enabled: bool = True


class GenerateReportRequest(BaseModel):
    report_type: str = Field(..., description="The clinical dataset metric to compile")
    file_format: str = Field(..., description="CSV, EXCEL, PDF")
    recipient_email: Optional[str] = Field(None, description="Optional target email address to notify on complete")


class ReportConfigResponse(BaseModel):
    report_id: str
    tenant_id: str
    report_type: str
    cron_expression: str
    recipient_email: str
    file_format: str
    enabled: bool


class GeneratedReportResponse(BaseModel):
    report_id: str
    tenant_id: str
    report_type: str
    file_format: str
    file_url: str
    data_summary: Dict[str, Any]
    generated_at: str


# --- ROUTERS ---

@router.post("/schedule", response_model=ReportConfigResponse, status_code=status.HTTP_200_OK)
def configure_schedule(
    req: ScheduleReportRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Configures or updates a report delivery schedule."""
    use_case = ConfigureReportScheduleUseCase(_report_repo)
    try:
        config = use_case.execute(
            report_id=req.report_id,
            tenant_id=x_tenant_id,
            report_type=req.report_type,
            cron_expression=req.cron_expression,
            recipient_email=req.recipient_email,
            file_format=req.file_format,
            enabled=req.enabled
        )
        return ReportConfigResponse(
            report_id=config.report_id,
            tenant_id=config.tenant_id,
            report_type=config.report_type,
            cron_expression=config.schedule.cron_expression,
            recipient_email=config.schedule.recipient_email,
            file_format=config.schedule.file_format,
            enabled=config.schedule.enabled
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate", response_model=GeneratedReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    req: GenerateReportRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Compiles statistics data and registers download file URL paths instantly."""
    use_case = GenerateReportUseCase(_report_repo, _email_mailer)
    try:
        report = use_case.execute(
            tenant_id=x_tenant_id,
            report_type=req.report_type,
            file_format=req.file_format,
            recipient_email=req.recipient_email
        )
        return GeneratedReportResponse(
            report_id=report.report_id,
            tenant_id=report.tenant_id,
            report_type=report.report_type,
            file_format=report.file_format,
            file_url=report.file_url,
            data_summary=report.data_summary,
            generated_at=report.generated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list", response_model=List[GeneratedReportResponse], status_code=status.HTTP_200_OK)
def list_reports(
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
) -> Any:
    """Lists past generated reports historical log files."""
    reports = _report_repo.list_generated_reports(x_tenant_id)
    return [
        GeneratedReportResponse(
            report_id=r.report_id,
            tenant_id=r.tenant_id,
            report_type=r.report_type,
            file_format=r.file_format,
            file_url=r.file_url,
            data_summary=r.data_summary,
            generated_at=r.generated_at
        ) for r in reports
    ]
