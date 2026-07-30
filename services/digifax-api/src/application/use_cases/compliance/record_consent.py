"""
record_consent.py
Use case for recording patient consent settings.
"""

from src.application.ports.icompliance_repository import IComplianceRepository
from src.domain.compliance.entities import PatientConsent
from src.domain.compliance.value_objects import ConsentPolicy


class RecordPatientConsentUseCase:
    """
    Usecase registering patient opt-in / opt-out privacy consents.
    """

    def __init__(self, repo: IComplianceRepository) -> None:
        self.repo = repo

    def execute(
        self,
        tenant_id: str,
        patient_id: str,
        consent_type: str,
        scope: str,
        signed_date: str
    ) -> PatientConsent:
        """Saves patient consent policies."""
        consent = self.repo.get_consent(tenant_id, patient_id)
        if not consent:
            consent = PatientConsent(tenant_id=tenant_id, patient_id=patient_id)

        policy = ConsentPolicy(
            consent_type=consent_type,
            scope=scope,
            signed_date=signed_date
        )
        consent.set_consent_policy(policy)
        self.repo.save_consent(consent)
        return consent
