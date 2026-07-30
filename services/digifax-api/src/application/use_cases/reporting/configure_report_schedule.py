"""
configure_report_schedule.py
Use case configuring report delivery schedules.
"""

from src.application.ports.ireport_repository import IReportRepository
from src.domain.reporting.entities import ReportConfiguration
from src.domain.reporting.value_objects import ReportSchedule


class ConfigureReportScheduleUseCase:
    """
    Usecase mapping tenant cron rules for recurring compliance reports.
    """

    def __init__(self, repo: IReportRepository) -> None:
        self.repo = repo

    def execute(
        self,
        report_id: str,
        tenant_id: str,
        report_type: str,
        cron_expression: str,
        recipient_email: str,
        file_format: str,
        enabled: bool = True
    ) -> ReportConfiguration:
        """Configures or updates a report delivery schedule."""
        config = self.repo.get_configuration(tenant_id, report_id)
        schedule = ReportSchedule(
            cron_expression=cron_expression,
            recipient_email=recipient_email,
            file_format=file_format,
            enabled=enabled
        )

        if not config:
            config = ReportConfiguration(
                report_id=report_id,
                tenant_id=tenant_id,
                report_type=report_type,
                schedule=schedule
            )
        else:
            config.update_schedule(schedule)

        self.repo.save_configuration(config)
        return config
