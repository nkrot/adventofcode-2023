import pytest

from aoc import Point


@pytest.fixture
def point_9_10():
    return Point([9, 10])


def test_create_from_sequence():
    point = Point([9, 10])
    assert isinstance(point, Point)
    assert point.values == [9, 10]


def test_create_from_arguments():
    point = Point(1, 2, 3)
    assert isinstance(point, Point)
    assert point.values == [1, 2, 3]


def test_access_axes_2d(point_9_10):
    assert point_9_10.x == 9
    assert point_9_10.y == 10


def test_around4_with_2d_point(point_9_10):
    points_around = [
        Point(8, 10), Point(10, 10), # above and below
        Point(9, 9), Point(9, 11),   # left and right
    ]
    for pt in point_9_10.around4():
        assert isinstance(pt, Point)
        assert pt in points_around

# 4+-dimesional points?