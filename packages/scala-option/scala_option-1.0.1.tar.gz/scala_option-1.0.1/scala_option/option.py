from abc import ABC, abstractmethod
from typing import Callable, Union

class Option[T](ABC):
    """Abstract base class for NoneOption and SomeOption."""

    @abstractmethod
    def get(self) -> T:
        """Returns the option's value."""
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        """Check if the option is empty."""
        pass
    
    @abstractmethod
    def non_empty(self) -> bool:
        """Check if the option is non-empty."""
        pass

    @abstractmethod
    def get_or_else(self, default: Union[T, Callable[[], T]]) -> T:
        """
        Returns the option's value if non-empty, otherwise returns the default.
        Supports both eager and lazy evaluation.
        """
        pass

    @abstractmethod
    def or_else(self, alternative: Callable[[], 'Option[T]']) -> 'Option[T]':
        """
        Returns this option if non-empty, otherwise returns the alternative.
        Lazy evaluation of alternative.
        """
        pass

    @abstractmethod
    def map[U](self, f: Callable[[T], U]) -> 'Option[U]':
        """Applies the function to the option's value if non-empty."""
        pass

    @abstractmethod
    def flat_map[U](self, f: Callable[[T], 'Option[U]']) -> 'Option[U]':
        """
        Applies the function that returns an Option to the option's value.
        """
        pass

    @abstractmethod
    def fold[U](self, if_empty: Callable[[], U], f: Callable[[T], U]) -> U:
        """
        If the option is empty, applies the 'if_empty' function and returns its result.
        If the option is non-empty, applies the function 'f' to the option's value.
        """
        pass

    @abstractmethod
    def filter(self, p: Callable[[T], bool]) -> 'Option[T]':
        """
        Returns the option if non-empty and the predicate returns True.
        """
        pass

    @abstractmethod
    def exists(self, p: Callable[[T], bool]) -> bool:
        """
        Returns True if non-empty and the predicate returns True.
        """
        pass

    @abstractmethod
    def contains(self, elem: T) -> bool:
        """
        Checks if the option contains the given element.
        """
        pass

    @abstractmethod
    def to_list(self) -> list[T]:
        """
        Converts the option to a list.
        """
        pass
