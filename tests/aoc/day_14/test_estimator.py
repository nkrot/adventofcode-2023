import pytest

from aoc.day_14 import Estimator

# test.d9.1.txt | 63  | 7 14 21 28 35 42 49 56 63 70 | (+7)        |
# test.d9.2.txt | 64  | 5 12 19 26 33 40 47 54 61 68 | (+7)        |
# test.d9.3.txt | 65  | 4  6 11 13 18 20 25 27 32 34 | (+2, +5)    |
# test.d9.4.txt | 68  | 8 15 22 29 36 43 50 57 64 71 | (+7)        |
# test.d9.5.txt | 69  | 1  2  3 9  10 16 17 23 24 30 | +1, (+1,+6)  |
# test.d9.5.2.txt | 69 | . 2  3 9  10 16 17 23 24 30 | (+1, +6)     |

@pytest.fixture
def inputs_01():
    return [7, 14, 21, 28, 35, 42, 49, 56, 63, 70]


@pytest.fixture
def function_01(inputs_01):
    f = Estimator()
    f.recurrent_constants = (7, )
    return f


@pytest.fixture
def inputs_02():
    return [5, 12, 19, 26, 33, 40, 47, 54, 61, 68]

@pytest.fixture
def function_02(inputs_02):
    f = Estimator()
    f.offset_constants = (inputs_02[0], )
    f.recurrent_constants = (7,)
    return f


@pytest.fixture
def inputs_03():
    return [1, 2, 3, 9, 10, 16, 17, 23, 24, 30]

@pytest.fixture
def function_03(inputs_03):
    f = Estimator()
    f.offset_constants = (inputs_03[0], 1)
    f.recurrent_constants = (1, 6)
    return f


@pytest.fixture
def inputs_04():
    # real input from day14p2
    return [93, 94, 131, 132, 169, 170, 207, 208, 245, 246, 283]

@pytest.fixture
def function_04(inputs_04):
    # load value: 104409
    f = Estimator()
    f.offset_constants = (inputs_04[0],)
    f.recurrent_constants = (1, 37)
    return f


@pytest.fixture
def inputs_05():
    return [12, 108, 146, 184, 222, 260, 298, 336, 374, 412] #, 450, 488, 526, 564, 602, 640, 678, 716, 754, 792]

@pytest.fixture
def function_05(inputs_05):
    # load value: 104375
    f = Estimator()
    f.offset_constants = (inputs_05[0], 96)
    f.recurrent_constants = (38,)
    return f


@pytest.fixture
def target():
    # number of cycles from day14p2
    # target-1 because in counting of cycles starts at 1
    return 1_000_000_000-1


@pytest.mark.parametrize(
    "inputs,params", [
    # 63, pattern: (+7)
    ( "inputs_01", ((), (7,))),
    # 64, pattern: (+7)
    ( "inputs_02", "function_02") ,
    # 65, pattern: (+2,+5)
    ( [4,  6, 11, 13, 18, 20, 25, 27, 32, 34],  ((4,), (2, 5)) ),
    # 69, pattern: +1, (+1,+6)
    ( "inputs_03", "function_03"),
    # 104375, pattern: +96, (+38)
    ( "inputs_05", "function_05"),
])
def test_compute_estimator(inputs, params, request):
    if isinstance(inputs, str):
        inputs = request.getfixturevalue(inputs)
    if isinstance(params, str):
        params = request.getfixturevalue(params).params()
    f = Estimator().analyse(inputs)
    assert params == f.params()


@pytest.mark.parametrize(
    "inputs,func", [
    ("inputs_01", "function_01"),
    ("inputs_02", "function_02"),
    ("inputs_03", "function_03"),
    ("inputs_04", "function_04"),
])
def test_function_range(inputs, func, request):
    inputs = request.getfixturevalue(inputs)
    func = request.getfixturevalue(func)
    for value in inputs:
        assert value in func

@pytest.mark.parametrize(
    "inputs,func", [
    ("inputs_01", "function_03"),
    ("inputs_02", "function_01"),
    ("inputs_03", "function_04"),
    #("inputs_04", "function_01"), # some inputs are in all functions
])
def test_not_function_range(inputs, func, request):
    inputs = request.getfixturevalue(inputs)
    func = request.getfixturevalue(func)
    for value in inputs:
        assert value not in func


def test_target_from_day14_p2_in_range(
    target, function_01, function_02, function_03, function_04
):
    assert target not in function_01
    assert target in function_02  # test input
    assert target not in function_03
    assert target in function_04  # real input


def test_target_from_day14_p2(inputs_04, target):
    """The whole thing, starting from numbers."""
    func = Estimator().analyse(inputs_04)
    assert target in func

# TODO:
# 1. add test for input sequence of all zeroes. what happens?
# 2. what about negative numbers?
