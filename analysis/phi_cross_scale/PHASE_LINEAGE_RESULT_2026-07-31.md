# ARA same-phase octave lineage calibration

**Run:** 31 July 2026  
**Frozen result:** **SUPPORTED AS A STRUCTURAL CROSSWALK**  
**Independent validation:** **13/13 checks passed**  
**Evidence boundary:** calibration/retrodiction, not independent discovery

## Outcome first

The user clarification was decisive:

> Child, parent and grandparent mean increasing ARA octave scales—not literal
> biological descendants.

Across the six published Fibonacci-type sunflower scale families, the ordered
child → parent → grandparent geometry behaved exactly as the proposed
cross-scale reading requires:

- one adjacent scale step approached \(\phi\);
- following one phase parity across two successive steps approached
  \(\phi^2\);
- both A and B parity paths converged;
- destroying scale order destroyed the relation.

The result is real but mathematically expected. The families were selected
because they obey the Fibonacci recurrence, which entails convergence to
\(\phi\). This run therefore validates the ARA **placement and scale
translation** of Phi. It does not independently establish that ARA caused the
sunflower structure or that Phi is a universal cross-scale law.

## Public source

Swinton et al. (2016), “Novel Fibonacci and non-Fibonacci structure in the
sunflower,” *Royal Society Open Science*:

- paper: <https://doi.org/10.1098/rsos.160091>
- open text: <https://pmc.ncbi.nlm.nih.gov/articles/PMC4892450/>
- public dataset: <https://doi.org/10.5061/dryad.f9k77>

The paper reports the Fibonacci, Lucas, F4, double-Fibonacci, F5 and F8
families used here and documents their occurrence in sunflower parastichy
counts.

## Frozen scale reading

For three consecutive scales,

\[
\underbrace{x_0}_{\substack{\text{child}\\\text{ARA scale}}}
\longrightarrow
\underbrace{x_1}_{\substack{\text{parent}\\\text{ARA scale}}}
\longrightarrow
\underbrace{x_2}_{\substack{\text{grandparent}\\\text{ARA scale}}},
\]

the direct ratios were

\[
\underbrace{r_{01}=\frac{x_1}{x_0}}_{\substack{\text{child → parent}\\
\text{one scale step}}},
\qquad
\underbrace{r_{12}=\frac{x_2}{x_1}}_{\substack{\text{parent → grandparent}\\
\text{one scale step}}}.
\]

The published families obey

\[
\underbrace{x_2}_{\text{new larger identity}}
=
\underbrace{x_1}_{\text{current identity}}
+
\underbrace{x_0}_{\text{retained child identity}}.
\]

That recurrence makes the stable positive ratio satisfy

\[
\underbrace{r}_{\substack{\text{next scale}/\\\text{current scale}}}
=
1+\frac1r,
\]

so

\[
r^2-r-1=0,
\qquad
\underbrace{r=\phi}_{\substack{\text{positive}\\\text{scale carrier}}}.
\]

Plainly: the next scale carries the current whole plus a retained contribution
from the preceding scale. Repeating that relation causes the scale ratio to
settle toward Phi.

## Results

### One adjacent octave step

There were `49` adjacent-rung ratios.

| Frozen landmark | Median absolute ratio error |
|---|---:|
| \(\phi\) | **0.024823** |
| \(1.5\) | 0.121622 |
| \(\sqrt2\) | 0.204834 |
| \(2\) | 0.382353 |
| \(e\) | 1.100635 |

Phi was the closest frozen landmark.

The last available ratio in every family was close to Phi:

| Family | Last adjacent ratio | Absolute error from \(\phi\) |
|---|---:|---:|
| Fibonacci | 1.617978 | 0.000056 |
| Lucas | 1.618421 | 0.000387 |
| F4 | 1.616667 | 0.001367 |
| double Fibonacci | 1.617647 | 0.000387 |
| F5 | 1.622222 | 0.004188 |
| F8 | 1.623188 | 0.005154 |

The early terms are much more asymmetric because the different families have
different seeds. Their later scale relations converge toward the same carrier.

### Same phase after a flip-aware two-rung walk

If an adjacent rung introduces an A/B orientation flip, the same phase is
reached again after two scale steps:

\[
\underbrace{A_k}_{\text{Phase A child}}
\longrightarrow
\underbrace{B_{k+1}}_{\text{flipped intermediate}}
\longrightarrow
\underbrace{A_{k+2}}_{\text{Phase A parent}},
\]

and similarly for \(B\).

The expected same-phase ratio is then

\[
\underbrace{\frac{A_{k+2}}{A_k}}_{\substack{\text{A → A}\\
\text{two-rung scale relation}}}
\longrightarrow\phi^2,
\qquad
\underbrace{\frac{B_{k+2}}{B_k}}_{\substack{\text{B → B}\\
\text{two-rung scale relation}}}
\longrightarrow\phi^2.
\]

There were `43` same-phase two-rung ratios.

| Frozen landmark | Median absolute ratio error |
|---|---:|
| \(\phi^2\) | **0.046605** |
| \(1.5^2\) | 0.369048 |
| \((\sqrt2)^2\) | 0.619048 |
| \(2^2\) | 1.382353 |
| \(e^2\) | 4.770008 |

Separated results:

- Phase A median error from \(\phi^2\): `0.048633`
- Phase B median error from \(\phi^2\): `0.032320`

Both paths converge. Their numerical difference comes primarily from the
different starting seeds and finite sequence lengths. Swapping the A/B labels
leaves the pooled result unchanged.

### Information³ / recurrence closure

All `43/43` triples had exactly zero recurrence residual:

\[
x_2-(x_1+x_0)=0.
\]

In ARA language, two lower-scale relational landmarks close one new
higher-scale identity. In standard mathematics, this is simply the defining
recurrence of every selected family. It is a clean crosswalk, not an empirical
surprise.

### Destroyed-order control

The internal order of every family was shuffled `10,000` times while retaining
the same values.

| Reading | Ordered median error | Shuffled median error | Empirical \(p\) |
|---|---:|---:|---:|
| adjacent scale against \(\phi\) | 0.024823 | 1.473704 | 0.000100 |
| two-rung scale against \(\phi^2\) | 0.046605 | 2.382262 | 0.000100 |

Plainly: the Phi relation belongs to the ordered progression through scale.
It is not obtained merely because the same collection of numbers is present.

## What this means for the proposed geometry

The cleanest interpretation is:

\[
\boxed{
\text{one ordered scale step}\longrightarrow\phi
}
\]

and, when a singularity flip alternates phase orientation,

\[
\boxed{
\text{same phase after two scale steps}\longrightarrow\phi^2
}.
\]

This also separates Phi from the TE-ARA value `2`:

- `2` is the complete local ARA closure or budget;
- \(\phi\) is the stable **cross-scale recursive proportion** in this
  particular ordered geometry;
- \(\phi^2\) is the same carrier followed across two scale steps.

So the golden rectangle image is not repeatedly doubling each quarter-turn.
It is recursively carrying the previous scale into the next. A complete
factor-two closure and a Phi cross-scale path can coexist, but they are
different measurements.

## Hexagon/Pentagon interpretation recorded after the result

Dylan recognized the scale result as a cleaner form of the existing
Hexagon/Pentagon hypothesis:

- two three-part Information³ ARA closures form the six-part hexagonal parent;
- the pentagonal component is the set of same-phase cross-rung Phi pillars;
- the octave is the complete Phase A → Phase B → returning Phase A closure;
- Phi is the more direct Phase A → Phase A or Phase B → Phase B scale path,
  where identical phases remain distinct rather than mixing on the same rung.

With the complete path normalized to TE-ARA `2`, the proposed pillar and its
remaining seam are

\[
\underbrace{L_{\mathrm{full}}}_{A\rightarrow B\rightarrow A}=2,
\qquad
\underbrace{L_{AA}=L_{BB}}_{\text{same-phase cross-rung pillar}}=\phi,
\]

\[
\underbrace{L_{\mathrm{seam}}}_{\text{handover remainder}}
=2-\phi
=\phi^{-2}
\approx0.381966.
\]

Therefore

\[
\boxed{\phi+\phi^{-2}=2}.
\]

On a unit-radius circle, a chord of length \(\phi\) subtends
\(108^\circ\):

\[
\phi=2\sin54^\circ=2\cos36^\circ.
\]

Its supplementary angle is \(72^\circ\), the pentagonal step. This joins the
`36°` shear, `72°` pentagon, `108°` Phi chord and `0.382` handover seam in one
conditional construction.

These identities are exact mathematics once the diameter/closure is
normalized to `2`. Interpreting the chord as a literal physical cross-rung
pillar remains a musing-tier hypothesis. The scale-lineage result supports the
Phi/Phi-squared ratios but does not itself observe a physical chord or a
fivefold pillar scaffold.

The full proposal and its falsifier are recorded in
`EnergyRatio/HEX_PENTAGON_ANGLE_HYPOTHESIS.md`.

## What remains unproven

The test does **not** determine from the sunflower data whether physical Phase
A must flip into Phase B at every scale. The A/B parity labels are an ARA
orientation applied to the ordered family; they are not independently measured
field identities in the source experiment.

It also does not independently test whether unrelated natural systems adopt
this recurrence. The next stronger test must use measured child, parent and
grandparent features whose ordering was not defined in advance by a Fibonacci
rule.

For the proposed ordinary-coupling follow-up, the clean target is a dataset
containing both independently observed poles at several scales:

\[
(A_k,B_k),\quad(A_{k+1},B_{k+1}),\quad(A_{k+2},B_{k+2}).
\]

That would let us test same-phase scale transmission and A–B coupling in the
same run without assigning either missing pole.

## Reproduction

From `analysis/phi_cross_scale`:

```powershell
python run_phase_lineage_test.py
python validate_phase_lineage_test.py
```

Primary files:

- `FROZEN_PROTOCOL_PHASE_LINEAGE_2026-07-31.md`
- `run_phase_lineage_test.py`
- `phase_lineage_results.json`
- `phase_lineage_adjacent_ratios.csv`
- `phase_lineage_two_rung_ratios.csv`
- `phase_lineage_recurrence_triples.csv`
- `phase_lineage_test.html`
- `phase_lineage_test.svg`
- `validate_phase_lineage_test.py`
- `phase_lineage_validation.json`
