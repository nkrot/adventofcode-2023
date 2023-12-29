import pytest

from aoc.point import Point, is_straight_line


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


def test_points_are_straight_horizontal_line():
    points = [(1, 1), (1, 2), (1, 3), (1, 4)]
    points = [Point(pt) for pt in points]
    assert is_straight_line(points)


def test_points_are_not_straight_horizontal_line_if_non_contiguous():
    points = [(1, 1), (1, 2), (1, 3), (1, 5)]
    points = [Point(pt) for pt in points]
    assert not is_straight_line(points)


def test_points_are_not_straight_horizontal_line():
    points = [(1, 1), (1, 2), (2, 2)]
    points = [Point(pt) for pt in points]
    assert not is_straight_line(points)


def test_points_are_straight_vertical_line():
    points = [(1, 1), (2, 1), (3, 1)]
    points = [Point(pt) for pt in points]
    assert is_straight_line(points)


def test_points_are_not_straight_vertical_line():
    points = [(1, 1), (2, 1), (3, 2)]
    points = [Point(pt) for pt in points]
    assert not is_straight_line(points)


def test_points_are_not_straight_vertical_line_if_non_contiguous():
    points = [(1, 1), (2, 1), (4, 1)] # gap (3, 1)
    points = [Point(pt) for pt in points]
    assert not is_straight_line(points)


# 4+-dimesional points?
