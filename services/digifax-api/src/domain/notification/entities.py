"""
entities.py
Domain Entities and Aggregate Roots for Tenant notification configurations and request orders.
"""

from src.domain.common.entity import Entity
from src.domain.notification.value_objects import NotificationTemplate, EscalationRule, DeliveryLog


class TenantNotificationConfig(Entity):
    """
    Aggregate Root containing templates registry and branding configurations.
    """

    def __init__(
        self,
        tenant_id: str,
        templates: dict[str, NotificationTemplate] = None,
        branding_header: str = "",
        branding_footer: str = "",
        version: int = 1
    ):
        super().__init__(id=tenant_id)
        self.tenant_id = tenant_id
        self.templates = templates or {}
        self.branding_header = branding_header
        self.branding_footer = branding_footer
        self.version = version

    def register_template(self, template: NotificationTemplate) -> None:
        """Saves a notification template layout."""
        self.templates[template.template_id] = template

    def configure_branding(self, header: str, footer: str) -> None:
        """Updates standard header and footer messages lines."""
        self.branding_header = header
        self.branding_footer = footer


class NotificationRequest(Entity):
    """
    Aggregate Root tracking a single notification dispatch request.
    """

    def __init__(
        self,
        notification_id: str,
        tenant_id: str,
        recipient_id: str,
        title: str,
        body: str,
        channels: list[str],
        escalation_rules: list[EscalationRule] = None,
        delivery_logs: list[DeliveryLog] = None,
        status: str = "PENDING",
        version: int = 1
    ):
        super().__init__(id=notification_id)
        self.notification_id = notification_id
        self.tenant_id = tenant_id
        self.recipient_id = recipient_id
        self.title = title
        self.body = body
        self.channels = channels
        self.escalation_rules = escalation_rules or []
        self.delivery_logs = delivery_logs or []
        self.status = status
        self.version = version

    def add_delivery_log(self, log: DeliveryLog) -> None:
        """Appends a tracking log entry. Updates request aggregate status."""
        self.delivery_logs.append(log)
        if log.status == "DELIVERED":
            self.status = "COMPLETED"
        elif log.status == "FAILED" and not any(l.status == "DELIVERED" for l in self.delivery_logs):
            self.status = "FAILED"
