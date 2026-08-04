from abc import ABC
from typing import Any


class ValueObject(ABC):
    """Base class for value objects compared by structural value equality."""

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ValueObject):
            return False
        if type(self) is not type(other):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        # Convert mutable fields/dicts into frozen representations for hash
        return hash(tuple(sorted(
            (k, tuple(v) if isinstance(v, (list, set)) else v)
            for k, v in self.__dict__.items()
        )))

    def __repr__(self) -> str:
        fields = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"
