"""
test_reporting_provider.py
Unit and controller integration tests verifying scheduled report configurations and instant generations.
"""

import pytest
from fastapi.testclient import TestClient

from src.domain.reporting.value_objects import ReportSchedule
from src.domain.reporting.entities import ReportConfiguration, GeneratedReport
from src.application.use_cases.reporting.configure_report_schedule import ConfigureReportScheduleUseCase
from src.application.use_cases.reporting.generate_report import GenerateReportUseCase
from src.infrastructure.persistence.in_memory_report_repository import InMemoryReportRepository
from src.infrastructure.delivery.local_email_mailer import LocalEmailMailer
from src.main import app


def test_report_value_object_validations() -> None:
    # 1. Invalid file format
    with pytest.raises(ValueError):
        ReportSchedule("0 9 * * *", "test@test.com", "TXT")

    # 2. Empty cron expression
    with pytest.raises(ValueError):
        ReportSchedule(" ", "test@test.com", "PDF")

    # 3. Invalid email address
    with pytest.raises(ValueError):
        ReportSchedule("0 9 * * *", "test-email-address", "EXCEL")


def test_report_entities_and_use_cases() -> None:
    repo = InMemoryReportRepository()
    mailer = LocalEmailMailer()

    configure_use_case = ConfigureReportScheduleUseCase(repo)
    generate_use_case = GenerateReportUseCase(repo, mailer)

    # 1. Configure schedule
    config = configure_use_case.execute(
        report_id="rpt-123",
        tenant_id="tenant-reporting",
        report_type="OCR_ACCURACY",
        cron_expression="0 0 * * 0",
        recipient_email="officer@openhealth.org",
        file_format="PDF"
    )
    assert config.report_id == "rpt-123"
    assert config.schedule.cron_expression == "0 0 * * 0"

    # 2. Generate report instantly and dispatch email
    report = generate_use_case.execute(
        tenant_id="tenant-reporting",
        report_type="OCR_ACCURACY",
        file_format="PDF",
        recipient_email="officer@openhealth.org"
    )
    assert report.report_type == "OCR_ACCURACY"
    assert report.file_format == "PDF"
    assert "reports/rpt-tenant-reporting-" in report.file_url

    # Check email mock delivery log
    assert len(mailer.dispatched_emails) == 1
    assert mailer.dispatched_emails[0]["recipient"] == "officer@openhealth.org"
    assert mailer.dispatched_emails[0]["format"] == "PDF"


def test_reporting_http_endpoints() -> None:
    client = TestClient(app)

    # 1. Configure schedule endpoint
    schedule_res = client.post(
        "/api/reporting/schedule",
        headers={"X-Tenant-Id": "tenant-reporting-http"},
        json={
            "report_id": "cfg-http-001",
            "report_type": "AI_ACCURACY",
            "cron_expression": "0 9 * * 1",
            "recipient_email": "admin@medingest.io",
            "file_format": "EXCEL",
            "enabled": True
        }
    )
    assert schedule_res.status_code == 200
    assert schedule_res.json()["file_format"] == "EXCEL"

    # 2. Generate report endpoint
    gen_res = client.post(
        "/api/reporting/generate",
        headers={"X-Tenant-Id": "tenant-reporting-http"},
        json={
            "report_type": "AI_ACCURACY",
            "file_format": "EXCEL",
            "recipient_email": "admin@medingest.io"
        }
    )
    assert gen_res.status_code == 201
    assert gen_res.json()["file_format"] == "EXCEL"
    assert "average_confidence" not in gen_res.json()["data_summary"]  # AI_ACCURACY is precision/recall
    assert "precision" in gen_res.json()["data_summary"]

    # 3. List reports endpoint
    list_res = client.get(
        "/api/reporting/list",
        headers={"X-Tenant-Id": "tenant-reporting-http"}
    )
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1
    assert list_res.json()[0]["report_type"] == "AI_ACCURACY"
