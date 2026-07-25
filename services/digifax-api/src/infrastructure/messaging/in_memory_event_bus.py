
from src.domain.common.domain_event import DomainEvent
from src.domain.common.event_bus import IEventBus


class InMemoryEventBus(IEventBus):
    """In-memory event bus adapter capturing published events for testing."""

    def __init__(self) -> None:
        self.published_events: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.published_events.append(event)

    def publish_batch(self, events: list[DomainEvent]) -> None:
        self.published_events.extend(events)

    def clear(self) -> None:
        self.published_events.clear()
