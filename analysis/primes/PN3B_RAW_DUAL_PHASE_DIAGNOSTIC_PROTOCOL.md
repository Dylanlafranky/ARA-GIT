# PN3B raw integer dual-phase diagnostic protocol

**Test ID:** `PN3B/RAW-DUAL-PHASE/OPENED-DEVELOPMENT-v1`  
**Method locked:** 18 July 2026  
**Evidence class:** opened-data exploratory diagnostic; not blind confirmation and not a rescue of PN2 or PN3  
**Target guard:** the p31 PN1H wheel, residues, masks, gaps and predictions remain prohibited  
**Geometry authority:** Dylan retains all ARA Phase A/Phase B, Space/Time, connection/traversal and up/down orientation. Statistical outputs remain neutral until he assigns them.

## 1. Question

The preceding prime tests may have measured only the connection-heavy half of the object. Numbers, gaps, factors,
candidate identity and cumulative survival all remain number-line or state descriptions. This diagnostic asks:

1. What phase/frequency structure is present in the **complete raw prime/composite sequence**?
2. How much of that structure is reproduced by ordinary deterministic divisibility masks?
3. After the known connection masks and slow density are separated, is there a coherent residual phase mode that
   recurs across opened decimal rungs?
4. Does a joint number-position x future-sieve-gate map contain stable non-separable structure that was destroyed by
   the previous terminal label and aggregate survival curve?

No observed mode will be called physical Time. The highest possible result is a **candidate time-like phase
coordinate** requiring a fresh frozen test.

## 2. Opened populations

Use every integer in the already opened PN3 windows:

| Rung | Interval | Raw integer events |
|---|---:|---:|
| R6 | `[1,000,000, 1,010,000)` | 10,000 |
| R7 | `[10,000,000, 10,100,000)` | 100,000 |
| R8 | `[100,000,000, 101,000,000)` | 1,000,000 |
| R9 | `[1,000,000,000, 1,010,000,000)` | 10,000,000 |

For each integer (n):

- (y(n)=1) if prime and (0) otherwise;
- (w_Q(n)=1) if (n) is not divisible by any prime at or below sieve budget (Q), otherwise (0);
- (d(n)) is the smallest prime divisor above 29 for p29-admissible candidates, with (d(n)=0) for a prime.

The raw `y(n)` sequence is always reported first. Masks are comparison layers.

## 3. Exact dual representation

For a mean-centred sequence (s_j) of length (N), use the exact rectangular-window discrete transform

\[
F_s(k)=\sum_{j=0}^{N-1}s_j e^{-2\pi i k j/N},\qquad k=1,\ldots,\lfloor N/2\rfloor.
\]

Report normalized power (|F_s(k)|^2/\sum_{h>0}|F_s(h)|^2), complex phase and log-binned spectral envelopes. A
Hann-window transform is a leakage sensitivity only and cannot rescue a failed rectangular result.

The full-spectrum envelope uses 512 logarithmic frequency bins. Adult-scale phase uses the first 128 scaled modes.
Because every window begins at exactly 100 window-lengths, local and absolute phase differ by an integer number of
turns at the scaled Fourier modes.

## 4. Connection-removal ladder

The fixed ordinary sieve budgets are

`Q = raw, 2, 3, 5, 7, 11, 29, 97, 313, 997`.

At budget (Q), define the constant-rate connection prediction

\[
\widehat y_Q(n)=\widehat p_Q w_Q(n),\qquad
\widehat p_Q=\frac{\sum_n y(n)}{\sum_n w_Q(n)},
\]

and residual (r_Q(n)=y(n)-\widehat y_Q(n)). This is descriptive projection on the opened window, not a forecast.
The ladder asks whether an apparent phase line is progressively absorbed as more ordinary factor connections are
represented.

Primary residual layer: `Q=29`. Deeper budgets are diagnostic controls, not alternative primaries. A 64-block
empirical-density residual is retained as a sensitivity because it may remove a genuinely slow mode.

## 5. Scale-normalized adult phase

Divide each full integer window into 256 equal number-line cells. Within cell (b), let (C_b) be p29-admissible
candidates and (P_b) the primes. Define

\[
z_b=\frac{P_b-\widehat p_{29}C_b}
{\sqrt{\widehat p_{29}(1-\widehat p_{29})C_b}}.
\]

This is the signed local excess after accounting for candidate exposure. It is not called energy. Use 128 and 512
cells as sensitivities. R6 is sample-size sensitivity only; primary cross-scale comparisons are R7->R8 and R8->R9.

Measure:

1. position-domain correlation of (z_b);
2. low-mode log-power correlation for modes 1-64;
3. complex phase coherence
   \(
   |\sum_k F_a(k)F_b(k)^*|/
   \sqrt{\sum_k|F_a(k)|^2\sum_k|F_b(k)|^2}
   \);
4. top-mode identity and phase.

## 6. Null controls

Use 500 fixed-seed (`20260718`) conditional null draws for the 256-cell primary:

- **global label null:** distribute the observed number of primes over cell candidate counts with a multivariate
  hypergeometric draw; preserves total primes and p29 candidate exposure but destroys position/phase;
- **16-macroblock null:** preserve the prime total inside each group of 16 adjacent cells, then redistribute within
  that macroblock; preserves the slow envelope while destroying finer phase.

Family-wise peak significance uses each draw's maximum low-mode power. Cross-rung correlations and coherence use
independent null draws for the two rungs. Report empirical (p=(1+\#\{T_{null}\ge T_{obs}\})/(501)).

## 7. Joint number-position x future-gate map

For p29-admissible candidates, bin number position into 128 cells and future death into 32 normalized log-sieve
stages plus a survivor class. Build count matrix (O_{bt}). Remove the independent row/column expectation

\[
E_{bt}=\frac{O_{b\cdot}O_{\cdot t}}{O_{\cdot\cdot}},\qquad
R_{bt}=\frac{O_{bt}-E_{bt}}{\sqrt{E_{bt}}}.
\]

Measure mutual information, leading singular-value energy and the first spatial/temporal singular vectors. Compare
with 500 exact label permutations across candidate records, preserving both observed position-block totals and
death-stage totals.
Test sign-invariant first-mode alignment across R7-R8 and R8-R9. A significant matrix only establishes dependence;
stable aligned modes are required for a reusable coordinate.

## 8. Interpretation gates

### Connection-dominated

Use this label when major raw spectral features are reproduced by `w_Q`, are progressively absorbed by the sieve
ladder, or residual modes do not recur across R7-R9 beyond null controls.

### Candidate time-like phase coordinate

This provisional label requires all of the following on opened data:

1. a residual low-mode family-wise (p\le0.01) on both R8 and R9;
2. R8-R9 phase coherence above the 99th percentile of the global and macroblock nulls;
3. the mode remains visible after at least the Q=997 connection control;
4. the joint gate map has non-null structure and its leading spatial and gate modes align R8-R9 above the 99th
   percentile;
5. the result is not merely a zero-frequency density shift, boundary leakage or a known represented sieve line.

Failure of this conjunction means **no candidate time-like wave recovered by this representation**. Partial results
remain descriptive leads only.

## 9. Required caveats

- Fourier duality is established mathematics; its use does not validate ARA.
- The prime sequence is deterministic. `Random` refers only to an explicit comparison distribution.
- A residual after Q=997 can still reflect larger unmodelled prime factors.
- Significance on opened data is exploratory and affected by method selection.
- No spectral or matrix pattern proves physical Time, a universal wave, RH or a new prime law.
- p31 remains untouched.

## 10. Required artifacts

1. primary script and saved arrays;
2. raw/connection/residual dual-spectrum figure;
3. scale-normalized phase and joint future-gate figure;
4. bounded CSV summaries and JSON results;
5. independently coded validation;
6. executed reproducibility notebook;
7. technical report and canonical recording updates.

## 11. Pre-interpretation implementation amendment — 18 July 2026

The first complete computation reached the export stage before any joint-map result was promoted. Audit found two
implementation issues:

1. the joint-map multinomial null preserved stage totals and expected exposure but did not preserve exact position
   totals, biasing mutual-information comparison;
2. spectral entropy was passed unnormalised power instead of its probability-normalised form.

Version 1 keeps every population, signal, sieve budget, Fourier mode, threshold, seed and interpretation gate
unchanged, but replaces the joint null with exact candidate-stage permutations preserving both margins and computes
entropy from normalised power. The initial output is not retained as a result. This correction is disclosed because
the opened-data method cannot acquire a blind evidence ceiling through repair.
