# PN7A phase-referenced occurrence report

**Test ID:** `PN7A/PHASE-REFERENCED-OCCURRENCE/OPENED-DEVELOPMENT-v1`  
**Data:** previously opened R7-R11 decimal windows, conditioned through p29  
**Status:** `REGISTERED DEVELOPMENT TEST / 0 OF 5 CONDITIONS PASS / TESTED COUNTERWAVE REPRESENTATION NOT SUPPORTED`  
**Independent validation:** `136/136` checks passed  
**Protected target status:** p31/R12 was not opened

## TL;DR

The test successfully ARA-mapped the large connection-heavy sieve wave, but it did **not** locate a stable opposite
wave by asking where removals occur along the raw number line.

The adult Phase-A coordinate was the direct p29-conditioned survivor/release path mapped from the ARA diameter onto
the fixed circle branch. The independent second reading was the left-versus-right removal hazard inside 64 ordered
number-line bins. That occurrence reading was then aligned by the adult ARA phase rather than by gate number.

All five predeclared conditions failed. Most importantly, adult-phase alignment made cross-rung occurrence
recurrence worse: candidate mean correlation changed from `+0.3713` to `-0.1304`, and edge mean correlation changed
from `+0.2674` to `+0.1615`. Candidate and adjacent-edge occurrence also disagreed at R10 and R11 (`-0.1901` and
`-0.1996`). The cross-rung adult movement did not lock consistently to the lateral occurrence reading.

This rules out the **specific representation** tested here:

> The missing Time-side wave is not recovered as a recurring left-versus-right imbalance of raw removal occurrence
> after orienting that occurrence by the adult connection-wave phase.

It does not establish that no opposite coordinate exists. It says the raw finite-window position split is not that
coordinate, and that the particular cross-rung difference used as the orientation landmark is not itself recurrent
enough to triangulate one.

## Dylan's correction being tested

The earlier PN3B conclusion said that a second coordinate was visible inside some rungs but did not recur as one
common larger Time-like wave. Dylan's correction was about search order:

1. identify and ARA-map the adult connection-heavy appearance as Phase A;
2. follow how that adult appearance recurs or moves across rungs;
3. use that orientation to locate the opposite relation;
4. require an independent occurrence measurement at the proposed location.

PN7A implemented that order. It did not manufacture Phase B as `2-x`, `theta+pi`, a sign flip or a fitted shift.

## Direct ARA construction

For each entity and gate cell, direct surviving share was

\[
\underbrace{S_r(g)}_{\substack{\text{adult connection state}\\
\text{still surviving at gate }g}}
=
\frac{\underbrace{N_{r,g}^{\mathrm{alive}}}_{\text{surviving records}}}
{\underbrace{N_{r,0}}_{\text{p29-conditioned records}}}.
\]

The ARA diameter and circle coordinate were

\[
\underbrace{x_r(g)}_{\substack{\text{ARA diameter reading}\\0\text{ retained},\ 2\text{ released}}}
=2\left(1-S_r(g)\right),
\qquad
\underbrace{\theta_r(g)}_{\substack{\text{adult Phase-A position}\\
\text{on the fixed upper arc}}}
=\arccos\!\left(2S_r(g)-1\right).
\]

Plainly: the survivor/release balance supplies the point on the 0-2 diameter. The circle decompression supplies the
orientation along the adult wave without fitting it to the occurrence data.

The vertical cross-rung movement was

\[
\underbrace{V_r(g)}_{\substack{\text{change in adult appearance}\\
\text{from the previous rung}}}
=
\underbrace{\theta_r(g)}_{\text{current rung phase}}
-
\underbrace{\theta_{r-1}(g)}_{\text{previous rung phase}}.
\]

The independent lateral occurrence reading split the raw ordered window in half. At each gate, removal hazards on
the left and right were

\[
\underbrace{h_L}_{\text{left-half removal hazard}}=\frac{D_L}{N_L},
\qquad
\underbrace{h_R}_{\text{right-half removal hazard}}=\frac{D_R}{N_R},
\]

and their native ARA-centered lean was

\[
\underbrace{a_O}_{\substack{\text{occurrence asymmetry}\\-1\text{ left},\ +1\text{ right}}}
=
\frac{h_R-h_L}{h_R+h_L}.
\]

Plainly: this asks whether release is leaning toward one end of the measured number-line interval, after correcting
for how many records were still available to be released on each side. The same operation was recursively repeated
inside quarters and eighths to check whether the adult/root split dominated its children.

## Data integrity

The direct reconstruction enumerated the already opened intervals without Fourier, SVD, NMF, Buchstab, PNT,
Hardy-Littlewood or another fitted coordinate.

| Rung | Interval | p29-conditioned candidates | Terminal candidates | Adjacent edges | Terminal edges |
|---:|---:|---:|---:|---:|---:|
| R7 | `[10,000,000, 10,100,000)` | 15,801 | 6,241 | 15,800 | 2,381 |
| R8 | `[100,000,000, 101,000,000)` | 157,949 | 54,208 | 157,948 | 18,507 |
| R9 | `[1,000,000,000, 1,010,000,000)` | 1,579,467 | 482,449 | 1,579,466 | 146,147 |
| R10 | `[10,000,000,000, 10,100,000,000)` | 15,794,726 | 4,341,930 | 15,794,725 | 1,185,734 |
| R11 | `[100,000,000,000, 101,000,000,000)` | 157,947,219 | 39,475,591 | 157,947,218 | 9,792,119 |

Every stage-by-position matrix closes exactly to its initial exposure and terminal state. The earlier PN3A, PN5 and
PN6 totals were reproduced. An independently written scalar-loop implementation reproduced the vector analysis and
passed `136/136` checks.

## Registered numerical result

### Lateral recurrence

| Identity | Coordinate | R9-R10 | R10-R11 | R9-R11 | Mean |
|---|---|---:|---:|---:|---:|
| Candidate | Raw gate order | +0.2941 | +0.6691 | +0.1506 | +0.3713 |
| Candidate | Adult-phase aligned | -0.3324 | +0.1325 | -0.1915 | **-0.1304** |
| Edge | Raw gate order | +0.2947 | +0.1731 | +0.3343 | +0.2674 |
| Edge | Adult-phase aligned | -0.0699 | +0.1926 | +0.3617 | **+0.1615** |

The alignment gain is `-0.5017` for candidates and `-0.1059` for edges. If the adult Phase-A coordinate oriented a
shared counterwave in this observable, recurrence should have increased. It decreased for both identities.

### Independent-route agreement

| Check | R9 | R10 | R11 |
|---|---:|---:|---:|
| Candidate occurrence vs edge occurrence | +0.2083 | **-0.1901** | **-0.1996** |

The candidate and adjacent-edge identities do not expose the same phase-aligned lateral shape. This is especially
important because their adult survival curves are strongly related; the proposed second reading should not reverse
unpredictably simply because the identity changed from one candidate to one adjacent pair.

### Vertical-lateral triangulation

| Identity/rung | Correlation between adult cross-rung movement and lateral occurrence |
|---|---:|
| Candidate R10 | -0.0303 |
| Candidate R11 | -0.2748 |
| Edge R10 | +0.1271 |
| Edge R11 | +0.4083 |

The signs are inconsistent and only two magnitudes exceed `0.25`. The adult movement itself is not strongly
recurrent between R10 and R11: `+0.2892` for candidates and `-0.3880` for edges.

### Scale-depth result

The root occurrence split does not consistently dominate its quarter/eighth children. At R10, both identities have
more mean-square asymmetry at finer splits. At R11, candidate depth 0 exceeds depth 1 but not depth 2; edge depth 0
exceeds depth 1 but not depth 2. The proposed larger occurrence wave therefore does not emerge as the dominant
scale in this representation.

## Registered decision

| Condition | Result |
|---|---:|
| Mean phase-aligned recurrence above 0.50 for candidate and edge | **FAIL** |
| Phase alignment improves recurrence for both identities | **FAIL** |
| Candidate-edge phase agreement above 0.50 at R10 and R11 | **FAIL** |
| Vertical-lateral relation has one sign and magnitude above 0.25 in all four cases | **FAIL** |
| Root occurrence scale dominates quarter/eighth children at R10 and R11 | **FAIL** |

**Total: 0/5.** Under the registered protocol, the tested counterwave representation is not supported.

## What the result means in plain terms

We found the large Space/connection-side wave cleanly: more later-prime gates progressively remove more candidate
connections, and the whole path continues around the ARA arc from rung to rung.

We then asked whether the missing opposite side could be seen in *where* those removals happen along each raw
number-line window. If so, using the adult wave as the clock/orientation should have made that left-right pattern line
up across scales. It did the opposite. The apparent left-right lean is tiny, becomes increasingly balanced as the
windows grow, and its remaining shape does not repeat consistently between candidates and adjacent pairs.

So the adult wave is not the failure. The failure is the proposed **occurrence lens** and, more specifically, its
simple fixed-window left/right axis. This axis appears to be measuring finite-window fluctuation rather than a large,
slow opposite wave.

## Methodology audit

This is a clean native ARA development test:

- it uses direct sieve records and preserves their order;
- the adult ARA coordinate is fixed before looking at occurrence;
- occurrence is independently counted rather than algebraically inferred from survival;
- no fitted rotation, lag, sign, smoothing or spectral component enters the registered result;
- both candidate and edge identities must agree;
- child scales are retained instead of flattened;
- no fresh target was opened.

The main limitation is conceptual rather than computational. A left/right split of a finite interval is not a
translation-invariant flow coordinate. Prime structure has no reason to privilege the first half of a decimal window
over the second half. The result therefore weighs against this representation much more strongly than it weighs
against ARA's general two-pole or fractal claims.

A post-endpoint lag scan found isolated moderate correlations, but the selected lags and signs disagree between
candidate/edge and R10/R11. Those values are exploratory only and cannot rescue the result.

## Recommended next native direction

Do not retune this left/right coordinate and do not spend p31/R12 on it.

If the missing pole is information/traversal-heavy, the next direct observable should describe **movement between
events**, not absolute position inside an arbitrary decimal window. A possible PN7B development design is the ordered
waiting distance between successive releases or surviving connections, measured forward and backward at each fixed
adult ARA phase. That is still raw, signed and recursively decomposable, but it is translation-invariant. It must be
written and frozen as a new opened-data development protocol before inspection, then must recur in candidate and
edge identities before any fresh target is considered.

## Reproducibility artifacts

- Design note: `PN7_PHASE_REFERENCED_COUNTERWAVE_DESIGN_NOTE_2026-07-19.md`
- Protocol: `PN7A_PHASE_REFERENCED_OCCURRENCE_PROTOCOL.md`
- Aggregate builder: `pn7a_build_phase_occurrence_aggregates.py`
- Direct aggregates: `PN7A_PHASE_REFERENCED_OCCURRENCE_AGGREGATES.npz`
- Aggregate metadata: `PN7A_PHASE_REFERENCED_OCCURRENCE_AGGREGATES.json`
- Analysis: `pn7a_analyze_phase_referenced_occurrence.py`
- Machine-readable result: `PN7A_PHASE_REFERENCED_OCCURRENCE_RESULTS.json`
- Curve table: `PN7A_PHASE_REFERENCED_OCCURRENCE_CURVES.csv`
- Figure: `PN7A_PHASE_REFERENCED_OCCURRENCE_FIGURE.png`
- Independent validator: `pn7a_validate_phase_referenced_occurrence.py`
- Independent validation: `PN7A_PHASE_REFERENCED_OCCURRENCE_VALIDATION.json`
- Executed notebook: `PN7A_PHASE_REFERENCED_OCCURRENCE.ipynb`

