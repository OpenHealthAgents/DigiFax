from typing import Generic, TypeVar

T = TypeVar('T')
E = TypeVar('E')

class Result(Generic[T, E]):
    """Encloses a success value or a failure error code/message."""

    def __init__(
        self,
        is_success: bool,
        value: T | None = None,
        error: E | None = None
    ):
        if is_success and error is not None:
            raise ValueError("Success result cannot have an error.")
        if not is_success and error is None:
            raise ValueError("Failure result must have an error.")

        self._is_success = is_success
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        return self._is_success

    @property
    def is_failure(self) -> bool:
        return not self._is_success

    @property
    def value(self) -> T:
        if not self._is_success:
            raise ValueError("Cannot access value of a failure result.")
        return self._value  # type: ignore

    @property
    def error(self) -> E:
        if self._is_success:
            raise ValueError("Cannot access error of a success result.")
        return self._error  # type: ignore

    @classmethod
    def ok(cls, value: T) -> 'Result[T, E]':
        return cls(is_success=True, value=value)

    @classmethod
    def fail(cls, error: E) -> 'Result[T, E]':
        return cls(is_success=False, error=error)
