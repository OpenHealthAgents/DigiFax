"""
record_usage_event.py
Use case recording tenant metered metric events.
"""

from src.application.ports.iusage_metering_repository import IUsageMeteringRepository
from src.domain.metering.entities import TenantUsageSummary
from src.domain.metering.value_objects import MeteredMetric


class RecordUsageEventUseCase:
    """
    Usecase appending metric events to a tenant's summary billing records.
    """

    def __init__(self, repo: IUsageMeteringRepository) -> None:
        self.repo = repo

    def execute(self, tenant_id: str, metric_name: str, quantity: float) -> TenantUsageSummary:
        """Records a metric usage event for the tenant."""
        summary = self.repo.get_usage_summary(tenant_id)
        if not summary:
            summary = TenantUsageSummary(tenant_id=tenant_id)

        metric = MeteredMetric(metric_name=metric_name, quantity=quantity)
        summary.record_metric(metric)
        
        self.repo.save_usage_summary(summary)
        return summary
