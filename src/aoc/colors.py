from typing import List

class Colorizer:
    """
    Infinite Cyclic Iterator over color names.

    Usage:
    >>> color = Colorizer()
    >>> next(color)
    >>> next(color)
    """

    NAMES = ('b', 'g', 'r', 'c', 'm', 'y', 'k', 'w')

    def __init__(self, names: List[str] = None):
        self.idx = -1
        self.names = names or self.NAMES

    def __iter__(self):
        return self

    def __next__(self):
        self.idx = (self.idx + 1) % len(self.names)
        return self.names[self.idx]
