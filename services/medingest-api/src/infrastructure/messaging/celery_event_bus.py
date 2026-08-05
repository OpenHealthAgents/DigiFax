"""
celery_event_bus.py
Celery-backed distributed event bus adapter.
"""

import json
from datetime import datetime
from src.domain.common.domain_event import DomainEvent
from src.domain.common.event_bus import IEventBus


class CeleryEventBus(IEventBus):
    """
    Asynchronous event bus that serializes domain events and dispatches them via Celery tasks.
    """

    def __init__(self) -> None:
        pass

    def _serialize_event(self, event: DomainEvent) -> str:
        """
        Helper method to serialize a DomainEvent instance into a JSON string.
        """
        # Collect base domain attributes
        data = {
            "event_type": event.__class__.__name__,
            "event_id": str(event.event_id),
            "aggregate_id": event.aggregate_id,
            "tenant_id": event.tenant_id,
            "organization_id": event.organization_id,
            "correlation_id": event.correlation_id,
            "trace_id": event.trace_id,
            "user_id": event.user_id,
            "version": event.version,
            "occurred_at": event.occurred_at.isoformat() if event.occurred_at else None
        }

        # Collect any custom attributes defined on subclasses
        payload = {}
        for key, value in event.__dict__.items():
            if key not in data and not key.startswith("_"):
                # Handle non-serializable objects (like datetime)
                if isinstance(value, datetime):
                    payload[key] = value.isoformat()
                else:
                    payload[key] = value

        data["payload"] = payload
        return json.dumps(data)

    def publish(self, event: DomainEvent) -> None:
        """
        Publishes a domain event by invoking the background Celery task.
        """
        from src.infrastructure.messaging.tasks import process_domain_event_task

        # Serialize domain event data to JSON
        event_str = self._serialize_event(event)

        # Dispatch task to background Celery worker
        process_domain_event_task.delay(event_str)

    def publish_batch(self, events: list[DomainEvent]) -> None:
        """
        Publishes a list of domain events sequentially.
        """
        for event in events:
            self.publish(event)
