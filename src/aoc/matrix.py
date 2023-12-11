from typing import Tuple, Any, Callable, Optional, List


class Matrix(object):
    """Matrix (n_rows, n_cols)

    Implementing it for fun.
    Not as good as pandas dataframe

    TODO:
    allow passing a callable as a parameter to __init__ for constructing
    a new value.
    """
    def __init__(self, *args):
        if len(args) == 1:
            # from List[List]
            shape = len(args[0]), len(args[0][0])
            self.__init__(*shape)
            self.values = args[0]  # TODO: make a copy of 2 levels
        elif len(args) > 1:
            n_rows, n_cols = args[:2]
            # TODO: is callable, get value by envoking it
            value = args[2] if len(args) > 2 else 0
            self.values = [[value] * n_cols for _ in range(n_rows)]

    def shape(self) -> Tuple[int, int]:
        return (len(self.values), len(self.values[0]))

    def _is_in_span(self, xy: Tuple[int, int]) -> bool:
        """Check that given coordinate `xy` exists in the matrix"""
        n_rows, n_cols = self.shape()
        x, y = xy
        return 0 <= x < n_rows and 0 <= y < n_cols

    def __getitem__(self, xy: Tuple[int, int]):
        if self._is_in_span(xy):
            x, y = xy
            return self.values[x][y]
        raise IndexError(f"Matrix index {xy} out of range")

    def __setitem__(self, xy: Tuple[int, int], newval: Any):
        if self._is_in_span(xy):
            x, y = xy
            self.values[x][y] = newval
        else:
            raise IndexError(f"Matrix index {xy} out of range")

    def get(self, xy: Tuple[int, int], default = None):
        if self._is_in_span(xy):
            x, y = xy
            return self.values[x][y]
        else:
            return default

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

    def __str__orig(self):
        row = self.values[0]
        print(type(row), dir(row))
        return "\n".join([str(row) for row in self.values])

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
