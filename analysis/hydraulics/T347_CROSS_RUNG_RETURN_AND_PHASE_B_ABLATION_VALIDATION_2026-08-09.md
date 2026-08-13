# T347 validation

**Status:** PASS

Validated 9,071 handovers from 3,622 tracks, 2,000 whole-track bootstrap replicates per frozen component, and 1,000 matched permutations.

All component formulas, point estimates, bootstrap intervals, loss curves, source hashes and gate logic were independently recomputed from the exported artifacts.

## Measurement warning

Using `abs(sin(theta)) < 0.01` as a descriptive near-horizontal threshold, 60.379% of retained entry directions and 58.814% of exits were near-horizontal. The numerical source is therefore strongly streamwise-oriented; this limits generalization to freely resolved two-dimensional circular paths.
