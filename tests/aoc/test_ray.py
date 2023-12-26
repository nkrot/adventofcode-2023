import pytest
from aoc import Ray, Point

# Data from day_24/test.1.txt
# 19, 13, 30 @ -2,  1, -2  (1) and (5)
# 18, 19, 22 @ -1, -1, -2  (2)
# 20, 25, 34 @ -2, -2, -4
# 12, 31, 28 @ -1, -2, -1  (3)
# 20, 19, 15 @  1, -5, -3  (4)
# 19, 13, 30 @ -2,  1,  2  (5) based on (1)
# 24, 13, 10 $ -3,  1,  2  (6) -- the rock from day_24/task.txt
# 24, 13, 10 $ -3,  1, -3  (7) -- variation of (6)
# 24, 13, 10 $ -3,  1, 11  (8) -- variation of (6)

@pytest.fixture
def ray2d_1():
    return Ray((19, 13), (-2, 1))

@pytest.fixture
def ray3d_1():
    return Ray((19, 13, 30), (-2, 1, -2))

@pytest.fixture
def ray2d_2():
    return Ray(Point(18, 19), Point(-1, -1))

@pytest.fixture
def ray3d_2():
    return Ray(Point(18, 19, 22), Point(-1, -1, -2))

@pytest.fixture
def ray2d_3():
    return Ray([12, 31], [-1, -2])

@pytest.fixture
def ray2d_4():
    return Ray((20, 19), (1, -5))

@pytest.fixture
def ray2d_5():
    return Ray((19, 13), (1, +2))

@pytest.fixture
def ray3d_6():
    return Ray((24, 13, 10), (-3, 1, 2))

@pytest.fixture
def ray3d_7():
    return Ray((24, 13, 10), (-3, 1, -3))

@pytest.fixture
def ray3d_8():
    return Ray((24, 13, 10), (-3, 1, 13))


def test_accessors_1(ray2d_1):
    assert isinstance(ray2d_1.s, Point)
    assert isinstance(ray2d_1.d, Point)
    assert (19, 13) == (ray2d_1.s.x, ray2d_1.s.y)
    assert (-2, 1) == (ray2d_1.d.x, ray2d_1.d.y)

def test_intersect_ray2d_1_and_self(ray2d_1):
    p = ray2d_1.intersects(ray2d_1)
    assert p is None

def test_intersect_ray2d_1_and_2(ray2d_1, ray2d_2):
    p = ray2d_1.intersects(ray2d_2)
    assert Point(14.333, 15.333) == round(p, 3)

def test_intersect_ray2d_1_and_3(ray2d_1, ray2d_3):
    p = ray2d_1.intersects(ray2d_3)
    assert Point(6.2, 19.4) == round(p, 1)

def test_intersect_ray2d_1_and_4_in_the_past(ray2d_1, ray2d_4):
    p = ray2d_1.intersects(ray2d_4)
    assert p is None

def test_intersect_ray2d_1_and_5(ray2d_1, ray2d_5):
    p = ray2d_1.intersects(ray2d_5)
    assert Point(19, 13) == p

def test_intersect_ray3d_1_and_6(ray3d_1, ray3d_6):
    p = ray3d_1.intersects(ray3d_6)
    assert Point(9, 18, 20) == p

def test_intersect_ray3d_1_and_7_parallel_in_z(ray3d_1, ray3d_7):
    p = ray3d_1.intersects(ray3d_7)
    assert p is None

def test_intersect_ray3d_1_and_8_in_the_past_along_z(ray3d_1, ray3d_8):
    p = ray3d_1.intersects(ray3d_8)
    assert p is None

def test_intersect_ray3d_2_and_6(ray3d_2, ray3d_6):
    p = ray3d_2.intersects(ray3d_6)
    assert Point(15, 16, 16) == p

# TODO
# 1) test for 2D where rays are vertical vs horizontal
# 2) add a test where 3D dont intersect in xy plane or intersect in the past
