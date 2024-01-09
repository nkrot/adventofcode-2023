"""
Part 1
------

Uses Dijkstra algorithm for finding the shortest path. In terms of the task,
the "shortest" means a path that would incur the lowest heat loss.

Dijkstra algorithm uses a priority queue (min heap) to decide which blocks
to consider next. Accumulated heat loss serves as priority metric: blocks
with lower accumulated heat loss are considered first.

Now the tricky part. Regular Dijkstra keeps a *single* best state for each
block visited. This is based on the assumption that local best solution
leads eventually to the global best solution. However, such an assumption
does not hold for this task: when a crucible is forced to turn (after
running max number of blocks in a straight line), the new state is not
guaranteed to be the best state. This fact invalidates previous states.

Therefore, we have to allow more than one best state in each block. Said
best states differ in the path how crucibles came to this block. Local
best is now a state with lowest heat loss among all states with the same
path. More precisely, with the same final segment of the path that is as
long as the number of blocks a crucible can run in a straight line before
it must turn.

[If viewed as a graph, we sort of create a single vertex from the vertices
along the straight line and make this vertex, add it to the graph, thus
creating a parallel path. Such parallel paths are an alternative to several
best states. Normal Dijkstra would work for such a graph, imo]

Implementation:

We have a class to represent a state, called `Crucible`. When a new block
is entered, a new instance is created. Here, the attribute `cost` is
accumulated heat loss. The attribute `path` is the full path from the
start location (`.`).

>>> Crucible(location=(1, 4) cost=17 path='.v>>>>')

The following two states are competing states: they have the same final
segment of the path, namely '>>v'. At some point, we have to compare them
and keep the one with lower cost.

>>> Crucible(location=(2, 4) cost=18 path='.>v>>>v') <-- better (selected)
>>> Crucible(location=(2, 4) cost=22 path='.>>v>>v') <-- worse

The following state, although has the same `location`, does not compete
with the above two because its path is different. At some point, this state
is also considered by the algorithm as a candidate.

>>> Crucible(location=(2, 4) cost=24 path='.>>v>>>v<')

Local best states for each block (aka `location`) are stored in a dictionary
keyed by `location`.

Part 2
------

The solution to the second part is based entirely on the solution for
the first part but uses a different class of state (`UltraCrucible`)
with a different moving behaviour.

Currently, the running time for part 2 is around 20 minutes. Additionally,
RAM consumption can go up to 4.7G.

There is a room for improvement. For example,
* as soon as Ultra Crucible turns, it can advance some blocks due to the
  constrains that it has a minimum path it must run before it can turn.
  That is, we can avoid analysing a number of intermediate blocks, including
  their neighbor blocks. Profit!
* when a crucible approaches the goal, we may try to estimate whether it
  is possible to reach the goal given the same constraint that a crucible
  must run a minimum number of blocks before it can stop.
  (thinking in the direction of A* algorithm)
"""

import functools
import os
from collections import defaultdict
from dataclasses import dataclass
from queue import PriorityQueue
from typing import Dict, Iterator, List, Optional, Tuple

from aoc import Direction, Matrix, Point, utils
from aoc.utils import dprint, to_numbers

DAY = '17'
DEBUG = int(os.environ.get('DEBUG', 0))


def solve_part_1(fname: str):
    res = solve_p1(load_input(fname))
    print(res)


def solve_part_2(fname: str):
    res = solve_p2(load_input(fname))
    print(res)


def load_input(fname: str = None):
    """
    Load input from given file (or input.txt by default)
    using task specific parser/line_parser
    """
    return utils.load_input(fname, parser=parse)


def parse(lines: List[str]) -> Matrix:
    """Parse a line of input into suitable data structure:
    """
    numbers = [
        to_numbers(list(line))
        for line in lines
    ]
    return Matrix(numbers)


@dataclass
class Crucible:
    location: Point
    cost: int = 0    # accumulated cost
    path: str = "."  # accumulated path as a sequence of <>v^
    predecessor: 'Crucible' = None

    @property
    def max_stable_path(self) -> int:
        """The number of blocks the crucible can move in a straight line"""
        return 3

    def __lt__(self, other: 'Crucible') -> bool:
        """Is used by PriorityQueue"""
        assert isinstance(other, type(self))
        return self.cost < other.cost

    def is_at(self, location: Point) -> bool:
        return self.location == location

    def __repr__(self):
        return "{}(location={} cost={} path='{}')".format(
            self.__class__.__name__,
            tuple(self.location.values),
            self.cost,
            self.path
        )

    def comes_from(self, src: 'Crucible'):
        """Set given crucible `src` as predecessor of the current one.
        This also means updating attributes as `path` and `cost` to accumulate
        correspondings attributes of all predecessors.
        """
        self.predecessor = src
        d = Direction(self.location - src.location)
        # for simplicity, path is already a complete string. alternatively,
        # it can be constructed on the the fly from all predecessor.path
        self.path = self.predecessor.path + str(d)
        self.cost += self.predecessor.cost
        return self

    def __contains__(self, location: Point) -> bool:
        """Check if current crucible is at given location `location` or
        passed through it on its was to the current location.
        """
        return (
            self.location == location
            or self.predecessor and location in self.predecessor
        )

    def has_valid_path(self, at_end=False) -> bool:
        """Check if the path of the current is valid in terms of trajectory
        rules:
        1) a crucible cannot intersect its own path;
        2) a crucible cannot move more than certain number of blocks in
           a straight line (self.max_stable_path). We only check the last
           fragment of the path assuming that predecessors are valid
           (have undergone the same check)

        If parameter `at_end` is True, a special validation of the path
        at the point when the crucible reached the goal is triggered.
        However, it is not applicable to the normal Crucible.
        """
        if self.location in self.predecessor:
            dprint(f"..no going back")
            return False
        ln = self.max_stable_path
        if len(self.path) > ln and len(set(self.path[-ln-1:])) == 1:
            dprint(f"..must turn! {self.path[-ln-1:]}")
            return False
        return True

    def has_same_final_path(self, other: 'Crucible') -> bool:
        """Check if the current crucible is at the same location as another
        one and their final path (as long as self.max_stable_path) is equal.

        TODO: explain why or move this logic outside of the class
        """
        ln = self.max_stable_path
        return (
            self.location == other.location
            and self.path[-ln:] == other.path[-ln:]
        )

class UltraCrucible(Crucible):
    """Unlike normal Crucible, an UltraCrucible has a slightly different
    moving behaviour:
    1) Once an ultra crucible starts moving in a direction, it needs to
       move a minimum of four blocks in that direction
       a) before it can turn
       b) or even before it can stop at the end.
    2) An ultra crucible can move a maximum of ten consecutive blocks
       without turning.
    """

    def has_valid_path(self, at_end=False) -> bool:
        if super().has_valid_path():
            if len(self.path) < 3:
                return True
            tail = self.path[-self.min_stable_path-1:]
            shape = self._shape(tail)
            if at_end:  # 1b
                ok = shape[-1] >= self.min_stable_path
                dprint(f"Tail (final): {tail} with shape {shape} -- {ok}")
                return ok
            if shape[-1] > 1:  # going in a straight line
                dprint(f"Tail: {tail} with shape {shape} -- True (straight line)")
                return True
            else:  # 1a. has just changed direction
                ok = shape[-2] >= self.min_stable_path
                dprint(f"Tail: {tail} with shape {shape} -- {ok} (changed direction)")
                return ok
        return False

    def _shape(self, text: str) -> Tuple[int]:
        """A shape of a string is a sequence of numbers each representing
        the quantify of contiguous repetitions of a single character:

        Examples:
        * shape('>>>') => (3,)
        * shape('>>v') => (2, 1)
        * shape('.>>>^^') => (1, 3, 2)
        """
        groups = functools.reduce(
            lambda a, b: a[:-1] + [a[-1]+b] if b in a[-1] else a + [b],
            text[1:],
            [text[0]]
        )
        return tuple(map(len, groups))

    @property
    def max_stable_path(self) -> int:
        """The maximum number of blocks the crucible can move in a straight
        line."""
        return 10

    @property
    def min_stable_path(self) -> int:
        """Minimal number of blocks the crucible moves in a straight line
        after starting moving or changing direction.
        """
        return 4


def find_path_with_min_cost(
    costs: Matrix, start: Point, goal: Point, cls = Crucible
):
    """Dijkstra algorithm to find a shortest path
    * uses PriorityQueue to decide which tiles of the city map (`costs`)
      to consider next.
    * allows more than one best-so-far (`best states`) in each tile as
      long as they differ by the path. More precisely, not the whole path
      but the final segment of it of the length `Crucible.max_stable_path`
      (after which the crucible turns). So, best-so-far means a state with
      the lowest heat loss among all the states with the same final path
      segment.
    """

    def push(cru: Crucible):
        """Add to priority queue"""
        queue.put((cru.cost, cru))

    def pop() -> Crucible:
        """Retrieve an item from the priority queue"""
        return queue.get()[-1]

    def add_state(cru: Crucible, old: Crucible = None):
        """Add a new crucible (`cru`) to best states or replace an old one
        with the new one."""
        if old and old.location in best_states:
            best_states[old.location].remove(old)
        best_states[cru.location].append(cru)

    def find_state(cru: Crucible) -> Optional[Crucible]:
        """Retrieve and return best state that
        * is located in the same tile as given crucible `cru`
        * has the same last path segment as `cru`
        In other words, a state that is a competitor of `cru`.
        """
        for crucible in best_states.get(cru.location, []):
            if crucible.has_same_final_path(cru):
                return crucible
        return None

    found = None

    # Here we store best crucibles (in terms of heat loss aka cost) that
    # reached each tile. There can be more than one crucible in a tile
    # because a tile can be reached following different paths.
    best_states: Dict[Point, List[Crucible]] = defaultdict(list)

    queue = PriorityQueue()
    push(cls(start, 0))

    while not queue.empty():
        crucible = pop()
        dprint(f"Current: {crucible}")

        if crucible.is_at(goal) and crucible.has_valid_path(True):
            dprint(f"..Goal reached!")
            found = crucible
            break

        for nbor in neighbors(costs, crucible):
            previous = find_state(nbor)
            if not previous:
                dprint("..is first visit")
                push(nbor)
                add_state(nbor)
                continue

            dprint("..competitors", previous)
            if nbor.cost < previous.cost:
                dprint("....new is better. replace")
                push(nbor)
                add_state(nbor, previous)

    if DEBUG:
        dump_queue(queue)

    return found.cost if found else None


def neighbors(city_map: Matrix, current: Crucible) -> Iterator[Crucible]:
    """Construct and yield one by one crucibles from the tiles on city map
    that are adjacent to the current crucible.
    Adjacent means in 4 directions: north, east, south, and west.

    Crucibles yielded are valid according to the rules:
    * a crucible cannot enter a location it already visited before
    * its moving trajectory is valid

    TODO
    * in case of UltraCrucible, there is a min_stable_path. This means,
      as soon as an ultra crucible turns, it can immediately advance
      a few blocks ahead (no need to generate crucibles for intermediate
      blocks and no need to consider turning at intermediate locations)
    """
    for loc in current.location.around4():
        cost = city_map.get(loc)
        if cost is None:  # loc is outside of the map
            continue

        crucible = type(current)(loc, cost).comes_from(current)
        dprint(f"\nNext tile: {crucible}")

        if crucible.has_valid_path():
            yield crucible


def dump_queue(queue):
    print(f"\n--- Dumping the queue ({queue.qsize()}) ---")
    while not queue.empty():
        print(queue.get())


def solve_p1(city_map: Matrix) -> int:
    """Solution to the 1st part of the challenge

    pypy runtime: 70s for real input
    """
    dprint(f"--- City Map (Heat Loss Map) ---:\n{city_map}\n-----")
    start = Point(0, 0)
    goal = Point(city_map.shape()) - (1, 1)
    return find_path_with_min_cost(city_map, start, goal)


def solve_p2(city_map: Matrix) -> int:
    """
    Solution to the 2nd part of the challenge.

    pypy (on gpu machine) runtime: 40min; RAM: 3.9G
    pypy (on localhost) runtime: 20 min, RAM: 4.6G
    """
    dprint(f"--- City Map (Heat Loss Map) ---:\n{city_map}\n-----")
    start = Point(0, 0)
    goal = Point(city_map.shape()) - (1, 1)
    return find_path_with_min_cost(city_map, start, goal, UltraCrucible)


tests = [
    # official tests
    (load_input('test.1.txt'), 102, 94),
    (load_input('test.4.txt'), None, 71),
    # non-official tests
    (load_input('test.2.txt'), 7, None),
    (load_input('test.3.txt'), 18-1, None),
]


reals = [
    (load_input(), 758, 892)
]


if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
