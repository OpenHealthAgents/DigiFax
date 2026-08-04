"""
test_metering_provider.py
Unit and controller integration tests verifying Usage Metering events tracking and billing cycles resets.
"""

import pytest
from fastapi.testclient import TestClient

from src.domain.metering.value_objects import MeteredMetric
from src.domain.metering.entities import TenantUsageSummary
from src.application.use_cases.metering.record_usage_event import RecordUsageEventUseCase
from src.application.use_cases.metering.get_usage_summary import GetUsageSummaryUseCase
from src.application.use_cases.metering.reset_billing_period import ResetBillingPeriodUseCase
from src.infrastructure.persistence.in_memory_usage_repository import InMemoryUsageRepository
from src.main import app


def test_metered_metric_validations() -> None:
    # 1. Unsupported metric type name
    with pytest.raises(ValueError):
        MeteredMetric(metric_name="UNSUPPORTED_METRIC", quantity=100.0)

    # 2. Negative quantity value
    with pytest.raises(ValueError):
        MeteredMetric(metric_name="AI_REQUESTS", quantity=-5.0)


def test_usage_summary_accrual_increments() -> None:
    repo = InMemoryUsageRepository()
    record_use_case = RecordUsageEventUseCase(repo)
    get_use_case = GetUsageSummaryUseCase(repo)

    tenant_id = "tenant-usage"

    # 1. Add metrics
    record_use_case.execute(tenant_id=tenant_id, metric_name="DOCUMENTS_UPLOADED", quantity=5.0)
    record_use_case.execute(tenant_id=tenant_id, metric_name="DOCUMENTS_UPLOADED", quantity=12.0)
    record_use_case.execute(tenant_id=tenant_id, metric_name="AI_REQUESTS", quantity=1000.0)

    # 2. Assert values accumulated
    summary = get_use_case.execute(tenant_id=tenant_id)
    assert summary.metrics["DOCUMENTS_UPLOADED"] == 17.0
    assert summary.metrics["AI_REQUESTS"] == 1000.0
    assert len(summary.raw_events) == 3


def test_reset_billing_period() -> None:
    repo = InMemoryUsageRepository()
    record_use_case = RecordUsageEventUseCase(repo)
    reset_use_case = ResetBillingPeriodUseCase(repo)

    tenant_id = "tenant-billing-reset"

    # 1. Add metrics
    record_use_case.execute(tenant_id=tenant_id, metric_name="OCR_REQUESTS", quantity=250.0)

    # 2. Reset period
    reset_use_case.execute(tenant_id=tenant_id, new_start="2026-08-01T00:00:00Z", new_end="2026-08-31T23:59:59Z")

    # 3. Assert metrics flushed
    summary = repo.get_usage_summary(tenant_id)
    assert summary is not None
    assert len(summary.metrics) == 0
    assert len(summary.raw_events) == 0
    assert summary.billing_period_start == "2026-08-01T00:00:00Z"


def test_metering_http_endpoints() -> None:
    client = TestClient(app)

    # 1. Record usage event (DOCUMENTS_UPLOADED)
    event_res = client.post(
        "/api/metering/event",
        headers={"X-Tenant-Id": "tenant-metering-http"},
        json={"metric_name": "DOCUMENTS_UPLOADED", "quantity": 10.0}
    )
    assert event_res.status_code == 200
    assert event_res.json()["metrics"]["DOCUMENTS_UPLOADED"] == 10.0

    # 2. Record second usage event (PAGES_PROCESSED)
    event_res2 = client.post(
        "/api/metering/event",
        headers={"X-Tenant-Id": "tenant-metering-http"},
        json={"metric_name": "PAGES_PROCESSED", "quantity": 45.0}
    )
    assert event_res2.status_code == 200
    assert event_res2.json()["metrics"]["PAGES_PROCESSED"] == 45.0
    assert event_res2.json()["raw_events_count"] == 2

    # 3. Get usage summary
    summary_res = client.get(
        "/api/metering/summary",
        headers={"X-Tenant-Id": "tenant-metering-http"}
    )
    assert summary_res.status_code == 200
    assert summary_res.json()["metrics"]["DOCUMENTS_UPLOADED"] == 10.0
    assert summary_res.json()["metrics"]["PAGES_PROCESSED"] == 45.0

    # 4. Reset billing period
    reset_res = client.post(
        "/api/metering/reset",
        headers={"X-Tenant-Id": "tenant-metering-http"},
        json={"new_start": "2026-08-01", "new_end": "2026-08-31"}
    )
    assert reset_res.status_code == 200
    assert reset_res.json()["metrics"] == {}
    assert reset_res.json()["raw_events_count"] == 0
