
from .point import Point


class Direction(Point):
    """
    (x,y) where x axis goes topdown and y-axis goes rightwards
    """

    SIGNS = ">v<^"  # the order is important for cw() and ccw()
    OFFSETS = [
        (0, 1),
        (1, 0),
        (0, -1),
        (-1, 0),
    ]

    def __init__(self, sign: str):
        if sign not in self.SIGNS:
            raise ValueError(f"Invalid direction spec: '{sign}'")
        self.sign = sign
        super().__init__(self._dxy())

    def _dxy(self):
        """TODO: make it public?"""
        return self.OFFSETS[self.SIGNS.index(self.sign)]

    def __str__(self):
        return self.sign

    def __repr__(self):
        return "<{}: sign='{}' {}>".format(
            self.__class__.__name__,
            self.sign,
            self._dxy()
        )

    def cw(self):
        """Rotate current Direction clockwise.
        Returns self to allow method chaining.
        """
        idx = (self.SIGNS.index(self.sign) + 1) % 4
        self.sign = self.SIGNS[idx]
        self.values = self._dxy()
        return self

    def ccw(self):
        """Rotate current Direction counterclockwise.
        Returns self to allow method chaining.
        """
        idx = (self.SIGNS.index(self.sign) - 1) % 4
        self.sign = self.SIGNS[idx]
        self.values = self._dxy()
        return self
