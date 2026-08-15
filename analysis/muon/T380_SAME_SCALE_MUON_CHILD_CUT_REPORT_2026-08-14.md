# T380 — same-scale muon child cut

**Date:** 14 August 2026  
**Frozen verdict:** **NOT SUPPORTED AS AN INDIVIDUAL HANDOVER CLOCK**

## Answer first

T380 made the requested cut at the children's own scale rather than comparing
the detector's upper and lower halves as one parent. The two children were

\[
x_U=\frac{2q_2}{q_1+q_2},
\qquad
x_L=\frac{2q_4}{q_3+q_4}.
\]

The child plane is real and orderly: both cuts concentrate close to their
`1.0` ridges, and their median same-scale coupling is `0.9527`. It is also
substantially less redundant with the old parent cut than T379's coarse
upper/lower coordinate was.

However, this same-scale child relation did **not** reliably predict when one
incoming muon's later visible daughter appeared. Its pooled score was slightly
better than the parent model, but the sign reversed across the two untouched
days, the uncertainty interval crossed zero, a wrong pairing scored slightly
better, and the observed increment did not clear the permutation control.

The clean interpretation is:

- the deeper cut exposes the two child states;
- those child states form a coherent relation around the ridge;
- their prompt-amplitude relation is not a reproducible individual decay
  countdown in this detector.

## What changed from T379

The detector, material, source, event linking, calibration/holdout dates and
later daughter outcome stayed fixed. Only the geometric cut changed.

T379 used the parent-scale relation

\[
x_P=\frac{2(q_3+q_4)}{q_1+q_2+q_3+q_4}.
\]

T380 retained `xP` as a control and decompressed each adjacent pair separately.
For the child relation,

\[
C=\frac{(x_U-1)+(x_L-1)}2,
\qquad
D=\frac{(x_U-1)-(x_L-1)}2,
\]

\[
K=1-|D|,
\qquad
I=(x_U-1)(x_L-1).
\]

`C` is their shared direction, `D` their mismatch, `K` their same-scale
coupling and `I` distinguishes aligned from opposed movement.

## Cohort and split

Only incoming events with a positive gain-normalised prompt measurement in all
four counters can expose both child pairs.

| split | eligible event-linked pairs |
|---|---:|
| calibration, February 11–12 | 682 |
| untouched holdout, March 17–18 | 572 |

The visible outcome remains the delay to the later charged-electron candidate,
restricted to `0.3–10 microseconds`. The neutrinos are co-created in the decay
but are not directly measured.

## Child geometry on untouched data

| coordinate | median | 5th–95th percentile |
|---|---:|---:|
| upper child `xU` | 0.9677 | 0.7342–1.1886 |
| lower child `xL` | 0.9534 | 0.5732–1.1582 |
| shared child direction `C` | -0.0492 | -0.2707–0.1501 |
| mismatch `D` | 0.00585 | -0.1081–0.2267 |
| coupling `K` | 0.9527 | 0.7513–0.9952 |
| parent `xP` | 1.0302 | 0.8531–1.1502 |

Quadrant occupancy was not uniform:

| child side | events | share | median daughter delay, us |
|---|---:|---:|---:|
| both below ridge | 269 | 47.0% | 2.501 |
| upper below, lower above | 94 | 16.4% | 2.133 |
| upper above, lower below | 109 | 19.1% | 2.438 |
| both above ridge | 100 | 17.5% | 1.908 |

These delay summaries are descriptive. They are not sufficient evidence by
themselves because pulse strength and ordinary stack depth also vary across the
plane.

The shared child direction and parent coordinate were only weakly related
(`Spearman rho=0.1587`). Thus the deeper cut is not merely another copy of the
parent cut. But the child coordinates had weak raw relations with daughter
delay:

- `rho(xU, delay)=-0.0535`;
- `rho(xL, delay)=-0.0609`;
- `rho(C, delay)=-0.0756`;
- `rho(K, delay)=-0.0564`.

Total prompt strength was much more strongly related to the delay
(`rho=-0.3760`), which is why prospective controls are decisive.

## Frozen prospective scores

Lower mean held-out negative log likelihood is better.

| model | held-out mean NLL |
|---|---:|
| `M0`, memoryless | 1.9793517 |
| `MG`, ordinary strength + depth | 1.9153274 |
| `MP`, ordinary + parent ARA | 1.9116356 |
| `MC`, parent + same-scale children | 1.9108504 |
| wrong pairing `(1,3)/(2,4)` | 1.9119321 |
| wrong pairing `(1,4)/(2,3)` | **1.9107854** |

The registered increment was

\[
\Delta_{child}=\operatorname{NLL}(MP)-\operatorname{NLL}(MC)
=+0.0007852.
\]

Its chronological-block 95% interval was

\[
[-0.0071691,\;0.0085103].
\]

The interval is far wider than the point estimate and contains zero.

## Why the support gates failed

All four frozen gates failed.

1. **Both runs positive:** failed. March 17 was `-0.0023148`; March 18 was
   `+0.0036555`.
2. **Bootstrap interval wholly above zero:** failed. The lower bound was
   `-0.0071691`.
3. **Correct adjacency beats both wrong pairings:** failed. The `(1,4)/(2,3)`
   wrong pairing was better by `0.0000650` NLL per event.
4. **Observed increment exceeds the 97.5% permutation boundary:** failed. The
   observed `+0.0007852` was below the frozen permutation boundary
   `+0.0052541`.

The child model therefore has a small positive pooled point estimate, but no
stable evidence that the physical adjacent-child identity is what supplied it.

## Framework interpretation

This result makes an important distinction rather than returning to the old
parent measurement.

The same-scale cut successfully shows two child coordinates with a strong
near-ridge coupling. That is the geometry the requested cut was meant to
expose. The failure occurs at the stronger predictive step: the prompt child
relation does not reproducibly say which otherwise similar individual event
will hand over earlier.

So the current evidence supports this narrower statement:

> A same-scale detector cut can expose coherent child asymmetry while the
> parent remains near its ridge, but these four prompt amplitudes do not contain
> a stable individual muon-decay clock.

If an individual child clock exists, this detector is probably missing the
state variable that carries it. Continuing to re-pair or subdivide the same
four amplitudes would be post-hoc geometry mining. A genuinely new cut needs a
new event-linked measurement: spin/polarisation, local field, stopping
material, or charged-daughter energy/direction.

## Reproduction and QA

- frozen protocol: `T380_SAME_SCALE_MUON_CHILD_CUT_PROTOCOL_2026-08-14.md`
- protocol SHA-256: `de8ac09efd8c2dc884bc469871a5e29920e010982f79dfca20acf4cccfdc4b06`
- executable: `t380_same_scale_muon_child_cut.py`
- derived event table: `T380_same_scale_muon_child/T380_SAME_SCALE_MUON_CHILD_EVENTS.csv`
- numerical results: `T380_same_scale_muon_child/T380_SAME_SCALE_MUON_CHILD_CUT_RESULTS.json`
- saveable report: `T380_same_scale_muon_child/T380_SAME_SCALE_MUON_CHILD_CUT.html`
- static QA figure: `T380_same_scale_muon_child/T380_SAME_SCALE_MUON_CHILD_CUT_FIGURE.png`
- validation: all eight saved-output checks passed.
- portable report validation and packaging passed. Browser-level report QA was
  unavailable because no compatible Chromium headless executable was
  installed; structural verification passed and semantic chart/table
  fallbacks are embedded in the self-contained HTML.

