"""
generate_report.py
Use case compiling clinical data metrics and generating downloadable files.
"""

import uuid
from src.application.ports.ireport_repository import IReportRepository
from src.application.ports.iemail_delivery_port import IEmailDeliveryPort
from src.domain.reporting.entities import GeneratedReport


class GenerateReportUseCase:
    """
    Usecase executing clinical data compilations and emailing results.
    """

    def __init__(self, repo: IReportRepository, mailer: IEmailDeliveryPort) -> None:
        self.repo = repo
        self.mailer = mailer

    def execute(
        self,
        tenant_id: str,
        report_type: str,
        file_format: str,
        recipient_email: str | None = None
    ) -> GeneratedReport:
        """Instantly compiles report data, registers generated output, and dispatches notification emails."""
        report_id = f"rpt-{tenant_id}-{uuid.uuid4().hex[:8]}"
        file_url = f"http://medingest.io/static/reports/{report_id}.{file_format.lower()}"

        # Compile dummy data summary depending on report type
        data_summary = {
            "OCR_ACCURACY": {"average_confidence": 0.942, "processed_pages": 4820},
            "AI_ACCURACY": {"precision": 0.915, "recall": 0.890},
            "FHIR_VALIDATION": {"valid_resources": 12800, "errors_detected": 12},
            "PRODUCTIVITY": {"average_review_seconds": 45.2, "completed_reviews": 312},
            "PROCESSING_TIME": {"average_end_to_end_seconds": 12.8},
            "EXPORT_SUCCESS": {"success_rate": 0.998, "total_transmissions": 8410},
            "TERMINOLOGY_MAPPING": {"auto_approved_mappings": 941, "reviewer_decisions": 48},
            "COMPLIANCE": {"active_legal_holds": 12, "right_to_deletion_requests": 2},
            "USAGE": {"ocr_limit_capacity_pct": 0.75, "ai_limit_capacity_pct": 0.83},
            "AUDIT": {"total_key_decryptions": 481, "warnings": 0}
        }.get(report_type, {"status": "compiled"})

        report = GeneratedReport(
            report_id=report_id,
            tenant_id=tenant_id,
            report_type=report_type,
            file_format=file_format,
            file_url=file_url,
            data_summary=data_summary
        )

        self.repo.save_generated_report(report)

        # Dispatch email notification if recipient is declared
        if recipient_email:
            self.mailer.send_report_email(
                recipient_email=recipient_email,
                subject=f"MedIngest {report_type} Diagnostic Report ready",
                report_url=file_url,
                file_format=file_format
            )

        return report
