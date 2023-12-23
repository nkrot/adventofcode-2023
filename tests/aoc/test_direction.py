import pytest

from aoc import Direction


@pytest.fixture
def rightward():
    return Direction(">")

@pytest.fixture
def leftward():
    return Direction("<")

@pytest.fixture
def upward():
    return Direction("^")

@pytest.fixture
def downward():
    return Direction("v")


@pytest.mark.parametrize(
    "direction,expected",
    [
        ("upward",    ("^", [-1,  0])),
        ("downward",  ("v", [ 1,  0])),
        ("leftward",  ("<", [ 0, -1])),
        ("rightward", (">", [ 0,  1])),
    ]
)
def test_create_direction(direction, expected, request):
    direction = request.getfixturevalue(direction)
    assert direction.sign == expected[0]
    assert direction.values == expected[1]


def test_rotate_clockwise(upward, rightward, downward, leftward):
    for rotated in [downward, leftward, upward, rightward]:
        rightward.cw()
        assert rightward == rotated


def test_rotate_counterclockwise(upward, rightward, downward, leftward):
    for rotated in [leftward, downward, rightward, upward]:
        upward.ccw()
        assert upward == rotated


def test_cw_returns_self(upward):
    obj_id = id(upward)
    assert obj_id == id(upward.cw())


def test_ccw_returns_self(downward):
    obj_id = id(downward)
    assert obj_id == id(downward.ccw())

# TODO
# - direction can be created from Tuple or Point
# - __eq__ can compare against other Direction or string (v^<>)
