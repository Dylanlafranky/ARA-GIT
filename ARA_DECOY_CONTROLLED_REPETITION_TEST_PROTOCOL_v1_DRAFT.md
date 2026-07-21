# ARA decoy-controlled repetition test protocol v1

**Status:** `DRAFT — NOT FROZEN / NO OUTCOME DATA MAY BE OPENED UNDER THIS VERSION`  
**Created:** 21 July 2026  
**Purpose:** measure whether the already-declared ARA geometry discriminates real structures from matched
alternatives more often than chance.

## 1. Primary claim

Across independently selected domains, a mapping frozen from the ARA core geometry will assign the real target a
higher preregistered compatibility score than nine matched decoy targets more often than the exchangeable null rate
of \(1/10\).

This tests repeatable constraint and discrimination. It does not directly test the unrestricted claim that every
thing in the universe is ARA-shaped.

## 2. Geometry permitted before the test

The primary mapping may use only core rules recorded before target data are opened:

1. a declared reversible 0–2 diameter with locally named poles;
2. 1.0 as a candidate equal-participation/cancellation/resonance ridge, with the physical discriminator declared;
3. orientation and phase/anti-phase reversal;
4. a declared observation grain and time slice;
5. child, current and parent rungs with an explicit coarse-graining direction;
6. two identities plus their retained ordered relation;
7. a prewritten ARA/TE-ARA normalisation when activity or participation is measured;
8. Phi, hexagon/pentagon or leak landmarks only when a numerical gate and a matched non-Phi control are frozen.

No new landmark may be introduced after a target packet is opened.

## 3. Unit of analysis and independence

The primary unit is **one locked result per domain family**, not one result per equation, variable, horizon, seed,
subtest or visual panel.

The initial battery will contain 12 domain families. Two targets are considered independent only if they do not
share the same governing identity, raw dataset, simulation, label construction or fitted transformation. Closely
related work is aggregated before scoring.

The previous Maxwell/plasma trail is one family. The previous prime-arithmetic trail is one family. Their internal
tests cannot be re-entered separately in the prospective primary count.

## 4. Target and decoy packets

For every domain, a curator who does not score the mapping prepares:

- one real target packet;
- nine matched decoy packets;
- an encrypted or separately held target key;
- a written matching audit.

Decoys must match the real target in data type, length, sampling cadence, units/dimensionality, missingness, broad
smoothness or sparsity, and ordinary difficulty. They must not be trivially identifiable from file names, metadata,
plot styling or impossible values.

Valid decoys may be independently measured comparison systems, label-permuted counterparts where permutation is
scientifically meaningful, or synthetic controls generated without the ARA score. The same decoy mechanism is used
for every packet within a domain.

## 5. Per-domain freeze

Before decoding the ten packets, record:

1. identity being measured;
2. Phase A and Phase B;
3. orientation of 0 and 2;
4. observational grain, spatial boundary and time window;
5. child/current/parent scale relation;
6. exact mathematical transformation from raw values to ARA coordinates;
7. one scalar primary fit score, including tie handling;
8. expected direction or landmark;
9. one failure condition;
10. all exclusions and numerical tolerances;
11. source hashes and executable code hash.

Exploratory plots and secondary scores may be generated only after the primary ranking is sealed.

## 6. Primary endpoint

For domain \(d\), define

\[
Y_d=
\begin{cases}
1,&\text{the real target has the uniquely highest frozen ARA-fit score},\\
0,&\text{otherwise.}
\end{cases}
\]

An exact tie for first is a failure in the primary analysis. With 12 domains,

\[
X=\sum_{d=1}^{12}Y_d.
\]

Under the exchangeable null,

\[
X\sim\operatorname{Binomial}(12,0.1).
\]

The primary pass gate is:

\[
X\ge4,
\qquad
P(X\ge4)=0.025637470165.
\]

The exact p-value for the observed \(X\) will be reported even if the pass gate is not reached.

## 7. Required negative controls

Each domain must also run:

- reversed pole labels;
- a shuffled or temporally broken relation where scientifically valid;
- the strongest conventional local baseline available without additional tuning;
- the same ARA score on all nine decoys;
- any domain-specific nuisance-only score capable of revealing a matching failure.

Passing the primary gate while a trivial nuisance score also identifies the real targets invalidates the battery until
the decoys are repaired.

## 8. Companion historical provenance audit

The provenance ledger will be audited separately rather than mixed into the prospective 12-domain count.

1. Enumerate every eligible pre-lookup statement in the declared time window, including recorded misses.
2. Preserve the statement text and timestamp while removing its later verdict.
3. Pair the actual later finding with nine matched decoy findings.
4. Ask at least two blinded independent evaluators to rank compatibility under a frozen rubric.
5. Resolve neither disagreements nor ambiguous statements by discussion before the rankings are sealed.
6. Report evaluator-specific and consensus top-rank rates, inter-rater agreement, and an exact randomisation test.

This audit estimates the historical chance-match rate that the pilot sensitivity analysis could not identify.

## 9. Verdicts

- `PRIMARY PASS`: at least 4 of 12 real targets rank uniquely first and the nuisance audit passes.
- `PRIMARY NULL`: fewer than 4 uniquely first with an adequate instrument and valid decoys.
- `INVALID DECOY SET`: packet identity is revealed by nuisance structure or exchangeability materially fails.
- `INCONCLUSIVE`: fewer than 12 valid independent domain outcomes remain.

No secondary result can convert `PRIMARY NULL` into `PRIMARY PASS`.

## 10. Reporting requirements

The final report must publish:

- all 120 packet scores and ranks;
- the target-key reveal;
- every failure and exclusion;
- conventional, reversed-pole and shuffled-control results;
- exact p-values and confidence intervals;
- source/code hashes;
- the unchanged frozen protocol;
- a plain-language statement distinguishing repeatable discrimination from proof of universal ontology.

## 11. Freeze requirements still open

This draft must not be frozen until the following are selected without viewing target outcomes:

- the 12 independent domain families;
- curator and independent evaluators;
- decoy-generation rules for every domain;
- the one scalar score used in every family, or a predeclared family-specific score registry;
- public timestamping or commit procedure;
- treatment of domains for which no adequate matched decoys can be built.

