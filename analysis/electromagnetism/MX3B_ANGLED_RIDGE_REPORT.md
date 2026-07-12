# MX3b angled-ridge and phase-sensitive development result

**Tier:** DEVELOPMENT / ALREADY INSPECTED / NOT CONFIRMATORY  
**Fixed test angle:** 25 degrees from the ridge; heuristic, not universal  
**Eligible slices:** 299

## Question

Does the earlier matched-amplitude null occur because the scalar closure index measures only absolute distance from
the ridge \(G=F\), discarding motion along the ridge, crossing direction and field-particle phase?

## Coordinates

With \(g=G-1\) and \(f=F-1\):

\[
q=(g+f)/\sqrt{2},\qquad d=(g-f)/\sqrt{2},\qquad
Z_{\theta}=q\cos\theta+d\sin\theta.
\]

Here \(q\) is position along the ridge, \(d\) is signed distance across it, and \(Z_{25^\circ}\) is the fixed
oblique probe named before the run. Relative phase is measured independently at the frozen identity mode \(k_0=5\).

## Matched-amplitude result

The primary comparison uses 36 one-to-one pre/post pairs matched within 1% field RMS, so no rising
slice is counted repeatedly:

| Coordinate | Mean post-minus-pre | Paired Cohen dz |
|---|---:|---:|
| closure distance | -0.001374 | -0.4627 |
| ridge-parallel q | 0.018174 | 0.1142 |
| ridge-normal d | 0.001943 | 0.4627 |
| predeclared 25-degree projection | 0.017293 | 0.1190 |
| approximate trapped fraction | 0.026457 | 0.8796 |

Relative field-particle phase changes by a circular mean of
-0.0002 radians across those pairs, with resultant
length 1.0000.

The earlier nearest-neighbour method produced 80 pairs but reused all rising information through only
35 unique rising slices. Its apparent 25-degree effect
\(d_z=-0.3451\) shrinks to
\(d_z=0.1190\) under one-to-one matching. The trapped-fraction
separation remains much larger \(\left(d_z=0.8796\right)\).

## Held-late trapping comparison

All models include field RMS and fundamental-mode fraction. Added coordinates are fitted on the first 70% of eligible
slices and scored on the final 30%.

| Added coordinate | Held-late R-squared | Change from baseline |
|---|---:|---:|
| none | 0.7071 | 0.0000 |
| absolute closure distance | 0.8461 | +0.1391 |
| ridge-parallel q | 0.9581 | +0.2511 |
| ridge-normal d | 0.8461 | +0.1391 |
| predeclared 25-degree projection | 0.9475 | +0.2404 |
| phase alignment + quadrature | 0.8614 | +0.1543 |
| 25-degree projection + phase | 0.9144 | +0.2074 |
| q + d + phase | 0.9091 | +0.2021 |

## Exploratory angle sweep

The angle was selected only on an internal chronological validation block, then refitted without changing the angle
and scored held-late. Selected angle: 90 degrees. Internal validation R-squared:
-4.0606. Held-late R-squared: 0.8461.

No angle achieved positive R-squared on the internal validation block. The named 25-degree angle scored
-6.3285 internally despite scoring 0.9475 held-late. The angle
relation is therefore regime-dependent in this trajectory, not yet a stable transferred law. The held-late gain is
primarily carried by the ridge-parallel coordinate: \(q\) scores 0.9581, slightly
above the 25-degree projection.

## Rolling split stability

| Training fraction | Baseline | q along ridge | d across ridge | 25 degrees |
|---:|---:|---:|---:|---:|
| 0.5 | -15.6840 | -8.4931 | -6.3890 | -9.9548 |
| 0.6 | -8.9965 | -0.1444 | 0.6459 | -0.6091 |
| 0.7 | 0.7071 | 0.9581 | 0.8461 | 0.9475 |
| 0.8 | -0.1038 | 0.9277 | 0.4628 | 0.9395 |

The oblique/along-ridge view becomes useful only after enough of the nonlinear trajectory is included in training.
This supports a state-dependent geometric reading but prevents a universal-angle claim from this run.

## Verdict

The ridge-only scalar was incomplete: retaining position along the ridge materially improves late-state description.
The predeclared 25-degree view is useful on the final block, but it is not uniquely favoured; the pure along-ridge
coordinate performs slightly better, the internal validation block rejects every angle, and one-to-one amplitude
matching leaves only a small 25-degree separation. Direct field-particle phase is almost fixed and adds no gain.

**Status:** `RIDGE-TANGENT INFORMATION POSITIVE / 25-DEGREE LATE-BLOCK POSITIVE / ANGLE-SPECIFIC AND TRANSFER CLAIMS NOT SUPPORTED`.

## Post-test clarification

The 25-degree value was a general geometric estimate, not a claim that identity has one fixed privileged angle. The
intended ARA hypothesis is that the viewing direction is itself a wave supplied by the next coupled rung down, much
as blood pressure supplied directional state missing from the aggregate heart series. MX3b therefore tested only a
fixed-angle proxy. The next test must obtain a changing angle from an independently declared daughter observable,
not optimise the angle against the trapping target.

The 25-degree result is the named geometric test. The sweep is diagnostic only and cannot retroactively replace it.
The whole archive was already inspected, so even the held-late block is development evidence.
