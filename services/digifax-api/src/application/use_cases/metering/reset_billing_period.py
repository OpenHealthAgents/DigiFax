"""
reset_billing_period.py
Use case resetting billing cycles.
"""

from src.application.ports.iusage_metering_repository import IUsageMeteringRepository
from src.domain.metering.entities import TenantUsageSummary


class ResetBillingPeriodUseCase:
    """
    Usecase flushing accrued summary metrics for a new cycle.
    """

    def __init__(self, repo: IUsageMeteringRepository) -> None:
        self.repo = repo

    def execute(self, tenant_id: str, new_start: str, new_end: str) -> TenantUsageSummary:
        """Resets accrued metrics on the summary keyring billing cycles."""
        summary = self.repo.get_usage_summary(tenant_id)
        if not summary:
            summary = TenantUsageSummary(tenant_id=tenant_id)

        summary.reset_billing_period(new_start=new_start, new_end=new_end)
        self.repo.save_usage_summary(summary)
        return summary
