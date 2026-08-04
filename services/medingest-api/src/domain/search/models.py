"""
models.py
Domain models mapping search query outcomes and indexed document schemas.
"""

from typing import Any
from src.domain.common.value_object import ValueObject


class SearchDocument(ValueObject):
    """
    Container schema for clinical documents indexed in OpenSearch.

    Purpose:
        Track document entities, embeddings, and tenant markers.
    """

    def __init__(
        self,
        document_id: str,
        tenant_id: str,
        ocr_text: str,
        entities: dict[str, Any],
        fhir_resources: list[dict[str, Any]],
        audit_logs: list[str],
        embedding: list[float] | None = None
    ):
        if not tenant_id.strip():
            raise ValueError("tenant_id is required for search indexing")
        self.document_id = document_id
        self.tenant_id = tenant_id
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
