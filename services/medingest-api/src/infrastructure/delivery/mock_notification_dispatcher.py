"""
mock_notification_dispatcher.py
In-memory mock Notification Dispatcher adapter.
"""

from src.application.ports.inotification_dispatcher_port import INotificationDispatcherPort


class MockNotificationDispatcher(INotificationDispatcherPort):
    """
    Mock dispatcher logging clinical alerts deliveries.
    """

    def __init__(self) -> None:
        self.dispatched_events: list[dict] = []

    def dispatch_email(self, to_address: str, subject: str, body: str) -> bool:
        """Mock dispatches email. Fails if recipient holds 'fail'."""
        if "fail" in to_address:
            raise RuntimeError("Email gateway down")
        self.dispatched_events.append({"channel": "EMAIL", "to": to_address, "body": body})
        return True

    def dispatch_sms(self, to_number: str, body: str) -> bool:
        """Mock dispatches SMS. Fails if recipient holds 'fail'."""
        if "fail" in to_number:
            return False
        self.dispatched_events.append({"channel": "SMS", "to": to_number, "body": body})
        return True

    def dispatch_webhook(self, url: str, payload: dict) -> bool:
        """Mock dispatches Webhook."""
        self.dispatched_events.append({"channel": "WEBHOOK", "url": url, "payload": payload})
        return True

    def dispatch_slack(self, webhook_url: str, text: str) -> bool:
        """Mock dispatches Slack."""
        self.dispatched_events.append({"channel": "SLACK", "url": webhook_url, "text": text})
        return True

    def dispatch_teams(self, webhook_url: str, text: str) -> bool:
        """Mock dispatches MS Teams."""
        self.dispatched_events.append({"channel": "TEAMS", "url": webhook_url, "text": text})
        return True
