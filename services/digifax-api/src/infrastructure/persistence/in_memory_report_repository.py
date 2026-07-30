"""
in_memory_report_repository.py
In-memory persistence adapter for Report configurations and Generated report document summaries.
"""

from src.application.ports.ireport_repository import IReportRepository
from src.domain.reporting.entities import ReportConfiguration, GeneratedReport
from src.domain.reporting.value_objects import ReportSchedule
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryReportRepository(BaseInMemoryRepository, IReportRepository):
    """
    Thread-safe in-memory adapter storing ReportConfiguration and GeneratedReport records.
    """

    def __init__(self) -> None:
        super().__init__()

    def save_configuration(self, config: ReportConfiguration) -> None:
        """Saves a tenant's scheduled report criteria."""
        schedule_data = None
        if config.schedule:
            schedule_data = {
                "cron_expression": config.schedule.cron_expression,
                "recipient_email": config.schedule.recipient_email,
                "file_format": config.schedule.file_format,
                "enabled": config.schedule.enabled
            }
        
        record_data = {
            "id": f"cfg:{config.tenant_id}:{config.report_id}",
            "report_id": config.report_id,
            "tenant_id": config.tenant_id,
            "report_type": config.report_type,
            "schedule": schedule_data,
            "created_at": config.created_at,
            "version": config.version
        }
        with self._lock:
            # Overwrite directly to allow thread-safe config updates
            self._records[record_data["id"]] = record_data

    def get_configuration(self, tenant_id: str, report_id: str) -> ReportConfiguration | None:
        """Loads a tenant's scheduled report criteria."""
        cfg_key = f"cfg:{tenant_id}:{report_id}"
        record = self._get_record_by_id(cfg_key, tenant_id)
        if not record:
            return None

        schedule = None
        if record["schedule"]:
            sd = record["schedule"]
            schedule = ReportSchedule(
                cron_expression=sd["cron_expression"],
                recipient_email=sd["recipient_email"],
                file_format=sd["file_format"],
                enabled=sd["enabled"]
            )

        return ReportConfiguration(
            report_id=record["report_id"],
            tenant_id=record["tenant_id"],
            report_type=record["report_type"],
            schedule=schedule,
            created_at=record["created_at"],
            version=record["version"]
        )

    def list_configurations(self, tenant_id: str) -> list[ReportConfiguration]:
        """Lists scheduled report configurations configured by the tenant."""
        with self._lock:
            results = []
            for r in self._records.values():
                if r.get("id", "").startswith("cfg:") and r.get("tenant_id") == tenant_id:
                    schedule = None
                    if r["schedule"]:
                        sd = r["schedule"]
                        schedule = ReportSchedule(
                            cron_expression=sd["cron_expression"],
                            recipient_email=sd["recipient_email"],
                            file_format=sd["file_format"],
                            enabled=sd["enabled"]
                        )
                    results.append(
                        ReportConfiguration(
                            report_id=r["report_id"],
                            tenant_id=r["tenant_id"],
                            report_type=r["report_type"],
                            schedule=schedule,
                            created_at=r["created_at"],
                            version=r["version"]
                        )
                    )
            return results

    def save_generated_report(self, report: GeneratedReport) -> None:
        """Saves a generated report output."""
        record_data = {
            "id": f"out:{report.tenant_id}:{report.report_id}",
            "report_id": report.report_id,
            "tenant_id": report.tenant_id,
            "report_type": report.report_type,
            "file_format": report.file_format,
            "file_url": report.file_url,
            "data_summary": dict(report.data_summary),
            "generated_at": report.generated_at,
            "version": report.version
        }
        with self._lock:
            # Overwrite directly to allow thread-safe config updates
            self._records[record_data["id"]] = record_data

    def list_generated_reports(self, tenant_id: str) -> list[GeneratedReport]:
        """Lists generated report outputs for the tenant."""
        with self._lock:
            results = []
            for r in self._records.values():
                if r.get("id", "").startswith("out:") and r.get("tenant_id") == tenant_id:
                    results.append(
                        GeneratedReport(
                            report_id=r["report_id"],
                            tenant_id=r["tenant_id"],
                            report_type=r["report_type"],
                            file_format=r["file_format"],
                            file_url=r["file_url"],
                            data_summary=r["data_summary"],
                            generated_at=r["generated_at"],
                            version=r["version"]
                        )
                    )
            # Sort by generated_at descending
            results.sort(key=lambda x: x.generated_at, reverse=True)
            return results
