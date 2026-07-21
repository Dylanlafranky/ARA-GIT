# PN10B child-phase prime-ranking protocol

**Test ID:** `PN10B/CHILD-PHASE/PRE-RIDGE-PRIME-RANKING/v1`  
**Declared:** 20 July 2026, before calculating any PN10B child feature or outcome  
**Evidence class:** registered development transfer plus fresh untouched-interval evaluation  
**Protected material:** do not construct the p31 primorial wheel and do not open R12

## 1. Question

PN10 stops the factor-sphere walk at `c=0.90`. Some survivors are prime and some are composite. Without testing a
single additional divisor, do the already-paid divisor gates contain useful child structure?

This is not another exact primality test. It asks whether a fixed ARA child representation compresses the residue
state into transferable ranking information better than controls receiving exactly the same already-paid gates.

## 2. Parent and child definitions

For each integer `n`, the parent stopping gate is

\[
y(n)=n^{0.45},
\]

because the PN10 diameter coordinate is `x_n(q)=2 log(q)/log(n)` and `x=0.90` gives `q=n^0.45`.

An integer enters PN10B only if no prime `q <= y(n)` divides it. The target label is `1` for prime and `0` for a
remaining composite.

Let `q_1 > q_2 > ... > q_9` be the nine largest prime gates not exceeding `y(n)`. Every one has already been tested
by the parent walk. For each gate,

\[
r_j(n)=n \bmod q_j,
\qquad
A_j=\frac{2r_j}{q_j},
\qquad
B_j=2-A_j.
\]

`A_j` is the progress from the previous multiple of `q_j`; `B_j` is the remaining progress to the next multiple.
They close exactly as `A_j+B_j=2`. They are two directions of one child axis, not two independent measurements.

Define the signed child orientation and adjacent ordered coupling by

\[
s_j=A_j-1,
\qquad
h_j=s_js_{j+1}\quad(j=1,...,8).
\]

Positive `h_j` means two adjacent gate children lie on the same side of their local ridge; negative means opposite
sides. This is the registered ARA coupling feature. No transform, smoothing, Fourier decomposition, NMF or SVD is
applied to the integer record.

## 3. Frozen datasets

- Stage A development: `D=[1,000,000,2,000,000)`.
- Stage A transfer: `E=[2,000,000,000,2,001,000,000)`.
- Stage B training: pooled `D+E` after Stage A is scored.
- Fresh target: `F=[4,000,000,000,4,001,000,000)`.

All intervals contain one million consecutive integers. `D` and `E` were opened by PN10, but their PN10B child
features have not been calculated before this registration. `F` has not been opened by the prime-test trail.

Ordinary divisor prime `31` may be tested as one gate. This does not construct the protected p31 primorial wheel.

## 4. Frozen representations

All learned models use the same deterministic L2-regularised logistic regression implementation, standardised on
training data only, `lambda=0.01`, at most 40 Newton steps and no hyperparameter tuning.

1. **Parent empirical:** one constant equal to training survivor prime prevalence.
2. **Buchstab parent:** the established asymptotic constant
   `p_B=(0.45)/omega(2/0.90)`, where for `2<u<=3`, `omega(u)=(1+log(u-1))/u`.
3. **ARA compact (4):** `mean(s)`, `mean(abs(s))`, `std(s)`, `mean(h)`.
4. **Raw compact (4):** `mean(r/q)`, `std(r/q)`, `min(r/q)`, `max(r/q)`.
5. **ARA full (17):** the nine ordered `s_j` and eight ordered `h_j`.
6. **Raw full (17):** the nine ordered `r_j/q_j` and eight adjacent differences
   `(r_j/q_j)-(r_{j+1}/q_{j+1})`.
7. **ARA order-scrambled (17):** circularly rotate the nine `s_j` positions by `n mod 9` before constructing the
   eight adjacent products. This preserves each row's child inventory while damaging the fixed gate-rank order.

`A` and `B` are not both passed as separate columns because `B=2-A`; duplicating them would falsely count one child
coordinate twice.

The primary child model is **ARA full**. ARA compact tests whether the child web can be compressed. The raw controls
test whether any gain is simply available from normalized residues rather than the declared ARA organisation.

## 5. Frozen fitting and scoring

Stage A fits each learned representation on D survivors and scores E survivors. Stage B refits on pooled D+E
survivors and scores F once. The target is never used for feature choice or model tuning.

Metrics are:

- binary log loss in bits (primary);
- Brier score;
- ROC AUC;
- top-decile prime lift relative to target prevalence;
- calibration intercept error (`mean(prediction)-mean(label)`).

For every fresh-target pairwise log-loss comparison, order F survivors by integer, split them into 100 contiguous
blocks, and bootstrap those blocks 2,000 times with seed `20260720`. Report the mean paired gain and percentile 95%
interval. Positive gain means the first named model is better.

Probabilities are clipped to `[1e-12,1-1e-12]` for scoring only.

## 6. Registered criteria

### P1 - child closure and gate guard

Across all retained rows, `max|A+B-2| <= 1e-12`, every selected gate satisfies `q<=n^0.45`, and no selected
remainder is zero.

### P2 - primary fresh child value

On F, ARA full has lower log loss than parent empirical, ROC AUC above `0.5`, and the paired bootstrap 95% interval
for its log-loss gain over parent lies wholly above zero.

### P3 - development-transfer sign

ARA full beats parent empirical in Stage A D-to-E transfer. This must have the same positive direction as Stage B.

### P4 - equal-budget raw control

On F, ARA full beats Raw full in log loss and the paired bootstrap 95% interval for the gain lies wholly above zero.

### P5 - ordered-coupling control

On F, ARA full beats ARA order-scrambled in log loss and the paired bootstrap 95% interval lies wholly above zero.

### P6 - compact representation

On F, ARA compact beats parent empirical and Raw compact in log loss. This is secondary; failure does not erase a
P2-P5 full-model result.

### L1 - information boundary

The ARA features are deterministic functions of already-known residues. They cannot create Shannon information.
A positive result would show useful organisation/generalisation at this fixed budget, not a new source of prime
information or an algorithm faster than exact trial division.

## 7. Verdict vocabulary

- `SUPPORTED`: P1-P5 pass.
- `SUGGESTIVE`: P1-P3 pass but P4 or P5 fails.
- `NULL`: P1 passes, the instrument is adequate, and P2 fails without a material implementation problem.
- `INCONCLUSIVE`: a closure, leakage, execution, sample or validation failure prevents interpretation.
- `NOT SUPPORTED`: a clean fresh result is materially worse than parent and controls.

## 8. Required artifacts

- frozen protocol, source and SHA-256 manifest;
- primary script, JSON results, prediction-score CSV and comparison CSV;
- independent implementation and validation JSON;
- executed reproducibility notebook;
- readable figure;
- technical/plain-language report and rendered Data Analytics report artifact;
- amendments to the prime mapping and prediction ledger;
- complete manifest of PN10B files.
