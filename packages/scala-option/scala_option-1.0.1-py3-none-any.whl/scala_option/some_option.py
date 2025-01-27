from typing import Callable, Union
from .none_option import none
from .option import Option

class SomeOption[T](Option[T]):

    def __init__(self, value: T) -> Option[T]:
        self._value = value

    def __repr__(self) -> str:
        return f"some({self._value})"

    def get(self) -> T:
        return self._value

    def is_empty(self) -> bool:
        return False
    
    def non_empty(self) -> bool:
        return True

    def get_or_else(self, default: Union[T, Callable[[], T]]) -> T:
        return self._value

    def or_else(self, alternative: Callable[[], Option[T]]) -> Option[T]:
        return self

    def map[U](self, f: Callable[[T], U]) -> 'SomeOption[U]':
        return some(f(self._value))

    def flat_map[U](self, f: Callable[[T], Option[U]]) -> Option[U]:
        return f(self._value)
    
    def fold[U](self, if_empty: Callable[[], U], f: Callable[[T], U]) -> U:
        return f(self._value)

    def filter(self, p: Callable[[T], bool]) -> Option[T]:
        return self if p(self._value) else none

    def exists(self, p: Callable[[T], bool]) -> bool:
        return p(self._value)

    def contains(self, elem: T) -> bool:
        return self._value == elem

    def to_list(self) -> list[T]:
        return [self._value]

# Factory function for creating SomeOption objects
def some[T](value: T) -> Option[T]:
    """Create a SomeOption with the given value."""
    return SomeOption(value)
