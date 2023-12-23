from typing import Any, Callable, List, Optional, Tuple, Union

from .point import Point

T_COORD = Tuple[int, int]

class Matrix(object):
    """Matrix (n_rows, n_cols)

    Implementing it for fun.
    Not as good as pandas dataframe or numpy matrix

    TODO:
    allow passing a callable as a parameter to __init__ for constructing
    a new value.
    """
    def __init__(self, *args):
        if len(args) == 1:
            # ex: Matrix(List[List[Any]])
            # print("From List[List[Any]]")
            n_rows, n_cols = len(args[0]), len(args[0][0])
            assert n_rows > 0 and n_cols > 0, (
                    f"Wrong dimensions requested: {(n_rows, n_cols)}")
            self.values = args[0]  # TODO: make a copy of 2 levels
        elif len(args) > 1:
            # ex: Matrix(2,3, 100)
            n_rows, n_cols = args[:2]
            # TODO: is callable, get value by envoking it
            value = args[2] if len(args) > 2 else 0
            self.values = [[value] * n_cols for _ in range(n_rows)]

    def shape(self) -> Tuple[int, int]:
        return (len(self.values), len(self.values[0]))

    def __len__(self) -> int:
        r, c = self.shape()
        return r*c

    def _is_in_span(self, xy: Tuple[int, int]) -> bool:
        """Check that given 2D coordinate `xy` exists in the matrix"""
        n_rows, n_cols = self.shape()
        x, y = xy
        return 0 <= x < n_rows and 0 <= y < n_cols

    def __getitem__(self, xy: Union[int, Tuple[int, int]]):
        _xy = xy
        xy = self.to_coord(xy)
        if self._is_in_span(xy):
            x, y = xy
            return self.values[x][y]
        raise IndexError(f"Matrix index {_xy} out of range")

    def __setitem__(self, xy: Union[int, Tuple[int, int]], newval: Any):
        xy = self.to_coord(xy)
        if self._is_in_span(xy):
            x, y = xy
            self.values[x][y] = newval
        else:
            raise IndexError(f"Matrix index {xy} out of range")

    def get(self, xy: Union[int, Tuple[int, int]], default = None):
        xy = self.to_coord(xy)
        if self._is_in_span(xy):
            x, y = xy
            return self.values[x][y]
        else:
            return default

    def to_coord(self, xy: Union[int, Tuple[int, int], Point]) -> T_COORD:
        """Canonical representation of a coordinate"""
        if isinstance(xy, int):
            return self.to_2d(xy)
        elif isinstance(xy, (tuple, list, Point)) and len(xy) == 2:
            return tuple(xy)
        else:
            raise ValueError(f"Wrong coordinate '{xy}' '{type(xy)}'")

    def to_1d(self, xy: Union[int, Tuple[int, int], Point]) -> int:
        """Convert 2D coordinate to linear (1D) coordinate, for example:
        (0, 0) -> 0
        (0, 1) -> 1
        (1, 0) -> 10  if n_cols is 10
        (1, 1) -> 11  if n_cols is 10
        (1, 1) -> 21  if n_cols is 20

        Calculation depends on the number of columns in the matrix.
        It is not checked whether resulting coordinate is out of matrix.
        """
        if isinstance(xy, int):
            return xy
        elif isinstance(xy, (tuple, list, Point)) and len(xy) == 2:
            _, n_cols = self.shape()
            x, y = xy
            return x * n_cols + y
        else:
            raise ValueError(f"Wrong coordinate '{xy}' '{type(xy)}'")

    def to_2d(self, idx: int) -> Tuple[int, int]:
        """Convert linear coordinate to 2d coordinate, for example:
        0 -> (0, 0)
        1 -> (0, 1)

        Calculation depends on the number of columns in the matrix.
        It is not checked whether resulting coordinate is out of matrix.
        """
        _, n_cols = self.shape()
        return (idx // n_cols, idx % n_cols)

    def __repr__(self):
        # Weird, not sure if I need it :)
        row_sep, col_sep = "\n", ", "
        values = row_sep.join(
            "[{}]".format(col_sep.join(repr(v) for v in row))
            for row in self.values
        )
        values = "[\n{}\n]".format(values)
        return "<{}: values={}>".format(self.__class__.__name__, values)

    def __str__(self):
        row_sep, col_sep = "\n", ""
        return row_sep.join(
            col_sep.join(str(v) for v in row)
            for row in self.values
        )

    def __iter__(self):
        return MatrixIterator(self)

    def transpose(self):
        shape = reversed(self.shape())
        other = type(self)(*shape)
        for xy, val in self:
            x, y = xy
            other[(y,x)] = val
        return other

    def find(self, predicate: Callable) -> Optional[Tuple]:
        """
        TODO: any predicate to check xy? is it useful?
        """
        for xy, value in self:
            if predicate(value):
                return xy, value
        return None

    def findall(self, predicate: Callable) -> List[Tuple]:
        selected = []
        for xy, value in self:
            if predicate(value):
                selected.append((xy, value))
        return selected

    def rows(self):
        return self.values

    def columns(self):
        # TODO: reimplement w/o creating a new matrix?
        return self.transpose().rows()


class MatrixIterator(object):

    def __init__(self, matrix):
        self.matrix = matrix
        self.shape = matrix.shape()
        self.pos = (0, 0)

    def __iter__(self):
        return self

    def _incr_pos(self) -> Tuple[int, int]:
        """columns then rows
        Return current position before incrementing
        """
        r, c = self.pos
        if c+1 == self.shape[-1]:
            self.pos = (r+1, 0)
        else:
            self.pos = (r, c+1)
        return (r, c)

    def __next__(self) -> Tuple[Tuple[int, int], Any]:
        """columns then rows"""
        curr_pos = self._incr_pos()
        try:
            val = self.matrix[curr_pos]
        except IndexError:
            raise StopIteration()
        return curr_pos, val
