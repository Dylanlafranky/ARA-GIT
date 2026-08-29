# T423 — parent Di-ARA temporal-architecture test

**Frozen:** 23 August 2026, before calculating any T423 development,
validation or holdout model comparison.  
**Originator hypothesis:** Dylan La Franchi.  
**Status at registration:** REGISTERED.

## Question

T421 located a full-detector child `U=R` crossover at a reconstructed parent
`H=1` ridge. T422 found a validation-only cross-bank ridge relation but did not
identify an independently specific parent. T423 asks whether `H` is better
understood as:

```text
M0: child C1 -> child C2
M1: child C1 -> one compressed parent H -> child C2
M2: child C1 -> parent PA -> parent PB -> child C2
```

The complete cyclic proposal is:

```text
child Di-ARA C1 -> parent PA -> parent PB -> alternative child Di-ARA C2
                   -> original child Di-ARA C1
```

M1 is allowed to be the coarse-grained appearance of M2. The test must not
declare them physically different systems merely because one has more
coordinates.

## Confirmed six-question card

### WHO — identity and generation

The physical identity is the full 96-detector muoniated-acetone ensemble in
the ISIS EMU archive already used by T416–T422. The test remains at detector-
population level. It does not observe an individual muon or either neutrino.

The reconstructed tiers are:

- child Di-ARA: the full-detector `U <-> R` relation;
- child handover types: the two opposite `U=R` crossing directions;
- candidate parent: the full-detector `H,Q` relation;
- `H`: unsigned parent amount/ridge coordinate;
- `Q`: signed parent orientation coordinate used to decompress entry and exit
  phases. Which sign is called `PA` or `PB` is frozen from development order,
  not assumed to be a universal physical polarity.

### WHAT — exact relation

Compare three nested causal predictors of the next opposite child crossover:

- **M0 child-only:** current `U,R`, their first differences, elapsed time since
  the current child crossover, parent-lifespan coordinate, field scale, RF
  condition and child-crossing direction;
- **M1 compressed parent:** M0 plus `H`, `dH` and `|H-1|`;
- **M2 decompressed parent Di-ARA:** M1 plus `Q`, `dQ` and `|Q-1|`.

The target is the remaining physical time to the next opposite `U=R` child
crossover. Every feature is read at or before the prediction slice. Models are
fit on development only. Results are reduced to one median absolute error per
child interval before fields are bootstrapped.

The independent order diagnostic finds every `Q=1` crossing between successive
opposite child crossovers and selects the one at which `H` is closest to its
ridge. Development freezes whether parent-orientation crossing direction is
the same as or opposite to child-crossing direction. Validation and holdout
then test that mapping without relabelling it.

### WHEN — ordering and causality

- the existing phase basis is calibrated using the first `2.25 microseconds`;
- T423 reads only the already saved causal T421 timelines at or after that
  boundary;
- a child interval begins at an interpolated `U=R` crossing and ends at the
  next opposite-direction crossing;
- prediction rows use only present and previous reconstructed values;
- development fits models and freezes parent orientation;
- validation and the 1800–2484 G / 202 K holdout are untouched scoring splits.

The order diagnostic is descriptive of the interval; the nested prediction is
the causal primary. A post-event landmark cannot be called a forecast trigger.

### WHERE — cut, rung and orientation

Use the full-detector relation, not the T422 forward/backward bank split.

- all ARA coordinates run from `0` to `2`;
- `U=R` is the child singularity/crossover;
- `H=1` is the candidate parent ridge;
- `Q=1` is the candidate internal parent `PA/PB` handover;
- the two child crossing directions define `C1` and `C2` relationally and are
  reversed symmetrically in the mirror cycle.

`PA` and `PB` are moving labels for entry and exit order inside the candidate
parent. They are not assigned to positive/negative `Q` until development
freezes the observed orientation.

### WHY — discriminating question and rivals

The test distinguishes:

1. direct child alternation with no useful parent state (`M0`);
2. one useful but unresolved parent landmark (`M1`);
3. an internally traversed parent Di-ARA (`M2`).

Rivals are child-only autocorrelation, monotonic lifespan, magnetic-field
cadence, RF condition, wrong-frequency parent reconstruction, temporally
reversed parent history, circular alignment and one unusually influential
field.

### HOW — implementation and uncertainty

1. Load the frozen T421 development, validation and holdout timelines.
2. Reconstruct interpolated child crossings without changing T421's formulas.
3. Form complete intervals only when the next crossing has the opposite
   direction. Preserve incomplete tails as exclusions.
4. Generate causal prediction rows inside each interval.
5. Fit standardized fixed-ridge linear regressions on development only. Use
   ridge penalty `1e-3`; do not tune it by validation.
6. Freeze the development parent-orientation mapping and all fitted model
   parameters in `T423_DEVELOPMENT_FREEZE.json`.
7. Score interval-balanced MAE, field-bootstrap uncertainty, event order,
   circular shift, wrong-frequency, reversed-parent and RF controls.
8. Run an independent saved-artifact validator.

## Frozen metrics

For interval `j` and model `m`:

```text
E_j(m) = median over causal slices in j of |predicted remaining us - true remaining us|
```

Model advantage is:

```text
Delta(m_a,m_b) = field-median E(m_a) - field-median E(m_b)
```

Positive `Delta(M0,M2)` means the decompressed parent improves on child-only;
positive `Delta(M1,M2)` means `Q` adds information beyond scalar `H`.

Parent-phase ridge exposure is:

```text
median_interval |H-1| - |H at selected Q=1 crossing - 1|
```

The temporal control shifts the parent `H,Q` history circularly within each
child interval by a non-trivial offset. The reversed control reverses `H,Q`
within the interval. Wrong-frequency controls use T421's frozen wrong-parent
`H,Q` columns.

## Frozen gates

### Availability

- **G1:** at least 20 complete opposite-direction child intervals in validation
  and at least 10 in holdout.

### Nested predictive architecture

- **G2:** validation `Delta(M0,M2)` has a positive 95% field-bootstrap lower
  bound.
- **G3:** validation `Delta(M1,M2)` has a positive 95% field-bootstrap lower
  bound.
- **G4:** holdout `Delta(M0,M2)` and `Delta(M1,M2)` are both positive. If G1
  holdout availability fails, G4 is UNAVAILABLE rather than passed.

### Parent-order geometry

- **G5:** at least 60% of validation child intervals contain a `Q=1` parent
  crossing in the development-frozen orientation, and that share exceeds the
  opposite-orientation share.
- **G6:** validation parent-phase ridge exposure has a positive 95% field-
  bootstrap lower bound.

### Specificity and robustness

- **G7:** correct M2 beats both wrong-frequency M2 and reversed-parent M2 in
  validation; both field-bootstrap lower bounds are positive.
- **G8:** `Delta(M1,M2)` is positive in RF-on and RF-off validation subsets.

## Status rules

- **SUPPORTED AS DECOMPRESSED PARENT DI-ARA:** G1–G8 pass.
- **SUPPORTED AS COMPRESSED PARENT ONLY:** G1, G2 and G4 pass; M1 beats M0,
  but G3 or the parent-order gates fail.
- **CHILD-ONLY ARCHITECTURE RETAINED:** M1 and M2 do not beat M0 on validation.
- **SUGGESTIVE / INCONCLUSIVE:** directional improvements appear but required
  confidence, specificity, availability or holdout gates fail.
- **NOT SUPPORTED:** the registered temporal order reverses, correct parent
  histories lose to controls, or the nested models reproducibly worsen the
  forecast.

The benchmark verdict and ARA geometry verdict must be reported separately.

## Forbidden interpretations

This test must not:

- call `H,Q` a unique microscopic parent without a direct independent physical
  observable;
- call detector-population timing an individual muon/neutrino decay clock;
- infer `PA/PB` polarity from sign alone;
- move a crossing, lag, tier or identity after seeing validation;
- call an interval-selected landmark a causal forecast;
- combine `U,R,H,Q` into one additive TE-ARA budget;
- treat missing holdout intervals as a successful transfer.

## Required durable outputs

- frozen development parameters and hashes;
- interval, prediction and parent-event tables for all splits;
- nested model comparisons and bootstrap intervals;
- control and RF tables;
- independent validation receipt;
- visual HTML report with full labels and provenance;
- post-test report with Bridge Map and Pivot Log;
- ledger and claims-status update.

