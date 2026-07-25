from collections.abc import Callable
from typing import Any, Generic, TypeVar

L = TypeVar('L')
R = TypeVar('R')

class Either(Generic[L, R]):
    """Represents a disjoint union value of Left (Error) or Right (Success)."""

    def __init__(self, left: L | None = None, right: R | None = None):
        if left is not None and right is not None:
            raise ValueError("Either cannot be both Left and Right.")
        if left is None and right is None:
            raise ValueError("Either must be either Left or Right.")
        self._left = left
        self._right = right

    @property
    def is_left(self) -> bool:
        return self._left is not None

    @property
    def is_right(self) -> bool:
        return self._right is not None

    @property
    def left(self) -> L:
        if not self.is_left:
            raise ValueError("Cannot access Left value of a Right Either.")
        return self._left  # type: ignore

    @property
    def right(self) -> R:
        if not self.is_right:
            raise ValueError("Cannot access Right value of a Left Either.")
        return self._right  # type: ignore

    def fold(self, left_fn: Callable[[L], Any], right_fn: Callable[[R], Any]) -> Any:
        if self.is_left:
            return left_fn(self.left)
        return right_fn(self.right)


class Left(Either[L, R], Generic[L, R]):
    """Left represents the failure/exception outcome in Either."""

    def __init__(self, value: L):
        super().__init__(left=value)


class Right(Either[L, R], Generic[L, R]):
    """Right represents the success/value outcome in Either."""

    def __init__(self, value: R):
        super().__init__(right=value)
