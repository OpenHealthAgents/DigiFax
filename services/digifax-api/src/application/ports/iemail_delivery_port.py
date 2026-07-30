"""
iemail_delivery_port.py
Outbound port abstracting clinical email dispatch systems.
"""

from abc import ABC, abstractmethod


class IEmailDeliveryPort(ABC):
    """
    SMTP mailer dispatch gateway port.
    """

    @abstractmethod
    def send_report_email(
        self,
        recipient_email: str,
        subject: str,
        report_url: str,
        file_format: str
    ) -> None:
        """Dispatches an outbound notification containing report download parameters."""
        pass
