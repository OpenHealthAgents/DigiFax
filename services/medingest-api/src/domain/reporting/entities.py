"""
entities.py
Domain Entities and Aggregate Roots for clinical Reporting.
"""

from datetime import datetime
from src.domain.common.entity import Entity
from src.domain.reporting.value_objects import ReportSchedule

ALLOWED_REPORT_TYPES = {
    "OCR_ACCURACY",
    "AI_ACCURACY",
    "FHIR_VALIDATION",
    "PRODUCTIVITY",
    "PROCESSING_TIME",
    "EXPORT_SUCCESS",
    "TERMINOLOGY_MAPPING",
    "COMPLIANCE",
    "USAGE",
    "AUDIT"
}


class ReportConfiguration(Entity):
    """
    Aggregate Root scoping a tenant's scheduled report criteria.
    """

    def __init__(
        self,
        report_id: str,
        tenant_id: str,
        report_type: str,
        schedule: ReportSchedule | None = None,
        created_at: str = None,
        version: int = 1
    ):
        super().__init__(id=report_id)
        self.report_id = report_id
        self.tenant_id = tenant_id
        
        if report_type not in ALLOWED_REPORT_TYPES:
            raise ValueError(f"Invalid report type: {report_type}. Must be one of {ALLOWED_REPORT_TYPES}")
        self.report_type = report_type
        
        self.schedule = schedule
        self.created_at = created_at or datetime.now().isoformat()
        self.version = version

    def update_schedule(self, schedule: ReportSchedule) -> None:
        """Schedules or updates schedule details."""
        self.schedule = schedule


class GeneratedReport(Entity):
    """
    Aggregate Root scoping an output report document record.
    """

    def __init__(
        self,
        report_id: str,
        tenant_id: str,
        report_type: str,
        file_format: str,
        file_url: str,
        data_summary: dict = None,
        generated_at: str = None,
        version: int = 1
    ):
        super().__init__(id=report_id)
        self.report_id = report_id
        self.tenant_id = tenant_id
        self.report_type = report_type
        self.file_format = file_format
        self.file_url = file_url
        self.data_summary = data_summary or {}
        self.generated_at = generated_at or datetime.now().isoformat()
        self.version = version
