"""
record_audit_log.py
Use case appending compliance audit logs.
"""

from src.application.ports.icompliance_repository import IComplianceRepository
from src.domain.compliance.value_objects import AuditLogEntry


class RecordAuditLogUseCase:
    """
    Usecase writing access audit logs entries.
    """

    def __init__(self, repo: IComplianceRepository) -> None:
        self.repo = repo

    def execute(
        self,
        tenant_id: str,
        user_id: str,
        resource_id: str,
        action: str,
        justification: str
    ) -> AuditLogEntry:
        """Appends audit access logs."""
        entry = AuditLogEntry(
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            justification=justification
        )
        self.repo.save_audit_entry(tenant_id, entry)
        return entry
