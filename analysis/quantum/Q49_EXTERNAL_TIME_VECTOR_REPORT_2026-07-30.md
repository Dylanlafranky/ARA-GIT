# Q49 — External Quantum ARA Time-Vector Test

**Date:** 30 July 2026  
**Ledger:** T309  
**Frozen directional-path verdict:** **NOT SUPPORTED**  
**Frozen ordered-wobble verdict:** **NOT SUPPORTED**  
**Independent validation:** **PASS — 10/10 checks**

## Answer first

Q49 corrected the object measured in the invalid Q48 proxy. It did not measure
how much the quantum circle turns internally. It treated every complete
four-quadrant ARA cycle as one circle, found that circle's centre, and followed
the centre from one complete cycle to the next. This is the external path
carrying the whole rotating circle through time.

The declared directional arc was:

\[
\underbrace{1/e}_{\substack{\text{local heading}\\\text{pole 0}}}
\longrightarrow
\underbrace{\phi-1}_{\substack{\text{full Phi wrapped}\\\text{onto one turn; pole 2}}},
\]

whose width is

\[
(\phi-1)-1/e
=0.250154548
\]

of a full turn, or `90.0556°`. Three equal-width quarter-turn rotations were
the controls.

The pooled result pointed in the proposed direction:

| Matched heading arc | Eligible events | Fraction |
|---|---:|---:|
| **Declared \(1/e\rightarrow\phi\)** | **461** | **35.4615%** |
| \(+1/4\) turn | 169 | 13.0000% |
| Opposite \(+1/2\) turn | 388 | 29.8462% |
| \(-1/4\) turn | 282 | 21.6923% |
| Uniform expectation from arc width | — | 25.0155% |

That pooled enrichment is a genuine descriptive result. It was not stable
enough to pass the frozen claim:

- seed-cluster bootstrap probability that the declared arc beat its strongest
  control was only `0.7412`, below the frozen `0.95` gate;
- the bootstrap difference interval crossed zero:
  `[-0.13111, +0.20054]`;
- only the algebraic circle-centre estimator chose the declared arc at the
  frozen movement floor; centroid and extrema-midpoint estimators chose the
  opposite arc;
- no lineage completed an ordered half-traversal from one declared endpoint
  to the other.

The strongest correct reading is therefore:

> **The intended external whole-circle vector contains a pooled
> \(1/e\rightarrow\phi\)-arc enrichment, but the available simulator
> trajectory does not support one stable universal heading or an ordered
> wobble between those endpoints.**

## Plain-language translation

Imagine drawing one small circle around every complete internal quantum
cycle, then placing a pin at the centre of each circle. Q49 follows the line
made by those pins.

Across the full dataset, that line points into Dylan's proposed
`1/e → Phi` quarter of the direction circle more often than any other
quarter. That is the encouraging part.

However, the direction is not steady. Early in the trajectory it points
mainly into the proposed quarter. Later it points mainly into the quarter
directly opposite. Different trials therefore disagree about which direction
is dominant, and the sequence does not visibly travel all the way from the
`1/e` end to the Phi end. The frozen test consequently fails even though one
part of the proposed geometry is visible.

## Construct fidelity

The measured object was:

\[
\underbrace{\mathbf c_r}_{\substack{\text{centre of one complete}\\
\text{four-quadrant ARA circle}}}
=
\operatorname{CircleCentre}
\left(
\underbrace{u(t),v(t)}_{\substack{\text{state and flow cuts}\\
\text{inside cycle }r}}
\right).
\]

The external tangent at cycle \(r\) was:

\[
\underbrace{\mathbf d_r}_{\substack{\text{whole-circle}\\
\text{external movement}}}
=
\underbrace{\mathbf c_{r+1}}_{\text{next complete circle}}
-
\underbrace{\mathbf c_{r-1}}_{\text{previous complete circle}}.
\]

Its heading was measured as a fraction of one complete turn:

\[
\underbrace{h_r}_{\substack{\text{external heading}\\0\le h_r<1}}
=
\operatorname{frac}
\left[
\frac{\operatorname{atan2}(d_{r,v},d_{r,u})}{2\pi}
\right].
\]

This is not:

- Q47's geodesic rotation of the internal relation lattice;
- Q48's cycle-to-cycle turn amount;
- an average of the four internal quadrant flips;
- a Fourier phase or fitted carrier frequency.

The fidelity packet and protocol were frozen before the circle centres and
external headings were calculated:

- `Q49_EXTERNAL_TIME_VECTOR_FIDELITY_PACKET_v1.md`;
- `Q49_EXTERNAL_TIME_VECTOR_PROTOCOL_v1_FROZEN.md`.

## Source and population

Q49 reused the public `pure_strongmax` deterministic simulator archive from
Zenodo DOI [`10.5281/zenodo.16753415`](https://doi.org/10.5281/zenodo.16753415).
The deposit contains density matrices for changing-connectivity qubit
networks over `500` time steps and `100` trials.

The immutable derived source was:

- shape: `100 × 500 × 66`;
- SHA-256:
  `1253412803b3377c1bc8119fbdda32a5de64fcec432e621bf63dedfe0b10918d`;
- complete fitted circle centres: `34,969`;
- possible external tangent events: `32,420`;
- eligible tangents at the frozen movement floor: `1,300` (`4.0099%`);
- represented seeds in the eligible population: `72`.

The movement floor required the centre displacement to be at least `0.01` of
the mean fitted circle radius. This prevented numerical directions being
assigned to nearly stationary centres.

## Frozen gate table

| Frozen gate | Result | Verdict |
|---|---|---|
| G0 correct external object and coordinate invariances | Translation and rotation checks exact | **PASS** |
| G1 declared arc has greatest occupancy and seed-bootstrap support ≥95% | Pooled winner; bootstrap `74.12%` | **FAIL** |
| G2 repeats in development/evaluation and all centre estimators | Reversed by time stratum and estimator | **FAIL** |
| G3 at least five full ordered endpoint traversals in five lineages, both directions represented | `0` traversals in `0` lineages | **FAIL** |
| G4 ordered traversals exceed shuffled 99th percentile | Observed `0`; shuffled 99th `0` | **FAIL** |

The directional-path and ordered-wobble claims therefore remain
**NOT SUPPORTED** under the frozen rules.

## Why the pooled signal was unstable

### 1. A half-turn reversal separates the two time strata

The frozen split used slices `0–249` for development calibration and
`250–499` for evaluation. At the primary movement floor:

| Stratum | Declared arc | Opposite arc | Winner |
|---|---:|---:|---|
| Development | **39.8601%** | 25.0874% | declared |
| Evaluation | 3.3113% | **63.5762%** | opposite |

This was not peculiar to one centre estimator:

| Centre definition | Development winner | Evaluation winner |
|---|---|---|
| Algebraic circle fit | declared | opposite |
| Point centroid | declared | opposite |
| Extrema midpoint | declared | opposite |

The reversal is therefore present in the derived trajectory rather than
being created solely by the algebraic circle fit.

It was not predeclared as an ARA flip and cannot rescue Q49. It creates a
clean replication hypothesis:

> **A future untouched changing-connectivity trajectory should be given a
> predeclared orientation/parity coordinate. Conditional on that coordinate,
> its whole-circle external vector should occupy either the
> \(1/e\rightarrow\phi\) arc or the exactly half-turn-opposite arc.**

This must be tested on a new archive with the parity rule frozen before the
later trajectory is opened.

### 2. Stronger development movement sharpened the declared direction

Post-result movement-floor sensitivity showed:

| Minimum movement/radius | Declared pooled occupancy | Pooled winner |
|---:|---:|---|
| `0.005` | 33.0332% | opposite |
| `0.010` frozen | 35.4615% | declared |
| `0.020` | 39.2924% | declared |
| `0.050` | 46.5206% | declared |
| `0.100` | 53.2905% | declared |

At `0.05`, all three centre estimators chose the declared arc. This does not
constitute a stronger confirmatory result: nearly all high-movement events
came from the development stratum, while the later reversed events were
weaker. The sensitivity therefore describes the same time-regime split
rather than providing an independent replication.

### 3. Seed concentration reduced effective replication

Although `72` seeds contributed, unequal event counts gave an effective seed
count of only `38.70`. The two largest contributors, seeds `57` and `80`,
supplied `203/1,300` eligible events and strongly preferred the opposite arc.
That concentration explains why the pooled winner did not survive
seed-cluster uncertainty.

### 4. The circle centres were usable but not identical across estimators

Circle-fit quality:

- median relative radial residual: `0.07850`;
- 75th percentile: `0.11154`;
- 95th percentile: `0.18166`.

The circle and extrema-midpoint headings differed by a median `0.02787`
turns; `69.48%` were within `0.05` turns. Circle and centroid headings were
less stable: median difference `0.05895` turns, with `46.78%` within `0.05`
turns. This justifies retaining centre-definition sensitivity as a required
gate.

## The `3/8` triangulation landmark

On the declared heading arc,

\[
\underbrace{x_{3/8}}_{\substack{\text{ARA coordinate}\\
\text{inside the declared arc}}}
=
\frac{2(3/8-1/e)}{(\phi-1)-1/e}
=0.0569293.
\]

So `3/8` lies close to the `1/e` endpoint, not at the middle of this local
ARA diameter.

With equal `±0.01`-turn windows around `3/8` and its three quarter-turn
rotations, event counts were:

\[
(8,\;15,\;6,\;5).
\]

The `3/8` window was not the strongest. Q49 therefore does not support
`3/8` as the triangulation point of this external centreline.

## Scientific boundary

Supported descriptively:

- the correct external whole-circle vector can be constructed;
- its pooled heading is enriched in the declared `1/e → Phi` arc;
- the derived centreline direction undergoes a strong half-turn reversal
  between early and late portions of this simulator trajectory.

Not supported:

- one stable universal `1/e → Phi` time-vector direction;
- an ordered wobble between those endpoints;
- a special `3/8` crossing;
- a demonstrated physical singularity flip;
- a laboratory quantum-hardware effect;
- a universal rule for time.

The reversal is compatible with Dylan's ARA Phase-A/Phase-B or singularity
language, but the current result alone identifies only a reversal in a
derived centreline observable. The source is a deterministic
changing-connectivity simulator, and the cause of the reversal has not been
isolated.

## Independent validation and reproduction

Independent validation recalculated the event population from the saved
centres, checked `1,000` circle fits directly against the immutable source,
reproduced every headline arc count, and reran the seed bootstrap without
importing the primary implementation. All `10/10` checks passed.

Run:

```powershell
$env:PYTHONPATH='F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\.q27_deps'
$env:MPLCONFIGDIR='F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\.mplconfig'
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q49_external_time_vector.py'
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q49_validate_external_time_vector.py'
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum\q49_post_result_regime_diagnostic.py'
```

Artifacts:

- `Q49_EXTERNAL_TIME_VECTOR_RESULTS.json`;
- `Q49_EXTERNAL_TIME_VECTOR_EVENTS.csv.gz`;
- `Q49_EXTERNAL_TIME_VECTOR_CENTRES.csv.gz`;
- `Q49_EXTERNAL_TIME_VECTOR.png`;
- `Q49_EXTERNAL_TIME_VECTOR_REGIME_DIAGNOSTIC.png`;
- `Q49_EXTERNAL_TIME_VECTOR_VALIDATION.json`;
- `q49_external_time_vector.py`;
- `q49_validate_external_time_vector.py`;
- `q49_post_result_regime_diagnostic.py`.

