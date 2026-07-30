"""
entities.py
Domain Entities and Aggregate Roots for Tenant usage metering.
"""

from datetime import datetime
from src.domain.common.entity import Entity
from src.domain.metering.value_objects import MeteredMetric


class TenantUsageSummary(Entity):
    """
    Aggregate Root tracking tenant usage metrics accrued during billing cycle.
    """

    def __init__(
        self,
        tenant_id: str,
        billing_period_start: str = None,
        billing_period_end: str = None,
        metrics: dict[str, float] = None,
        raw_events: list[MeteredMetric] = None,
        version: int = 1
    ):
        super().__init__(id=tenant_id)
        self.tenant_id = tenant_id
        self.billing_period_start = billing_period_start or datetime.now().isoformat()
        self.billing_period_end = billing_period_end or datetime.now().isoformat()
        self.metrics = metrics or {}
        self.raw_events = raw_events or []
        self.version = version

    def record_metric(self, metric: MeteredMetric) -> None:
        """Appends a raw metered usage log event and increments total summary values."""
        self.raw_events.append(metric)
        current = self.metrics.get(metric.metric_name, 0.0)
        self.metrics[metric.metric_name] = current + metric.quantity

    def reset_billing_period(self, new_start: str, new_end: str) -> None:
        """Clears accrued billing metrics for next subscription schedule cycle."""
        self.billing_period_start = new_start
        self.billing_period_end = new_end
        self.metrics = {}
        self.raw_events = []
