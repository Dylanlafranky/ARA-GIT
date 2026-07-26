# Frozen protocol — Q28 ARA^9 interlocking rotational transport

**Protocol ID:** `Q28-ARA9-INTERLOCKING-ROTATIONAL-TRANSPORT-v1`  
**Date frozen:** 26 July 2026  
**Ledger:** T284  
**Source status:** complete Q27 values are already open; no Q28 rotation,
Procrustes, lag-selection or spectrum value has been calculated at freeze.

## 1. Question

Q27 compressed every connected ARA^9 relation to a scalar closure. It found
common local crest reconstruction and a non-random ordered
release-to-active-neighbour accumulation relation, while its simple mirrored
clock, strong one-neighbour Phase-B crest and determinant-sign flip failed.

Q28 asks whether the missing full-matrix information has the geometry Dylan
proposed:

> Does a releasing ARA^9 interlock with the active neighbouring web through a
> shared endpoint, undergo a proper angled rotation, and travel with a short
> positive delay while preserving more internal shape than matched controls?

## 2. Source and split

Use exactly the Q27 source:

- Zenodo DOI `10.5281/zenodo.16753415`;
- archive `unnati_submit_12_pure_random.hdf5.zip`;
- archive MD5 `06b6b278c4ce1e8ce14d2d662f0dc9dc`;
- extracted HDF5 SHA-256
  `0e10afb6e5c7bcc3b469a9bb18a9bcae9469bfae165d5da5add93eeeb1972eeb`;
- both 12-qubit connectivity strata;
- all 100 unitary seeds in each stratum;
- all 500 time steps;
- all 66 unordered pair relations.

Development is restricted to starting times `0–241`. Hidden evaluation is
restricted to starting times `250–491`. No trajectory crosses the split.

The source precision is known from Q27. Q28 accepts maximum sampled trace error
at or below `5e-5`, Hermiticity error at or below `1e-6`, and minimum
eigenvalue at or above `-1e-6`. This tolerance was set after Q27 and is not a
new blind source-quality result.

## 3. Complete ARA^9 object

For every pair:

\[
C=T-\mathbf a\mathbf b^\mathsf T\in\mathbb R^{3\times3}.
\]

The radial closure is retained from Q27:

\[
h=|\det C|^{1/3}.
\]

For a pair \(p=(i,j)\) and a selected endpoint \(e\):

\[
\mathcal O(C,p,e)=
\begin{cases}
C,&e=i,\\
C^\mathsf T,&e=j.
\end{cases}
\]

This places the selected endpoint on the row side of the ARA^9 relation.

## 4. Source release and neighbouring web

For source pair \(p\), starting time \(t\), endpoint \(e\in p\), and lag
\(\ell\in\{1,\ldots,8\}\):

\[
r_p(t)=\max(0,h_p(t)-h_p(t+1)).
\]

Use the six source-defined active edges for transition \(t\to t+1\). Retain
every active target \(q\ne p\) containing endpoint \(e\). Its lagged
accumulation is:

\[
a_q(t,\ell)=\max(0,h_q(t+\ell)-h_q(t)).
\]

The correct shared-endpoint target web is:

\[
W_e(t,\ell)=
\frac{\sum_q a_q(t,\ell)\,\mathcal O(C_q(t+\ell),q,e)}
{\sum_q a_q(t,\ell)}.
\]

The event weight is:

\[
w=r_p(t)\sum_q a_q(t,\ell).
\]

An event is eligible when `w>0`, source and web Frobenius norms exceed `1e-8`,
and all matrices are finite.

No single neighbour may be selected by its rotational outcome. All accumulating
active neighbours at the endpoint are retained in the web.

## 5. Deterministic sampling

To keep the full test reproducible and bounded while retaining every trial,
include an otherwise eligible source-endpoint-time event only when:

\[
(97\,s+53\,t+31\,p+17\,e+11\,b)\bmod16=0,
\]

where `s` is unitary seed, `p` pair index, `e` is the numeric endpoint and `b`
is branch index.

This rule is value-independent and frozen before Q28 outcomes.

## 6. Shared-point rotation

Let:

\[
S=\mathcal O(C_p(t),p,e),\qquad W=W_e(t,\ell).
\]

### 6.1 No-rotation scale baseline

Fit only a non-negative scale:

\[
\alpha_0=\max\left(0,\frac{\langle W,S\rangle_F}{\|S\|_F^2}\right),
\qquad
\epsilon_0=\frac{\|W-\alpha_0S\|_F}{\|W\|_F}.
\]

### 6.2 Proper shared-endpoint rotation

Let:

\[
WS^\mathsf T=U\Sigma V^\mathsf T,
\]

\[
R=U\,\operatorname{diag}(1,1,\det(UV^\mathsf T))\,V^\mathsf T\in SO(3).
\]

Then:

\[
\alpha_R=\max\left(0,
\frac{\langle W,RS\rangle_F}{\|S\|_F^2}\right),
\qquad
\epsilon_R=\frac{\|W-\alpha_RRS\|_F}{\|W\|_F}.
\]

Rotation gain is:

\[
g_R=\frac{\epsilon_0-\epsilon_R}{\max(\epsilon_0,10^{-12})}.
\]

The fitted angle is:

\[
\theta=\arccos\left(
\operatorname{clip}\frac{\operatorname{tr}(R)-1}{2},-1,1
\right).
\]

### 6.3 Internal-shape retention

Let \(\widehat{\boldsymbol\sigma}(M)\) be the three singular values of \(M\),
sorted descending and normalized to unit Euclidean norm. Define:

\[
S_\sigma=
\widehat{\boldsymbol\sigma}(S)\cdot
\widehat{\boldsymbol\sigma}(W).
\]

This is a rotation-invariant shape similarity in `[0,1]`.

## 7. Controls

Every control uses the same selected source events and exact event weights.

1. **No rotation:** \(\epsilon_0\).
2. **Wrong endpoint:** orient the source and each target through their
   non-shared endpoints, then repeat the proper-rotation fit.
3. **Seed displacement:** replace every target matrix by the same
   branch/pair/time matrix from seed `(seed+37) mod 100`; retain exact source,
   edge labels and weights.
4. **Time displacement:** replace every target time by a circular shift of
   `+137` steps inside the same development or hidden partition; retain exact
   source, labels and weights.
5. **Lag zero:** for the frozen hidden event set and weights, evaluate the
   correct target web at time \(t\), before the fitted positive delay.

Seed and time controls break the local transport relation without changing the
overall source branch, pair labels, event weights or source matrix.

## 8. Development-only lag selection

For every lag `1–8`, calculate the development weighted mean
\(\epsilon_R\). Select:

\[
\ell^\star=\arg\min_{\ell\in\{1,\ldots,8\}}\overline{\epsilon_R}.
\]

Ties go to the smaller lag. Freeze \(\ell^\star\), the development weighted
median angle and its weighted interquartile range before evaluating hidden
times.

## 9. Hidden metrics

Report pooled, `c2` and `c4`:

- event and trial counts;
- weighted \(\epsilon_R,\epsilon_0,g_R\);
- correct shared-endpoint, wrong-endpoint, seed-displaced, time-displaced and
  lag-zero residuals;
- paired trial-cluster bootstrap probabilities with `2,000` draws, seed
  `28028`;
- weighted median/IQR angle;
- angle difference from development;
- fraction of hidden weight inside the development angle IQR;
- singular-spectrum similarity;
- split-half results for seeds `0–49` and `50–99`.

## 10. Gates

### Data and eligibility

- `D1`: source checksums match Q27.
- `D2`: both branches, 200 trials and all 66 pairs are present.
- `D3`: known Q28 source-precision limits pass.
- `E1`: at least 100 trials and 100,000 eligible hidden events.

### Interlocking-rotation branch

- `I1`: weighted hidden rotation gain is at least `10%`.
- `I2`: rotation beats no rotation with paired trial-bootstrap probability
  at least `0.95`.
- `I3`: correct shared-endpoint residual is at least `5%` lower than the
  wrong-endpoint residual, with bootstrap probability at least `0.95`.
- `I4`: correct residual beats both seed- and time-displaced controls with
  bootstrap probability at least `0.95` for each.
- `I5`: singular-spectrum similarity is at least `0.90` and is higher than
  both displaced controls.

### Traveling angled-wave branch

- `T1`: the frozen positive lag residual is at least `5%` lower than lag zero,
  with bootstrap probability at least `0.95`.
- `T2`: hidden weighted-median angle is within `15°` of development.
- `T3`: at least `50%` of hidden event weight lies inside the development
  angle IQR.
- `T4`: the direction of `I1`, `I3`, `I4` and `T1` agrees separately in `c2`
  and `c4`.

## 11. Verdict

- **INTERLOCKING ROTATION SUPPORTED:** `D1–D3`, `E1` and `I1–I5` pass.
- **TRAVELING ANGLED WAVE SUPPORTED:** `D1–D3`, `E1` and `T1–T4` pass.
- **COMBINED SUPPORTED:** both branches pass.
- **PARTIAL:** exactly one branch passes.
- **NOT SUPPORTED:** eligibility passes and neither branch passes.
- **INCONCLUSIVE:** a data or eligibility gate fails.

Failure of the complete claim does not erase separately reported radial
transfer, rotation gain, shared-point specificity or deformation.

## 12. Visualization contract

Primary surface: executed analytical notebook plus static PNG/SVG.

Figure:

1. comparison bars for correct rotation, no rotation, wrong endpoint,
   seed displacement and time displacement;
2. development and hidden lag curves for `0–8`;
3. development/hidden fitted-angle distributions at \(\ell^\star\);
4. radial release, target accumulation and fitted angle for one
   predeclared worked trajectory selected by maximum eligible event weight in
   development only.

Use a white background, deep-charcoal text, blue for exact ARA geometry,
orange for controls, grey references, and non-colour line/marker differences.
Titles must describe what is plotted rather than announce a conclusion.

## 13. Evidence boundary

This is a registered transformation on a previously opened simulated source.
Positive results would establish that the new full-matrix ARA decomposition
captures a reproducible interlocking/transport relation here. They would not
establish a new quantum law, hardware behaviour, universal Phase B, universal
fractal geometry or an A-tier provenance prediction.

