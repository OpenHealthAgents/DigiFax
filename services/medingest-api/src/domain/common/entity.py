from abc import ABC
from typing import Any

from src.domain.common.domain_event import DomainEvent


class Entity(ABC):
    """Base class for entities compared by identity."""

    def __init__(self, id: str):
        if not id:
            raise ValueError("Entity ID cannot be empty.")
        self._id = id

    @property
    def id(self) -> str:
        return self._id

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Entity):
            return False
        if type(self) is not type(other):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.id))


class AggregateRoot(Entity, ABC):
    """Base class for aggregate roots managing domain events."""

    def __init__(self, id: str):
        super().__init__(id)
        self._domain_events: list[DomainEvent] = []

    @property
    def domain_events(self) -> list[DomainEvent]:
        return self._domain_events.copy()

    def add_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        self._domain_events.clear()
