"""
isearch_service.py
Outbound port representing OpenSearch index & query services.
"""

import abc

from src.domain.search.models import SearchDocument, SearchResult


class ISearchService(abc.ABC):
    """
    Abstract outbound port representing OpenSearch index & query services.

    Purpose:
        Define secure keyword/vector clinical retrieval functions.
    Business Reasoning:
        Clinical search engines must enforce tenant-aware boundaries to prevent cross-tenant exposure.
    """

    @abc.abstractmethod
    def index_document(self, doc: SearchDocument) -> None:
        """Indexes a clinical document with full text and vector embeddings."""
        pass

    @abc.abstractmethod
    def keyword_search(self, query: str, tenant_id: str, limit: int = 10) -> list[SearchResult]:
        """
        Performs full-text keyword retrieval scoped strictly to a tenant ID.

        Inputs:
            query (str): Keyword query search text.
            tenant_id (str): Filtering tenant namespace.
            limit (int): Cap on returned records count.
        Outputs:
            list[SearchResult]: Truncated list of matching items.
        """
        pass

    @abc.abstractmethod
    def vector_search(self, query_vector: list[float], tenant_id: str, limit: int = 10) -> list[SearchResult]:
        """
        Performs k-NN vector match retrieval using embeddings filtered by tenant ID.

        Inputs:
            query_vector (list): Float embedding vectors.
            tenant_id (str): Filtering tenant namespace.
            limit (int): k matches.
        Outputs:
            list[SearchResult]: Nearest neighbors results list.
        """
        pass
