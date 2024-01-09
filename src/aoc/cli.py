
import os
import re
import sys
from dataclasses import dataclass
from importlib import import_module
from types import ModuleType
from typing import Optional, Tuple, Union, List, Iterable

import click

from . import utils

CLICK_CONTEXT_SETTINGS = {
    "help_option_names": ['-h', '--help'],
}

class DayArgumentType(click.ParamType):
    def convert(self, value, param, ctx):
        return Day.from_string(value)

class DayArgument(click.Argument):

    def __init__(self, *args, **kwargs):
        kwargs = {
            'nargs': -1,
            'type': DayArgumentType(),
            'metavar': kwargs.get('metavar', f'[{Day.SPEC}]...'),
        }
        super().__init__(*args, **kwargs)

    def process_value(self, ctx, value):
        return super().process_value(ctx, value or list_available_days())

class PartsOption(click.Option):

    def __init__(self, *args, **kwargs):
        # print("args", args)
        # print("kwargs", kwargs)

        parts = ("1", "2")  # choices must be strings in click
        kwargs.update({
            "multiple": True,
            #"default": parts,  # let it be in DayArgument
            "show_default": True,
            "type" : click.Choice(parts),
            "help": (
                "Run part(s) specified. Multiple values can be"
                " provided either as `-p1 -p2` or `-p1,2`. This option"
                " overrides part(s) given in DAY spec."
            )
        })

        super().__init__(*args, **kwargs)

    def process_value(self, ctx, values):
        """
        User-provided values can be: ["1"] or ["1", "2"] or ["1,2"]
        Duplicates are not removed. If the user specified
          -p1 -p2,1 -p 2
        the list of parts will be
          ['1', '2', '1', '2']
        """
        new_values = []
        if values:
            for value in values:
                # handle the case of --part 1,2
                new_values.extend(value.split(','))
        return super().process_value(ctx, new_values)


def opt_explain(func):
    func = click.option(
        '-e', '--explain', 'show_explanation', is_flag=True,
        help=("Show documentation for given day(s) and exit"))(func)
    return func


class Day:
    SPEC = "DAY.PART"

    # TODO: PART can be either 1 or 2. Raise an error otherwise

    @classmethod
    def from_string(cls, text: str):
        m = re.match(r'(\d+)(.(\d+))?$', text)
        if m:
            parts = list(map(int, m[3])) if m[3] else None
            return cls(int(m[1]), parts)
        return text

    def __init__(self, day: int, parts = None):
        self.day: int = day or 0
        self._parts: List[int] = parts or [1, 2]

    @property
    def parts(self):
        return self._parts

    @parts.setter
    def parts(self, parts: Iterable):
        self.parts[:] = sorted(set(map(int, parts)))

    def __str__(self) -> str:
        return f"{self.day:02}"

    def __repr__(self):
        return "<{}: day={} parts={}>".format(
            self.__class__.__name__, self.day, self._parts)

    def dirname(self) -> str:
        """Return directory name for the current day.

        The convention for directory naming is as follows:
        * "day_01"
        * "day_10"

        The method can also be used as static method
        >>> DayArgument.dirname("3") => day_03
        >>> DayArgument.dirname(3)   => day_03
        """
        d = self.day if isinstance(self, Day) else self
        return f"day_{int(d):02}"

    def __contains__(self, part: Union[int, str]) -> bool:
        return int(part) in self._parts


def list_available_days() -> Tuple[str]:
    """
    Discover days for which solutions are available and return a list of
    day numbers. For example, if there are available day_01, day_02 and
    day_10, the result will be ("01", "02", "10"),

    This function relies on the following naming conventions:
    1) each day solution is implemented in its own subdirectory `day_NUMBER`
    2) and is in the file `solution.py`
    For example:
    * day_01/solution.py
    * day_02/solution.py
    * day_10/solution.py
    """
    thisdir = os.path.dirname(__file__)
    dirs = [
        d[4:]  # remove prefix `day_`
        for d in os.listdir(thisdir)
        if os.path.isfile(os.path.join(thisdir, d, "solution.py"))
    ]
    return tuple(sorted(dirs))


def load_solution_for_day(
    day: Union[str, int, Day]
) -> Optional[ModuleType]:
    """
    This function strongly relies on naming conventions
      * day_01/solution.py
      * day_10/solution.py
    """

    mdl = None
    path = day.dirname()  # or Day.dirname(day)
    try:
        mdl = import_module(f".{path}.solution", package=__package__)
    except ModuleNotFoundError:
        #raise RuntimeError(f"Solution for day {day} not found: {path}")
        print(f"ERROR: Solution for day {day} not found (directory '{path}').",
              file=sys.stderr)

    return mdl


def add_cwd(filepath: str):
    """If given `filepath` is not absolute, make it to absolute path
    by prepending current directory that is the directory from which
    the script is run.
    """
    if os.path.isabs(filepath):
        return filepath
    return os.path.join(os.getcwd(), filepath)


def combine_days_and_parts(days: List[Day], parts: List[str]):
    """If `parts` is provided, update each in `days` correspondingly.
    parts come from the option `-p/--part`.
    """
    if parts:
        for day in days:
            day.parts = parts


@click.group(context_settings=CLICK_CONTEXT_SETTINGS)
def main():
    """Solutions to AoC 2023"""
    pass


@main.command()
@click.argument('days', metavar=f"[{Day.SPEC}]... [FILES]", cls=DayArgument)
@click.option('-p', '--part', 'parts', cls=PartsOption)
@opt_explain
def solve(
    days: Tuple[Day], parts: Tuple[str], show_explanation: bool
):
    """Run solution(s) on the real inputs for given days.

    DAYs, one or many, are given as numbers from 1 to 25. A DAY can be
    followed by part number, e.g. 10.1 or 1.2. Parts can be overriden
    via the option `-p/--part`.

    If DAYs are not given, solutions for all days will be run, as long as
    a solution is available. To set parts in this case, use `-p/--part`
    option.

    If FILES is/are provided, they are used as inputs. If not provided,
    default inputs are used.
    """
    # print(f"Solving real: days={days} parts={parts}")

    # separate days from paths to input file
    files = [d for d in days if not isinstance(d, Day)]
    days = [d for d in days if isinstance(d, Day)]
    # print(f"Solving real: days={days} parts={parts} for files {files}")

    combine_days_and_parts(days, parts)

    if show_explanation:
        show_explanations(days)
        return

    for day in days:
        solution = load_solution_for_day(day)
        if not solution:
            continue

        if files:
            # if files were given on the command line, use them as input
            for f in files:
                if 1 in day:
                    solution.solve_part_1(add_cwd(f))
                if 2 in day:
                    solution.solve_part_2(add_cwd(f))

        else:
            # otherwise, use default inputs
            utils.run_real(
                solution.DAY,
                solution.reals,
                solution.solve_p1 if 1 in day else None,
                solution.solve_p2 if 2 in day else None,
            )


@main.command()
@click.argument('days', cls=DayArgument)
@click.option('-p', '--part', 'parts', cls=PartsOption)
@opt_explain
def test(days: Tuple[Day], parts: Tuple[str], show_explanation: bool):
    """Run solution(s) on the test inputs for given days.

    Test inputs are those that are given in the task description with
    answers.

    For a description on how DAYs can be specified, please refer to the
    description of the command `solve`.
    """
    combine_days_and_parts(days, parts)
    # print(f"Solving tests... days {days} parts {parts}")

    if show_explanation:
        show_explanations(days)
        return

    for day in days:
        solution = load_solution_for_day(day)
        if solution:
            utils.run_tests(
                solution.DAY,
                solution.tests,
                solution.solve_p1 if 1 in day else None,
                solution.solve_p2 if 2 in day else None,
            )


@main.command(name="list")
def list_days():
    """List available days.

    No guarantee they are solved :)
    """
    print(list_available_days())


def show_explanations(days: Tuple[Day]):
    """Print docstrings from solutions of the given day(s)"""
    for day in days:
        print(f"--- Explanation of day {day} solution ---")
        solution = load_solution_for_day(day)
        if solution and solution.__doc__:
            print(solution.__doc__)
        else:
            print("Not available")
        print()


if __name__ == "__main__":
    main()
