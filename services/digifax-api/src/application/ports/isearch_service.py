import abc

from src.domain.search.models import SearchDocument, SearchResult


class ISearchService(abc.ABC):
    """Abstract outbound port representing OpenSearch index & query services."""

    @abc.abstractmethod
    def index_document(self, doc: SearchDocument) -> None:
        """Indexes a clinical document with full text and vector embeddings."""
        pass

    @abc.abstractmethod
    def keyword_search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Performs full-text keyword retrieval across text/fields."""
        pass

    @abc.abstractmethod
    def vector_search(self, query_vector: list[float], limit: int = 10) -> list[SearchResult]:
        """Performs k-NN vector match retrieval using embeddings."""
        pass
