from typing import List, Optional

class Estimator:
    """
    Given a list of numbers, esimate a function that would generate this
    sequence of numbers.

    Based on the ideas from day_09
    """

    class SolutionNotFound(Exception):
        pass

    def __init__(self, **kwargs):
        self.initial_numbers = None
        self.number_of_steps = 0
        self.debug = kwargs.get("debug", False)
        # relevant for the function that we try to learn
        self.initial_value = None
        self.warmup_args = []
        self.recurrent_args = []

    def dprint(self, *args):
        if self.debug:
            print(*args)

    def reduce(self, numbers: List[int], prevs: List[int] = None):
        if not numbers:
            raise self.SolutionNotFound(self.initial_numbers)

        if all(n == 0 for n in numbers):
            self.recurrent_args.append(prevs[0])
            self.dprint(f"Done, recurrent argument(s) found = {self.recurrent_args}")
            return

        if numbers[0] <= 0: # TODO: can be several?
            self.dprint(f"..warm up argument found = {prevs}")
            self.warmup_args.append(prevs[0])
            numbers = numbers[1:]
            prevs = prevs[1:]

        if all(n == 0 for n in numbers[1:]):
            # [11, 0,0,0,0,]
            self.warmup_args.append(prevs[0])
            self.dprint(f"..warm up argument found = {prevs}")
            self.recurrent_args.append(prevs[1])
            self.dprint(f"Done, recurrent argument(s) found = {self.recurrent_args}")
            return

        cnt = self.sum_to_zero(numbers)
        if cnt:
            self.dprint(f"..sum to zero: {cnt} namely {numbers[:cnt]}")
            self.recurrent_args.extend(prevs[:cnt])
            self.dprint(f"Done, recurrent argument(s) found: {self.recurrent_args}")
            return

        reduced = [
            numbers[i] - numbers[i-1]
            for i in range(1, len(numbers))
        ]
        self.dprint(f"reduced at step {self.number_of_steps} = {reduced} sum = {sum(reduced)}")
        self.number_of_steps += 1

        self.reduce(reduced, numbers)

    def sum_to_zero(self, numbers: List[int]) -> int:
        """Find out how many initial elements of the list sum up to 0 and
        return this quantity.
        """
        s = 0
        for i, n in enumerate(numbers):
            s += n
            if s == 0:
                return 1+i
        return 0

    def __call__(self, numbers: List[int]):
        self.initial_numbers = list(numbers)
        self.initial_value = self.initial_numbers[0]
        return self.reduce(numbers)

    def __repr__(self):
        return "<{}: number_of_steps={} initial_value={} warm_up_args={} recurrent_args={} initial_numbers={}>".format(
            self.__class__.__name__,
            self.number_of_steps,
            self.initial_value,
            self.warmup_args,
            self.recurrent_args,
            self.initial_numbers
        )

    def number_of_steps_to(self, target: int) -> Optional[int]:
        """"""
        # self.dprint(f"number of steps to {target}")
        target -= self.initial_value
        n_steps = 1
        if target < 0:
            return None
        if target == 0:
            return n_steps
        if self.warmup_args:
            target -= sum(self.warmup_args)
            n_steps += len(self.warmup_args)
        if self.recurrent_args:
            s = sum(self.recurrent_args)
            n_steps += (target // s) * len(self.recurrent_args)
            remainder = target % s
            # self.dprint(f"consumed steps {n_steps} and remainder {remainder}")

            if not remainder:
                return n_steps

            for n in self.recurrent_args:
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

# test.d9.1.txt | 63  | 7 14 21 28 35 42 49 56 63 70 | (+7)        |
# test.d9.2.txt | 64  | 5 12 19 26 33 40 47 54 61 68 | (+7)        |
# test.d9.3.txt | 65  | 4  6 11 13 18 20 25 27 32 34 | (+2, +5)    |
# test.d9.4.txt | 68  | 8 15 22 29 36 43 50 57 64 71 | (+7)        |
# test.d9.5.txt | 69  | 1  2  3 9  10 16 17 23 24 30 | +1, (+1,+6)  |
# test.d9.5.2.txt | 69 | . 2  3 9  10 16 17 23 24 30 | (+1, +6)     |

TARGET_STEP = 1_000_000_000 - 1

tests = [
    # easy cases
    # pattern = (+7)+
    # (63, [7, 14, 21, 28, 35, 42, 49, 56, 63, 70],
    #      [(6, None), (7, 1), (19, None), (21, 3), (28, 4), (70, 10), (TARGET_STEP, None)]),
    # (64, [5, 12, 19, 26, 33, 40, 47, 54, 61, 68],
    #      [(TARGET_STEP, 142857143)]),
    # (68, [8, 15, 22, 29, 36, 43, 50, 57, 64, 71],
    #      [(TARGET_STEP, None)]),

    # pattern = (+2,+5)+
    # (65,     [4, 6, 11, 13, 18, 20, 25, 27, 32, 34, 39],
    #          [(4, 1), (6, 2), (11, 3), (13, 4), (17, None), (18, 5), (39, 11), (TARGET_STEP, None)]),
    # ("65.1", [   6, 11, 13, 18, 20, 25, 27, 32, 34, 39],
    #          [(TARGET_STEP, None)]),

    # pattern = (+1,+6)+
    # ("69.1", [    2,  3, 9,  10, 16, 17, 23, 24, 30], [(TARGET_STEP, None)]),

    # pattern = 1, (+1, +6)+
    (69, [1,  2,  3, 9,  10, 16, 17, 23, 24, 30],
     [(TARGET_STEP, None)]),

    # patten = +96, (+38)+
    (104375, [12, 108, 146, 184, 222, 260, 298, 336, 374, 412, 450, 488, 526, 564, 602, 640, 678, 716, 754, 792], []),

    # pattern = +27, (+38)+
    (104276, [54, 81, 119, 157, 195, 233, 271, 309, 347, 385, 423, 461, 499, 537, 575, 613, 651, 689, 727, 765], [])
]


def test_estimator():
    for load_value, numbers, steps_tests in tests:
        print(f"--- Learn function to get {load_value} from {numbers} ---")
        estimator = Estimator(debug=True)
        try:
            estimator(numbers)
            print(estimator)
            for target, exp_n_steps in steps_tests:
                 act_n_steps = estimator.number_of_steps_to(target)
                 print(exp_n_steps == act_n_steps, exp_n_steps, act_n_steps)
        except Estimator.SolutionNotFound:
            print("--> Solution not found")
        print("==== END ====\n")


if __name__ == "__main__":
    test_estimator()
