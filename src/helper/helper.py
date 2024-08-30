"""Module providing some python helper functions."""
from typing import Callable, List, Optional, TypeVar

T = TypeVar('T')


def find_first(items: List[T], predicate: Callable[[T], bool]) -> Optional[T]:
    """
    Finds the first item in the list that matches the given predicate.

    Args:
        items (List[T]): A list of items to search through.
        predicate (Callable[[T], bool]): A function that returns True for a matching item.

    Returns:
        Optional[T]: The first matching item if found, otherwise None.
    """
    for item in items:
        if predicate(item):
            return item
    return None
