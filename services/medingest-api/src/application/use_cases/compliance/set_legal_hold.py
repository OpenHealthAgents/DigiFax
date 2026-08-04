"""
set_legal_hold.py
Use case applying legal holds restricting patient deletions.
"""

from src.application.ports.icompliance_repository import IComplianceRepository
from src.domain.compliance.entities import PatientConsent


class SetLegalHoldUseCase:
    """
    Usecase applying or releasing legal hold lock overrides on patient accounts.
    """

    def __init__(self, repo: IComplianceRepository) -> None:
        self.repo = repo

    def execute(self, tenant_id: str, patient_id: str, active: bool) -> PatientConsent:
        """Sets legal hold state on patient profiles."""
        consent = self.repo.get_consent(tenant_id, patient_id)
        if not consent:
            consent = PatientConsent(tenant_id=tenant_id, patient_id=patient_id)

        consent.set_legal_hold(active)
        self.repo.save_consent(consent)
        return consent
class LegalHoldException(Exception):
    """Exception raised when an operation violates active legal hold constraints."""
    pass
