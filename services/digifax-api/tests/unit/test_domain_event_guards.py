"""
test_domain_event_guards.py
Unit tests verifying domain event metadata parameters and consumer tenant boundary guards.
"""

import pytest

from src.domain.common.domain_event import DomainEvent
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus


class MockEvent(DomainEvent):
    """Simple mock event subclass for testing."""
    pass


def test_domain_event_metadata_attributes() -> None:
    event = MockEvent(
        aggregate_id="agg-123",
        tenant_id="tenant-123",
        organization_id="org-main",
        correlation_id="corr-abc",
        trace_id="trace-xyz",
        user_id="user-789",
        version=3
    )

    assert event.aggregate_id == "agg-123"
    assert event.tenant_id == "tenant-123"
    assert event.organization_id == "org-main"
    assert event.correlation_id == "corr-abc"
    assert event.trace_id == "trace-xyz"
    assert event.user_id == "user-789"
    assert event.version == 3
    assert event.occurred_at is not None

    with pytest.raises(ValueError):
        MockEvent("agg-123", "   ")


def test_event_bus_delivery_success() -> None:
    bus = InMemoryEventBus()
    received = []

    def handler(ev: DomainEvent) -> None:
        received.append(ev)

    # Subscribe consumer scoped to tenant-123
    bus.subscribe(MockEvent, handler, consumer_tenant_id="tenant-123")

    # Publish event belonging to tenant-123
    event = MockEvent("agg-1", "tenant-123")
    bus.publish(event)

    assert len(received) == 1
    assert received[0] == event


def test_event_bus_delivery_wildcard() -> None:
    bus = InMemoryEventBus()
    received = []

    def handler(ev: DomainEvent) -> None:
        received.append(ev)

    # Subscribe consumer with wildcard tenant scope (None)
    bus.subscribe(MockEvent, handler, consumer_tenant_id=None)

    # Publish event belonging to tenant-456
    event = MockEvent("agg-1", "tenant-456")
    bus.publish(event)

    assert len(received) == 1
    assert received[0] == event


def test_event_bus_delivery_blocked_mismatch() -> None:
    bus = InMemoryEventBus()
    received = []

    def handler(ev: DomainEvent) -> None:
        received.append(ev)

    # Subscribe consumer scoped to tenant-abc
    bus.subscribe(MockEvent, handler, consumer_tenant_id="tenant-abc")

    # Publish event belonging to tenant-xyz
    event = MockEvent("agg-1", "tenant-xyz")

    with pytest.raises(PermissionError) as exc_info:
        bus.publish(event)

    assert "Cross-tenant event consumption blocked" in str(exc_info.value)
    assert len(received) == 0


def test_event_bus_batch_and_clear() -> None:
    bus = InMemoryEventBus()
    received = []

    def handler(ev: DomainEvent) -> None:
        received.append(ev)

    bus.subscribe(MockEvent, handler)
    event1 = MockEvent("agg-1", "tenant-123")
    event2 = MockEvent("agg-2", "tenant-123")
    
    # Test batch publish
    bus.publish_batch([event1, event2])
    assert len(received) == 2
    assert len(bus.published_events) == 2

    # Test clear
    bus.clear()
    assert len(bus.published_events) == 0
    assert len(bus._subscribers) == 0

