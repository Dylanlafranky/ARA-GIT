# T344 — controlled-weir Irrationality Di-ARA combined report

**Date:** 6 August 2026  
**Overall verdict:** **Di-ARA coupling partially supported; registered Irrationality
Di-ARA mechanism not supported**  
**Source:** BAW DOI [10.48437/99f329-73aee6](https://doi.org/10.48437/99f329-73aee6)  
**Associated study:** [10.59490/jchs.2025.0050](https://doi.org/10.59490/jchs.2025.0050)

## Answer first

This was the right kind of dataset for a substantially stronger test: 5,365 laboratory
particle trajectories moving through a controlled weir under three tailwater conditions,
followed by a separate 5,400-trajectory numerical representation of the same apparatus.
The native `0.01 s` records produced 2,847,023 laboratory ARA events and 10,794,600
numerical ARA events. Source hashes, frozen-method hashes, every fitted optimiser and all
saved gate verdicts passed independent validation.

The result separates two claims.

1. **Coupled Di-ARA geometry has real predictive content in the laboratory.** The intact
   line×turn relation predicted the next quadrant in an unseen hydraulic condition better
   than either child alone, their additive flattening, a persistence rule and a causally
   broken child pairing. Every effect had a whole-trajectory bootstrap interval above zero.
2. **The registered irrationality mechanism failed.** Coherent non-closing windows did
   not occupy the frozen middle regime of more retained information than random-like
   motion plus greater direct traversal than low-order closure. The information contrast
   was unresolved in the laboratory and negative numerically; the traversal contrast was
   strongly negative in both representations.

The numerical representation partially replicated the coupling result. Interaction and
correct child pairing remained useful, but its radial child alone beat the full parent in
all three settings. Gate E therefore fails the full direction-agreement criterion.

## ARA-first construction

For consecutive displacement vectors

\[
w_t=(x_t-x_{t-1})+i(z_t-z_{t-1}),
\qquad
q_t=\frac{w_t}{w_{t-1}}=s_t e^{i\delta_t},
\]

the two frozen ARA children were

\[
X_t=\frac{2s_t}{1+s_t}
\quad\text{and}\quad
Y_t=1+\frac{\delta_t}{\pi}.
\]

- `X<1` / `X>1`: radial contraction / expansion;
- `Y<1` / `Y>1`: reverse / forward turn;
- their intact ordered pair: the Di-ARA parent;
- the four mixed regions: `Ba`, `Ab`, `bA`, `aB`.

No smoothing, interpolation, Fourier transform, modal decomposition or imported flow
classification generated these coordinates. Entire hydraulic conditions were held out in
turn. The false-parent control paired the radial child with a present-time turn child from
a different trajectory without wrapping into future data.

## Frozen gates

| Gate | Laboratory | Numerical | Combined reading |
|---|---:|---:|---|
| A — all four sectors | PASS | PASS | complete descriptive quadrant support |
| B — intact parent beats both children and broken parent | PASS | FAIL | laboratory support; representation boundary |
| C — interaction beats additive children | PASS | PASS | replicated coupling-asymmetry advantage |
| D — structured-nonclosure sandwich | FAIL | FAIL | typed irrationality mechanism not supported |
| E — numerical direction agreement | — | FAIL | partial, not full, replication |

### Held-out log-loss improvement of intact parent

Positive values favour the intact parent.

| Comparison | Laboratory pooled effect (95% CI) | Numerical pooled effect (95% CI) |
|---|---:|---:|
| versus radial child | `+0.04872` (`0.04779, 0.04958`) | `−0.11876` (`−0.12048, −0.11711`) |
| versus turn child | `+0.05941` (`0.05849, 0.06037`) | `+0.01488` (`0.01274, 0.01694`) |
| versus causally broken parent | `+0.03725` (`0.03654, 0.03793`) | `+0.02406` (`0.02344, 0.02469`) |
| versus additive children | `+0.00527` (`0.00509, 0.00546`) | `+0.02422` (`0.02384, 0.02460`) |

The laboratory parent advantage is not a large absolute prediction gain, but it is
consistent across all three unseen conditions and independent trajectories. The numerical
radial reversal is equally unambiguous and must remain part of the result.

## Irrationality gate

At the registered `W=15` scale:

| Frozen contrast | Laboratory pooled effect (95% CI) | Numerical pooled effect (95% CI) |
|---|---:|---:|
| structured minus random predictive information | `−0.00219` (`−0.01044, 0.00337`) nats | `−0.000778` (`−0.001227, −0.000301`) nats |
| structured minus closure direct traversal | `−0.36083` (`−0.37050, −0.34921`) | `−0.24118` (`−0.24507, −0.23716`) |

The first contrast does not support extra information retention. The second runs strongly
opposite the frozen prediction. This is a real failure of the registered mechanism under
this observable; exact `Phi`, reciprocal-Phi, `e` or `1/e` landmarks cannot rescue it.

## What the failure exposed (post-result, exploratory)

The frozen traversal score was

\[
T=\frac{\lVert p_{t+W}-p_t\rVert}{\sum_j\lVert p_{j+1}-p_j\rVert}.
\]

It measures **path directness**, not amount of movement or persistence through a return
flow. Low-order closure windows were overwhelmingly carried by the direct downstream
branch (`T≈0.96` in the laboratory), while structured non-closing windows were more
curved (`T≈0.57–0.62`). The numerical representation showed the same direction.

This does not change Gate D. It creates a new testable possibility: the proposed
irrationality role may be expressed as coherent persistence through curvature,
recirculation or handover, whereas rational closure can be spatially direct. A successor
must freeze a curvature/return-flow persistence endpoint on new data before inspecting
its outcome.

## Representation boundary

The numerical ARA plane is visibly more ridge-concentrated and radial-dominant than the
laboratory plane. The interaction still improves over adding `X` and `Y`, and correct
pairing still improves over the causal false parent, but `X` alone is best. A cautious
inference is that the numerical representation retains the connection/radial branch more
strongly than the turn branch. This is an inference from the cross-representation result,
not proof that one simulator component is literally an ARA Phase B.

## Artifacts

- Laboratory figure: `T344_BAW_WEIR_IRRATIONALITY_DI_ARA_FIGURE.png`
- Laboratory explorer: `T344_BAW_WEIR_IRRATIONALITY_DI_ARA_EXPLORER.html`
- Numerical figure: `T344_BAW_WEIR_IRRATIONALITY_DI_ARA_NUMERICAL_REPLICATION_FIGURE.png`
- Numerical explorer: `T344_BAW_WEIR_IRRATIONALITY_DI_ARA_NUMERICAL_REPLICATION_EXPLORER.html`
- Frozen protocol and three implementation/mapping addenda are stored beside this report.
- Independent validations: `T344_BAW_WEIR_IRRATIONALITY_DI_ARA_VALIDATION_2026-08-06.md`
  and `T344_BAW_WEIR_IRRATIONALITY_DI_ARA_NUMERICAL_REPLICATION_VALIDATION_2026-08-06.md`.

## Claim boundary

T344 supports a narrower statement than the original target:

> In controlled moving flow, the exact ordered coupling between radial and turn ARA
> children can carry out-of-condition next-state information beyond an additive or
> causally mispaired representation; the size and even usefulness of the full parent
> relative to its strongest child are representation-specific.

T344 does **not** establish a universal Irrationality Di-ARA, exact irrational constants,
or the universal fractal-sphere hypothesis. It directly rejects the current
information-plus-direct-traversal sandwich as a transferable operational rule.

