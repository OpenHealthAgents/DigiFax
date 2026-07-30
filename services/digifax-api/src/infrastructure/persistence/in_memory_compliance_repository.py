"""
in_memory_compliance_repository.py
In-memory persistence adapter for compliance configurations, patient consents, and audit logs.
"""

from src.application.ports.icompliance_repository import IComplianceRepository
from src.domain.compliance.entities import TenantComplianceConfiguration, PatientConsent
from src.domain.compliance.value_objects import AuditLogEntry, ComplianceRegulation, RetentionRule, ConsentPolicy
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryComplianceRepository(BaseInMemoryRepository, IComplianceRepository):
    """
    Thread-safe in-memory adapter storing compliance configurations, consents, and audit trails.
    """

    def __init__(self) -> None:
        super().__init__()

    def save_configuration(self, config: TenantComplianceConfiguration) -> None:
        """Saves compliance configuration settings for a tenant."""
        record_data = {
            "id": config.tenant_id,
            "tenant_id": config.tenant_id,
            "enabled_regulations": [
                {
                    "name": r.name,
                    "description": r.description,
                    "region": r.region
                } for r in config.enabled_regulations
            ],
            "retention_rules": [
                {
                    "resource_type": r.resource_type,
                    "retention_days": r.retention_days,
                    "expiration_action": r.expiration_action
                } for r in config.retention_rules
            ],
            "version": config.version
        }
        with self._lock:
            self._records[config.tenant_id] = record_data

    def get_configuration(self, tenant_id: str) -> TenantComplianceConfiguration | None:
        """Loads compliance configuration settings for a tenant."""
        record = self._get_record_by_id(tenant_id, tenant_id)
        if not record:
            return None

        regs = [
            ComplianceRegulation(
                name=r["name"],
                description=r["description"],
                region=r["region"]
            ) for r in record["enabled_regulations"]
        ]
        rules = [
            RetentionRule(
                resource_type=r["resource_type"],
                retention_days=r["retention_days"],
                expiration_action=r["expiration_action"]
            ) for r in record["retention_rules"]
        ]

        return TenantComplianceConfiguration(
            tenant_id=record["tenant_id"],
            enabled_regulations=regs,
            retention_rules=rules,
            version=record["version"]
        )

    def save_consent(self, consent: PatientConsent) -> None:
        """Saves patient consent policies."""
        record_data = {
            "id": consent.id,
            "tenant_id": consent.tenant_id,
            "patient_id": consent.patient_id,
            "consent_policies": [
                {
                    "consent_type": p.consent_type,
                    "scope": p.scope,
                    "signed_date": p.signed_date
                } for p in consent.consent_policies
            ],
            "legal_hold": consent.legal_hold,
            "version": consent.version
        }
        with self._lock:
            self._records[consent.id] = record_data

    def get_consent(self, tenant_id: str, patient_id: str) -> PatientConsent | None:
        """Loads patient consent policies."""
        consent_id = f"{tenant_id}:{patient_id}"
        record = self._get_record_by_id(consent_id, tenant_id)
        if not record:
            return None

        policies = [
            ConsentPolicy(
                consent_type=p["consent_type"],
                scope=p["scope"],
                signed_date=p["signed_date"]
            ) for p in record["consent_policies"]
        ]

        return PatientConsent(
            tenant_id=record["tenant_id"],
            patient_id=record["patient_id"],
            consent_policies=policies,
            legal_hold=record["legal_hold"],
            version=record["version"]
        )

    def save_audit_entry(self, tenant_id: str, entry: AuditLogEntry) -> None:
        """Appends a compliance audit access log entry."""
        audit_id = f"audit:{tenant_id}:{self._get_next_index()}"
        record_data = {
            "id": audit_id,
            "tenant_id": tenant_id,
            "user_id": entry.user_id,
            "resource_id": entry.resource_id,
            "action": entry.action,
            "justification": entry.justification,
            "timestamp": entry.timestamp,
            "version": 1
        }
        with self._lock:
            self._records[audit_id] = record_data

    def get_audit_entries(self, tenant_id: str, limit: int = 100) -> list[AuditLogEntry]:
        """Lists compliance audit logs for clinical reporting."""
        with self._lock:
            results = []
            for r in self._records.values():
                if r.get("id", "").startswith("audit:") and r.get("tenant_id") == tenant_id:
                    results.append(
                        AuditLogEntry(
                            user_id=r["user_id"],
                            resource_id=r["resource_id"],
                            action=r["action"],
                            justification=r["justification"],
                            timestamp=r["timestamp"]
                        )
                    )
            # Sort by timestamp descending
            results.sort(key=lambda x: x.timestamp, reverse=True)
            return results[:limit]

    def _get_next_index(self) -> int:
        """Helper to increment index primary key."""
        return len(self._records) + 1
