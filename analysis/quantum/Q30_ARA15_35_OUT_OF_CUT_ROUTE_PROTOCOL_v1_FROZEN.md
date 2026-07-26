# Q30 — Frozen 1.5 / 3.5 Out-of-Cut Route Protocol

**Frozen before Q30 outcomes:** 26 July 2026  
**Status:** exploratory test on the completely opened Q27–Q29 simulator source  
**Test ID:** `Q30-ARA15-35-OUT-OF-CUT-ROUTE-EXPLORATION-v1`

## Question

Does the repository-native ARA `1.5` perpendicular leg identify a relation
outside Q29's source/child cut, and does the complete `3.5 = 2 + 1.5`
diagonal route carry Q29's unresolved component into later slices?

This is not a blind confirmation test and cannot, by itself, identify a new
quantum object or Phase B.

## Frozen geometric translation

For each retained Q29 handover event:

1. The released source relation is an unordered edge
   \(S=(u,e)\) at time \(t\).
2. Q28's positively accumulating child is the edge
   \(C=(e,v)\) at \(t+2\).
3. The source and child share endpoint \(e\).
4. Their two nonshared endpoints determine exactly one closing relation
   \(H=(u,v)\).

The three relations form the smallest Information³ closure:

\[
S=(u,e),\qquad C=(e,v),\qquad H=(u,v).
\]

The ARA route names are coordinates, not numerical multipliers:

- **1.5 leg:** the perpendicular closing relation \(H\) considered by itself;
- **3.5 route:** the complete source-to-child span `2` followed by the
  perpendicular closing leg `1.5`, hence `2 + 1.5 = 3.5`.

The `3.5` route must not be folded modulo `2`; its crossed-rung history is part
of the hypothesis.

## Frozen measurements

Q29's residual remains

\[
R=W-\alpha F(S),
\]

where \(W\) is the later child web and \(\alpha F(S)\) is Q28's frozen
positive-scale proper-flip transport.

At each lag \(\ell=0,\ldots,6\), fit

\[
R \approx \beta_\ell G\!\left(H_{t+2+\ell}\right),
\qquad \beta_\ell\ge 0,
\]

over exactly the same four proper diagonal sign transformations used in Q29.
No continuous rotation, intercept, axis selection, or fitted lag is allowed.

Two linked readings are reported:

1. **1.5 leg error:** residual-normalized error
   \(\lVert R-\beta GH\rVert/\lVert R\rVert\).
2. **3.5 composite error:** target-web-normalized error after adding the
   closing leg to Q28's transported source,
   \(\lVert R-\beta GH\rVert/\lVert W\rVert\).

Residual recovery is

\[
1-\frac{\lVert R-\beta GH\rVert}{\lVert R\rVert}.
\]

The late continuation window is frozen as lags `4–6`, where Q29's direct
signed-axis trace had decayed to its controls.

## Frozen controls

Every control receives one relation, the same four proper flips, one
non-negative scale, and the same lag set.

- **Seed displacement:** the exact closing pair in seed `+37 mod 100`.
- **Time displacement:** the exact closing pair shifted by `+137` inside the
  same 250-slice half.
- **Open-edge topology control:** replace the closing edge by a deterministic
  edge from source-other endpoint \(u\) to one node outside
  \(\{u,e,v\}\). The selected node is fixed by the event identifiers and is
  not chosen from outcome values.
- **Direct child control:** use the positively accumulating child relation
  \(C\) itself.

## Frozen event population

Reuse the exact Q29 deterministic event population:

- Q28 sampler:
  `(97*seed + 53*time + 31*pair + 17*endpoint + 11*branch) mod 16 = 0`;
- Q29 sampler:
  `(89*seed + 47*time + 23*pair + 13*endpoint + 7*branch) mod 4 = 0`;
- Q28 lag: `2`;
- development starts: `0–241`;
- opened later-half starts: `250–491`.

No event may be selected or removed according to Q30 route performance.

## Frozen decision gates

All gates are descriptive inside this opened simulator source.

### R1 — perpendicular 1.5 route

At lag `0`, the exact closing edge must:

- reduce weighted residual-normalized error by at least `5%` relative to both
  seed and time controls;
- beat the open-edge topology control by at least `5%`;
- beat both seed and time controls in at least `95%` of 2,000 later-half
  trial bootstrap draws.

### R2 — crossed-rung 3.5 composite

At lag `0`:

- exact median/weighted residual recovery must be at least `10%`;
- exact composite error must beat both seed- and time-displaced composite
  errors by at least `5%`.

### R3 — continuation beyond the Q29 cut

Across frozen lags `4–6`, exact closing-edge error must:

- beat both seed and time controls by at least `5%`;
- do so in at least `95%` of later-half trial bootstrap draws.

### R4 — route interpretation

- If `R1` and `R2` pass but `R3` fails: a local triangle-closing handover
  relation is supported, but it does not see past Q29's decay.
- If `R1`, `R2`, and `R3` pass: a reproducible out-of-cut continuation route
  is supported inside this source.
- Neither outcome identifies Phase B. That stronger label still requires an
  independently coherent counterpart, stable identity, return, and
  TE-ARA closure on an identifiable non-diagonal source.

## Required outputs

- complete JSON result;
- compact trial and lag CSVs;
- deterministic event sample;
- route figure;
- independent validation;
- executed reproducible notebook;
- plain-language report with ARA and established-data readings side by side.
