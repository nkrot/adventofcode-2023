from typing import List, Optional, Dict


# class SolutionNotFound(Exception):
#     pass

class Estimator:
    """
    Given a list of numbers with repetitions (recursive sequence) esimate
    a function that would generate this sequence.
    The function has the following components:
    * offset constants (non-recurrent arguments)
    * recurrent constants

    Tested for positive numbers only.
    Not tested for all zeroes and negative numbers.

    Usage:
    >>> f = Estimator()
    >>> f.analyse(List[int])
    >>> some_number in f

    Algorithm is based on the ideas from day_09.

    Related Terminology?
    - Arithmetic progression
    - Polynomial sequence
    - Constant-recursive
    - Linear recurrence
    """

    def __init__(self, **kwargs):
        self.inputs = None
        self.debug = kwargs.get("debug", False)
        # components of the function that we try to learn
        self.offset_constants = []
        self.recurrent_constants = []
        # cache of values to which the function is applied.
        self.multiples: Dict[int, int] = {}

    def dprint(self, *args):
        if self.debug:
            print(*args)

    def analyse(self, numbers: List[int]):
        self.inputs = list(numbers)
        self.offset_constants.append(self.inputs[0])  # from zero
        self.dprint(f"Inputs: {self.inputs}")
        self._analyse(numbers)
        return self

    def _analyse(self, numbers):
        """Analyse given numbers and estimate a function that can generate
        them.

        Based on the ideas from day_09.
        """
        steps = [numbers]
        for i in range(3):
            self.dprint(f"Step #{i}:")
            steps.append(self._reduce(steps[-1]))
            for j in range(2):  # we allow zero or one offset constant
                if all(n == 0 for n in steps[-1][j:]):
                    self.offset_constants.extend(steps[1][:j])
                    self.recurrent_constants.extend(steps[1][j:][:i])
                    self.dprint(f"Found offset constant(s): {self.offset_constants}")
                    self.dprint(f"Found recurrent constant(s): {self.recurrent_constants}")
                    break
            if self.recurrent_constants:
                break
        # remove offset constants because they are captured by recurrent ones
        if self.offset_constants == self.recurrent_constants:
            self.offset_constants.clear()

    def _reduce(self, numbers: List[int]):
        res = [
            abs(numbers[i]) - abs(numbers[i-1])
            for i in range(1, len(numbers))
        ]
        self.dprint(f"Reduced: {res}")
        return res

    def params(self):
        """Return all relevant arguments of the function w/o names.
        Sort of function signature. Used in tests :)
        """
        return (tuple(self.offset_constants), tuple(self.recurrent_constants))

    def __call__(self, *args):
        return self.analyse(*args)

    def __repr__(self):
        return "<{}: offsets={} recurrent={} inputs={}>".format(
            self.__class__.__name__,
            self.offset_constants,
            self.recurrent_constants,
            self.inputs
        )

    def __contains__(self, number: int) -> bool:
        return self.has_in_range(number)

    def has_in_range(self, number: int) -> bool:
        """Tell if given target value is in the range of the current function.
        """
        if number not in self.multiples:
            self.multiples[number] = self._count_steps_to(number)
        return bool(self.multiples[number])

    def _count_steps_to(self, target: int) -> Optional[int]:
        """Count how many times the function needs to be applied to reach
        given number `target`.

        If the result is > 0, then the target number belongs to the range
        of the function.
        """
        # self.dprint(f"number of steps to {target}")
        n_steps = 0
        if target < 0:
            return None
        if target == 0:
            return n_steps

        for c in self.offset_constants:
            target -= c
            n_steps += 1
            if target < 0:
                return None
            if target == 0:
                return n_steps

        if self.recurrent_constants:
            s = sum(self.recurrent_constants)
            n_steps += (target // s) * len(self.recurrent_constants)
            remainder = target % s
            # self.dprint(f"consumed steps {n_steps} and remainder {remainder}")
            if remainder == 0:
                return n_steps
            for n in self.recurrent_constants:
                n_steps += 1
                remainder -= n
                if remainder < 0:
                    return None
                if remainder == 0:
                    return n_steps
        return None

    # implement it for fun?
    # def __iter__(self):
    #     """Iterator that will generate all values according to the function
    #     that has been learnt"""
    #     pass
