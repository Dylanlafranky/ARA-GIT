# T343 inference addendum — non-overlapping block units

**Frozen:** 5 August 2026  
**Status:** frozen before any T343 endpoint was scored  
**Precedence:** replaces protocol section 7's lineage-level sign-flip unit and section 8's `20`-lineage eligibility requirement; all other protocol and computational-addendum rules remain unchanged

## Pre-score feasibility finding

The executable source audit found that four otherwise information-rich domains
contain only `3–10` named source lineages after the frozen split, despite
containing hundreds or thousands of non-overlapping T342 analysis blocks. A
literal `20`-lineage gate would make the seven-domain transfer question
ineligible by construction.

Individual transitions must still not be treated as independent.

## Frozen inference unit

T343 therefore uses the already-frozen, non-overlapping T342 blocks as the
resampling units. Those blocks:

- never cross a source lineage, split or continuity break;
- contain at most `256` consecutive valid states;
- were selected and capped before T343 existed;
- preserve each domain's native sampling cadence;
- prevent high-rate domains from receiving one vote per raw sample.

For each parent-versus-child comparison, compute the mean loss difference
inside every holdout block. Apply exactly `10,000` sign-flip permutations to
those block means using the seeds in the main protocol. No transition-level
IID p-value is permitted.

Named source lineages and their counts remain reported as a dependence
caveat. A later independent replication should prefer more independently
sampled lineages where available.

## Corrected eligibility gate

A domain is inferentially eligible when it has:

- at least `1,000` intact within-block holdout transitions;
- at least `20` frozen non-overlapping holdout blocks;
- all four parent addresses present;
- at least `20` holdout states in each address;
- finite scores for every intact, child-only and broken-pair model.

The cross-domain gate remains at least five eligible domains and at least 70%
passing for transferable support.

## Evidence fence

This correction was determined from source shape and test feasibility before
any T343 score was calculated. It does not use effect direction, p-values or
domain outcomes. The original protocol remains preserved for audit, and both
addenda are mandatory for reproduction.
