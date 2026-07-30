"""
test_notification_provider.py
Unit and controller integration tests verifying templates resolving, retries logging, and escalation backup routing.
"""

import pytest
from fastapi.testclient import TestClient

from src.domain.notification.value_objects import NotificationTemplate, EscalationRule, DeliveryLog
from src.domain.notification.entities import TenantNotificationConfig, NotificationRequest
from src.application.use_cases.notification.configure_notification_settings import ConfigureNotificationSettingsUseCase
from src.application.use_cases.notification.send_notification import SendNotificationUseCase
from src.infrastructure.persistence.in_memory_notification_repository import InMemoryNotificationRepository
from src.infrastructure.delivery.mock_notification_dispatcher import MockNotificationDispatcher
from src.main import app


def test_notification_value_object_validations() -> None:
    # 1. Invalid Template
    with pytest.raises(ValueError):
        NotificationTemplate(" ", "Subject", "Body")

    # 2. Negative escalation delays
    with pytest.raises(ValueError):
        EscalationRule(-5, "EMAIL", "backup@digifax.io")

    # 3. Invalid escalation channel
    with pytest.raises(ValueError):
        EscalationRule(10, "TELEPHONE", "backup@digifax.io")


def test_notifications_accrual_and_escalations() -> None:
    repo = InMemoryNotificationRepository()
    dispatcher = MockNotificationDispatcher()

    config_use_case = ConfigureNotificationSettingsUseCase(repo)
    send_use_case = SendNotificationUseCase(repo, dispatcher)

    tenant_id = "tenant-notify-test"

    # 1. Save config with templates & branding
    config_use_case.execute(
        tenant_id=tenant_id,
        templates=[
            {
                "template_id": "tpl_alert",
                "subject_template": "URGENT: Patient {{patient_name}}",
                "body_template": "Dear Practitioner, please review faxes intake for {{patient_name}}."
            }
        ],
        branding_header="OpenHealth Header",
        branding_footer="OpenHealth Footer"
    )

    # 2. Test successful EMAIL dispatch
    req = send_use_case.execute(
        tenant_id=tenant_id,
        recipient_id="doctor@digifax.io",
        template_id="tpl_alert",
        template_params={"patient_name": "John Doe"},
        channels=["EMAIL"]
    )
    assert req.status == "COMPLETED"
    assert req.title == "URGENT: Patient John Doe"
    assert "OpenHealth Header" in req.body
    assert "Dear Practitioner" in req.body
    assert len(req.delivery_logs) == 1
    assert req.delivery_logs[0].retry_count == 0

    # 3. Test failed primary channel routing with retries and escalation trigger
    # Recipient 'fail@fail.com' triggers gateway failures
    req_fail = send_use_case.execute(
        tenant_id=tenant_id,
        recipient_id="fail@fail.com",
        template_id="tpl_alert",
        template_params={"patient_name": "John Doe"},
        channels=["EMAIL"],
        escalation_rules=[
            {
                "delay_minutes": 5,
                "next_channel": "EMAIL",
                "backup_recipient": "backup@digifax.io"
            }
        ]
    )
    # The primary fails (retry 3 times), escalation succeeds on backup
    assert len(req_fail.delivery_logs) == 2  # Primary log + Escalation log
    assert req_fail.delivery_logs[0].status == "FAILED"
    assert req_fail.delivery_logs[0].retry_count == 3  # Max retries
    assert req_fail.delivery_logs[1].status == "DELIVERED"  # Escalation backup succeeds


def test_notification_http_endpoints() -> None:
    client = TestClient(app)

    # 1. Config settings endpoint
    config_res = client.post(
        "/api/notifications/config",
        headers={"X-Tenant-Id": "tenant-notify-http"},
        json={
            "branding_header": "Clinic Welcome Banner",
            "branding_footer": "Clinic Footer Banner",
            "templates": [
                {
                    "template_id": "clinical_notice",
                    "subject_template": "Notice for {{doctor}}",
                    "body_template": "Update regarding clinic workspace."
                }
            ]
        }
    )
    assert config_res.status_code == 200
    assert config_res.json()["templates_count"] == 1

    # 2. Send notification endpoint
    send_res = client.post(
        "/api/notifications/send",
        headers={"X-Tenant-Id": "tenant-notify-http"},
        json={
            "recipient_id": "kalyan@openhealth.org",
            "template_id": "clinical_notice",
            "template_params": {"doctor": "Dr. Kalyan"},
            "channels": ["EMAIL", "SMS"]
        }
    )
    assert send_res.status_code == 201
    assert send_res.json()["status"] == "COMPLETED"
    assert "Notice for Dr. Kalyan" in send_res.json()["title"]
    assert len(send_res.json()["delivery_logs"]) == 2

    # 3. Status endpoint
    not_id = send_res.json()["notification_id"]
    status_res = client.get(
        f"/api/notifications/status?notification_id={not_id}",
        headers={"X-Tenant-Id": "tenant-notify-http"}
    )
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "COMPLETED"
