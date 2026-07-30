"""
icompliance_repository.py
Outbound port repository interface for compliance settings, consent registries, and audit logs.
"""

from abc import ABC, abstractmethod
from src.domain.compliance.entities import TenantComplianceConfiguration, PatientConsent
from src.domain.compliance.value_objects import AuditLogEntry


class IComplianceRepository(ABC):
    """
    Interface for persistence of compliance configurations, patient consent settings, and audit logs.
    """

    @abstractmethod
    def save_configuration(self, config: TenantComplianceConfiguration) -> None:
        """Saves compliance configuration settings for a tenant."""
        pass

    @abstractmethod
    def get_configuration(self, tenant_id: str) -> TenantComplianceConfiguration | None:
        """Loads compliance configuration settings for a tenant."""
        pass

    @abstractmethod
    def save_consent(self, consent: PatientConsent) -> None:
        """Saves patient consent policies."""
        pass

    @abstractmethod
    def get_consent(self, tenant_id: str, patient_id: str) -> PatientConsent | None:
        """Loads patient consent policies."""
        pass

    @abstractmethod
    def save_audit_entry(self, tenant_id: str, entry: AuditLogEntry) -> None:
        """Appends a compliance audit access log entry."""
        pass

    @abstractmethod
    def get_audit_entries(self, tenant_id: str, limit: int = 100) -> list[AuditLogEntry]:
        """Lists compliance audit logs for clinical reporting."""
        pass
