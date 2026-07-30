"""
ireport_repository.py
Outbound port repository interface for clinical report configurations and outputs.
"""

from abc import ABC, abstractmethod
from src.domain.reporting.entities import ReportConfiguration, GeneratedReport


class IReportRepository(ABC):
    """
    Interface for persistence of ReportConfigurations and GeneratedReport outputs.
    """

    @abstractmethod
    def save_configuration(self, config: ReportConfiguration) -> None:
        """Saves a tenant's scheduled report criteria."""
        pass

    @abstractmethod
    def get_configuration(self, tenant_id: str, report_id: str) -> ReportConfiguration | None:
        """Loads a tenant's scheduled report criteria."""
        pass

    @abstractmethod
    def list_configurations(self, tenant_id: str) -> list[ReportConfiguration]:
        """Lists scheduled report configurations configured by the tenant."""
        pass

    @abstractmethod
    def save_generated_report(self, report: GeneratedReport) -> None:
        """Saves a generated report output."""
        pass

    @abstractmethod
    def list_generated_reports(self, tenant_id: str) -> list[GeneratedReport]:
        """Lists generated report outputs for the tenant."""
        pass
