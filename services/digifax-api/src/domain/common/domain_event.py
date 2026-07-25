from abc import ABC
from datetime import UTC, datetime

from src.domain.common.uuid import UniqueId


class DomainEvent(ABC):
    """Base class for all domain events."""

    def __init__(self, aggregate_id: str, occurred_at: datetime | None = None):
        self._event_id = UniqueId.generate()
        self._aggregate_id = aggregate_id
        self._occurred_at = occurred_at or datetime.now(UTC)

    @property
    def event_id(self) -> str:
        return self._event_id

    @property
    def aggregate_id(self) -> str:
        return self._aggregate_id

    @property
    def occurred_at(self) -> datetime:
        return self._occurred_at
