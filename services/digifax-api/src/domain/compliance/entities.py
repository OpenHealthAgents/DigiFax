"""
entities.py
Domain Entities and Aggregate Roots for Tenant compliance configurations and Patient consents.
"""

from src.domain.common.entity import Entity
from src.domain.compliance.value_objects import ComplianceRegulation, RetentionRule, ConsentPolicy


class TenantComplianceConfiguration(Entity):
    """
    Aggregate Root representing active privacy regulations and retention rules of a tenant.
    """

    def __init__(
        self,
        tenant_id: str,
        enabled_regulations: list[ComplianceRegulation] = None,
        retention_rules: list[RetentionRule] = None,
        version: int = 1
    ):
        super().__init__(id=tenant_id)
        self.tenant_id = tenant_id
        self.enabled_regulations = enabled_regulations or []
        self.retention_rules = retention_rules or []
        self.version = version

    def enable_regulation(self, reg: ComplianceRegulation) -> None:
        """Enables a privacy regulation."""
        if reg.name not in [r.name for r in self.enabled_regulations]:
            self.enabled_regulations.append(reg)

    def disable_regulation(self, reg_name: str) -> None:
        """Disables a privacy regulation."""
        self.enabled_regulations = [
            r for r in self.enabled_regulations if r.name != reg_name
        ]

    def set_retention_rule(self, rule: RetentionRule) -> None:
        """Sets or replaces a retention policy rule for a resource type."""
        self.retention_rules = [
            r for r in self.retention_rules if r.resource_type != rule.resource_type
        ]
        self.retention_rules.append(rule)


class PatientConsent(Entity):
    """
    Aggregate Root managing a patient's consent scope registry and legal hold locks.
    """

    def __init__(
        self,
        tenant_id: str,
        patient_id: str,
        consent_policies: list[ConsentPolicy] = None,
        legal_hold: bool = False,
        version: int = 1
    ):
        super().__init__(id=f"{tenant_id}:{patient_id}")
        self.tenant_id = tenant_id
        self.patient_id = patient_id
        self.consent_policies = consent_policies or []
        self.legal_hold = legal_hold
        self.version = version

    def set_consent_policy(self, policy: ConsentPolicy) -> None:
        """Sets or replaces a specific consent policy path."""
        self.consent_policies = [
            p for p in self.consent_policies if p.scope != policy.scope
        ]
        self.consent_policies.append(policy)

    def set_legal_hold(self, active: bool) -> None:
        """Applies or releases legal hold locks, restricting deletion of patient records."""
        self.legal_hold = active
