"""
local_email_mailer.py
In-memory mock SMTP mailer delivery adapter logging dispatches.
"""

from src.application.ports.iemail_delivery_port import IEmailDeliveryPort


class LocalEmailMailer(IEmailDeliveryPort):
    """
    SMTP mailer gateway adapter logging clinical diagnostic report attachments.
    """

    def __init__(self) -> None:
        self.dispatched_emails: list[dict] = []

    def send_report_email(
        self,
        recipient_email: str,
        subject: str,
        report_url: str,
        file_format: str
    ) -> None:
        """Appends email log details in cache memory."""
        self.dispatched_emails.append({
            "recipient": recipient_email,
            "subject": subject,
            "report_url": report_url,
            "format": file_format
        })
