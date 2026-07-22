# PN25 — corrected pair-ridge compression

**Run:** 22 July 2026  
**Status:** **GEOMETRIC-ONLY SUPPORT / DYNAMIC NULL**  
**Independent validation:** **PASS, 14/14 checks**  
**Fresh target:** 6,000 anchors across three previously unused scale ranges  
**Protected 87-bit anchor:** remained sealed

## Answer first

The corrected compression is mathematically exact:

\[
\frac1{13}\rightarrow\frac3{11}\rightarrow\frac5{9}\rightarrow\frac7{7}=1
\]

is a monotone odds progression toward the missing mod-14 ridge. Converting those odds into TE-ARA's total-2
coordinate gives

\[
(1/7,13/7),\quad(3/7,11/7),\quad(5/7,9/7),\quad(1,1).
\]

Every pair is one complete identity because its two shares sum to 2. The first coordinate measures where that
identity sits relative to the ridge; it does not measure whether the identity is complete.

The six raw residue lanes also compress safely into three pair-closeness classes for the tested outcomes. The
three-class model matched the six-lane model to much better than the frozen 2% tolerance.

However, greater ridge-closeness did **not** predict fewer remaining handovers, immediate prime closure, closure
within three candidate states, or upward movement along the candidate path. All four prospective dynamic predictions
failed across 6,000 fresh anchors.

The clean conclusion is:

> The pair coordinate is an exact lateral coordinate inside the mod-14 wheel. It is not a temporal distance to the
> next-prime ridge. Later factor gates supply an effectively orthogonal/vertical coordinate that this compression
> does not contain.

## The corrected mathematics

Let the left member of a reversible pair be (a\in\{1,3,5\}), with opposite member (14-a). Its directional odds
are

\[
q(a)=\frac{a}{14-a}.
\]

Odds are not yet a bounded ARA coordinate. Convert them by

\[
\underbrace{x_A}_{\substack{\text{ARA share}\text{from the left}}}
=
\frac{2q}{1+q}
=
\frac a7,
\qquad
\underbrace{x_B}_{\substack{\text{opposite}\text{ARA share}}}
=2-x_A
=
\frac{14-a}{7}.
\]

| Pair identity | Directional odds | TE-ARA composition | Closeness to ridge |
|---|---:|---:|---:|
| `(1,13)` | `1/13` | `(1/7,13/7)` | `1/7` |
| `(3,11)` | `3/11` | `(3/7,11/7)` | `3/7` |
| `(5,9)` | `5/9` | `(5/7,9/7)` | `5/7` |
| `(7,7)` | `1` | `(1,1)` | `1` |

Every row obeys

\[
x_A+x_B=2.
\]

Residue 7 is absent from the survivor wheel because gate 7 divides it. The exact `(1,1)` ridge is therefore a
collision boundary rather than a surviving lane.

For all six oriented lanes, the complete coordinate is

\[
x(r)=\frac r7,
\qquad
c(r)=1-|x(r)-1|=\frac{\min(r,14-r)}7,
\qquad
s(r)=\operatorname{sign}(r-7).
\]

The three-valued (c) records pair/ridge distance; the sign (s) restores orientation. Together they reconstruct
all six lanes exactly.

## Prospective data

The protocol was frozen before calculating target outcomes. It used 2,000 deterministic anchors in each range:

- `[61,000,000, 61,500,000)`;
- `[61,000,000,000, 61,000,500,000)`;
- `[610,000,000,000, 610,000,500,000)`.

The 6,000 anchors produced 5,536 distinct next-prime labels. PN24's already-open 2,000-anchor sample supplied all
probability estimates used by the frozen compression models; target outcomes were scoring-only.

## Primary dynamic result

The predicted order was that moving from `1/7` to `3/7` to `5/7` would reduce the mean number of future handovers.
It did not.

### Pooled target

| Pair class | n | Mean handovers | Base candidate already prime | Prime within 3 states |
|---:|---:|---:|---:|---:|
| `1/7` | 1,710 | 2.1585 | 9.415% | 64.035% |
| `3/7` | 1,758 | 2.1917 | 10.922% | 62.457% |
| `5/7` | 2,532 | 2.1730 | 10.269% | 63.547% |

None of the three outcomes was monotone in the frozen direction.

### Correlation across scales

| Scale | Correlation: closeness vs handovers |
|---|---:|
| low | `-0.000920` |
| middle | `+0.011323` |
| high | `+0.000126` |
| pooled | `+0.003335` |

The pooled scale-stratified 10,000-permutation test gave one-sided `p=0.6110` for the predicted negative relation.
The result is effectively zero and slightly opposite the predicted direction.

## Path-direction result

If the mod-14 coordinate were itself an upward handover clock, terminal primes should usually sit closer to its
`(7,7)` ridge than their initial candidates.

| Final minus initial closeness | Count | Share |
|---|---:|---:|
| Positive / moved toward ridge | 1,611 | 26.85% |
| Zero / same pair class | 2,200 | 36.67% |
| Negative / moved away | 2,189 | 36.48% |

Mean change was `-0.04238`. Candidates moved away more often than toward the base-wheel ridge. Frozen prediction P4
therefore failed.

This does not invalidate the pair coordinate. It shows that the next-prime completion path does not travel
monotonically through this one projection.

## Compression result

Models were fitted only on PN24 development outcomes and scored without target refitting.

### Base candidate already prime (`Y0`)

| Frozen model | Target Brier loss |
|---|---:|
| Global constant | **0.091920** |
| Orientation only | 0.091990 |
| Three pair classes | 0.092043 |
| Six raw lanes | 0.092087 |

The pair model was `0.0486%` better than the six-lane model, easily passing the “no more than 2% worse” fidelity
criterion. Both residue models were slightly worse than the global constant.

### Prime within three candidate states (`Y3`)

| Frozen model | Target Brier loss |
|---|---:|
| Global constant | 0.232141 |
| Orientation only | **0.232094** |
| Three pair classes | 0.232229 |
| Six raw lanes | 0.232235 |

The pair model was `0.00253%` better than the full six-lane model, again passing compression fidelity. Neither pair
nor lane model beat the global constant.

Therefore:

> Pairing loses essentially no tested outcome information because the six individual lanes carry essentially no
> useful transferable handover information to begin with.

This is a faithful structural compression, not predictive compression of a strong signal.

## Frozen decision

| Prediction | Result |
|---|---|
| P1 — greater closeness means fewer handovers | **FAILED** |
| P2 — greater closeness means more immediate primes | **FAILED** |
| P3 — greater closeness means more three-state closures | **FAILED** |
| P4 — paths move upward toward the ridge | **FAILED** |
| Exact odds-to-ARA conversion | **PASSED** |
| Three-pair versus six-lane fidelity | **PASSED** for both outcomes |

Under the frozen rule: **GEOMETRIC-ONLY SUPPORT / DYNAMIC NULL**.

## ARA interpretation

The correction successfully separates three notions:

1. **Identity completeness:** every A/B pair totals 2.
2. **Lateral composition:** (x=r/7) records the balance and orientation inside the mod-14 rung.
3. **Vertical completion:** later prime gates determine when a surviving candidate releases and hands over.

The earlier confusion arose from treating lateral approach to the local `(7,7)` boundary as vertical approach to
prime completion. PN25 shows they are different coordinates. This is consistent with the wider ARA warning that a
valid diameter reading can still flatten an orthogonal rung relation.

The useful retained object is therefore

\[
\underbrace{(c,s)}_{\substack{\text{pair distance}\text{and orientation}}}
+
\underbrace{V}_{\substack{\text{higher-gate}\text{vertical state}}}
\longrightarrow
\underbrace{\text{handover path}}_{\text{next-prime completion}}.
\]

PN25 identifies the first coordinate exactly and demonstrates that the second cannot be inferred from it on these
targets.

## Claim boundary

PN25 supports an exact ARA reparameterisation and symmetry compression of the mod-14 wheel. It does not support a
new prime predictor, a reduction in factor-gate computation, or the claim that local ridge-closeness is a universal
time-to-handover coordinate.

## Artifacts

- Frozen protocol: `PN25_PAIR_RIDGE_COMPRESSION_PROTOCOL_v1_FROZEN.md`
- Primary script: `pn25_pair_ridge_compression.py`
- Machine results: `PN25_PAIR_RIDGE_COMPRESSION_RESULTS.json`
- Target paths: `PN25_PAIR_RIDGE_COMPRESSION_TARGETS.csv`
- Pair-group summaries: `PN25_PAIR_RIDGE_COMPRESSION_GROUPS.csv`
- Frozen-model scores: `PN25_PAIR_RIDGE_COMPRESSION_SCORES.csv`
- Independent validator: `validate_pn25_pair_ridge_compression.py`
- Validation receipt: `PN25_PAIR_RIDGE_COMPRESSION_VALIDATION.json`
