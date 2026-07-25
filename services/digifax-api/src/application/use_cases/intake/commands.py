class IngestDocumentCommand:
    """Carries inputs to run the document ingestion use case."""

    def __init__(
        self,
        filename: str,
        content_type: str,
        file_bytes: bytes,
        source: str
    ):
        self.filename = filename
        self.content_type = content_type
        self.file_bytes = file_bytes
        self.source = source
