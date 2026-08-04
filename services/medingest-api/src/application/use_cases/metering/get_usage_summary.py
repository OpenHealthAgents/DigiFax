"""
get_usage_summary.py
Use case resolving tenant accrued usage totals.
"""

from src.application.ports.iusage_metering_repository import IUsageMeteringRepository
from src.domain.metering.entities import TenantUsageSummary


class GetUsageSummaryUseCase:
    """
    Usecase loading a tenant's summary billing records.
    """

    def __init__(self, repo: IUsageMeteringRepository) -> None:
        self.repo = repo

    def execute(self, tenant_id: str) -> TenantUsageSummary:
        """Returns the accrued usage summary details for the tenant."""
        summary = self.repo.get_usage_summary(tenant_id)
        if not summary:
            summary = TenantUsageSummary(tenant_id=tenant_id)
            self.repo.save_usage_summary(summary)
        return summary
