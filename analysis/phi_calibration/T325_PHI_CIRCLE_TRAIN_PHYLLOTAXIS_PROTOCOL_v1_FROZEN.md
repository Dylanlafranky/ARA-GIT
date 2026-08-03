# T325 — frozen Phi circle-train test in ordered plant phyllotaxis

**Frozen:** 2 August 2026, before T325 endpoint calculation  
**Test ID:** `T325-PHI-CIRCLE-TRAIN-PHYLLOTAXIS-v1`  
**Originator of ARA/Phi geometry:** Dylan La Franchi  
**Formalisation and boundary audit:** Codex  
**Status:** calibration/construct test on previously opened T302 source data; not a pristine external holdout

## 1. Question

Does the ordered placement lineage of successive Arabidopsis flower primordia
retain the proposed ARA Phi circle-train handover more strongly than nearby
rational rotations, an unconstrained development fit, shuffled order and
broken-lineage controls?

This is a direct child test of
`ARA_PHI_CIRCLE_TRAIN_DETECTION_PROCEDURE_LIVING.md`, version 0.1.

## 2. Source and prior-exposure boundary

The source is Tameshige et al. (2025), *Nature Communications*, DOI
`10.1038/s41467-025-65792-y`, Source Data 21.

- archive SHA-256:
  `1D93DE8B177F7556525DBCA07D34F1D40880DA33F68DC44ECCF93BBC7CB0D563`;
- workbook SHA-256:
  `E78372214B1386A486B25C8340C19F22BC74D3382F80A9B36A2972CC3D35ADFB`;
- worksheet: `EPFL_phyllo-angle`;
- raw columns: `genotype`, `meristem`, `angle`;
- expected records: 359 successive divergence angles from 58 plants.

The data and the earlier T302 endpoints have already been inspected. T325 is
therefore a frozen re-analysis and method-construction test. It can test new
operators honestly but cannot count as independent replication or blind
discovery.

## 3. ARA-first declaration

1. **Identity:** one physical meristem/plant retained while its recorded
   primordia advance in meristem-index order.
2. **Observable:** the source-measured divergence angle between successive
   primordia.
3. **Parent cycle:** one complete angular turn, `360 degrees`, mapped onto one
   ARA cycle `0..2`.
4. **Rung:** each recorded primordium-to-primordium divergence is a child
   handover; its ordered cumulative placement path is the parent carrier.
5. **Projection:** the azimuthal cut around the meristem centre.
6. **Event detector:** the published successive meristem indices. Phi is not
   used to select events.
7. **Eligibility:** a plant is valid only when its recorded indices are exactly
   `1,2,...,m`. The entire test stops on any violation.
8. **Missing/tie rule:** no interpolation. Non-finite angles stop the test.
9. **Direction boundary:** Source Data 21 records the smaller unsigned
   divergence angle and does not preserve independent clockwise/counter-clockwise
   handedness. T325 therefore tests the source-compatible minor-arc orientation,
   not physical chirality.

## 4. Exact ARA/Phi prediction

For source angle \(\theta_i\), define the observed ARA handover increment

\[
u_i=2\frac{\theta_i}{360^\circ}=\frac{\theta_i}{180^\circ},
\qquad 0\le u_i\le1.
\]

The living procedure's directed Phi increment is

\[
\delta_\phi^+=\frac{2}{\phi}=1.2360679775\ldots.
\]

Because the source uses the unsigned minor angle, the predeclared
source-compatible orientation is

\[
\boxed{
\delta_\phi^-=
-\frac{2}{\phi}\pmod 2
=2-\frac{2}{\phi}
=\frac{2}{\phi^2}
=0.7639320225\ldots
}.
\]

Thus the ordered parent position is

\[
p_0=0,
\qquad
p_i=(p_{i-1}+u_i)\bmod2,
\]

and the frozen Phi prediction from anchor \(p_a\) is

\[
\widehat p_{a+h}^{(\phi)}
=(p_a+h\delta_\phi^-)\bmod2.
\]

The circular loss is

\[
d_2(x,y)=\min(|x-y|,2-|x-y|).
\]

The equivalence between `+2/phi` and `-2/phi` is mathematical. The source does
not independently test which handed orientation the plant used.

## 5. Frozen split and anchor

Plant IDs are reconstructed exactly as in T302: within each genotype, a new
plant begins whenever `meristem` resets to 1.

- odd plant IDs: development;
- even plant IDs: confirmation;
- events 1 and 2: observed anchor construction;
- events 3 and later: untouched evaluation positions for that plant.

Headline predictive scores use wild-type `Col` confirmation plants. Mutants
are biological perturbation diagnostics, not alternative fitted datasets.

## 6. Frozen competitors

All increments are written in the source-compatible minor orientation.

| Model | ARA increment |
|---|---:|
| persistence | `0` |
| one-third phase | `2/3` |
| nearest eighth / 3/8 child | `3/4` |
| exact Phi | `2/phi^2` |
| Fibonacci rational 8/21 | `16/21` |
| two-fifths phase | `4/5` |
| half-turn / ridge | `1` |
| matched irrational 1/e | `2/e` |
| silver conjugate | `2(sqrt(2)-1)` |

Two development-only free controls are frozen before confirmation scoring:

1. **step fit:** median of development-plant median increments;
2. **carrier fit:** grid value on `[0.60,0.90]` with step `0.00001` that
   minimizes the median development-plant multi-step loss; ties choose the
   smallest value.

## 7. Scores

### 7.1 One-step

For each plant and competitor, take the median `d2(u_i, delta)` over held-out
events. The headline is the median of those plant medians. Exact Phi must beat
every fixed competitor to pass the one-step gate.

### 7.2 Multi-step carrier

Anchor at the observed cumulative position after event 2. Predict every later
position without re-anchoring. Take the median circular error per plant, then
the median across plants. Exact Phi must beat every fixed competitor to pass
the carrier gate.

Report separate horizon profiles for `h=1,2,3,4,5` where data exist.

### 7.3 Free-fit control

Bootstrap development plants 5,000 times and refit the carrier increment.
The free-fit gate passes only when:

1. exact Phi lies inside the percentile 95% interval of fitted increments; and
2. on confirmation plants, the carrier fit does not have a significant
   positive advantage over Phi under a 10,000-draw paired plant bootstrap
   (`95%` interval for `Phi loss - fitted loss` does not lie wholly above 0).

### 7.4 Order dependence

Within every confirmation wild-type plant, hold the first two events fixed and
permute only the held-out increments. Reconstruct cumulative positions and
score the frozen Phi carrier. Use 10,000 deterministic shuffles. The order gate
passes when the true-order loss is lower than the shuffle distribution with
lower-tail `p < 0.05`.

### 7.5 Local compensation and broken lineage

Let `e_i = u_i - delta_phi`. For adjacent held-out child residuals, define

\[
C=
\frac{
\operatorname{median}|(e_i+e_{i+1})/2|
}{
\operatorname{median}[(|e_i|+|e_{i+1}|)/2]
}.
\]

`C<1` means adjacent deviations partially cancel. Compare the observed `C`
with two 10,000-draw nulls:

1. within-plant order permutation;
2. residual pairing across different plants, preserving the marginal residual
   distribution while breaking lineage.

Each gate passes when observed `C` is smaller with lower-tail `p < 0.05`.

### 7.6 Fibonacci near-return fingerprint

For lags `F = 2,3,5`, compute within-plant circular return distances
`d2(p_(i+F), p_i)`. Aggregate first within plant and then across confirmation
wild-type plants. For every fixed competitor, compare the observed three-lag
profile with its predicted profile

\[
r_F(\delta)=d_2((F\delta)\bmod2,0).
\]

Exact Phi passes only if its three-lag mean absolute error is the lowest fixed
candidate. Because the sequences are short and expose only three Fibonacci
lags, this endpoint is a bounded fingerprint, not a full recurrence proof.

## 8. Resolution and source limitations

The workbook records angles to `0.001 degrees`; this is numerical record
precision, not a validated ImageJ measurement-uncertainty estimate. The exact
Phi versus `3/8` separation is

\[
2.507764^\circ
\quad\text{or}\quad
0.0139320\text{ ARA units}.
\]

T325 will report cluster-bootstrap uncertainty in score differences. It will
not infer physical measurement accuracy from decimal precision. Failure to
separate close competitors is an empirical non-separation; uncertainty about
the instrument remains a caveat.

## 9. Robustness diagnostics

Report, without changing the frozen gates:

- development versus confirmation;
- wild type versus `e2` and `e1e2`;
- per-plant distributions and event counts;
- removal of the longest and shortest sequence;
- mean alongside median losses;
- the full fixed-candidate ranking;
- exact Phi versus `3/8`, `8/21`, and both free fits;
- first ten source rows and source hashes.

## 10. Verdict boundary

The living procedure's core conditions are reported separately rather than
collapsed into an inflated single score. The allowed overall verdicts are:

- `MIXED / PARTIAL CALIBRATION`;
- `NOT SUPPORTED IN THIS PLANT CUT`;
- `INCONCLUSIVE — CONSTRUCT OR RESOLUTION`.

T325 cannot return universal confirmation because:

- the data and T302 results were previously opened;
- handed direction is absent;
- parent seams are the known angular cycle rather than a separately measured
  temporal oscillator;
- no independent external replication is included.

No result here proves the complete ARA sphere, universal Phi handover, TE-ARA,
or causal biological use of the proposed operator.

## 11. Reproduction outputs

The run must write:

- complete event geometry;
- per-plant candidate scores;
- horizon profiles;
- null-control summaries;
- Fibonacci-return profiles;
- one machine-readable result JSON;
- one independent validation JSON;
- one technical Markdown report;
- a bounded report artifact rendered through the Data Analytics report surface.

