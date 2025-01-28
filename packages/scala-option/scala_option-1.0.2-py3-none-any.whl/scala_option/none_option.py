from typing import Callable, Union
from .exceptions import NoSuchElementException
from .option import Option

class NoneOption(Option[None]):
    def __repr__(self) -> str:
        return "none"

    def get(self) -> None:
        raise NoSuchElementException("Called get on NoneOption")

    def is_empty(self) -> bool:
        return True

    def non_empty(self) -> bool:
        return False

    def get_or_else[T](self, default: Union[T, Callable[[], T]]) -> T:
        return default() if callable(default) else default

    def or_else[T](self, alternative: Callable[[], Option[T]]) -> Option[T]:
        return alternative()

    def map[T, U](self, f: Callable[[T], U]) -> 'NoneOption':
        return none

    def flat_map[T](self, f: Callable[[T], None]) -> 'NoneOption':
        return none

    def fold[T, U](self, if_empty: Callable[[], U], f: Callable[[T], U]) -> U:
        return if_empty()

    def filter[T](self, p: Callable[[T], bool]) -> 'NoneOption':
        return none

    def exists[T](self, p: Callable[[T], bool]) -> bool:
        return False

    def contains[T](self, elem: T) -> bool:
        return False

    def to_list[T](self) -> list[T]:
        return []

none: NoneOption = NoneOption()
"""Singleton NoneOption instance"""
