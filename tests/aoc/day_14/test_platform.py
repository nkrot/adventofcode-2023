import pytest

from aoc.day_14 import Platform


@pytest.fixture
def platform_01(datadir):
    return Platform.from_file(datadir / "platform.01.txt")

@pytest.fixture
def platform_02(datadir):
    return Platform.from_file(datadir / "platform.02.txt")


def test_compute_load_01(platform_01):
    assert 136 == platform_01.compute_load()


def test_compute_load_02(platform_02):
    # level is the distance from the south edge
    rocks_per_level = [5, 1, 4, 2, 2, 2, 1, 0, 1, 0]
    total = sum((1+lvl) * n_rocks
                for lvl, n_rocks in enumerate(rocks_per_level))
    assert total == platform_02.compute_load()
