import pytest
from aoc import utils


@pytest.mark.parametrize(
    "input,expected", [
    (0, True),
    (2, True),
    ([2, 4], True),
    ([2, 3, 4], False),
])
def test_is_even(input, expected):
    assert expected == utils.is_even(input)


@pytest.mark.parametrize(
    "input,expected", [
    (0, False),
    (2, False),
    (1, True),
    ((1, 3, 5), True),
    ([2, 4], False),
    ([2, 3, 4], False),
])
def test_is_odd(input, expected):
    assert expected == utils.is_odd(input)
