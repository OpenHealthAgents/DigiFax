"""
in_memory_event_bus.py
In-memory event bus adapter enforcing consumer-level tenant boundary scopes.
"""

from typing import Callable
from src.domain.common.domain_event import DomainEvent
from src.domain.common.event_bus import IEventBus


class InMemoryEventBus(IEventBus):
    """
    In-memory event bus adapter capturing published events and dispatching to tenant-aware consumers.

    Purpose:
        Verify asynchronous messaging isolation.
    Business Reasoning:
        Prevents event handlers from processing clinical events from other tenants.
    """

    def __init__(self) -> None:
        self.published_events: list[DomainEvent] = []
        # Maps event types -> list of (handler_callback, consumer_tenant_id_or_none)
        self._subscribers: dict[type, list[tuple[Callable[[DomainEvent], None], str | None]]] = {}

    def subscribe(
        self,
        event_type: type,
        handler: Callable[[DomainEvent], None],
        consumer_tenant_id: str | None = None
    ) -> None:
        """
        Registers a subscriber handler with a target tenant scoping boundary.

        Purpose:
            Subscribe to event feeds.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append((handler, consumer_tenant_id))

    def publish(self, event: DomainEvent) -> None:
        """
        Publishes a single event, triggering subscribers and enforcing consumer scoping boundaries.

        Purpose:
            Dispatch events.
        Assumptions:
            None.
        Edge Cases:
            Raises PermissionError if a tenant-scoped subscriber receives cross-tenant event data.
        """
        self.published_events.append(event)
        
        event_type = type(event)
        if event_type in self._subscribers:
            for handler, consumer_tenant_id in self._subscribers[event_type]:
                # Enforce consumer tenant scoping guard
                if consumer_tenant_id is not None and event.tenant_id != consumer_tenant_id:
                    raise PermissionError(
                        f"Cross-tenant event consumption blocked: "
                        f"event belongs to {event.tenant_id}, consumer scoped to {consumer_tenant_id}"
                    )
                handler(event)

    def publish_batch(self, events: list[DomainEvent]) -> None:
        """Publishes multiple events sequentially."""
        for event in events:
            self.publish(event)

    def clear(self) -> None:
        """Clear published events history and subscriptions."""
        self.published_events.clear()
        self._subscribers.clear()
