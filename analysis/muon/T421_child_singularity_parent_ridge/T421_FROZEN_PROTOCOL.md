# T421 — Child Singularity / Parent Ridge Hierarchy

Status: frozen before development, validation, and holdout scoring on 22 August 2026.

## ARA identity map

- **Observed identity:** the detector-population spin relation of the muoniated-acetone radical. This is not an individual muon and is not a neutrino event.
- **Child ARA:** independently constructed openness `U` and closure `R` histories from T419/T420.
- **Child singularity event:** a sign-changing crossover of `U-R`, linearly interpolated to `U=R`. The observed crossing coordinate may differ from the ideal 1.0 landmark because of identity asymmetry and external participation.
- **Parent ARA:** the lag-angle history `H` from T420, computed from the angular component of the complex lag relation whose magnitude supplies `R`.
- **Parent ridge:** `H=1` on its own 0–2 coordinate.
- **Correct hierarchy:** the child crossover is tested against the parent ridge. `H` is not added to `U+R`, and no `U+R+H=2` claim is made.

The primary ARA prediction is

```text
child singularity: |U-R| -> 0
parent ridge:      |H-1| -> 0
```

allowing observable distortion and a development-frozen timing offset.

## Data and frozen splits

Reuse the T414/T416/T419/T420 public ISIS/RAL muoniated-acetone archive and manifest without changing membership:

- development: 13 runs at 300 K;
- interleaved validation: 13 runs at 300 K;
- regime holdout: 20 runs at 202 K and 1800–2484 G;
- RF-on and RF-off remain separate histories;
- each read is based only on the preceding 128 native bins and advances by four native bins.

## Coordinates

For a phase history `z`, define complex lag relations

```text
C_l = mean(exp(i 2pi z[j+l]) * conj(exp(i 2pi z[j]))) , l=1,...,32.
```

The existing coordinates remain unchanged:

```text
U = 2 * local prediction loss / (local loss + null loss)
R = 2 * median_l |C_l|
H = 2 * median_l |arg(C_l)| / pi
```

Define two distances:

```text
d_child  = |U-R|
d_parent = |H-1|.
```

To retain the orientation erased by the absolute value in `H`, define a signed parent branch coordinate

```text
J = mean_l C_l / max(|C_l|, eps)
Q = 1 + Im(J),        Q in [0,2].
```

`Q>1` and `Q<1` are opposite angular branches; `Q=1` is their balanced signed ridge. `|J|` is retained as branch concentration and no row is discarded when it is small.

Wrong-frequency `H_wrong` and `Q_wrong` use the same sideband family frozen in T416/T420.

## Event construction

Within each run/RF history, find adjacent reads where `U-R` changes sign. Interpolate the crossing time, `U`, `R`, `H`, and `Q` linearly. An exact endpoint zero is allowed once; no hand-picked band around the crossing is used.

For every event retain four reads before and four reads after for the signed-branch test. Events lacking this complete local window remain valid for ridge alignment but are ineligible for branch reversal.

## Timing offset

Evaluate integer offsets from -8 to +8 T416 reads. Positive offset means the parent `H` is read after the child crossover; negative means it is read before.

Development selects the offset with the smallest field-balanced median `d_parent`. Ties choose the smallest absolute offset, then the negative offset. The selected offset is frozen before validation and holdout. Zero-offset results remain separately reported as the literal simultaneous hierarchy test.

## Primary tests

### T1 — Parent-ridge exposure

At the frozen child-to-parent offset, compare event `d_parent` with the median `d_parent` across that event's complete run/RF history.

```text
ridge exposure = history median d_parent - event d_parent.
```

Positive values mean the parent is closer to its ridge at the child singularity than it normally is.

### T2 — Timing specificity

Within each run/RF history, circularly shift the complete `H` history by a non-zero random offset before reading it at the fixed child crossings. Use 1,000 draws and the frozen seed 421. The real field-balanced median `d_parent` must lie below the shifted null with empirical `p<0.05`.

### T3 — Identity specificity

Two controls must be worse than the correct parent coordinate:

- wrong-frequency `H_wrong` from the frozen T416/T420 sidebands;
- mismatched-history `H_mismatch` from the next magnetic-field run in cyclic field order, matched by RF condition and normalized history progress.

Comparison effects are `control d_parent - correct d_parent`; positive favours the declared parent.

### T4 — Signed parent branch reversal

For each eligible event,

```text
DeltaQ = median(Q after) - median(Q before).
direction code = +1 for R->U and -1 for U->R.
raw oriented branch = direction code * DeltaQ.
```

Development freezes one global orientation sign from the field-balanced median raw-oriented branch. Validation and holdout apply that sign unchanged. A positive held-out effect means the two child crossing directions use opposite sides of the signed parent branch.

Wrong-frequency and circularly shifted `Q` are retained as controls.

## Aggregation and uncertainty

- First take the median within each magnetic field so repeated crossings and RF histories do not inflate replication.
- Then take the median across fields.
- Use 10,000 field bootstraps and frozen seed 421 for 95% intervals.
- Report event, eligible-event, sequence, and field counts.
- Report development, validation, and holdout separately.

## Frozen gates

- **G1 availability:** every eligible run/RF history supplies `U`, `R`, `H`, `Q`, wrong-frequency controls, and finite distances.
- **G2 literal hierarchy:** zero-offset parent-ridge exposure has a field-bootstrap 95% lower bound above zero.
- **G3 frozen-offset hierarchy:** exposure at the development-frozen offset has a 95% lower bound above zero.
- **G4 timing specificity:** shifted-null empirical `p<0.05`.
- **G5 frequency specificity:** wrong-frequency distance-minus-correct distance has a 95% lower bound above zero.
- **G6 lineage specificity:** mismatched-history distance-minus-correct distance has a 95% lower bound above zero.
- **G7 signed reversal:** development-oriented branch effect has a 95% lower bound above zero.
- **G8 signed controls:** correct oriented branch exceeds both wrong-frequency and shifted-branch controls with 95% lower bounds above zero.

The full hierarchy is supported in a stage only if G1–G8 all pass. A narrower child-singularity/parent-ridge result may still be supported if G1–G6 pass while signed direction fails.

Validation and holdout must both support a claim before it is described as archive-replicated.

## Falsifiers and boundaries

The child/parent hierarchy is weakened or falsified for this instrument if real child crossings are no closer to `H=1` than ordinary history, shifted time, wrong frequency, or a different lineage. The directional opening/closing interpretation is weakened if `Q` does not reverse with crossing direction or if its controls perform equally well.

Even a positive result concerns this detector-population relation. It does not by itself establish individual-muon structure, neutrino production, or a universal physical law.

## Visual contract

The final report must show:

1. labelled U, R, H, and Q histories for validation and holdout examples;
2. the lag profile from -8 to +8 reads with zero and the frozen offset marked;
3. parent-ridge distance at real, shifted, wrong-frequency, and mismatched controls;
4. event-centred U/R/H histories;
5. signed Q before/after crossing by direction;
6. field-level exposure and branch effects;
7. every frozen gate, sample count, units, identity, and caveat.
