# PN9 tangent-sphere ridge / scale protocol

**Test ID:** `PN9/TANGENT-SPHERE-RIDGE-SCALE/OPENED-R9-R11-v1`  
**Declared:** 19 July 2026, before calculating any PN9 coordinate, model or outcome  
**Evidence class:** registered retrospective transfer/structural test on already-opened actual-prime gaps  
**Protected material:** do not construct the p31 primorial wheel and do not open R12

## 1. Question

PN7B measured the relative sizes of the gap entering and leaving each actual prime. PN7C showed that the resulting
0–2 state contains transferable sequential structure, but its compressed predictor remained worse than an exact
raw-gap Markov control. The geometric diagnosis made after PN7C is that the relative ARA reading retained the contact
balance while discarding the absolute diameter or sphere scale.

PN9 therefore asks:

> If each consecutive-prime gap is represented as a one-dimensional sphere diameter and the shared prime is the exact
> contact ridge between adjacent spheres, does a second native ARA coordinate for local sphere scale recur across
> logarithmic rungs and improve transfer prediction beyond the relative ridge coordinate alone?

This remains a test of known actual-prime gaps. It is not a blind prediction of an unknown prime location.

## 2. Frozen data separation

- Development/first transfer: train R9 `[1,000,000,000, 1,010,000,000)` and evaluate R10
  `[10,000,000,000, 10,100,000,000)`.
- Final transfer: train the union of R9 and R10 while excluding their boundary, then evaluate R11
  `[100,000,000,000, 101,000,000,000)`.
- Use the existing PN7C exact gap packets without modification.
- Never join windows when constructing states or transitions.

R9, R10 and R11 have all been opened in previous work. Registration prevents post-result redefinition of this test,
but it does not restore blindness.

## 3. Tangent-sphere construction

At an internal prime `p_i`, define the incoming and outgoing gaps

\[
g_i^- = p_i-p_{i-1},\qquad g_i^+=p_{i+1}-p_i.
\]

Treat each gap interval as a one-dimensional section of a sphere whose diameter is that gap. Its midpoint is the
section centre and its radius is half the gap. Adjacent sections are exactly externally tangent at `p_i` because

\[
\left|\frac{p_i+p_{i+1}}2-\frac{p_{i-1}+p_i}2\right|
=\frac{g_i^-+g_i^+}{2}
=\frac{g_i^-}{2}+\frac{g_i^+}{2}.
\]

This identity is true for every strictly increasing sequence. It validates the representation, but is not by itself
prime-specific evidence.

## 4. Two frozen native ARA coordinates

### 4.1 Contact/ridge balance

Retain the PN7B coordinate

\[
x_i=\frac{2g_i^+}{g_i^-+g_i^+},\qquad 0<x_i<2.
\]

`x_i=1` means equal incoming and outgoing diameters. Values below or above one state which side is larger.

### 4.2 Adult sphere-scale coordinate

First retain the local mean diameter

\[
L_i=\frac{g_i^-+g_i^+}{2}.
\]

The prime number theorem supplies the established local home scale `h_i=ln(p_i)`. Compare observed sphere scale with
that home scale using the same reversible 0–2 ARA ratio:

\[
y_i=\frac{2L_i}{L_i+h_i},\qquad 0<y_i<2.
\]

`y_i=1` means that the local mean diameter equals the logarithmic home scale. This is the registered candidate for
the slower adult coordinate. It is not claimed to be a new prime law: `ln(p)` is an established control supplied in
advance.

The unbinned pair is reversible at a known prime location:

\[
L_i=\frac{h_i y_i}{2-y_i},\qquad
g_i^+=x_iL_i,\qquad
g_i^-=(2-x_i)L_i.
\]

Thus `x` says how the two tangent diameters divide the local span; `y` says how large that span is relative to its
logarithmic rung. PN9 tests whether this factorisation is useful, not whether it creates information absent from the
raw gaps.

## 5. Frozen measurement grain and models

Bin both `x` and `y` into fixed equal bins on `[0,2]`. Primary resolution: 24 bins. Sensitivities: 12 and 48 bins.
Values may not be reoriented, smoothed or rebinned after results. Additive categorical smoothing is `alpha=0.5`.

For four consecutive gaps, construct `x_previous`, `x_current`, `y_current`, and `x_next`. Fit:

1. `X-M2`: `P(x_next | x_previous, x_current)` — the PN7C shape-only model.
2. `XY-M2`: `P(x_next | x_previous, x_current, y_current)` — the registered ridge-plus-scale model.
3. `RawGap-M1`: the existing PN7C exact-current-gap transition projected onto `x_next`, with alphabet `1..1024`,
   shrinkage `lambda=64`, and target fallback to the frozen training marginal.

The primary comparison is `X-M2 CE - XY-M2 CE`. A positive value means the scale coordinate adds transferable
information at the declared grain. `XY-M2` has more contexts and is therefore required to win out of sample.

## 6. Frozen recurrence and controls

### 6.1 Across-rung scale recurrence

At 24 bins, compare the marginal `y` distributions between R9/R10 and R10/R11 using Jensen–Shannon divergence in
bits. This checks whether dividing local sphere scale by its logarithmic home produces a recurring coordinate.

### 6.2 Exact-inventory shuffle

Make five copies of the R11 gap sequence, shuffled with seeds `2026071941..2026071945`. Reconstruct overlapping
`x` and `y` readings at the unchanged ordered R11 prime positions. Calculate

\[
I(y_i;x_{i+1}\mid x_{i-1},x_i)
=H(x_{i+1}\mid x_{i-1},x_i)
-H(x_{i+1}\mid x_{i-1},x_i,y_i).
\]

The shuffle preserves the exact gap inventory, the logarithmic rung and the mechanical shared-gap overlap while
destroying genuine gap order. This is an explanatory control, not a model-tuning source.

## 7. Registered scores

For R10 and R11 record cross-entropy, Brier score, top-1, top-3 and perplexity. On R11 divide observations into 100
fixed contiguous blocks and record the ridge-plus-scale cross-entropy gain in each block. Bootstrap the 100 block
means with 10,000 seeded resamples (`2026071949`) for a 95% percentile interval.

Also record exact reconstruction error before binning, coordinate ranges, marginal `y` distributions, and the
empirical conditional scale information for observed and shuffled R11.

## 8. Registered conditions

### P1 — transferred scale information

At 24 bins, R11 `X-M2 CE - XY-M2 CE >= 0.010` bits per reading.

### P2 — two-rung recurrence

The ridge-plus-scale cross-entropy gain is positive on both R9→R10 and R9+R10→R11 transfers.

### P3 — measurement-grain recurrence

The R11 ridge-plus-scale gain is positive at 12, 24 and 48 bins.

### P4 — distributed rather than isolated

At least 80 of 100 R11 blocks are positive and the bootstrap lower 95% bound is above zero.

### P5 — recurring adult coordinate

At 24 bins, both R9/R10 and R10/R11 marginal-`y` Jensen–Shannon divergences are at most `0.005` bits.

### P6 — order beyond mechanical tangent overlap

Observed R11 conditional scale information exceeds the maximum of the five exact-inventory shuffles by at least
`0.010` bits.

### P7 — competitive factorisation

At 24 bins, `XY-M2` R11 cross-entropy is lower than `RawGap-M1` cross-entropy.

P1–P5 are the **ridge-plus-scale transfer core**. P6 asks whether the ordered prime sequence contributes more than
the mechanically overlapping tangent construction. P7 asks whether the compressed factorisation is practically
competitive with an exact-gap control; neither P6 nor P7 may rescue a failed core.

## 9. Interpretation rules

If P1–P5 pass, the allowed statement is:

> On already-opened R9–R11 actual-prime gaps, the native ARA factorisation into tangent-ridge balance and logarithmic
> sphere scale recurs across the tested rungs, and the scale coordinate improves out-of-rung prediction of the next
> relative gap state.

If P6 fails, the extra information is adequately explained by the shared-gap/tangent construction plus the target
gap inventory. If P7 fails, the factorisation is informative but still loses useful detail relative to exact raw
gaps.

No outcome establishes that:

- primes are physical spheres;
- a literal Time wave causes prime gaps;
- ARA predicts exact unknown prime locations;
- ARA outperforms established prime-counting or prime-generation methods;
- the tangent representation is unique to primes;
- R12 or any untouched sequence has been predicted.

## 10. Required outputs

- protocol hash and source-packet hash verification;
- reproducible script and executed notebook;
- result JSON, score/block/control tables and static figure;
- independent validator that recomputes headline coordinates and scores without importing the main scorer;
- plain-language report and prime mapping update;
- complete SHA-256 manifest.
