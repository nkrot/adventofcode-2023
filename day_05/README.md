p5.2 runs ca 40 minutes with python and ca. 4 minutes with pypy

TODO
1. How to reduce search space?
2. Study others' solutions


Idea to explore for 5.2:
- start from locations and go bottom up
- split the sieve(s) just above it into smaller sieved such that all inputs that
  fall into the subsieve to into one and the same location
- continue doing it for the previous sieve untill seeds level is reached
- we can assume that at the end at the top level we have groups of seeds
  such that all seeds from a single group fall through the levels and
  come one in the same location sieve.
- now check the location sieve that contains the minimal location:
  for all locations from that seed, find out what seed ends up in this location

