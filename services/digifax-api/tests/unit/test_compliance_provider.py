"""
test_compliance_provider.py
Unit and controller integration tests verifying Compliance configurations, consent settings, and legal holds.
"""

import pytest
from fastapi.testclient import TestClient

from src.domain.compliance.value_objects import ConsentPolicy, RetentionRule, AuditLogEntry
from src.domain.compliance.entities import TenantComplianceConfiguration, PatientConsent
from src.application.use_cases.compliance.configure_compliance import ConfigureComplianceUseCase
from src.application.use_cases.compliance.record_consent import RecordPatientConsentUseCase
from src.application.use_cases.compliance.set_legal_hold import SetLegalHoldUseCase, LegalHoldException
from src.application.use_cases.compliance.request_data_deletion import RequestDataDeletionUseCase
from src.application.use_cases.compliance.request_data_export import RequestDataExportUseCase
from src.application.use_cases.compliance.record_audit_log import RecordAuditLogUseCase
from src.infrastructure.persistence.in_memory_compliance_repository import InMemoryComplianceRepository
from src.main import app


def test_compliance_value_object_validations() -> None:
    # 1. Negative retention days
    with pytest.raises(ValueError):
        RetentionRule("Patient", -1, "PURGE")

    # 2. Invalid retention action
    with pytest.raises(ValueError):
        RetentionRule("Patient", 30, "DELETE_NOW")

    # 3. Invalid consent type
    with pytest.raises(ValueError):
        ConsentPolicy("OPT_MAYBE", "CLINICAL_SHARING", "2026-07-30")

    # 4. Empty audit justifications
    with pytest.raises(ValueError):
        AuditLogEntry("user-1", "Patient:123", "READ", " ")


def test_legal_hold_restricts_deletion() -> None:
    repo = InMemoryComplianceRepository()
    legal_hold_use_case = SetLegalHoldUseCase(repo)
    delete_use_case = RequestDataDeletionUseCase(repo)

    # 1. Set legal hold to True for patient-alpha
    legal_hold_use_case.execute(tenant_id="tenant-compliance", patient_id="patient-alpha", active=True)

    # 2. Deletion request must throw LegalHoldException
    with pytest.raises(LegalHoldException):
        delete_use_case.execute(
            tenant_id="tenant-compliance",
            patient_id="patient-alpha",
            justification="GDPR Right to Deletion"
        )

    # 3. Release legal hold
    legal_hold_use_case.execute(tenant_id="tenant-compliance", patient_id="patient-alpha", active=False)

    # 4. Deletion succeeds and logs audit entry
    delete_use_case.execute(
        tenant_id="tenant-compliance",
        patient_id="patient-alpha",
        justification="GDPR Right to Deletion"
    )
    audits = repo.get_audit_entries("tenant-compliance")
    assert len(audits) == 1
    assert audits[0].action == "PURGE"
    assert audits[0].resource_id == "Patient:patient-alpha"


def test_right_to_export_reconstitution() -> None:
    repo = InMemoryComplianceRepository()
    export_use_case = RequestDataExportUseCase(repo)

    res = export_use_case.execute(
        tenant_id="tenant-compliance",
        patient_id="patient-beta",
        justification="GDPR Right to Export"
    )

    assert res["resourceType"] == "Bundle"
    assert len(res["entry"]) == 2

    # Check export audit logged
    audits = repo.get_audit_entries("tenant-compliance")
    assert len(audits) == 1
    assert audits[0].action == "EXPORT"


def test_compliance_http_endpoints() -> None:
    client = TestClient(app)

    # 1. Configure regulations
    config_res = client.post(
        "/api/compliance/config",
        headers={"X-Tenant-Id": "tenant-compliance-http"},
        json={
            "regulations": [{"name": "GDPR", "description": "European Privacy", "region": "EU"}],
            "retention_rules": [{"resource_type": "Patient", "retention_days": 365, "expiration_action": "PURGE"}]
        }
    )
    assert config_res.status_code == 200
    assert config_res.json()["enabled_regulations"][0]["name"] == "GDPR"

    # 2. Record patient consent opt-in
    consent_res = client.post(
        "/api/compliance/consent",
        headers={"X-Tenant-Id": "tenant-compliance-http"},
        json={
            "patient_id": "pat-100",
            "consent_type": "OPT_IN",
            "scope": "CLINICAL_SHARE",
            "signed_date": "2026-07-30"
        }
    )
    assert consent_res.status_code == 200
    assert consent_res.json()["consent_policies"][0]["consent_type"] == "OPT_IN"

    # 3. Toggle legal hold
    hold_res = client.post(
        "/api/compliance/legal-hold",
        headers={"X-Tenant-Id": "tenant-compliance-http"},
        json={"patient_id": "pat-100", "active": True}
    )
    assert hold_res.status_code == 200
    assert hold_res.json()["legal_hold"]

    # 4. Deletion fails due to legal hold conflict (409 status code!)
    del_res_fail = client.post(
        "/api/compliance/delete",
        headers={"X-Tenant-Id": "tenant-compliance-http"},
        json={"patient_id": "pat-100", "justification": "Purge requested"}
    )
    assert del_res_fail.status_code == 409

    # 5. Clear legal hold
    client.post(
        "/api/compliance/legal-hold",
        headers={"X-Tenant-Id": "tenant-compliance-http"},
        json={"patient_id": "pat-100", "active": False}
    )

    # 6. Deletion now succeeds
    del_res_success = client.post(
        "/api/compliance/delete",
        headers={"X-Tenant-Id": "tenant-compliance-http"},
        json={"patient_id": "pat-100", "justification": "Purge requested"}
    )
    assert del_res_success.status_code == 200

    # 7. Get audits list
    audit_res = client.get(
        "/api/compliance/audit",
        headers={"X-Tenant-Id": "tenant-compliance-http"}
    )
    assert audit_res.status_code == 200
    assert len(audit_res.json()) >= 1
    assert any(a["action"] == "PURGE" for a in audit_res.json())
