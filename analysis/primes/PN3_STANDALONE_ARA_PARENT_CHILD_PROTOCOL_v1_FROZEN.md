# PN3 standalone ARA parent-child prime-survival protocol v1 (frozen)

**Test ID:** `PN3/STANDALONE-ARA-PARENT-CHILD/v1`  
**Freeze date:** 17 July 2026  
**Status at freeze:** development intervals open; target labels and target prime counts not generated or inspected  
**Target:** `[1,000,000,000,1,010,000,000)`  
**Prime-31 PN1H wheel:** prohibited and unchanged

## 1. Question

Can ARA produce an absolute fixed-budget prime-survival probability from its own scale and child geometry, without
receiving a prime-number-theorem or Hardy-Littlewood probability as a baseline?

PN2 answered a different question: whether local ARA states improve an imported analytic baseline. PN3 tests the
standalone decomposition

\[
\underbrace{P_{k+1}^{\rm ARA}}_{\text{slow parent-rung amplitude}}
+
\underbrace{\Delta_{\rm child}^{\rm ARA}}_{\text{local redistribution}}
\longrightarrow
\underbrace{\widehat P_{\rm standalone}^{\rm ARA}}_{\text{absolute survival probability}}.
\]

PNT and Hardy-Littlewood are computed only after the frozen ARA prediction packet exists. They may score the result
but cannot enter an ARA fit, offset, normalization or prediction.

## 2. Population and data boundary

The scored population is the same fixed-budget population used by PN2: integers coprime to `29#`. The p29 wheel is
the declared child-population boundary, not a probability model. PN3 asks which of those candidates survive all
larger prime factors.

This conditional population is retained because scoring all raw integers would be dominated by the already recovered
exact divisibility filters and would not isolate the missing parent-scale relation.

### 2.1 Parent calibration windows

Use the first 1% of three consecutive decimal scale rungs:

| Rung | Interval | Role |
|---|---|---|
| 6 | `[1,000,000,1,010,000)` | curvature sensitivity only |
| 7 | `[10,000,000,10,100,000)` | primary prior parent |
| 8 | `[100,000,000,101,000,000)` | primary current parent |
| 9 | `[1,000,000,000,1,010,000,000)` | untouched target |

Rung-8 labels are already open through PN2 and are development data for PN3.

### 2.2 Child training intervals

Use two already opened ten-million-number intervals:

- `[10,000,000,20,000,000)`;
- `[100,000,000,110,000,000)`.

No target labels, prime counts, survival rates, gap-class results or target-fitted quantities may enter development.

## 3. Parent ARA rule

For candidate-survival amplitudes `p7` and `p8`, define the oriented parent ARA relation

\[
x_{78}=\frac{2p_8}{p_7+p_8}.
\]

Holding that relational transfer for one further logarithmic rung gives

\[
\widehat p_9^{\rm ARA}
=p_8\frac{x_{78}}{2-x_{78}}
=\frac{p_8^2}{p_7}.
\]

Apply the same rule independently to adjacent-candidate edge-survival amplitudes `e7` and `e8`:

\[
\widehat e_9^{\rm ARA}=\frac{e_8^2}{e_7}.
\]

This is the primary large, slow parent prediction. It contains no PNT or Hardy-Littlewood value.

### 3.1 Required equivalence control

Record that the same numerical extrapolation can be written as ordinary log-linear transfer:

\[
\log \widehat p_9=2\log p_8-\log p_7.
\]

If the two predictions are identical, the parent rule is an ARA/log-linear crosswalk, not uniquely ARA evidence.

### 3.2 Parent controls and sensitivity

Candidate and edge endpoints both record:

1. **Home:** use the rung-8 rate unchanged.
2. **Raw additive:** `2*p8-p7` or `2*e8-e7`, clipped only to remain a probability.
3. **Three-rung log-linear OLS:** fit `log(rate)` against rung `6,7,8`, extrapolate to rung 9.
4. **ARA curvature sensitivity:** transfer the change in rung ratios,
   `r89=(r78^2/r67)` and `p9=p8*r89`, with the analogous edge rule.

Only the two-rung relational transfer is primary.

## 4. Child ARA rule

For p29-wheel gaps surrounding candidate `i`, define

\[
x_i=\frac{2g_i}{g_{i-1}+g_i}\in(0,2).
\]

Use 12 fixed equal-width bins on `[0,2]` and shrinkage `lambda=64`.

Candidate child representations:

1. **Plain ARA:** `x_i`.
2. **ARA Information^3:** ordered `(x_(i-1),x_i,x_(i+1))`.
3. **ARA decompressed:** that ordered triple plus its three local total widths.

Edge child representations:

1. **ARA endpoints:** ordered ARA readings at the two edge endpoints.
2. **ARA decompressed edge:** endpoint readings plus the central candidate gap.

Raw controls use the corresponding exact gap pair or four-gap stencil with the same development intervals and
shrinkage.

### 4.1 Standalone empirical child offsets

Within each development interval, use that interval's empirical aggregate rate as the local parent amplitude. For
each child state, estimate a smoothed log-odds offset relative to that interval rate. Combine the two interval offsets
by their state event counts. No analytic density is used.

### 4.2 TE-ARA conservation

On the unlabeled target state distribution, apply one label-free intercept correction so the mean child-model
probability equals the frozen parent prediction exactly:

\[
\frac1N\sum_i
\sigma\!\left(
\operatorname{logit}(\widehat p_9^{\rm ARA})
+\delta_{s_i}-\alpha
\right)
=\widehat p_9^{\rm ARA}.
\]

This prevents a child model from changing the total parent amplitude after target inspection. It may only
redistribute the frozen TE-ARA total among target child states. The correction uses target features but no labels.

## 5. Frozen models

### 5.1 Candidate models

- `ara_parent_only` — primary slow parent.
- `ara_parent_plain_child`.
- `ara_parent_i3_child` — primary full standalone ARA candidate model.
- `ara_parent_decompressed_child`.
- `raw_parent_pair_child`.
- `raw_parent_stencil_child`.
- parent controls from section 3.2.
- post-prediction reference only: `pnt29`.

### 5.2 Edge models

- `ara_edge_parent_only` — primary slow parent.
- `ara_edge_parent_endpoints` — primary full standalone ARA edge model.
- `ara_edge_parent_decompressed`.
- `raw_edge_parent_child`.
- parent controls from section 3.2.
- post-prediction reference only: conditional `hl29`.

## 6. Endpoints and decision rules

All event scores use binary log loss in bits; lower is better. Use 40 contiguous target blocks and 10,000 seeded
block-bootstrap resamples (`seed=20260717`).

### P1 — standalone parent recovery

For candidates and edges separately, record calibration error and log loss of the ARA parent prediction.

- **Parent recovery:** absolute relative aggregate-rate error at most 1% and no worse log loss than both Home and raw
  additive controls.
- **Analytic parity/support:** ARA parent log loss is no worse than PNT29 or HL29 respectively.
- ARA/log-linear equality must be labelled a crosswalk, not unique evidence.

### P2 — child redistribution

Primary candidate delta:

\[
\Delta_C=L_{\rm ARA\ parent}-L_{\rm ARA\ parent+I3}.
\]

Primary edge delta:

\[
\Delta_E=L_{\rm ARA\ edge\ parent}-L_{\rm ARA\ edge\ endpoints}.
\]

Child support requires a positive observed delta, a positive lower 95% block-bootstrap bound and improvement over the
corresponding raw child control. Failure or equality is preserved.

### P3 — full standalone comparison

Full standalone support requires both:

1. parent recovery under P1;
2. the full ARA parent-child model beats the relevant analytic reference with a positive lower 95% block-bootstrap
   bound.

Record partial outcomes exactly; do not collapse parent recovery, child redistribution and analytic superiority into
one label.

### Secondary outputs

- 20 target-location blocks;
- candidate-gap-class edge counts for classes with at least 100 survivors;
- parent-rate transfer table across rungs 6-9;
- sensitivity parent rules;
- ARA/raw child state coverage and unseen-state share;
- exact TE-ARA target-mean conservation error;
- exact ARA/log-linear parent equality error.

## 7. Leakage and contamination guards

1. The standalone ARA implementation must contain no PNT, twin-prime constant, singular-series or Hardy-Littlewood
   calculation in its fit or prediction path.
2. The ARA target packet is hashed before the established-comparator script reads target labels.
3. Comparator predictions cannot modify the ARA packet.
4. All target feature normalization is label-free and limited to the predeclared TE-ARA conservation intercept.
5. No retuning of bins, shrinkage, state definitions, parent rule, target or success criteria after target opening.
6. The p31 PN1H wheel is not generated, inspected or summarized.
7. An independent validator must reconstruct primality, features, parent transfer, child offsets, conservation,
   predictions, scores and block intervals without importing the primary implementation.

## 8. Freeze sequence

1. Hash this protocol.
2. Implement standalone development and target code with hard-coded interval guards.
3. Run development only and save the parent/child model.
4. Hash the executable and development model.
5. Write and hash a target-run configuration containing those hashes and the exact target.
6. Generate and hash the standalone ARA target packet.
7. Only then calculate PNT29/HL29 reference predictions and final scores.
8. Run the independent reconstruction and preserve every result.

## 9. Allowed interpretation

PN3 can test whether an ARA-defined logarithmic parent transfer plus locally conserved child geometry reconstructs
prime-survival probabilities on one fresh scale rung. It cannot prove that primes are physical waves, establish a
unique 0-to-2 cosmic orientation, prove the Hardy-Littlewood conjecture, address the Riemann hypothesis or establish
universal ARA geometry.

