# Frozen protocol: same-phase ARA octave lineage

Frozen: 2026-07-31, Australia/Brisbane

## Question

Does an ARA scale lineage preserve a golden-ratio relation when the same phase is
followed from child scale to parent scale to grandparent scale?

“Child”, “parent”, and “grandparent” mean adjacent ARA octave scales. They do
not mean biological descendants.

## Data fixed before calculation

Use the Fibonacci-type parastichy scale families explicitly reported in
Swinton et al. (2016):

- Fibonacci: 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144
- Lucas: 1, 3, 4, 7, 11, 18, 29, 47, 76, 123
- F4: 1, 4, 5, 9, 14, 23, 37, 60, 97
- double Fibonacci: 2, 4, 6, 10, 16, 26, 42, 68, 110
- F5: 1, 5, 6, 11, 17, 28, 45, 73
- F8: 1, 8, 9, 17, 26, 43, 69, 112

These are published scale families rather than inferred missing phases.

## Frozen ARA readings

For every consecutive triple `(x0, x1, x2)` in each family:

1. Direct adjacent-rung reading:
   - child → parent ratio: `r01 = x1 / x0`
   - parent → grandparent ratio: `r12 = x2 / x1`
   - recurrence closure residual: `e_rec = (x2 - x1 - x0) / x2`
2. Same-phase two-rung reading, allowing a singularity flip between adjacent
   rungs:
   - `r02 = x2 / x0`

The sequence is also split into two independently evaluated phase-parity
lineages:

- Phase A: even-indexed terms
- Phase B: odd-indexed terms

This label fixes orientation only. Swapping the labels must not alter the
numerical conclusion.

## Frozen hypotheses

Primary:

- direct adjacent-rung ratios converge toward `phi`
- both phase-parity lineages show the same convergence

Flip-aware:

- same-phase two-rung ratios converge toward `phi^2`

Recurrence/Information³ crosswalk:

- the grandparent scale is reconstructed by the preceding two scale identities,
  `x2 = x1 + x0`

## Frozen rivals and controls

Compare direct-ratio absolute error against:

- `sqrt(2)`
- `1.5`
- `2`
- `e`

Compare two-rung absolute error against the squared versions of the same
constants.

Controls:

- reverse each lineage
- shuffle the internal order of each family with a fixed random seed
- swap the A/B phase labels

## Evaluation

Report:

- count of evaluated triples and same-phase jumps
- median and mean absolute error for every landmark
- per-family results
- Phase A and Phase B results separately
- convergence with increasing scale
- recurrence closure error
- shuffled-order comparison

No result may be described as an independent discovery of phi: every fixed
family obeys the Fibonacci recurrence by definition. This is a structural
crosswalk/calibration of the ARA scale interpretation. The empirical content is
that these families are observed in sunflower parastichy structure; the phi
limit itself is mathematically entailed by the recurrence.

## Falsification boundary

This calibration fails if:

- the direct ordered scale relation is not closer to `phi` than the frozen
  rival landmarks at sufficiently developed rungs;
- the separated Phase A and Phase B lineages do not approach `phi^2`;
- or the result survives equally well after destroying scale order.

A stronger future empirical test requires independently measured multi-scale
features whose scale ordering was not defined by a Fibonacci recurrence.
