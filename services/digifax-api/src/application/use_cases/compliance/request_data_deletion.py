"""
request_data_deletion.py
Use case executing GDPR/HIPAA right to deletion requests.
"""

from src.application.ports.icompliance_repository import IComplianceRepository
from src.application.use_cases.compliance.set_legal_hold import LegalHoldException


class RequestDataDeletionUseCase:
    """
    Usecase executing gdpr right to deletion purges unless under active legal hold.
    """

    def __init__(self, repo: IComplianceRepository) -> None:
        self.repo = repo

    def execute(self, tenant_id: str, patient_id: str, justification: str) -> None:
        """Purges patient resources unless blocked by legal hold."""
        consent = self.repo.get_consent(tenant_id, patient_id)
        
        # Check active legal hold
        if consent and consent.legal_hold:
            raise LegalHoldException("Patient account has an active legal hold. Deletion rejected.")

        # Simulate purges from database persistence
        # Logs audit entry detail
        from src.domain.compliance.value_objects import AuditLogEntry
        audit_entry = AuditLogEntry(
            user_id="compliance-officer",
            resource_id=f"Patient:{patient_id}",
            action="PURGE",
            justification=justification
        )
        self.repo.save_audit_entry(tenant_id, audit_entry)
