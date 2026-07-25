from typing import Any

from src.domain.common.value_object import ValueObject


class SearchDocument(ValueObject):
    """Container schema for documents indexed in OpenSearch."""

    def __init__(
        self,
        document_id: str,
        ocr_text: str,
        entities: dict[str, Any],
        fhir_resources: list[dict[str, Any]],
        audit_logs: list[str],
        embedding: list[float] | None = None
    ):
        self.document_id = document_id
        self.ocr_text = ocr_text
        self.entities = entities
        self.fhir_resources = fhir_resources
        self.audit_logs = audit_logs
        self.embedding = embedding or []


class SearchResult(ValueObject):
    """Represents a single query match containing match scores and text snippets."""

    def __init__(
        self,
        document_id: str,
        score: float,
        highlights: dict[str, list[str]],
        metadata: dict[str, Any]
    ):
        self.document_id = document_id
        self.score = score
        self.highlights = highlights
        self.metadata = metadata
