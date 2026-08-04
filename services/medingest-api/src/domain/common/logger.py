import abc
from typing import Any


class ILogger(abc.ABC):
    """Interface for logger adapter to decouple domain from logging libraries."""

    @abc.abstractmethod
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None: ...

    @abc.abstractmethod
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None: ...

    @abc.abstractmethod
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None: ...

    @abc.abstractmethod
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None: ...

    @abc.abstractmethod
    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
