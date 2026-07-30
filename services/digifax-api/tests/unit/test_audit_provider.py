"""
test_audit_provider.py
Unit and controller integration tests asserting immutable cryptographic chaining and tamper detection alerts.
"""

import pytest
from fastapi.testclient import TestClient

from src.domain.audit.value_objects import AuditActor, AuditPayload
from src.domain.audit.entities import AuditEvent
from src.application.use_cases.audit.log_audit_event import LogAuditEventUseCase
from src.application.use_cases.audit.verify_audit_integrity import VerifyAuditIntegrityUseCase
from src.infrastructure.persistence.in_memory_audit_repository import InMemoryAuditRepository
from src.main import app


def test_audit_value_object_validations() -> None:
    # 1. Unsupported audit action type
    with pytest.raises(ValueError):
        AuditPayload("UNSUPPORTED_ACTION", "FHIR_RESOURCE", "pat-101")

    # 2. Empty user ID reference
    with pytest.raises(ValueError):
        AuditActor(" ", "ADMIN", "127.0.0.1")

    # 3. Empty entity ID reference
    with pytest.raises(ValueError):
        AuditPayload("CREATE", "FHIR_RESOURCE", " ")


def test_audit_chain_and_tamper_detection() -> None:
    repo = InMemoryAuditRepository()
    log_use_case = LogAuditEventUseCase(repo)
    verify_use_case = VerifyAuditIntegrityUseCase(repo)

    tenant_id = "tenant-audit-test"

    # 1. Log 3 sequential events
    ev1 = log_use_case.execute(
        tenant_id=tenant_id,
        user_id="usr-kalyan",
        role="PRACTITIONER",
        ip_address="192.168.1.5",
        action="CREATE",
        entity_type="FHIR_RESOURCE",
        entity_id="pat-201"
    )

    ev2 = log_use_case.execute(
        tenant_id=tenant_id,
        user_id="usr-kalyan",
        role="PRACTITIONER",
        ip_address="192.168.1.5",
        action="UPDATE",
        entity_type="FHIR_RESOURCE",
        entity_id="pat-201"
    )

    ev3 = log_use_case.execute(
        tenant_id=tenant_id,
        user_id="usr-admin",
        role="ADMIN",
        ip_address="192.168.1.10",
        action="KEY_ROTATION",
        entity_type="VAULT",
        entity_id="kek-ref-99"
    )

    # Verify sequential hash calculation chaining
    assert ev2.log_hash == ev2.calculate_hash(ev1.log_hash)
    assert ev3.log_hash == ev3.calculate_hash(ev2.log_hash)

    # Verify initial integrity check passes
    initial_res = verify_use_case.execute(tenant_id)
    assert initial_res["status"] == "SECURE"
    assert initial_res["verified_count"] == 3

    # 2. Simulate database tampering by modifying the second event payload details in-place
    record_key = f"aud:{tenant_id}:{ev2.event_id}"
    repo._records[record_key]["payload"]["entity_id"] = "pat-ALTERED-ID"

    # Verify tamper detector catches the modification
    tampered_res = verify_use_case.execute(tenant_id)
    assert tampered_res["status"] == "TAMPERED"
    assert ev2.event_id in tampered_res["tampered_event_ids"]


def test_audit_http_endpoints() -> None:
    client = TestClient(app)

    # 1. Log audit event
    log_res = client.post(
        "/api/audit/log",
        headers={"X-Tenant-Id": "tenant-audit-http"},
        json={
            "user_id": "usr-admin",
            "role": "ADMIN",
            "ip_address": "127.0.0.1",
            "action": "CONFIG_CHANGE",
            "entity_type": "TENANT_CONFIG",
            "entity_id": "cfg-101"
        }
    )
    assert log_res.status_code == 201
    assert log_res.json()["payload"]["action"] == "CONFIG_CHANGE"
    assert log_res.json()["log_hash"] != ""

    # 2. Search audit logs
    search_res = client.get(
        "/api/audit/search?action=CONFIG_CHANGE",
        headers={"X-Tenant-Id": "tenant-audit-http"}
    )
    assert search_res.status_code == 200
    assert len(search_res.json()) == 1
    assert search_res.json()[0]["actor"]["user_id"] == "usr-admin"

    # 3. Verify integrity
    verify_res = client.post(
        "/api/audit/verify",
        headers={"X-Tenant-Id": "tenant-audit-http"}
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "SECURE"
