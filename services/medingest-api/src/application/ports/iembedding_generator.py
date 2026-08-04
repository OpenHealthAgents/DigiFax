import abc


class IEmbeddingGenerator(abc.ABC):
    """Abstract outbound port representing LLM semantic vector embedding engines."""

    @abc.abstractmethod
    def generate_embedding(self, text: str) -> list[float]:
        """Translates text strings into floating-point semantic embeddings."""
        pass
