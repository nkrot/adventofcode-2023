import functools
from typing import Iterable, Union, Callable


class Vector(object):

    def __init__(self, values: Iterable = None):
        self.values = list(values or [])

    def __hash__(self):
        return hash(tuple(self.values))

    def __add__(self, other: Union["Vector", Iterable]) -> "Vector":
        return self.pairwise(other, lambda a, b: a+b)

    def __sub__(self, other: Union["Vector", Iterable]) -> "Vector":
        return self.pairwise(other, lambda a, b: a-b)

    def __mod__(self, other: Union["Vector", Iterable, int]) -> "Vector":
        if isinstance(other, (int, float)):
            other = [other] * len(self)
        return self.pairwise(other, lambda a, b: a % b)

    def __mul__(self, other: Union["Vector", Iterable, int]) -> "Vector":
        if isinstance(other, (int, float)):
            other = [other] * len(self)
        return self.pairwise(other, lambda a, b: a * b)

    def __round__(self, ndigits=0) -> "Vector":
        values = [round(v, ndigits) for v in self.values]
        return self.__class__(values)

    def pairwise(
        self,
        other: Union["Vector", Iterable],
        func: Callable  # to be used with functools.reduce()
    ) -> "Vector":
        if not isinstance(other, (type(self), list, tuple)):
            return NotImplemented
        assert len(self) == len(other), (
            f"Length mismatch: {len(self)} vs. {len(other)}"
        )
        values = [functools.reduce(func, pair) for pair in zip(self, other)]
        return self.__class__(values)

    # def __getattr__(self, name: str):
    #     print("method", name, type(name))

    def __abs__(self):
        # TODO: implement generically via __getattr__
        return self.__class__(abs(v) for v in self)

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return iter(self.values)

    def __repr__(self):
        return "<{}: values={}>".format(self.__class__.__name__, self.values)

    def __str__(self):
        return str(tuple(self.values))

    def __getitem__(self, idx: int):
        return self.values[idx]

    def __eq__(self, other: "Vector"):
        return tuple(self.values) == tuple(other)
