from __future__ import annotations

from typing import Any, Iterable, Iterator, overload

from pydantic import BaseModel


class Pair[T](BaseModel):
    first: T
    second: T

    @overload
    def __init__(self, *, first: T, second: T) -> None:
        ...

    @overload
    def __init__(self, first: T, second: T, /) -> None:
        ...

    @overload
    def __init__(self, values: Iterable[T], /) -> None:
        ...

    def __init__(self, *args, **kwargs) -> None:
        if len(kwargs) == 2:
            super().__init__(**kwargs)
            return
        if len(args) == 2:
            super().__init__(
                first=args[0],
                second=args[1],
            )
            return
        iterator = iter(args[0])
        first = next(iterator)
        second = next(iterator)
        try:
            next(iterator)
        except StopIteration:
            super().__init__(
                first=first,
                second=second,
            )
            return
        raise ValueError('Expected 2 values, got more')

    def __getattr__(self, item) -> Pair[Any]:
        return Pair([getattr(self.first, item), getattr(self.second, item)])

    def __iter__(self) -> Iterator[T]:
        return iter((self.first, self.second))

    def __getitem__(self, index: int) -> T:
        if index == 0:
            return self.first
        elif index == 1:
            return self.second
        else:
            raise ValueError('Index out of range')
