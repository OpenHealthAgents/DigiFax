"""
commands.py
Data transfer object wrapping ingestion payload alongside requesting TenantContext.
"""

from src.application.common.tenant_context import TenantContext


class IngestDocumentCommand:
    """
    Carries inputs to run the document ingestion use case.

    Purpose:
        Container bundling file bytes and resolved tenant configurations.
    Business Reasoning:
        Aligns ingestion actions under context parameters.
    """

    def __init__(
        self,
        context: TenantContext,
        filename: str,
        content_type: str,
        file_bytes: bytes,
        source: str
    ):
        self.context = context
        self.filename = filename
        self.content_type = content_type
        self.file_bytes = file_bytes
        self.source = source
