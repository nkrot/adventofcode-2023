#!/usr/bin/env python

ranges = [
    (2880930400, 17599561),
    (549922357,  200746426),
    (1378552684, 43534336),
    (155057073,  56546377),
    (824205101,  378503603),
    (1678376802, 130912435),
    (2685513694, 137778160),
    (2492361384, 188575752),
    (3139914842, 1092214826),
    (2989476473, 58874625),
]

count = sum([r[1] for r in ranges])
print("Total number of items", count)

ranges = sorted([(rng[0], rng[0]+rng[1]) for rng in ranges])

print("--- initial ---")
print(ranges)

def overlap(a, b) -> bool:
    """Test if two intervals overlap"""
    a, b = sorted([a, b])
    return not(a[1] < b[0])

new_ranges = [ranges.pop(0)]

while ranges:
    base_range = new_ranges.pop()
    new_range = ranges.pop(0)
    print("Overlap?", base_range, new_range)
    if overlap(base_range, new_range):
        print("..yes")
        # combine
        pass
    else:
        print("..no")
        new_ranges.append(base_range)
        new_ranges.append(new_range)

print("-- result --")
print(new_ranges)
