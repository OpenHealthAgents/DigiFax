from datetime import datetime

from src.domain.common.domain_event import DomainEvent


class DocumentIngestedEvent(DomainEvent):
    """Event emitted when a document is successfully saved and registered."""

    def __init__(
        self,
        aggregate_id: str,
        filename: str,
        source: str,
        storage_path: str,
        hash_sha256: str,
        occurred_at: datetime | None = None
    ):
        super().__init__(aggregate_id, occurred_at)
        self.filename = filename
        self.source = source
        self.storage_path = storage_path
        self.hash_sha256 = hash_sha256


class DocumentIntakeFailedEvent(DomainEvent):
    """Event emitted when ingestion validation or storage fails."""

    def __init__(
        self,
        aggregate_id: str,
        filename: str,
        reason: str,
        occurred_at: datetime | None = None
    ):
        super().__init__(aggregate_id, occurred_at)
        self.filename = filename
        self.reason = reason
