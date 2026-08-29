# T422 — Independent Detector-Bank Parent Test

**Status:** frozen before any T422 development, validation, or holdout outcome was calculated on 22 August 2026.  
**Orientation:** each reported coordinate runs from 0 to 2 and has its declared ridge at 1. `U=R` is the child crossover; `H=1` is the candidate parent ridge.  
**Dylan fidelity verdict:** EXACT ENOUGH TO TEST, reconfirmed after context compaction on 22 August 2026.

## F0 — frozen claim packet

**USER PRIOR:** pursue whether `H` is the unique physical parent or a generic parent-scale coordinate shared by several related cuts.  
**Identity:** the muoniated-acetone detector-population spin relation recorded by the ISIS EMU instrument; not an individual muon and not a neutrino event.  
**Child/current rung:** the `U,R` relation reconstructed from one detector bank.  
**Candidate parent:** the independently reconstructed lag-angle coordinate `H` from the opposing detector bank.  
**Invariant claim:** if `H` is a shared parent-scale relation rather than only same-cut arithmetic, a child `U=R` crossing in one bank should expose `H≈1` in the other bank.  
**Forbidden proxy:** computing child and parent from the same bank and calling that independence; identifying `H` as a unique physical parent merely because it is independently reconstructed; interpreting this population test as an individual-muon or neutrino event.

## Confirmed six-question card

### WHO

The same public ISIS/RAL muoniated-acetone archive used by T414–T421 is split into its physically separate forward and backward EMU detector banks. The observed identity remains the detector-population spin relation.

### WHAT

Construct child `U,R` from one bank and candidate-parent `H` from the other, then reverse the direction. Test whether the other-bank `H` approaches its 1.0 ridge when the child bank crosses `U=R`.

### WHEN

Use causal 128-native-bin histories advancing four native bins at a time. Detect sign-changing `U-R` crossings by interpolation and read the other bank simultaneously at zero lag; lead/event/lag traces are descriptive and may not replace the frozen zero-lag result.

### WHERE

The primary cuts are

```text
(U_F,R_F) -> H_B
(U_B,R_B) -> H_F
```

on separate 0–2 coordinates. Secondary calibrated cuts compare corresponding axial rings—inner/inner, middle/middle, outer/outer—against mismatched rings.

### WHY

This distinguishes a shared parent-scale physical relation from reuse of one reconstructed phase history. The ARA prediction fails for this instrument if other-bank `H` is no closer to 1 at child crossings than during ordinary history or the declared controls.

### HOW

Use the frozen T416 phase reconstruction and T421 `U,R,H` definitions without refitting their formulas. Aggregate event effects first within magnetic field, then across fields; use 10,000 field bootstraps and 1,000 circular-shift draws with seed 422, preserving development, validation, holdout, and RF-on/off partitions.

## Translation

### Plain restatement

One detector bank says when its child relation changes hands. The other detector bank is asked independently whether a larger relation is simultaneously at its balanced ridge.

### Mathematical representation

For bank `b∈{F,B}`, reconstruct phase history `z_b` and define

```text
U_b = 2 * local prediction loss_b / (local loss_b + null loss_b)
R_b = 2 * median_l |C_b,l|
H_b = 2 * median_l |arg(C_b,l)| / pi
C_b,l = mean(exp(i2pi z_b[j+l]) conj(exp(i2pi z_b[j]))), l=1,...,32.
```

At every interpolated child crossing `U_b=R_b`, let `p` be its read position and `b'` the opposing bank. The primary event effect is

```text
E_(b->b') = median_history |H_b'-1| - |H_b'(p)-1|.
```

Positive `E` means the independent bank is nearer its ridge at the child event than it ordinarily is.

### Back-translation

The test asks whether a handover visible in one independently recorded population occurs when the complementary population exposes a balanced parent-scale angle. It does not name the underlying parent mechanism.

### Added assumptions and discarded information

- **AI ADDITION:** the opposing EMU banks are independent observational views sufficient to challenge same-cut arithmetic; common source particles and common electronics may still create shared-mode structure.
- **AI ADDITION:** simultaneity at zero T416 reads is the primary cross-bank prediction; no development-selected lag is permitted.
- Detector-level spatial angle, raw hit-time covariance, and event identity are compressed by the phase reconstruction.
- A bank-level relation can support a shared population geometry but cannot identify an individual microscopic parent.

## Detector partitions

The one-based EMU spectrum layout is frozen as:

- forward bank: detectors 1–48;
- backward bank: detectors 49–96;
- forward inner/middle/outer: `1,4,...,46` / `2,5,...,47` / `3,6,...,48`;
- backward inner/middle/outer: `49,52,...,94` / `50,53,...,95` / `51,54,...,96`.

The code converts these to zero-based array indices. No detector is shared by the two primary bank reconstructions.

## Frozen data partitions

Reuse the T413 manifest without changing membership:

- development: 13 runs at 300 K;
- interleaved validation: 13 runs at 300 K;
- regime holdout: 20 runs at 202 K and 1800–2484 G;
- RF-on and RF-off remain separate sequences.

## Calibration and eligibility

For each bank/path, retain the T416 harmonic fit at the run's declared muon frequency. Because that basis uses samples before `2.25 µs`, only reads and crossings at or after `2.25 µs` enter T422 scoring; this makes the calibration historical rather than future information relative to every scored event. A sequence is primary-eligible only if both bank paths produce finite coordinates, finite basis condition, positive calibration improvement, and at least one complete child crossing. No outcome-based signal threshold is fitted.

Ring analysis is secondary and eligible per direction/ring only when both ring paths meet the same finite/positive checks and the correct-frequency calibration improvement exceeds the median wrong-frequency improvement in both rings. Ineligible rings remain reported; they cannot be silently discarded or promoted into the primary result.

## Controls

1. **Same-bank benchmark:** `child_b -> H_b`; shows the T421 within-view relation but is not evidence of independence.
2. **Circular time shift:** move other-bank `H` by a non-zero random read offset while keeping child crossings fixed.
3. **Wrong frequency:** reconstruct other-bank `H` at the four frozen T416 sidebands.
4. **Mismatched lineage:** use the next magnetic-field run with the same RF condition and normalized sequence progress.
5. **Mismatched ring:** for eligible ring cuts, compare corresponding axial rings with cyclically wrong axial rings.
6. **RF robustness:** report RF-on and RF-off effects separately; neither is allowed to disappear silently inside the combined result.

## Aggregation and uncertainty

- Median within each magnetic field first.
- Median across fields second.
- 10,000 field bootstraps; seed family 422.
- 1,000 non-zero circular shifts per stage.
- Report events, sequences, fields, directions, RF conditions, and ring eligibility.
- Development, validation, and holdout are scored separately.

## Frozen gates

- **G1 availability:** every primary-eligible sequence has finite `U,R,H`, control values, and disjoint detector membership; at least 90% of attempted sequences are eligible in each direction.
- **G2 bidirectional independent ridge:** the 95% bootstrap lower bound of `E_(F->B)` and `E_(B->F)` is above zero.
- **G3 timing specificity:** the real other-bank ridge distance beats its circular-shift null at empirical `p<0.05` in both directions.
- **G4 frequency specificity:** wrong-frequency distance minus correct other-bank distance has a 95% lower bound above zero in both directions.
- **G5 lineage specificity:** mismatched-run distance minus correct other-bank distance has a 95% lower bound above zero in both directions.
- **G6 RF robustness:** the field-balanced exposure is positive for RF-on and RF-off separately in both directions. This is a sign gate, not a separate significance claim.
- **G7 ring correspondence (secondary):** where all three ring pairs are eligible, the median corresponding-ring exposure exceeds the cyclic mismatched-ring exposure with a 95% lower bound above zero.

The primary independent-parent result is supported in a stage only when G1–G6 pass. G7 can strengthen spatial specificity but cannot rescue a failed primary result. Validation and holdout must both support the result before it is called archive-replicated.

## Falsifiers and boundaries

The registered result is not supported if either direction has non-positive ridge exposure, if shifted/wrong-frequency/mismatched-lineage controls perform equally well, or if one RF condition reverses the effect. A failure remains evidence about this bank-split measurement, not a universal refutation of ARA.

A pass establishes only that independently recorded detector populations share the T421 child-crossing/parent-ridge geometry. It does **not** prove that `H` is the unique physical parent, identify a microscopic mechanism, or locate an individual muon or neutrino handover.

## Visual contract

The durable report must show:

1. bank-separated `U,R,H` histories with axes, 0–2 orientation, ridge, time, and provenance;
2. event-centred child and other-bank parent traces in both directions;
3. ridge exposure with 95% intervals for both directions and all three stages;
4. real versus shifted, wrong-frequency, mismatched-lineage, and same-bank values;
5. RF-on/off effects;
6. calibrated ring correspondence and all ineligible-ring reasons;
7. coordinate distributions and at least one worked sequence;
8. the full Relational Bridge Map and Pivot Log.
