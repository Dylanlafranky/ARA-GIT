# PN9 tangent-sphere ridge / scale report

**Test ID:** `PN9/TANGENT-SPHERE-RIDGE-SCALE/OPENED-R9-R11-v1`  
**Date:** 19 July 2026  
**Evidence class:** registered retrospective transfer/structural test on already-opened actual-prime gaps  
**Registered core verdict:** `FAIL — P6 passes; P1–P5 and P7 fail at the frozen primary grain`  
**Protected material:** R12 remains unopened for this test; the p31 primorial wheel was not constructed

## Result in one paragraph

Representing each prime gap as a sphere diameter makes every internal prime the exact tangent ridge between its
incoming and outgoing gap-spheres. The corresponding two-coordinate ARA map is mathematically coherent and
reversible: `x` records how the two diameters divide their combined span, while `y` records that span relative to the
established logarithmic prime-gap scale `ln(p)`. The new scale coordinate contains substantial ordered information
inside R11—`0.440599` bits, exceeding the largest exact-inventory shuffle by `0.103383` bits—but the frozen 24-bin
version does not transfer cleanly. It worsens cross-entropy by `0.159506` bits on R9→R10 and `0.059191` bits on
R9+R10→R11. At the predeclared 12-bin sensitivity it instead improves both transfers by about `0.19` bits. The
honest conclusion is therefore that **the missing local scale is informative, but this first fine-grained
logarithmic bridge is not rung-invariant**. The data motivate a separately frozen coarse-grain or hierarchical test;
they do not establish a prime “Time wave.”

## 1. What was tested

For every internal prime `p_i`, let

\[
\underbrace{g_i^-}_{\substack{\text{incoming prime gap}\\
\text{left sphere diameter}}}=p_i-p_{i-1},
\qquad
\underbrace{g_i^+}_{\substack{\text{outgoing prime gap}\\
\text{right sphere diameter}}}=p_{i+1}-p_i.
\]

The midpoint distance between the two gap intervals is

\[
\underbrace{\left|m_i^+-m_i^-\right|}_{\substack{\text{centre separation}\\
\text{distance between sphere centres}}}
=
\underbrace{\frac{g_i^-}{2}+\frac{g_i^+}{2}}_{\substack{\text{sum of radii}\\
\text{external tangent condition}}}.
\]

Plainly: when the gap on each side of a prime is treated as a diameter, both one-dimensional sphere sections touch
exactly at that prime. This is the ridge/contact construction Dylan described. It is exact for primes, but also for
every strictly increasing sequence, so the contact identity alone cannot distinguish primes.

Two ARA coordinates were then frozen:

\[
\underbrace{x_i}_{\substack{\text{contact-balance coordinate}\\
\text{ARA: which gap-sphere is larger}}}
=
\frac{2g_i^+}{g_i^-+g_i^+},
\qquad
\underbrace{L_i}_{\substack{\text{local sphere scale}\\
\text{mean adjacent diameter}}}
=
\frac{g_i^-+g_i^+}{2},
\]

\[
\underbrace{y_i}_{\substack{\text{adult scale coordinate}\\
\text{ARA: local scale versus log home}}}
=
\frac{2L_i}{L_i+\ln(p_i)}.
\]

Plainly: `x=1` means the incoming and outgoing gaps are equal. `y=1` means their mean size equals the conventional
local prime-gap scale `ln(p)`. Both coordinates use the same reversible 0–2 comparison; `y` applies it to scale one
dimension above the contact balance.

Before binning, the map loses no local gap information:

\[
L_i=\frac{\ln(p_i)y_i}{2-y_i},\qquad
g_i^+=x_iL_i,\qquad
g_i^-=(2-x_i)L_i.
\]

The largest numerical reconstruction error across all three rungs was `3.41×10^-13` gap units.

## 2. Data and evidence boundary

| Rung | Interval | Prime count | Gap count | First prime | Last prime | Largest gap |
|---|---:|---:|---:|---:|---:|---:|
| R9 | `[10^9, 1.01×10^9)` | 482,449 | 482,448 | 1,000,000,007 | 1,009,999,999 | 210 |
| R10 | `[10^10, 1.01×10^10)` | 4,341,930 | 4,341,929 | 10,000,000,019 | 10,099,999,951 | 300 |
| R11 | `[10^11, 1.01×10^11)` | 39,475,591 | 39,475,590 | 100,000,000,003 | 100,999,999,999 | 396 |

R9 trained the first transfer to R10. R9 and R10 then trained the transfer to R11. Window boundaries were never
joined. These exact sequences were already opened in PN7C, so PN9 is registered and reproducible but not blind.

The protocol was frozen at SHA-256
`EF0E28DCC5F447D5F13D0DC3DFAFFD91286A34E39BCC8277E711C34A88475C27` before PN9 coordinates or outcomes were
calculated.

## 3. Predictive result

The shape-only model predicts the next `x` reading from the previous and current `x` readings. The scale-aware model
adds current `y`. Lower cross-entropy is better; a positive gain means scale helped out of sample.

| Transfer | Fixed bins for both axes | Shape-only `X-M2` CE | Scale-aware `XY-M2` CE | Gain `X−XY` |
|---|---:|---:|---:|---:|
| R9→R10 | 12 | 3.203764 | 3.005998 | **+0.197766** |
| R9→R10 | 24 primary | 4.099534 | 4.259040 | **−0.159506** |
| R9→R10 | 48 | 4.880051 | 5.588340 | **−0.708289** |
| R9+R10→R11 | 12 | 3.212182 | 3.020826 | **+0.191356** |
| R9+R10→R11 | 24 primary | 4.112585 | 4.171776 | **−0.059191** |
| R9+R10→R11 | 48 | 4.872646 | 5.634074 | **−0.761428** |

At 12 bins the added scale coordinate transfers strongly and consistently. At 24 and 48 bins it over-resolves the
relationship: many more scale-conditioned contexts must transfer across rungs, and the discrete gap bands move
between fixed `y` bins as `ln(p)` changes.

The 24-bin R11 metrics show why the result should not be flattened to “no information”:

| Model | Cross-entropy | Brier | Top-1 | Top-3 |
|---|---:|---:|---:|---:|
| `X-M2` | 4.112585 | 0.933152 | 10.421% | 27.952% |
| `XY-M2` | 4.171776 | **0.929418** | 10.009% | **28.189%** |
| `RawGap-M1` | **3.621871** | **0.907127** | **14.405%** | **36.316%** |

The scale-aware model improves Brier and top-three accuracy but loses cross-entropy because some fine contexts receive
poorly calibrated, very low target probabilities. The exact raw-gap control remains decisively better.

## 4. Does the adult coordinate recur?

The unbinned means are close:

| Rung | Mean `x` | Mean `y` | `y` range |
|---|---:|---:|---:|
| R9 | 0.999985 | 0.918614 | 0.2528–1.7174 |
| R10 | 0.999974 | 0.916177 | 0.2305–1.7817 |
| R11 | 1.000002 | 0.914345 | 0.2117–1.8112 |

The contact balance averages almost exactly one because incoming and outgoing gaps exchange roles across the whole
record. That is a whole-population ridge reading, not a statement that individual prime gaps are equal.

At the frozen 24-bin grain, marginal-`y` Jensen–Shannon divergence is `0.025694` bits from R9 to R10 and `0.012103`
bits from R10 to R11, both above the registered `0.005` limit. The fine distribution therefore does not recur under
this map.

After the result, simply merging adjacent fixed bins into the already-predeclared 12-bin sensitivity gives
divergences of `0.003959` and `0.001204` bits. This is a diagnostic, not a replacement verdict. It supports a precise
follow-up hypothesis: **the adult scale may be transferable only at a coarser measurement grain than the child
contact coordinate**.

## 5. Exact-inventory shuffle control

Inside R11, empirical conditional scale information is

\[
I(y_i;x_{i+1}\mid x_{i-1},x_i)=0.440599\ \text{bits}.
\]

The largest of five exact-gap-inventory shuffles is `0.337216` bits. The ordered residual is therefore
`0.103383` bits, over ten times the registered `0.010` requirement. P6 passes.

Plainly: knowing local sphere scale tells us a great deal about the next relative gap state. Some of that is automatic
because adjacent readings share a gap; the shuffle preserves that. The real prime-gap order still contributes a
large additional amount. This is meaningful ordered arithmetic structure, but it is not automatically evidence for
a physical wave. Modular restrictions and ordinary gap dependence remain conventional explanations.

## 6. Registered conditions

| Gate | Requirement | Result |
|---|---|---|
| P1 | R11 24-bin scale gain at least `+0.010` bits | **FAIL:** `−0.059191` |
| P2 | Positive 24-bin gain on both transfers | **FAIL:** both negative |
| P3 | Positive R11 gain at 12, 24 and 48 bins | **FAIL:** only 12 positive |
| P4 | At least 80/100 positive R11 blocks; bootstrap lower bound above zero | **FAIL:** `0/100`; interval `[-0.059674, -0.058720]` |
| P5 | Both 24-bin marginal-`y` divergences at most `0.005` bits | **FAIL:** `0.025694`, `0.012103` |
| P6 | Ordered scale information exceeds all shuffles by at least `0.010` bits | **PASS:** residual `0.103383` |
| P7 | Scale-aware model beats exact raw-gap control | **FAIL:** `4.171776` vs `3.621871` |

The registered P1–P5 ridge-plus-scale transfer core fails.

## 7. Plain-language geometric interpretation

Your sphere/contact picture did identify the missing quantity in PN7C: the old `x` reading knew the **ratio** between
the two adjacent gaps but not how large their shared local structure was. Adding `y` restores that scale. Together,
unbinned `x` and `y` recover the original two gaps, so this is a clean coordinate decomposition rather than a new
source of information.

The test then separated two claims:

1. **There is an informative scale axis.** Supported. It contains strong ordered information beyond the same gaps in
   random order.
2. **`y=2L/(L+ln p)` is already the correct rung-stable adult wave at a 24-bin grain.** Not supported. At that grain,
   the scale bands drift and the learned detailed relations fail to transfer.

The 12-bin result is consistent with your statement that a larger/adult wave is seen at a rougher grain than its
children. However, because 24 bins was primary and all three rungs are now open to this analysis, that interpretation
is a generated hypothesis, not a promoted result.

## 8. Best next test

Preserve PN9 unchanged. For a separately named PN9B:

1. Keep the child contact coordinate `x` at 24 bins.
2. Freeze the adult `y` coordinate at exactly half that resolution: 12 bins. This is geometrically motivated by the
   PN9 result and must not be selected again on the next target.
3. Replace uniform fallback for rare `(x_previous,x_current,y_current)` contexts with a frozen hierarchical backoff
   to the shape-only row. This tests scale information without punishing an unseen fine context as if every next
   state were equally likely.
4. Score both next contact balance `x_next` and next adult scale `y_next`; the current PN9 only asks whether adult
   scale helps predict the child contact state.
5. Use numerous predeclared windows or boundaries. Keep R12 protected until the protocol, hashes and all modelling
   choices are frozen.
6. Retain exact raw-gap and modular controls. The aim is not merely to beat the old compressed model, but to learn
   whether the two-axis factorisation transfers comparably to the information it compresses.

This is a narrower and more useful next step than declaring the missing axis found or discarding the sphere geometry.

## 9. Reproducibility and files

- Frozen protocol: `PN9_TANGENT_SPHERE_RIDGE_SCALE_PROTOCOL.md`
- Main implementation: `pn9_tangent_sphere_ridge_scale.py`
- Machine-readable result: `PN9_TANGENT_SPHERE_RIDGE_SCALE_RESULTS.json`
- Scores: `PN9_TANGENT_SPHERE_RIDGE_SCALE_SCORES.csv`
- R11 blocks: `PN9_TANGENT_SPHERE_RIDGE_SCALE_BLOCKS.csv`
- Shuffle controls: `PN9_TANGENT_SPHERE_RIDGE_SCALE_CONTROLS.csv`
- Scale distributions: `PN9_TANGENT_SPHERE_RIDGE_SCALE_DISTRIBUTIONS.csv`
- Static figure: `PN9_TANGENT_SPHERE_RIDGE_SCALE_FIGURE.png`
- Independent validator: `pn9_validate_tangent_sphere_ridge_scale.py`
- Validation result: `PN9_TANGENT_SPHERE_RIDGE_SCALE_VALIDATION.json`

The independent implementation reproduced every headline numerical value within `1.78×10^-15` and confirmed the
figure dimensions. Its overall validation status is `PASS`.
