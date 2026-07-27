"""
search_orchestrator.py
Orchestrates hybrid search combining keyword matching and vector semantic matching with tenant validation.
"""

from typing import Any

from src.application.ports.iembedding_generator import IEmbeddingGenerator
from src.application.ports.isearch_service import ISearchService
from src.domain.search.models import SearchDocument


class SearchOrchestrator:
    """
    Orchestrates hybrid search combining keyword matching and vector semantic matching.

    Purpose:
        Coordinate secure multi-tenant clinical indexing and searches.
    """

    def __init__(self, search_service: ISearchService, embedding_generator: IEmbeddingGenerator):
        self.search_service = search_service
        self.embedding_generator = embedding_generator

    def index(
        self,
        doc_id: str,
        tenant_id: str,
        ocr_text: str,
        entities: dict[str, Any],
        fhir_resources: list[dict[str, Any]],
        audit_logs: list[str]
    ) -> None:
        """
        Helper to generate embeddings and index the document in OpenSearch under tenant namespaces.
        """
        # Generate the dense semantic embedding representing raw OCR text
        embedding = self.embedding_generator.generate_embedding(ocr_text)

        # Assemble the unified SearchDocument domain model containing tenant_id
        doc = SearchDocument(
            document_id=doc_id,
            tenant_id=tenant_id,
            ocr_text=ocr_text,
            entities=entities,
            fhir_resources=fhir_resources,
            audit_logs=audit_logs,
            embedding=embedding
        )
        # Dispatch to the index handler adapter
        self.search_service.index_document(doc)

    def hybrid_search(
        self,
        query: str,
        tenant_id: str,
        limit: int = 10,
        alpha: float = 0.5
    ) -> list[dict[str, Any]]:
        """
        Executes keyword and vector queries, merging results using Reciprocal Rank Fusion (RRF).
        """
        if not tenant_id or not tenant_id.strip():
            raise ValueError("tenant_id is required for hybrid search queries")

        # Fetch candidate lists. We pull twice the requested limit to ensure overlap
        kw_results = self.search_service.keyword_search(query, tenant_id=tenant_id, limit=limit * 2)

        # Generate the dense embedding vector matching user query terms
        query_vector = self.embedding_generator.generate_embedding(query)
        vec_results = self.search_service.vector_search(query_vector, tenant_id=tenant_id, limit=limit * 2)

        # RRF Rank Fusion Constant 'k'. A value of 60 is standard in information retrieval literature
        k = 60
        rrf_scores: dict[str, float] = {}
        highlights_map: dict[str, dict[str, list[str]]] = {}
        metadata_map: dict[str, dict[str, Any]] = {}

        # 1. Accumulate scores from keyword matching results list
        for rank, res in enumerate(kw_results):
            doc_id = res.document_id
            rrf_score = 1.0 / (k + (rank + 1))
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1 - alpha) * rrf_score
            highlights_map[doc_id] = res.highlights
            metadata_map[doc_id] = res.metadata

        # 2. Accumulate scores from vector matching results list
        for rank, res in enumerate(vec_results):
            doc_id = res.document_id
            rrf_score = 1.0 / (k + (rank + 1))
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + alpha * rrf_score
            if doc_id not in highlights_map:
                highlights_map[doc_id] = res.highlights
            if doc_id not in metadata_map:
                metadata_map[doc_id] = res.metadata

        # 3. Sort merged matches by consolidated RRF scores descending
        sorted_docs = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)

        # 4. Return formatted results containing scores, highlights, and source metadata
        return [
            {
                "document_id": doc_id,
                "rrf_score": score,
                "highlights": highlights_map[doc_id],
                "metadata": metadata_map[doc_id]
            }
            for doc_id, score in sorted_docs[:limit]
        ]
