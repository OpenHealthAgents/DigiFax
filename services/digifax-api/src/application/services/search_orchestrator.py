from typing import Any

from src.application.ports.iembedding_generator import IEmbeddingGenerator
from src.application.ports.isearch_service import ISearchService
from src.domain.search.models import SearchDocument


class SearchOrchestrator:
    """Orchestrates hybrid search combining keyword matching and vector semantic matching.

    This service coordinates:
    1. Full-text keyword searches across traditional database fields (OCR text, audit logs).
    2. Dense vector searches using embedded representations of user query strings.
    3. Consolidated ranking using the Reciprocal Rank Fusion (RRF) algorithm to merge results
       from heterogeneous search engines without requiring raw score normalization.
    """

    def __init__(self, search_service: ISearchService, embedding_generator: IEmbeddingGenerator):
        """Initializes the orchestrator with required outbound adapters.

        Args:
            search_service: Exposes index and search query capabilities (e.g. OpenSearch).
            embedding_generator: Exposes text embedding vector generation (e.g. LiteLLM).
        """
        self.search_service = search_service
        self.embedding_generator = embedding_generator

    def index(
        self,
        doc_id: str,
        ocr_text: str,
        entities: dict[str, Any],
        fhir_resources: list[dict[str, Any]],
        audit_logs: list[str]
    ) -> None:
        """Helper to generate embeddings and index the document in OpenSearch.

        This method follows a sequential ingest workflow:
        1. Translates the raw OCR text string into a 1536-dimensional float vector.
        2. Packages the original fields, metadata, and vectors into a SearchDocument.
        3. Invokes the search service port to write the document to the active indices.

        Args:
            doc_id: Unique document identifier.
            ocr_text: Raw string text extracted by OCR layout engines.
            entities: Extracted demographic and clinical key-value observations.
            fhir_resources: List of generated FHIR R4 JSON resources.
            audit_logs: Historic log statements tracking pipeline operations.
        """
        # Generate the dense semantic embedding representing raw OCR text
        embedding = self.embedding_generator.generate_embedding(ocr_text)

        # Assemble the unified SearchDocument domain model
        doc = SearchDocument(
            document_id=doc_id,
            ocr_text=ocr_text,
            entities=entities,
            fhir_resources=fhir_resources,
            audit_logs=audit_logs,
            embedding=embedding
        )
        # Dispatch to the index handler adapter
        self.search_service.index_document(doc)

    def hybrid_search(self, query: str, limit: int = 10, alpha: float = 0.5) -> list[dict[str, Any]]:
        """Executes keyword and vector queries, merging results using Reciprocal Rank Fusion (RRF).

        The hybrid search follows these steps:
        1. Executes traditional BM25-based keyword matches across text fields.
        2. Generates semantic query vectors and retrieves nearest neighbors using cosine similarity.
        3. Merges the lists using the RRF algorithm. The RRF score for a document is computed as:
           RRF_Score(d) = (1 - alpha) * RRF_Keyword(d) + alpha * RRF_Vector(d)
           where RRF_List(d) = 1.0 / (k + rank_in_list(d))
           - 'k' is a constant parameter (default=60) that penalizes low-ranked documents.
           - 'alpha' (0.0 to 1.0) controls the relative weight of vector searches versus keyword searches.

        Args:
            query: String query matching patient records, analytes, or logs.
            limit: Maximum number of merged results to return.
            alpha: Semantic weight factor (0.5 balances keyword and vector equally).

        Returns:
            List of merged matching documents sorted by reciprocal rank score.
        """
        # Fetch candidate lists. We pull twice the requested limit to ensure overlap
        kw_results = self.search_service.keyword_search(query, limit=limit * 2)

        # Generate the dense embedding vector matching user query terms
        query_vector = self.embedding_generator.generate_embedding(query)
        vec_results = self.search_service.vector_search(query_vector, limit=limit * 2)

        # RRF Rank Fusion Constant 'k'. A value of 60 is standard in information retrieval literature
        # to prevent outlier high-ranking hits from completely dominating lower-ranked matches.
        k = 60
        rrf_scores: dict[str, float] = {}
        highlights_map: dict[str, dict[str, list[str]]] = {}
        metadata_map: dict[str, dict[str, Any]] = {}

        # 1. Accumulate scores from keyword matching results list
        for rank, res in enumerate(kw_results):
            doc_id = res.document_id
            # Compute reciprocal rank score for keyword matches
            rrf_score = 1.0 / (k + (rank + 1))
            # Scale score by keyword weighting factor (1 - alpha)
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1 - alpha) * rrf_score
            highlights_map[doc_id] = res.highlights
            metadata_map[doc_id] = res.metadata

        # 2. Accumulate scores from vector matching results list
        for rank, res in enumerate(vec_results):
            doc_id = res.document_id
            # Compute reciprocal rank score for vector nearest neighbors
            rrf_score = 1.0 / (k + (rank + 1))
            # Scale score by semantic weighting factor (alpha)
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + alpha * rrf_score
            # Retain keyword highlights if already matched, otherwise fallback to empty highlights
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

