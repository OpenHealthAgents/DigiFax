"""
send_notification.py
Use case executing template resolution, branding injections, retries, and escalations.
"""

from datetime import datetime
import uuid
from src.application.ports.inotification_repository import INotificationRepository
from src.application.ports.inotification_dispatcher_port import INotificationDispatcherPort
from src.domain.notification.entities import NotificationRequest
from src.domain.notification.value_objects import DeliveryLog, EscalationRule


class SendNotificationUseCase:
    """
    Usecase executing notification dispatches over email, SMS, Slack, Webhooks, and Teams.
    """

    def __init__(
        self,
        repo: INotificationRepository,
        dispatcher: INotificationDispatcherPort
    ) -> None:
        self.repo = repo
        self.dispatcher = dispatcher

    def execute(
        self,
        tenant_id: str,
        recipient_id: str,
        template_id: str,
        template_params: dict,
        channels: list[str],
        escalation_rules: list[dict] = None
    ) -> NotificationRequest:
        """Resolves template placeholders, wraps branding headers/footers, and dispatches via channels."""
        # 1. Resolve tenant branding details
        config = self.repo.get_config(tenant_id)
        header = config.branding_header if config else ""
        footer = config.branding_footer if config else ""

        # 2. Resolve template values
        subject = "MedIngest Update"
        body = f"Clinical update notice parameters: {template_params}"
        if config and template_id in config.templates:
            tpl = config.templates[template_id]
            body_text = tpl.body_template
            for k, v in template_params.items():
                body_text = body_text.replace(f"{{{{{k}}}}}", str(v))
            body = f"{header}\n\n{body_text}\n\n{footer}".strip()
            subject = tpl.subject_template
            for k, v in template_params.items():
                subject = subject.replace(f"{{{{{k}}}}}", str(v))

        # 3. Create request aggregate
        notification_id = f"not-{tenant_id}-{uuid.uuid4().hex[:8]}"
        rules = []
        if escalation_rules:
            for r in escalation_rules:
                rules.append(
                    EscalationRule(
                        delay_minutes=r["delay_minutes"],
                        next_channel=r["next_channel"],
                        backup_recipient=r["backup_recipient"]
                    )
                )

        req = NotificationRequest(
            notification_id=notification_id,
            tenant_id=tenant_id,
            recipient_id=recipient_id,
            title=subject,
            body=body,
            channels=channels,
            escalation_rules=rules
        )

        # 4. Dispatch over each channel with retry logic
        for channel in channels:
            success = False
            error_message = None
            retry_count = 0
            max_retries = 3

            while retry_count < max_retries and not success:
                try:
                    if channel == "EMAIL":
                        success = self.dispatcher.dispatch_email(recipient_id, subject, body)
                    elif channel == "SMS":
                        success = self.dispatcher.dispatch_sms(recipient_id, body)
                    elif channel == "WEBHOOK":
                        success = self.dispatcher.dispatch_webhook(recipient_id, {"title": subject, "body": body})
                    elif channel == "SLACK":
                        success = self.dispatcher.dispatch_slack(recipient_id, body)
                    elif channel == "TEAMS":
                        success = self.dispatcher.dispatch_teams(recipient_id, body)
                    else:
                        success = True  # Fallback
                except Exception as e:
                    error_message = str(e)
                    success = False

                if not success:
                    retry_count += 1
                else:
                    break

            log = DeliveryLog(
                dispatch_time=datetime.now().isoformat(),
                channel=channel,
                status="DELIVERED" if success else "FAILED",
                error_message=None if success else (error_message or "Gateway timeout"),
                retry_count=retry_count
            )
            req.add_delivery_log(log)

        # 5. Handle escalation backup triggers if all primary channels fail
        if req.status == "FAILED" and req.escalation_rules:
            esc = req.escalation_rules[0]
            success = False
            try:
                if esc.next_channel == "EMAIL":
                    success = self.dispatcher.dispatch_email(esc.backup_recipient, f"[ESCALATED] {subject}", body)
                elif esc.next_channel == "SMS":
                    success = self.dispatcher.dispatch_sms(esc.backup_recipient, body)
            except Exception as e:
                pass
            
            esc_log = DeliveryLog(
                dispatch_time=datetime.now().isoformat(),
                channel=esc.next_channel,
                status="DELIVERED" if success else "FAILED",
                error_message=None if success else "Escalation delivery failure",
                retry_count=0
            )
            req.add_delivery_log(esc_log)

        self.repo.save_request(req)
        return req
