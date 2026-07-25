import abc

from src.domain.common.domain_event import DomainEvent


class IEventBus(abc.ABC):
    """Inbound/Outbound port interface for publishing domain events."""

    @abc.abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publishes a single domain event to the bus."""
        pass

    @abc.abstractmethod
    def publish_batch(self, events: list[DomainEvent]) -> None:
        """Publishes a batch of domain events to the bus."""
        pass
