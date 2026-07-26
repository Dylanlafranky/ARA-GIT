# Q3 Ridge-Normal Quantum-Output Cut Calibration

**Date:** 24 July 2026  
**Source:** [Arnold and Werner public superconducting-qubit I/Q archive](https://doi.org/10.5281/zenodo.14033026)  
**Evidence class:** post-hoc calibration on the already-open Q2 source  
**Verdict:** `CALIBRATED — 7/7 GATES`  
**Independent validation:** `18/18` checks passed

## Answer first

The corrected ARA cut instruction behaved cleanly on the known Q2 measurement plane.

Using five hardware conditions only, the ground-to-excited direction was estimated in a covariance-whitened I/Q
plane. The Phase-A cut was drawn perpendicular to the equal-class ridge; the Phase-B control was drawn along that
ridge. On the sixth, completely held-out condition:

- the Phase-A cut reproduced the full raw-I/Q linear discriminant exactly, with `0` different decisions;
- it retained `88.2808%` condition-weighted balanced accuracy;
- the perpendicular Phase-B control scored `49.6607%`, essentially chance;
- `99.1162%` of held-out centroid-separation magnitude lay on the Phase-A direction on average;
- even the least aligned condition retained `96.3241%` on that direction;
- reversing both poles changed `0` decisions.

This is a successful instrument calibration, not new quantum evidence. The Phase-A/Fisher-LDA equality is
established linear-discriminant geometry, and this source was already opened before the calibration was frozen.
The useful empirical result is narrower: the training-defined orientation remained stable across all six
held-out hardware conditions.

## The cut rule in ARA and standard mathematics

| ARA instruction | Standard measurement geometry |
|---|---|
| whiten the local two-cut section | remove within-class scale and covariance |
| find the equal-readout ridge | locate the shared-covariance decision boundary |
| Information-facing Phase A crosses the ridge | Fisher/LDA discriminant normal |
| Phase B follows the ridge | orthogonal tangent/control direction |
| walk the cut around the section | rotate the one-dimensional projection angle |

Let \(\Sigma\) be the training pooled covariance and let \(\mu_g,\mu_e\) be the two training centroids. In the
whitened plane,

\[
\hat n_A
=
\frac{(\mu_e-\mu_g)\Sigma^{-1/2}}
{\|(\mu_e-\mu_g)\Sigma^{-1/2}\|},
\qquad
\hat n_B=(-n_{A,y},n_{A,x}).
\]

For any held-out point \(\mathbf x\), the Phase-A reading is

\[
s_A=(\mathbf x-\mathbf m)\Sigma^{-1/2}\cdot\hat n_A,
\qquad
\mathbf m=\frac{\mu_g+\mu_e}{2}.
\]

This score is proportional to the ordinary raw-I/Q LDA score. Their exact decision equality is therefore a
translation check, not an ARA performance advantage.

## Held-out condition results

| Held-out condition | Phase-A BA | Phase-B control BA | Separation on Phase A | Target angle from Phase A | Best sweep angle |
|---:|---:|---:|---:|---:|---:|
| 0 Hz | 0.941400 | 0.390970 | 0.963241 | -11.05° | 0° |
| 10 Hz | 0.946880 | 0.505180 | 0.999817 | +0.78° | 1° |
| 50 Hz | 0.935670 | 0.512710 | 0.999297 | +1.52° | 0° |
| 250 Hz | 0.885020 | 0.517730 | 0.998364 | +2.32° | 0° |
| 500 Hz | 0.829540 | 0.529150 | 0.994066 | +4.42° | 2° |
| 1000 Hz | 0.758340 | 0.523900 | 0.992190 | +5.07° | 0° |

The `0 Hz` fold is the largest domain shift. Its tangent control falls slightly below chance and its target
centroid direction is displaced by about `11°`, but the frozen Phase-A orientation still gives the best
one-degree sweep result. In the other five folds, the empirically best cut is within `0–2°` of the
training-defined Phase-A direction.

## What this adds after Q2

Q2 correctly found that adding native Q to native I did not improve classification because the useful direction
was already almost aligned with I. Q3 asks a different question: whether the newly clarified ARA cut-selection
rule can recover the useful direction and distinguish it from the perpendicular non-informative direction.

It can. The result explains Q2 geometrically without reversing Q2's negative verdict:

- Q2: the second native cut did not add useful class information;
- Q3: after orienting the plane around the actual ridge, one normal cut contains essentially all linear class
  direction and its tangent contains essentially none.

## Validation and limitations

Independent checks recomputed all aggregate values, separation shares, angles, sweep maxima and seven calibration
gates from the saved fold and sweep tables. The protocol hash and public archive checksum also matched.

Required limits:

- I/Q are hardware-output quadratures, not qubit Bloch X/Y/Z axes.
- “Information-facing” names the direction relevant to this readout question; it is not proof of a universal
  physical Information axis.
- Whitening, Fisher direction and tangent orthogonality are standard statistics.
- The source and Q2 result were already known, so the thresholds are calibration thresholds, not a blind
  confirmatory prediction.
- The next evidential step must freeze the same orientation rule before opening a fresh real quantum target with
  genuinely independent measurement directions or changing readout orientation.

## Reproduction

Run:

```powershell
python q3_ridge_normal_cut_test.py
python q3_ridge_normal_cut_validate.py
```

Primary artifacts:

- `Q3_RIDGE_NORMAL_CUT_FIDELITY_v1.md`;
- `Q3_RIDGE_NORMAL_CUT_PROTOCOL_v1_FROZEN.md`;
- `Q3_RIDGE_NORMAL_CUT_FOLDS.csv`;
- `Q3_RIDGE_NORMAL_CUT_SWEEP.csv`;
- `Q3_RIDGE_NORMAL_CUT_RESULTS.json`;
- `Q3_RIDGE_NORMAL_CUT_VALIDATION.json`.

