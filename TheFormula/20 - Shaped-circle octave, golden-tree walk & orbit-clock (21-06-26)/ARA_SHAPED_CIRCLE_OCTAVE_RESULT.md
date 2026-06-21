# Octave ARA-shaped circles — shape helps (ENSO), size-weight hurts (14 Jun 2026)

**Dylan La Franchi & Claude.** Tested Dylan's reframe of the nested-circle predictor onto the CORRECTED
foundation: **octave spacing (×2), not φ-power** (V4's circles used φ^k periods — superseded), with each rung a
circle whose ARA both **sizes** (diameter = ARA) and **shapes** (asymmetric rise/fall loop) it — option (c).
Strict-causal, correlation-led. Scripts: `ara_circle_predictor.py` (solar), `ara_circle_enso.py` (ENSO).

Variants per octave rung k (period 2^k), measured causally from past only (amp A_k, phase θ_k, rise-fraction
f_rise_k → ARA_k=(1−f_rise)/f_rise; shaped loop S = skewed cosine, round at ARA 1.0):
- **cosine** = Σ A_k·cos(φ)  — plain Fourier on the same rungs (control).
- **shapeonly** = Σ A_k·S(φ;f_rise) — amplitude × ARA-SHAPE, no ARA size-weight.
- **varB** = Σ A_k·ARA_k·S — shape × ARA size-weight (full option c).
- **varA** = Σ ARA_k·S — diameter = ARA ONLY (the literal reading).

## SOLAR (symmetric — shaping has nothing to grip), corr:
| h(mo) | persist | cosine | varA | varB |
|---|---|---|---|---|
| 12 | 0.657 | 0.537 | −0.011 | 0.487 |
| 24 | 0.266 | 0.320 | −0.276 | 0.368 |
| 60 | −0.642 | 0.598 | −0.000 | 0.533 |
| 132 | 0.674 | 0.718 | −0.060 | 0.601 |
varA dud; varB ≤ cosine. Solar is roundish → asymmetry can't help.

## ENSO NINO3.4 (asymmetric/noisy — where shaping should pay), corr:
| h(mo) | persist | cosine | **shapeonly** | varB | varA |
|---|---|---|---|---|---|
| 3 | 0.664 | 0.390 | **0.402** | 0.282 | 0.220 |
| 6 | 0.300 | 0.146 | **0.220** | 0.139 | 0.054 |
| 12 | −0.066 | 0.083 | **0.184** | 0.040 | 0.151 |
| 18 | −0.216 | 0.093 | **0.177** | −0.031 | −0.076 |
| 24 | −0.316 | 0.145 | 0.133 | 0.034 | 0.052 |

## Verdict — (c) splits into a winner and a loser
- **The ARA SHAPE helps (real lift over Fourier on the asymmetric system).** `shapeonly` beats plain cosine at
  h=6/12/18 (+0.07/+0.10/+0.08), and beats persistence at the mid-long horizons (persistence goes anti-phase).
  "Asymmetric circle beats the perfect circle" — CONFIRMED where asymmetry exists.
- **The ARA SIZE-weighting HURTS** (varB < shapeonly everywhere; varA dud). The amplitude is the diameter; ARA
  is only the *shape*. The literal "diameter = ARA" is killed by the data (varA ≈ 0).
- **So the kept mechanic: octave rungs + amplitude × ARA-shaped loop** (shapeonly). Drop the ARA size-weight.
- Honest fences: lift is MODEST (~+0.08–0.10 corr over Fourier at h=6–18); correlation-only; solar+ENSO only;
  h=3 persistence still wins. A real, leak-free edge from the shape — not a value-ceiling breaker.

Next candidates: confirm shapeonly>cosine on more asymmetric systems (ECG PQRST, QBO); compare to home_ar/AR
properly; tune the skew. Aligns with the value-ceiling (the win is small, on shape) but the SHAPE lever is real.

---

## Frozen / blind-generative ("just the geometry, run forward") — 14 Jun
Stricter test (Dylan): calibrate each octave rung's amp + ARA-shape + phase ONCE on the first 63%, **freeze**,
then roll the spin forward over the WHOLE remainder with **no further data reads** (generative). Script
`frozen_geometry.py`. Amplitude × ARA-shaped loop (the kept mechanic).

| system | held-out | frozen-shape corr | frozen-cosine | near third | far third |
|---|---|---|---|---|---|
| SOLAR | 1232 mo (~100 yr) | **+0.313** | +0.270 | +0.365 | **+0.493** |
| ENSO | 693 mo | **−0.064** | −0.015 | −0.213 | −0.247 |

- **Solar: the geometry runs on its own for a century.** Frozen at 1923, the ARA-shaped circles track the
  11-yr cycle blind for 100 yr — corr +0.31 overall, *rising* to +0.49 in the far third (a regular engine stays
  in phase under freezing), and the shape beats plain cosine. A clean standalone "the geometry predicts" result.
- **ENSO: frozen geometry FAILS** (−0.06, negative far out). No stable period to freeze → phase drifts. The
  earlier ENSO shape-edge came from the ROLLING RE-READ keeping up, not from the frozen geometry.
- **Takeaway:** the ARA-shaped circle works, but blind-generative power depends on the system having a real
  clock to freeze. Regular engines (solar) → frozen geometry holds a century. Irregular (ENSO) → needs the
  continuous re-read; can't fly blind. (Value-ceiling vs strong baselines still applies; this is the
  standalone-geometry result.) Visualised: solar tracks, ENSO drifts.
