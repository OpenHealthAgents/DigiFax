"""
verify_audit_integrity.py
Use case evaluating chain consistency to verify tamper detection parameters.
"""

from src.application.ports.iaudit_repository import IAuditRepository
from src.domain.audit.entities import SecurityTamperException


class VerifyAuditIntegrityUseCase:
    """
    Usecase verifying cryptographic logs chain consistency.
    """

    def __init__(self, repo: IAuditRepository) -> None:
        self.repo = repo

    def execute(self, tenant_id: str) -> dict:
        """
        Recalculates sequential SHA256 chain signatures to audit database health status.
        """
        events = self.repo.list_events(tenant_id)
        # Since list_events is sorted descending (latest first) with stable insertion order,
        # reversing it is the most robust way to recover the original oldest-to-newest sequence.
        sorted_events = list(reversed(events))

        previous_hash = "GENESIS"
        tampered_ids = []

        for e in sorted_events:
            if not e.verify_integrity(previous_hash):
                tampered_ids.append(e.event_id)
                # If we detect tampering, we flag it immediately, but keep checking remainder
                # In strict environments we raise SecurityTamperException
            previous_hash = e.log_hash

        if tampered_ids:
            return {
                "status": "TAMPERED",
                "verified_count": len(sorted_events),
                "tampered_event_ids": tampered_ids,
                "message": f"Tampering detected in {len(tampered_ids)} audit events!"
            }

        return {
            "status": "SECURE",
            "verified_count": len(sorted_events),
            "tampered_event_ids": [],
            "message": "Cryptographic integrity check succeeded. Zero modifications detected."
        }
