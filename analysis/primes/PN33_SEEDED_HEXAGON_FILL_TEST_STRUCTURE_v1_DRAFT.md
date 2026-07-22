# PN33 seeded-hexagon fill and rung doubling - test structure v1 DRAFT

**Date:** 22 July 2026  
**Status:** DRAFT ONLY - no target calculation, no ledger registration and no evidential status  
**Fidelity dependency:** `PN33_SEEDED_HEXAGON_FILL_FIDELITY_PACKET_v1_DRAFT.md`  
**Orientation:** connection constraint accumulates upward from local `0` to local `2`; raw survivor spacing is retained when the local coordinate resets.

## 1. Question

Does the prime connection web support this ordered ARA sequence?

\[
\boxed{
\text{old completion}
\rightarrow
\text{prime seed}
\rightarrow
\text{gradual connection fill}
\rightarrow
\text{spacing-capacity doubling}
\rightarrow
\text{new locally empty generation}
}
\]

This is not the PN32 claim that `N -> 2N` instantly creates a complete parent. PN33 instead asks whether a new rung accumulates between doublings.

## 2. Exact arithmetic substrate

For prime gates through `p`, let

\[
W(p)=\prod_{r\le p}r,
\qquad
S(p)=\frac{\varphi_E(W(p))}{W(p)}
=\prod_{r\le p}\left(1-\frac1r\right),
\]

where `S` is the surviving share of one completed wheel. Define raw connection spacing

\[
D(p)=\frac1{S(p)}=\prod_{r\le p}\frac{r}{r-1}.
\]

Adding one new prime gate `q` multiplies the raw spacing by exactly

\[
\frac{D(q)}{D(p)}=\frac{q}{q-1}.
\]

Plainly: each new prime makes one new independent connection rule. It removes one of every `q` previously surviving lifts, so surviving positions move slightly farther apart.

## 3. Proposed ARA fill coordinate

Let `b_j` be the last gate of a completed generation. For later gate `p`, define

\[
R_j(p)=\frac{D(p)}{D(b_j)},
\qquad
x_j(p)=2\frac{\log R_j(p)}{\log2}.
\]

Interpretation:

| Quantity | Mathematical meaning | ARA meaning |
|---|---|---|
| `D(b_j)` | retained inverse survivor density | completed old rung's raw size |
| first prime after `b_j` | first new independent gate | seed / first connection |
| `0 < x_j < 1` | less than a square-root-of-two spacing gain | early accumulation |
| `x_j = 1` | spacing has grown by `sqrt(2)` | local ridge / half log-doubling |
| `1 < x_j < 2` | remaining accumulation | late fill |
| first `x_j >= 2` | spacing has doubled | completed generation |

Because prime gates are discrete, completion may overshoot `2`. Preserve

\[
\epsilon_j=R_j(c_j)-2
\]

as a measured completion overshoot. Do not round it away or call it Phi leakage without a separate test.

## 4. The reset rule

At completion `c_j`, retain the raw baseline and reset only local progress:

\[
b_{j+1}=c_j,
\qquad
D(b_{j+1})=D(c_j),
\qquad
x_{j+1}(b_{j+1})=0.
\]

The next prime gate `s_(j+1)>b_(j+1)` is the first connection of the next generation and must read as a small positive `x`, not as a completed `2`.

This distinction is load-bearing. A plot must show both raw `D(p)` and locally reset `x_j(p)`.

## 5. Stage A - fidelity calibration, no claim verdict

Use only already opened small-prime material to make three views:

1. **raw view:** `D(p)` against prime-gate order;
2. **local ARA view:** `x_j(p)` from `0` to the first crossing of `2`;
3. **decompressed wheel view:** survivor masks before the seed, after the seed and at completion.

Also mark, without using them as the completion definition:

- the seed prime;
- the seed's child-scale square `q^2`;
- `x=1`;
- the nearest observed gate to golden Phi;
- the first `x>=2` completion;
- the exact overshoot `epsilon`.

Dylan reviews these pictures for translation fidelity. Model fit, prime prediction and p-values are forbidden in Stage A.

## 6. Stage B - freeze before target calculation

After `EXACT ENOUGH TO TEST`:

1. freeze the coordinate formula and orientation;
2. choose target starting gates by a deterministic public rule, not by attractive geometry;
3. hash the list of starts before calculating any completion gates;
4. predeclare the number of target generations and maximum computation limit;
5. generate gates and fills without inspecting prime-gap outcomes;
6. hash the complete coordinate table;
7. only then attach the gap outcomes and controls.

Recommended target selection rule:

- development: the already discussed low gate ending at `13`;
- target starts: the smallest prime gates at or above fixed decimal anchors chosen before calculation;
- at least three non-overlapping target generations if computation permits.

The final protocol must name the anchors and computational ceiling. This draft deliberately does not select them before fidelity sign-off.

## 7. Independent outcome: do primes actually space out with fill?

The coordinate uses survivor-density products. The outcome uses raw consecutive-prime gaps, kept separate.

Divide each completed generation into eight fixed ARA bands:

\[
[0,.25),[.25,.5),\ldots,[1.75,2].
\]

For every band report:

- number of prime gates;
- all raw consecutive gaps;
- mean, median, interquartile range and 10th/90th percentiles;
- first and last worked examples;
- raw `D`, local `x`, child `q^2` landmarks and completion overshoot.

Normalize each generation's gap scale by its first band's median. The parameter-free ARA transfer curve is

\[
\widehat G_{\mathrm{ARA}}(x)=2^{x/2}.
\]

It predicts a retained gap-scale multiplier of `1` near the start, `sqrt(2)` near the ridge and `2` near completion. This is a scale prediction, not an assertion that every individual prime gap doubles.

## 8. Primary endpoints

1. **Monotone fill endpoint:** Spearman association between ARA band and block-median raw prime gap is positive in every target generation.
2. **Doubling endpoint:** the final-band/first-band median-gap ratio is compatible with `2` under a block bootstrap and is materially closer to `2` than to `1`.
3. **Curve endpoint:** log-scale MAE of observed normalized band medians against `2^(x/2)`.
4. **Reset endpoint:** after completion the new local `x` returns near `0`, while the absolute gap/spacing scale remains near the completed generation's doubled baseline rather than falling back to the original baseline.
5. **Replication endpoint:** the direction and approximate curve reproduce across the frozen target generations.

Because prime gaps are dependent and heavy-tailed, use moving-block bootstrap intervals and report medians alongside means. Do not treat individual gaps as independent observations.

## 9. Required controls and rivals

### Established control - prime number theorem

At gate size `p`, the established local mean-gap scale is approximately `log p`. Report

\[
\widehat G_{\mathrm{PNT}}(p)=\frac{\log p}{\log b_j}
\]

on exactly the same bands. ARA recovery of a doubling-scale curve is a crosswalk, not new prime mathematics, if it merely reproduces this baseline.

### Structural rivals

1. **Raw gate-count fill:** progress is the fraction of gate labels processed, ignoring their unequal `q/(q-1)` effects.
2. **Raw integer doubling:** completion at `p=2b_j`; this is the flattened interpretation already separated from the claim.
3. **Fixed polygon count:** completion after `6`, then `12`, then `24` new gates. This tests a literal edge-count reading but is not the primary ARA translation.
4. **Order-broken control:** preserve each gate's `q/(q-1)` increment but permute their within-generation order before reconstructing the fill curve.
5. **Matched composite-square landmarks:** retain square-scale changes that do not introduce a new independent prime gate.

All controls must use the same target ranges and gap summaries.

## 10. Decision rules

### Geometry verdict

- **Exact crosswalk:** seed, cumulative gate effects, local reset and raw-scale retention are reconstructed exactly from wheel arithmetic.
- **Supported spacing expression:** the no-fit `2^(x/2)` curve transfers across frozen generations and is not materially worse than PNT.
- **ARA-specific residual support:** the ARA fill coordinate predicts held-out deviations beyond PNT with a predeclared positive margin and passes all controls.
- **Null:** the normalized coordinate is mathematically valid but does not organize independent gap outcomes beyond scale alone.
- **Not supported:** observed gap scale fails to rise toward the doubled endpoint or resets in the opposite way after adequate measurement.

### Scientific fence

Even a positive result would not prove that primes are literal spatial hexagons, that Phi causes primes, or that ARA generates primes more efficiently. It would show that the declared seed-fill-completion geometry is an exact and potentially useful crosswalk for how independent prime constraints accumulate across scale.

## 11. Two-output reporting requirements

The final report must keep separate:

1. **benchmark verdict:** performance against PNT and structural controls;
2. **geometry verdict:** seed, fill bands, ridge, completion, overshoot, reset and raw-scale retention.

A null benchmark may coexist with a clear exact geometry. Neither conclusion may erase the other.

## 12. Files to create only after sign-off

- `PN33_SEEDED_HEXAGON_FILL_PROTOCOL_v1_FROZEN.md`
- `PN33_PROTOCOL_FREEZE_MANIFEST.json`
- `pn33_seeded_hexagon_fill.py`
- `PN33_SEEDED_HEXAGON_FILL_COORDINATES.csv`
- `PN33_SEEDED_HEXAGON_FILL_RESULTS.json`
- `PN33_SEEDED_HEXAGON_FILL_REPORT.md`
- `validate_pn33_seeded_hexagon_fill.py`
- `PN33_SEEDED_HEXAGON_FILL_VALIDATION.json`

No result script should be run and no `MASTER_PREDICTION_LEDGER.md` status entry should be created until the fidelity packet receives Dylan's explicit verdict.

