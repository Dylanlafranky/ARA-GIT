# T422 — independent detector-bank parent test

**Date:** 22 August 2026  
**Status:** **NOT SUPPORTED [pre-registered]** for the independent-parent claim  
**Geometry status:** **A validation-only cross-bank ridge exposure was recovered, but it was not frequency-specific, did not reproduce in development and could not be evaluated in the high-field holdout.**

## 1. Test identity and one-sentence outcome

| Field | Entry |
|---|---|
| Test ID and name | T422 — independent detector-bank parent test |
| Domain and dataset | ISIS EMU muoniated-acetone population spectra; development, interleaved validation and high-field/temperature holdout runs |
| Frozen protocol | `T422_FROZEN_PROTOCOL.md` |
| Script | `t422_independent_detector_bank_parent.py` |
| Validator | `validate_t422.py` |
| Result data | `results/T422_{DEVELOPMENT,VALIDATION,HOLDOUT}_RESULTS.json` and supporting CSV files |
| Claim class | Real-data candidate-mechanism test with frozen development/validation/holdout gates |
| One-sentence outcome | Opposing-bank `H` approached its ridge at validation child crossings with timing specificity, but the registered bidirectional, frequency-specific, lineage-specific and holdout requirements failed. |

**Orientation signature:** every ARA coordinate runs from 0 to 2. The child event is the reconstructed `U=R` crossing in one detector bank. The candidate parent is the opposing bank's reconstructed lag-angle coordinate `H`; `H=1` is its ridge. Forward and backward banks are reversed symmetrically rather than assigned as Phase A and Phase B.

## 2. Confirmed six-question test card

- **WHO — identity and generation:** the muoniated-acetone detector-population spin relation, not an individual muon or neutrino. EMU forward and backward detector banks are independent views of the same ensemble and were not assigned as Phase A/Phase B.
- **WHAT — exact relation:** construct child `U,R` from one bank and candidate-parent `H` from the disjoint other bank; ask whether the child's `U=R` crossing independently exposes the other's `H=1` ridge.
- **WHEN — ordering:** causal 128-bin histories sampled in four-bin steps; crossings were linearly interpolated. The first 2.25 microseconds calibrated the phase basis and were not scored. Simultaneous zero lag was primary; lead/event/lag histories were descriptive.
- **WHERE — cut and orientation:** `(U_F,R_F) -> H_B` and `(U_B,R_B) -> H_F` on independent 0–2 coordinates. Calibrated inner/middle/outer rings were secondary only.
- **WHY — discriminating question:** separate a shared parent-scale relation from same-cut arithmetic reuse, common-mode response, timing coincidence, wrong-frequency reconstruction and neighbouring-field lineage.
- **HOW — implementation:** field-first medians; 10,000 field bootstraps; 1,000 circular shifts; same-bank, wrong-frequency, different-field, RF-on/off and ring controls; development, validation and high-field holdout partitions.

**Geometry fidelity check:** **YES for the registered bank-level cut; PARTLY for physical identity.** The code held the intended bank, axis, direction and tier fixed, but an opposing bank is still another projection of the same ensemble rather than a separately anchored physical parent observable.

## 3. Relational Bridge Map

| Anchor | T422 answer |
|---|---|
| **Physical identity** | Muoniated-acetone ensemble measured by the 96-detector EMU instrument. The source ensemble and acquisition run define the identity; the two banks are disjoint detector populations viewing that same identity. |
| **Raw measurement** | Time-binned positron-count spectra from detectors 1–48 and 49–96, split by magnetic field and RF condition. Development and validation each contain 13 runs; holdout contains 20 higher-field/temperature runs. |
| **Transformation** | Detector counts are **MEASURED**. Complex lag coefficients, local-loss/null shares, centring and 0–2 normalization are **DERIVED/RECONSTRUCTED**. `U=2*local/(local+null)`, `R=2*median|C_l|`, and `H=2*median(|arg C_l|/pi)` are **RECONSTRUCTED** coordinates. The parent label assigned to `H` is a **TESTED CANDIDATE**, not a measured identity. |
| **ARA cut** | The current-bank `U=R` equality is the child singularity/crossover. The other-bank `H=1` is the candidate parent ridge. Both directions were tested on the same rung bookkeeping without declaring detector bank ownership as physical Phase A/Phase B. |
| **Established translation** | Forward/backward detector banks provide separate projections of a shared ensemble spin asymmetry. Their independence is instrumental, not source independence. |
| **Actual finding** | Validation crossings occurred with other-bank median `H=0.985` and `0.989`, and real timing beat shifts in both directions. Only F-to-B ridge exposure had a positive 95% lower bound. Development did not reproduce timing specificity, wrong-frequency and lineage controls failed, and holdout had no post-calibration crossings. |
| **Importance** | A controlled real-data test of whether T421's candidate parent survives a disjoint detector projection. It narrows the interpretation of `H`; it is not a new physical mechanism or prediction of individual decay. |
| **Missing bridge** | A parent-scale observable that is physically different from the phase history—such as detector-total population/decay amplitude—measured simultaneously at the full 96-detector `U=R` crossing. |

Explicit bridge:

```text
muoniated-acetone ensemble
  -> forward/backward time-binned detector counts
  -> bank-specific complex-lag and local/null reconstruction
  -> U,R child coordinates in one bank + H coordinate in the other
  -> child U=R crossover + candidate parent H=1 ridge
  -> separate detector projections of one ensemble spin relation
  -> validation-only cross-bank ridge/timing exposure without specificity or holdout events
  -> H remains a generic/shared candidate coordinate, not a uniquely identified physical parent
```

## 4. Pivot Log

| Step | From | To | Why | Data forced? | User confirmed? | Effect |
|---|---|---|---|---|---|---|
| Pre-run causality clarification | Score all reconstructed times | Fit the phase basis on the first 2.25 microseconds and score only later reads | Make the confirmed past-only rule true in code | No; implementation clarification before scoring | Yes | No identity, rung, axis, target or claim changed |

**No material pivot occurred after execution.** The holdout's absence of `U=R` crossings was retained as an event-availability result; it was not replaced by a different event definition.

## 5. Results without interpretation

### Development

| Direction | Eligible | Events / fields | Median crossing | Median other-bank H | Ridge exposure, 95% CI | Shift p | Wrong-frequency advantage | Different-field advantage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| F -> B | 13/26 (50.0%) | 17 / 7 | 0.834 | 0.894 | +0.043 [-0.037, +0.063] | 0.541 | -0.151 [-0.170, -0.057] | -0.066 [-0.084, -0.008] |
| B -> F | 11/26 (42.3%) | 17 / 6 | 0.831 | 1.115 | +0.058 [-0.060, +0.217] | 0.208 | -0.074 [-0.156, -0.007] | -0.042 [-0.122, +0.022] |

Development failed every primary gate. Negative control advantages mean the declared real pairing was not better than those controls.

### Validation

| Direction | Eligible | Events / fields | Median crossing | Median other-bank H | Ridge exposure, 95% CI | Shift p | Wrong-frequency advantage | Different-field advantage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| F -> B | 13/26 (50.0%) | 17 / 8 | 0.784 | 0.985 | +0.082 [+0.017, +0.283] | 0.0050 | -0.016 [-0.160, +0.015] | +0.011 [-0.178, +0.189] |
| B -> F | 14/26 (53.8%) | 17 / 9 | 0.828 | 0.989 | +0.151 [-0.040, +0.285] | 0.0090 | -0.002 [-0.152, +0.034] | +0.064 [-0.104, +0.200] |

Validation passed timing specificity and RF-sign robustness. It failed availability, bidirectional positive-CI exposure, frequency specificity and lineage specificity.

### Holdout and robustness

- The high-field/temperature holdout attempted 40 sequences in each direction and produced **zero post-calibration `U=R` crossings**. Event-conditioned ridge, timing and control gates were therefore unavailable, not numerically contradicted.
- RF-on and RF-off validation effects were positive in both directions: F-to-B `+0.050/+0.158`; B-to-F `+0.052/+0.077`.
- Ring correspondence was unavailable: only one development middle-ring sequence was eligible; validation and holdout had none.
- Independent saved-artifact validation passed **119/119** checks, including hashes, disjoint bank membership, causal time boundary, event arithmetic, bootstraps, controls and equality of the real/shift event populations.
- Portable report packaging passed schema/package validation. Visual verification is **structural-only** because no Chromium renderer was available in this runtime.

## 6. Two required verdicts

### 6.1 Claim or benchmark verdict

**NOT SUPPORTED [pre-registered].** The claim required both directions to have positive bootstrap lower bounds, beat timing/frequency/lineage controls, preserve RF direction and remain evaluable in holdout. Only validation timing and RF direction passed. The stricter frozen claim therefore fails.

### 6.2 ARA geometry verdict

**A nontrivial but non-specific cross-bank ridge geometry appeared in validation.** At child crossings, both opposing-bank medians sat very near `H=1`, and actual timing beat circular shifts. That geometry was not stable enough to identify `H` as the unique parent: development timing failed; wrong-frequency coordinates were at least as ridge-like; different-field lineage was not separated; holdout never crossed. The earlier T421 same-view child-singularity/parent-ridge geometry is not falsified by this result.

## 7. Interpretation in three layers

1. **ARA reading:** a child crossover in one bank can coincide with a ridge-like state in the disjoint bank, particularly in validation, but detector-bank separation did not isolate two independently specific parent/child identities. The cleaner current reading is that `H` may describe the combined 96-detector identity or a generic parent-scale coordinate shared by several cuts.
2. **Established-science crosswalk:** opposing detectors observe the same ensemble precession/asymmetry from different directions. A shared phase/ridge feature across banks is physically plausible without requiring a new parent entity.
3. **New or unresolved physical claim:** it remains unresolved whether `H` corresponds to a distinct physical parent observable. That requires a different measurement channel, not another subdivision of the same phase reconstruction.

**Dylan's interpretation:** pending originator review of the completed visual report. No wording has been inferred on Dylan's behalf.

## 8. Claim boundary and importance

- [x] **Empirical regularity, bounded to validation:** a timed opposing-bank ridge exposure appeared in both directions.
- [ ] Predictive result.
- [ ] Candidate physical mechanism.
- [ ] Confirmed physical claim.

**This test does show:** the T421 ridge is not necessarily confined to exact same-cut arithmetic; a disjoint detector projection can carry a closely timed ridge-like relation.

**This test does not show:** that `H` is the unique physical parent, that bank identity equals ARA phase identity, that a microscopic muon or neutrino handover was seen, or that the relation transfers to high field.

**Known physics already explains:** why forward and backward banks share information about one ensemble spin relation.

**ARA adds:** the frozen child-crossover/parent-ridge question, explicit cross-rung orientation and controls that expose where the parent identity remains unanchored.

## 9. Missing bridge and next test

- **Current information island:** a reconstructed phase-history child crossing and ridge-like `H` coordinate across disjoint detector banks.
- **Next island:** a directly measured, non-phase parent-scale observable.
- **Smallest clean cut:** use all 96 detectors for the child `U=R` event, and independently read the detector-total population/decay envelope or another amplitude channel at that event.
- **ARA expectation:** the independently frozen parent coordinate should approach its declared ridge, pole or handover at the full-identity child crossing and beat timing, frequency and lineage controls.
- **Rival:** both phase and amplitude merely share the same decay envelope or normalization.
- **Abandon/remap condition:** if independent amplitude behaves like `H` under wrong-frequency and mismatched-lineage transforms, treat the ridge as a generic reconstruction property rather than a parent identity.

## 10. Durable artifacts

- Frozen protocol: `T422_FROZEN_PROTOCOL.md`
- Analysis: `t422_independent_detector_bank_parent.py`
- Independent validator: `validate_t422.py`
- Development freeze: `T422_DEVELOPMENT_FREEZE.json`
- Result JSON and CSV: `results/`
- Canonical report artifact: `artifact.json`
- Portable HTML: `results/T422_INDEPENDENT_DETECTOR_BANK_PARENT_REPORT.html`
- Validation receipt: `results/T422_INDEPENDENT_VALIDATION.json`
- Ledger: `../../../MASTER_PREDICTION_LEDGER.md`

