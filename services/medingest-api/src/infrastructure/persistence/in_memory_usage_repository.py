"""
in_memory_usage_repository.py
In-memory persistence adapter for TenantUsageSummary.
"""

from src.application.ports.iusage_metering_repository import IUsageMeteringRepository
from src.domain.metering.entities import TenantUsageSummary
from src.domain.metering.value_objects import MeteredMetric
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryUsageRepository(BaseInMemoryRepository, IUsageMeteringRepository):
    """
    Thread-safe in-memory adapter storing TenantUsageSummary records.
    """

    def __init__(self) -> None:
        super().__init__()

    def save_usage_summary(self, summary: TenantUsageSummary) -> None:
        """Saves usage summary statistics for a tenant."""
        record_data = {
            "id": summary.tenant_id,
            "tenant_id": summary.tenant_id,
            "billing_period_start": summary.billing_period_start,
            "billing_period_end": summary.billing_period_end,
            "metrics": dict(summary.metrics),
            "raw_events": [
                {
                    "metric_name": e.metric_name,
                    "quantity": e.quantity,
                    "timestamp": e.timestamp
                } for e in summary.raw_events
            ],
            "version": summary.version
        }
        with self._lock:
            # Overwrite directly to allow thread-safe config updates
            self._records[summary.tenant_id] = record_data

    def get_usage_summary(self, tenant_id: str) -> TenantUsageSummary | None:
        """Loads usage summary statistics for a tenant."""
        record = self._get_record_by_id(tenant_id, tenant_id)
        if not record:
            return None

        events = [
            MeteredMetric(
                metric_name=e["metric_name"],
                quantity=e["quantity"],
                timestamp=e["timestamp"]
            ) for e in record["raw_events"]
        ]

        return TenantUsageSummary(
            tenant_id=record["tenant_id"],
            billing_period_start=record["billing_period_start"],
            billing_period_end=record["billing_period_end"],
            metrics=record["metrics"],
            raw_events=events,
            version=record["version"]
        )
