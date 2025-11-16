from typing import Callable, Sequence


def unique[T, P](seq: Sequence[T], keep_ordinal: bool = False, key: Callable[[T], P] | None = None) -> list[T]:
    """
    Remove duplicate elements from a sequence.
    Args:
        seq: A sequence of elements that may contain duplicates.
        keep_ordinal: If True, preserves the original order of first occurrence.
                      If False, uses set conversion (order not guaranteed).
                      Defaults to False.
        eq: An optional equality function to compare elements.
    Returns:
        A list of unique elements from the input sequence.
        If keep_ordinal is True, elements appear in their original order.
        If keep_ordinal is False, the order is arbitrary.
    Examples:
        >>> unique([1, 2, 2, 3, 1])
        [1, 2, 3]  # or any permutation
        >>> unique([1, 2, 2, 3, 1], keep_ordinal=True)
        [1, 2, 3]  # preserves order of first occurrence
    """

    if not keep_ordinal and key is None:
        # short cut
        return list(set(seq))

    seen: set[T | P] = set()

    def key_func(item: T) -> T | P:
        if key is None:
            return item

        return key(item)

    result: list[T] = []
    for item in seq:
        item_key = key_func(item)
        if item_key not in seen:
            seen.add(item_key)
            result.append(item)

    return result
