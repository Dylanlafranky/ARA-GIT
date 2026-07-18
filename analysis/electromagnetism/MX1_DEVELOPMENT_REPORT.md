# MX1 development report — Gauss ↔ ARA/TE-ARA geometry

**Tier:** DEVELOPMENT / EXPLORATORY / NOT CONFIRMATORY  
**Confirmation arrays opened:** No  
**Fidelity verdict:** EXACT ENOUGH TO TEST

## Outcome

**13 July audit calibration:** the full-source and identity-only Gauss agreements below are primarily
simulator/solver consistency checks. OSIRIS uses charge-conserving particle deposition and evolves fields subject to
Gauss consistency, so these correlations must not be presented as independent ARA evidence. The honest ARA-specific
development result is the imperfect transfer of the separately defined TE-ARA participation coordinate
\(r=0.798664\), together with the local pair-coordinate result \(r=0.7706\) and the scalar-magnitude null.

The established Gauss instrument check passes on 299 eligible time slices. The spectral derivative
of the electric field matches the independently deposited particle charge with correlation
0.997102, NRMSE 0.0767, and
through-origin slope 1.007699.

The identity family is spatial mode 5 plus its first 12 available multiples through
mode 60. Field-side Gauss weighting and particle-side measurement give source-participation
TE-ARA analogues with correlation 0.798664 and mean absolute difference 0.091058 on the 0–2 scale.
The identity-only Gauss reconstruction matches the separately read identity-only particle source with
correlation 0.999059. Against the unfiltered full particle
source, its correlation is 0.674687; the difference is the
declared Other structure rather than discarded error.

The whole periodic-domain pair coordinate remains close to its 1.0 cancellation ridge: median
1.007423; maximum observed displacement 0.126589.
That is expected because the ring contains complete peer cycles. After phase-aligning and measuring its five cells
separately, particle-side pair ARA ranges from 0.7896 to
1.4912. Field-side and particle-side local pair coordinates correlate
0.7706. Their local total unsigned source magnitudes correlate
0.999659, while their local signed net results correlate
0.995309. Total unsigned activity remains non-zero, distinguishing intense
positive/negative structure from an empty zero.

All compressed models were compared on the same 75 clean bounded-ARA late slices. The best internal
chronological development model was scale_only, with held-late source-activity correlation
0.9916 and R² 0.6768. In this development run, adding scalar ARA/TE-ARA coordinates did
not beat the dimensional scale-only bridge. That is a narrowing result: TE-ARA still describes identity participation,
but the tested scalar compression adds no held-late source-magnitude skill here. This is calibration evidence only and
cannot support the ARA claim until a frozen rule transfers to the sealed archive.

## What each coordinate contributes

- Pair ARA x_Q supplies signed positive/negative composition around the 1.0 ridge.
- Whole-ring x_Q is the coarse cancellation view; phase-aligned per-cell x_Q is the local moving view.
- Total unsigned source activity supplies magnitude.
- Field TE-ARA analogue supplies the fraction of field signal power in the declared identity family.
- Source TE-ARA analogue tests whether that identity survives the quarter-turn and k-weighting imposed by Gauss.
- Component ARAs retain positive- and negative-lobe shape. Raw values above 2 are preserved but flagged as compound
  rather than forced onto the bounded scale.
- Other remains one minus identity participation and is never discarded.
- The dimensional source scale is k0 × E_rms. The compressed models predict only the remaining dimensionless shape
  factor, because TE-ARA is a fraction and cannot create absolute magnitude by itself.

## Frozen development choices — superseded by the registered freeze

The list below was written before registration. It is retained as development history, but
`MX1_CONFIRMATION_FREEZE_v1.md` now supersedes the phrase “not yet registered” and is the controlling transfer
protocol.

- Eligibility: E_rms at least ten times the first-ten-slice noise median and fundamental fraction at least 0.25.
- Rung: fixed spatial mode 5.
- Identity family: fixed multiples [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60].
- Phase folding: 64 bins with a fixed one-pass circular 1:2:1 deposition-noise smoother.
- Development assessment: chronological 70/30 split.

The confirmation arrays remain sealed. Review these development choices before hashing and registering the transfer test.
