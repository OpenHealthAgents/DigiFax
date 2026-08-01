"""
request_data_export.py
Use case executing GDPR right to export formatting patient bundles.
"""

from typing import Any
from src.application.ports.icompliance_repository import IComplianceRepository
from src.domain.compliance.value_objects import AuditLogEntry


class RequestDataExportUseCase:
    """
    Usecase packing and exporting patient clinical resources in standard json layout.
    """

    def __init__(self, repo: IComplianceRepository) -> None:
        self.repo = repo

    def execute(self, tenant_id: str, patient_id: str, justification: str) -> dict[str, Any]:
        """Packs patient files and records audit access logs."""
        # Logs audit entry
        audit_entry = AuditLogEntry(
            user_id="compliance-officer",
            resource_id=f"Patient:{patient_id}",
            action="EXPORT",
            justification=justification
        )
        self.repo.save_audit_entry(tenant_id, audit_entry)

        # Reconstitute mock patient bundle export
        return {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 2,
            "entry": [
                {
                    "fullUrl": f"http://medingest.io/fhir/Patient/{patient_id}",
                    "resource": {
                        "resourceType": "Patient",
                        "id": patient_id,
                        "gender": "unknown"
                    }
                },
                {
                    "fullUrl": "http://medingest.io/fhir/Observation/obs-999",
                    "resource": {
                        "resourceType": "Observation",
                        "id": "obs-999",
                        "status": "final",
                        "subject": {"reference": f"Patient/{patient_id}"}
                    }
                }
            ]
        }
