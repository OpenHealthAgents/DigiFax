"""
in_memory_notification_repository.py
In-memory persistence adapter for TenantNotificationConfig and NotificationRequest aggregates.
"""

from src.application.ports.inotification_repository import INotificationRepository
from src.domain.notification.entities import TenantNotificationConfig, NotificationRequest
from src.domain.notification.value_objects import NotificationTemplate, EscalationRule, DeliveryLog
from src.infrastructure.persistence.base_repository import BaseInMemoryRepository


class InMemoryNotificationRepository(BaseInMemoryRepository, INotificationRepository):
    """
    Thread-safe in-memory adapter storing TenantNotificationConfig and NotificationRequest records.
    """

    def __init__(self) -> None:
        super().__init__()

    def save_config(self, config: TenantNotificationConfig) -> None:
        """Saves a tenant's notification templates and branding preferences."""
        templates_data = {
            tid: {
                "template_id": t.template_id,
                "subject_template": t.subject_template,
                "body_template": t.body_template
            } for tid, t in config.templates.items()
        }
        record_data = {
            "id": f"cfg:{config.tenant_id}",
            "tenant_id": config.tenant_id,
            "templates": templates_data,
            "branding_header": config.branding_header,
            "branding_footer": config.branding_footer,
            "version": config.version
        }
        with self._lock:
            # Overwrite directly to allow thread-safe config updates
            self._records[record_data["id"]] = record_data

    def get_config(self, tenant_id: str) -> TenantNotificationConfig | None:
        """Loads a tenant's notification templates and branding preferences."""
        cfg_key = f"cfg:{tenant_id}"
        record = self._get_record_by_id(cfg_key, tenant_id)
        if not record:
            return None

        templates = {
            tid: NotificationTemplate(
                template_id=t["template_id"],
                subject_template=t["subject_template"],
                body_template=t["body_template"]
            ) for tid, t in record["templates"].items()
        }

        return TenantNotificationConfig(
            tenant_id=record["tenant_id"],
            templates=templates,
            branding_header=record["branding_header"],
            branding_footer=record["branding_footer"],
            version=record["version"]
        )

    def save_request(self, req: NotificationRequest) -> None:
        """Saves a notification request dispatch log."""
        record_data = {
            "id": f"req:{req.tenant_id}:{req.notification_id}",
            "notification_id": req.notification_id,
            "tenant_id": req.tenant_id,
            "recipient_id": req.recipient_id,
            "title": req.title,
            "body": req.body,
            "channels": list(req.channels),
            "escalation_rules": [
                {
                    "delay_minutes": r.delay_minutes,
                    "next_channel": r.next_channel,
                    "backup_recipient": r.backup_recipient
                } for r in req.escalation_rules
            ],
            "delivery_logs": [
                {
                    "dispatch_time": l.dispatch_time,
                    "channel": l.channel,
                    "status": l.status,
                    "error_message": l.error_message,
                    "retry_count": l.retry_count
                } for l in req.delivery_logs
            ],
            "status": req.status,
            "version": req.version
        }
        with self._lock:
            self._records[record_data["id"]] = record_data

    def get_request(self, tenant_id: str, notification_id: str) -> NotificationRequest | None:
        """Loads a notification request dispatch log."""
        req_key = f"req:{tenant_id}:{notification_id}"
        record = self._get_record_by_id(req_key, tenant_id)
        if not record:
            return None

        rules = [
            EscalationRule(
                delay_minutes=r["delay_minutes"],
                next_channel=r["next_channel"],
                backup_recipient=r["backup_recipient"]
            ) for r in record["escalation_rules"]
        ]

        logs = [
            DeliveryLog(
                dispatch_time=l["dispatch_time"],
                channel=l["channel"],
                status=l["status"],
                error_message=l["error_message"],
                retry_count=l["retry_count"]
            ) for l in record["delivery_logs"]
        ]

        return NotificationRequest(
            notification_id=record["notification_id"],
            tenant_id=record["tenant_id"],
            recipient_id=record["recipient_id"],
            title=record["title"],
            body=record["body"],
            channels=record["channels"],
            escalation_rules=rules,
            delivery_logs=logs,
            status=record["status"],
            version=record["version"]
        )
