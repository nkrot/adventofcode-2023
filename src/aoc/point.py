from typing import List, Union

from .vector import Vector

__all__ = [
    'Point',
    'is_straight_line'
]

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
        offsets = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
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

    def __lt__(self, other: 'Point') -> bool:
        """TODO: I wonder why I implemented it like this...
        why is z coordinate not taken into account?
        """
        return self.x < other.x or self.x == other.x and self.y < other.y


def is_straight_line(points: List[Point]) -> bool:
    """Check if given 2D points constitute a single straight line.
    Points must be contiguous.
    If there are less than 2 points given, return false.

    TODO:
    - allow list of tuples instead of Points and make points on the fly?
      or use Direction class :)
    """
    if len(points) < 2:
        return False
    directions = [b - a for a, b in zip(points, points[1:])]
    res = len(set(directions)) == 1
    return res
