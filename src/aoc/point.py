from typing import Union, List
from .vector import Vector

class Point(Vector):
    """for purposes of clearer naming"""

    def __init__(self, *coords: Union[int, List[int]]):
        if isinstance(coords[0], (list, tuple, type(self))):
            super().__init__(*coords)
        else:
            super().__init__(coords)

    def around4(self) -> List['Point']:
        """List points around current point along height and width.
        Points with negative coordinates are excluded.

        TODO: in case of 3D point, also along depth
        """
        if len(self) > 2:
            raise NotImplementedError("3D point pending implementation")
        offsets = ((-1, 0), (0, 1), (1, 0), (0, -1))
        pts = [self + offset for offset in offsets]
        # select points with positive coordinates only
        pts = [pt for pt in pts if all(crd > -1 for crd in pt)]
        return pts

    def around8(self) -> List['Point']:
        """List points around current point along height and width
        including diagonals.
        Points with negative coordinates are excluded.

        TODO: in case of 3D point, also along depth
        """
        if len(self) > 2:
            raise NotImplementedError("3D point pending implementation")
        offsets = ((-1, 0), (-1, 1), (0, 1), (1,1), (1, 0), (1,-1), (0, -1), (-1, -1))
        pts = [self + offset for offset in offsets]
        # select points with positive coordinates only
        pts = [pt for pt in pts if all(crd > -1 for crd in pt)]
        return pts

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value: int):
        self.values[0] = value

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, value: int):
        self.values[1] = value

    @property
    def z(self):
        return self[2]

    @z.setter
    def z(self, value: int):
        self.values[2] = value

    def l1_dist(self, other: 'Point') -> int:
        """L1 distance aka Manhattan distance"""
        return sum(*abs(self - other))

    def __lt__(self, other: 'Point'):
        return self.x < other.x or self.x == other.x and self.y < other.y

class DirectedPoint(Point):
    """A point that has an idea of direction.
    If you try to move it by a number of steps, it moves in known
    direction.

    Assumptions:
    * coodinate is (x, y)
    * the origin is located in the top left corner
    * x axis goes from left to right
    * y axis goes from top to bottom
    """

    UP    = ( 0, -1)
    RIGHT = ( 1,  0)
    DOWN  = ( 0,  1)
    LEFT  = (-1,  0)

    def __init__(self, position, direction=DOWN):
        super().__init__(position)
        self.direction = Vector(direction)

    def __repr__(self):
        return "<{}: position={}, direction={}>".format(
            self.__class__.__name__,
            self.values,
            self.direction
        )

    def turn_cw(self):
        """Turn one step (90 deg) clockwise"""
        direction = self.direction + (1, 1)
        sign = direction[0] - direction[1]
        self.direction = direction % 2 * sign

    def turn_ccw(self):
        "Turn one step (90 deg) counterclockwise"
        direction = self.direction + (-1, -1)
        sign = direction[1] - direction[0]
        self.direction = direction % 2 * sign


def demo_directed_point():
    """
    TODO: make testcases from it
    """
    pt = DirectedPoint((0, 8), DirectedPoint.RIGHT)
    print(repr(pt))

    print("turning clockwise")
    for _ in range(5):
        pt.turn_cw()
        print(repr(pt))

    print("turn counterclockwise")
    for _ in range(5):
        pt.turn_ccw()
        print(repr(pt))
