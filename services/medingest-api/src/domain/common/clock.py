import abc
from datetime import UTC, datetime


class IClock(abc.ABC):
    """Interface for time clock abstractions (useful for test mocks)."""

    @abc.abstractmethod
    def now(self) -> datetime:
        """Returns the current date and time in UTC."""
        pass


class SystemClock(IClock):
    """Default system clock implementation utilizing system time."""

    def now(self) -> datetime:
        return datetime.now(UTC)
