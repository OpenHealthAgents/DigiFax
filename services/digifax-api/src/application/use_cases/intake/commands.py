"""
commands.py
Data transfer object carrying ingestion parameters scoped by tenant.
"""

class IngestDocumentCommand:
    """
    Carries inputs to run the document ingestion use case.

    Purpose:
        Wrap request parameters into a type-safe object.
    Business Reasoning:
        Decouples FastAPI controller protocols from core application use cases.
    Inputs:
        tenant_id (str): Associated requesting tenant identifier.
        filename (str): Source filename.
        content_type (str): MIME file type.
        file_bytes (bytes): Raw binary document content.
        source (str): Upload pathway.
    Outputs:
        An IngestDocumentCommand instance.
    Assumptions:
        None.
    Edge Cases:
        None.
    """

    def __init__(
        self,
        tenant_id: str,
        filename: str,
        content_type: str,
        file_bytes: bytes,
        source: str
    ):
        if not tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")
        self.tenant_id = tenant_id
        self.filename = filename
        self.content_type = content_type
        self.file_bytes = file_bytes
        self.source = source
