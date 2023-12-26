from typing import Optional, Tuple, Union, Dict, Literal

from .point import Point

# TODO
# create a container (class) for storing intersection data

class Line:
    """Geometric Line in 2D or 3D space"""

    def __init__(
        self,
        source: Union[Point, Tuple[int, int]],
        direction: Union[Point, Tuple[int, int]]
    ):
        self.source = source
        self.direction = direction

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, val: Union[Point, Tuple[int, int]]):
        self._source = Point(val)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, val: Union[Point, Tuple[int, int]]):
        self._direction = Point(val)

    # aliases / shorthands
    s = property(lambda self: self._source)
    d = property(lambda self: self._direction)

    def __repr__(self):
        return "<{}: source={} direction={}>".format(
            self.__class__.__name__, self.source, self.direction)

    def intersects(self, other: 'Line') -> Optional[Point]:
        """
        If current Ray intersects (right now or in the future) with
        the other ray, return their point of intersection.
        Otherwise return None.
        """
        assert type(self) is type(other), \
            f"Cannot intersect {type(self)} with {type(other)}"
        idata = self._get_intersection_data(other)
        return idata.get('p', None)

    def _get_intersection_data(
        self, other: 'Line'
    ) -> Dict[Literal['xy', 'xz'], Dict[str, Union[float, Point]]]:
        idata = {'xy': self._get_intersection_data_2d(other)}
        if len(self.s) == 2:
            idata['p'] = idata['xy'].get('p')
        elif len(self.s) == 3:
            self_xz = type(self)((self.s.x, self.s.z), (self.d.x, self.d.z))
            other_xz = type(self)((other.s.x, other.s.z), (other.d.x, other.d.z))
            idata['xz'] = self_xz._get_intersection_data_2d(other_xz)
            # print("--- intersection in 3D ---")
            # print("XY", idata['xy'])
            # print("XZ", idata['xz'])
            p_xy = idata['xy'].get('p')
            p_xz = idata['xz'].get('p')
            if p_xy and p_xz:
                idata['p'] = Point((p_xy.x, p_xy.y, p_xz.y))
        return idata

    def _get_intersection_data_2d(
        self, other: 'Line'
    ) -> Dict[str, Union[float, Point]]:
        """Find out where the current line and another line intersect
        in the X-Y plane.
        Return the point of intersection and other computed terms of
        the relevant equations as a dictionary.

        Source: https://stackoverflow.com/a/2932601/1056268
        """
        det = other.d.x * self.d.y - other.d.y * self.d.x
        data = {'det': det}
        if det:  # lines are not parallel
            dx = other.s.x - self.s.x
            dy = other.s.y - self.s.y
            u = (dy * other.d.x - dx * other.d.y) / det
            v = (dy * self.d.x - dx * self.d.y) / det
            # print(u, v)
            data.update({
                'u': u,
                'v': v,
                'p': self.s + self.d * u  # point of intersection
                # 'p2': other.s + other.d * v  # same as p
            })
            # print(p, p2, round(p, 5) == round(p2, 5))
        return data

    def __and__(self, other: 'Line'):
        """Alias of Line.intersects()"""
        return self.intersects(other)


class Ray(Line):
    """Geometric Ray"""

    def intersects(self, other: 'Ray') -> Optional[Point]:
        """If current Ray intersects (right now or in the future) with
        the other ray, return their point of intersection.
        Otherwise return None.
        """
        # TODO: implementing intersecting Ray and Line is left for future
        assert type(self) is type(other), \
            f"Cannot intersect {type(self)} with {type(other)}"
        idata = self._get_intersection_data(other)
        if idata.get('p', None) is None:
            return None
        for plane in ['xy', 'xz']:
            d = idata.get(plane, {})
            if d and (d['u'] < 0 or d['v'] < 0):
                # intersection point is in the past
                return None
        return idata.get('p')
