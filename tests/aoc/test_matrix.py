import pytest
from aoc import Matrix

# Test plan
# an element can be accessed using 2D or linear coordinates:
# print(plan[1])
# for idx, (xy, val) in enumerate(plan):
#     print(xy, val, plan[idx], val == plan[idx], plan.to_1d(xy) == idx)
# setting new value should also be possible with 2d and 1d linear coordinate
#     plan[idx] = "x"
# print(plan)
# Point object can also be used as 2d coordinate

# test methods to_1d(), to_2d(), although to_2d() is tested implicitly
# when getting/setting by linear coordinates
