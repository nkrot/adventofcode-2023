
import os
import sys
import re
from typing import Union, Optional, Tuple
from types import ModuleType
from importlib import import_module
import click

from . import utils


CLICK_CONTEXT_SETTINGS = {
    "help_option_names": ['-h', '--help'],
}


class DaysArgument(click.Argument):

    def __init__(self, *args, **kwargs):
        kwargs['nargs'] = -1
        super().__init__(*args, **kwargs)

    def process_value(self, ctx, value):
        return super().process_value(ctx, value or list_available_days())


class PartsOption(click.Option):

    def __init__(self, *args, **kwargs):
        # print("args", args)
        # print("kwargs", kwargs)

        parts = ["1", "2"]
        kwargs.update({
            "multiple": True,
            "default": parts,
            "show_default": True,
            "type" : click.Choice(parts),
            "help": (
                "run part(s) specified. Multiple values can be"
                " provided either as `-p1 -p2` or `-p1,2`"
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
        for value in values:
            # handle the case of --part 1,2
            new_values.extend(value.split(','))
        return super().process_value(ctx, new_values)


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


def load_solution_for_day(day: Union[str, int]) -> Optional[ModuleType]:
    """
    This function strongly relies on naming conventions
      * day_01/solution.py
      * day_10/solution.py
    """

    mdl = None
    path = f"day_{int(day):02}"
    try:
        mdl = import_module(f".{path}.solution", package=__package__)
    except ModuleNotFoundError:
        #raise RuntimeError(f"Solution for day {day} not found: {path}")
        print(f"ERROR: Solution for day {day} not found ('{path}').",
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


@click.group(context_settings=CLICK_CONTEXT_SETTINGS)
def main():
    """Solutions to AoC 2023"""
    pass


@main.command()
@click.argument('days', metavar="[DAYS] [FILES]", cls=DaysArgument)
@click.option('-p', '--part', 'parts', cls=PartsOption)
def solve(days: Tuple[str], parts: Tuple[str]):
    """Run solution(s) on the real inputs for given days.

    DAYS, one or many, are given as numbers from 1 to 25. If none is
    given, solutions for all days will be run, as long as a solution
    is available.

    If FILES is/are provided, they are used as inputs. If not provided,
    default inputs are used.
    """
    # separate numbers from paths to file
    files = [d for d in days if not re.match(r'\d+$', d)]
    days = [d for d in days if re.match(r'\d+$', d)]
    #print(f"Solving real... days {days} parts {parts} for files {files}")

    for d in days:
        solution = load_solution_for_day(d)
        if not solution:
            continue

        if files:
            # if files were given on the command line, use them as input
            for f in files:
                if '1' in parts:
                    solution.solve_part_1(add_cwd(f))
                if '2' in parts:
                    solution.solve_part_2(add_cwd(f))

        else:
            # otherwise, use default inputs
            utils.run_real(
                solution.DAY,
                solution.reals,
                solution.solve_p1 if '1' in parts else None,
                solution.solve_p2 if '2' in parts else None,
            )


@main.command()
@click.argument('days', cls=DaysArgument)
@click.option('-p', '--part', 'parts', cls=PartsOption)
def test(days: Tuple[str], parts: Tuple[str]):
    """Run solution(s) on the test inputs.

    Test inputs are those that are given in the task description with
    answers.
    """
    # print(f"Solving tests... days {days} parts {parts}")
    for d in days:
        solution = load_solution_for_day(d)
        if solution:
            utils.run_tests(
                solution.DAY,
                solution.tests,
                solution.solve_p1 if '1' in parts else None,
                solution.solve_p2 if '2' in parts else None,
            )


@main.command(name="list")
def list_days():
    """List available days.

    No guarantee they are solved :)
    """
    print(list_available_days())


if __name__ == "__main__":
    main()
