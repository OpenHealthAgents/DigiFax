"""
inotification_dispatcher_port.py
Outbound port abstracting delivery dispatchers (Email, SMS, Webhooks, Slack, Teams).
"""

from abc import ABC, abstractmethod


class INotificationDispatcherPort(ABC):
    """
    Dispatcher port abstracting third-party notification delivery gateways.
    """

    @abstractmethod
    def dispatch_email(self, to_address: str, subject: str, body: str) -> bool:
        """Dispatches an email message. Returns success status."""
        pass

    @abstractmethod
    def dispatch_sms(self, to_number: str, body: str) -> bool:
        """Dispatches an SMS message. Returns success status."""
        pass

    @abstractmethod
    def dispatch_webhook(self, url: str, payload: dict) -> bool:
        """Dispatches a JSON webhook payload. Returns success status."""
        pass

    @abstractmethod
    def dispatch_slack(self, webhook_url: str, text: str) -> bool:
        """Dispatches a Slack channel payload. Returns success status."""
        pass

    @abstractmethod
    def dispatch_teams(self, webhook_url: str, text: str) -> bool:
        """Dispatches a Microsoft Teams channel payload. Returns success status."""
        pass
