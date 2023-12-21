
import os
import itertools
import functools
import inspect
from pprint import pprint
from copy import deepcopy
from typing import List, Union, Tuple, Optional, Callable, Any

DEBUG = int(os.environ.get('DEBUG', 0))


def load_input(fname: Optional[str] = None, **kwargs) -> List[Any]:
    """
    Load file, either given or default 'input.txt' and return its content
    as a list of lines. All lines are returned, including empty ones.

    If `fname` is not provided by a full (absolute) path, it assumed to
    be in the same directory as the script that envoked load_input().
    In this very projects, this means in the same directory where the file
    `solution.py` is located.
    """

    fname = fname or 'input.txt'
    if not os.path.isabs(fname):
        srcdir = os.path.dirname(inspect.stack()[1][1])
        fname = os.path.join(srcdir, fname)
        dprint(f"Data file: {fname}")

    lines = []
    with open(fname) as fd:
        for line in fd:
            lines.append(line.rstrip('\r\n'))

    parse_line = kwargs.get("line_parser")
    if parse_line:
        lines = list(map(parse_line, lines))

    parse = kwargs.get("parser")
    if parse:
        lines = parse(lines)

    return lines


def text_from(fpath: str):
    with open(fpath) as fd:
        return fd.read().strip("\n")


def group_lines(data: Union[str, List[str]]) -> List[List[str]]:
    """Make groups of lines: a group is a sequence of lines that are separated
    by an empty line from another group.
    Input <data> is either of these:
    1) (str) a string that is the whole content of a file;
    2) (List[str]) a list of lines that 1) already split into individual lines.
    """
    groups = [[]]
    if isinstance(data, str):
        data = [ln.strip() for ln in data.split('\n')]
    for ln in data:
        if ln:
            groups[-1].append(ln)
        else:
            groups.append([])
    return groups


def to_numbers(lines: List[str]) -> List[int]:
    """Convert list of lines (strings) to list of ints"""
    return [int(line) for line in lines]


def dprint(*args):
    if DEBUG:
        print(*args)

def minmax(numbers: List[int]) -> Tuple[int, int]:
    """Return min and max values from given list of integers"""
    return (min(numbers), max(numbers))


def flatten(items: List[List]) -> List:
    """Flatten one level"""
    return [item for subitems in items for item in subitems]

# Source
# https://stackoverflow.com/questions/55774054/precise-time-in-nano-seconds-for-python-3-6-and-earlier

import ctypes

CLOCK_REALTIME = 0

class timespec(ctypes.Structure):
    _fields_ = [
        ('tv_sec', ctypes.c_int64), # seconds, https://stackoverflow.com/q/471248/1672565
        ('tv_nsec', ctypes.c_int64), # nanoseconds
    ]

clock_gettime = ctypes.cdll.LoadLibrary('libc.so.6').clock_gettime
clock_gettime.argtypes = [ctypes.c_int64, ctypes.POINTER(timespec)]
clock_gettime.restype = ctypes.c_int64


def time_ns():
    tmp = timespec()
    ret = clock_gettime(CLOCK_REALTIME, ctypes.pointer(tmp))
    if bool(ret):
        raise OSError()
    return tmp.tv_sec * 10 ** 9 + tmp.tv_nsec


def mytimeit(func, n=1):
    """A decorator to measure runtime of a function in nanoseconds"""
    def wrapper(*args, **kwargs):
        start = time_ns()
        res = func(*args, **kwargs)
        end = time_ns()
        print("Runtime[{}]: {} nsec".format(func.__name__, end-start))
        return res
    return wrapper


def mdrange_my(*ranges):
    """
    Generates all combinations (n-tuples)
    >>> ranges = [(0, 3), (10, 12), (101, 104)]
    >>> for x,y,z in mdrange(*ranges):
    >>>   ...
    """
    assert ranges, "Cannot be empty"
    head, tails = ranges[0], ranges[1:]
    if not tails:
        for x in range(*head):
            yield (x,)
    else:
        for x in range(*head):
            for y in mdrange(*tails):
                yield (x, *y)


def mdrange(*ranges):
    # TODO: add support for mdrange(5, 6) where range(5) and range(6)
    rngs = [rng if isinstance(rng, range) else range(*rng) for rng in ranges]
    yield from itertools.product(*rngs)


def prod(numbers: List[int]):
    return functools.reduce(lambda a, b: a*b, numbers, 1)


def listfold(lst: List[Any], width: int) -> List[List[Any]]:
    """Folds (reshapes) a list into 2 dimentional matrix by folding at
    given position `width`. each row will contain at most `width` items
    """
    reshaped = []
    for ridx in range(len(lst) // width):
        start = ridx * width
        reshaped.append(lst[start:start+width])
    return reshaped


def test2str(success, expected, actual):
    lines = []
    if "\n" in str(expected) or "\n" in str(actual):
        lines.append(str(success))
        if success:
            lines += ["Expected and Actual:", str(expected)]
        else:
            lines += ["Expected:", str(expected), "Actual:", str(actual)]
    else:
        lines.append(f"{success} {expected} {actual}")
    return "\n".join(lines)


def run_tests(
    day: str,
    tests: List[Tuple], # (input, expected-part-1, expected-part-2)
    solve_p1: Callable = None,
    solve_p2: Callable = None
):
    print(f"--- Tests day {day} ---")

    for tid, (inp, exp1, exp2) in enumerate(tests):
        if solve_p1 and exp1 is not None:
            res1 = solve_p1(deepcopy(inp))
            print(f"T.{tid}.p1:", test2str(res1 == exp1, exp1, res1))

        if solve_p2 and exp2 is not None:
            res2 = solve_p2(inp)
            print(f"T.{tid}.p2:", test2str(res2 == exp2, exp2, res2))


def run_real(
    day: str,
    tests: List[Tuple], # (input, expected-part-1, expected-part-2)
    solve_p1: Callable = None,
    solve_p2: Callable = None
):
    for tid, (inp, exp1, exp2) in enumerate(tests):
        if solve_p1:
            print(f"--- Day {day} p.1 ---")
            res1 = solve_p1(deepcopy(inp))
            print(test2str(exp1 == res1, exp1, res1))

        if solve_p2:
            print(f"--- Day {day} p.2 ---")
            res2 = solve_p2(inp)
            print(test2str(exp2 == res2, exp2, res2))


def is_even(obj: Union[int, List[int], Tuple[int]]) -> bool:
    """Test if a number is even or all numbers in a list are even"""
    if isinstance(obj, (list, tuple)):
        return all(map(is_even, obj))
    return obj % 2 == 0


def is_odd(obj: Union[int, List[int], Tuple[int]]) -> bool:
    """Test if a number is odd or all numbers in a list are odd"""
    if isinstance(obj, (list, tuple)):
        return all(map(is_odd, obj))
    return obj % 2 != 0
