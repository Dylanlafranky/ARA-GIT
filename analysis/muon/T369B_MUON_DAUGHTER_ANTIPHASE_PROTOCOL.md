# T369B post-result diagnostic - daughter timing anti-phase

**Frozen:** 12 August 2026, after T369 exposed a `-0.9992%` first-neutron
timing result but before inspecting the signed prompt-time/neutron-time
orientation  
**Evidence class:** explicitly post-result diagnostic; not an untouched
confirmatory test

## Question

Does T369's negative timing score hide an opposite Phase-B relation, or is
there no stable timing relation in the released detector coordinates?

## Who, what, where, when, why and how

- **Who:** T369 holdout rows containing both a prompt child and at least one
  tagged neutron.
- **What:** development-ECDF ARA coordinates for prompt time `x_G` and first
  neutron-tag time `x_N`, each on `0-2`.
- **Where:** within the same stopped-muon source row.
- **When:** prompt child at `1.1-5 us`, followed by the first delayed neutron
  tag.
- **Why:** an anti-phase daughter relation predicts `x_N ~= 2-x_G`; absence of
  a stable relation predicts neither diagonal.
- **How:** compare aligned error `|x_N-x_G|` with anti-phase error
  `|x_N-(2-x_G)|`; compare same-bin and anti-bin occupancy in a frozen 8x8
  table; calculate rank correlation; and repeat after 1,000 shuffles of
  neutron time within observed neutron-multiplicity classes.

## Frozen interpretation

- **Anti-phase supported:** anti-phase mean absolute error is at least 1%
  lower than the shuffled median, no more than 10/1,000 shuffles equal or
  exceed the effect, the 95% bootstrap interval is wholly positive, and the
  strict `5-15 MeV` window retains direction.
- **Same-phase supported:** the symmetric criteria hold for aligned error.
- **No oriented relation:** neither orientation passes.

The exact value `-0.9992%` is not itself an ARA pole or ridge. It is only the
observation that motivated this diagnostic. First-neutron detection time is
also not neutron-emission time, so even a passed orientation would describe
the released detector relation first.

