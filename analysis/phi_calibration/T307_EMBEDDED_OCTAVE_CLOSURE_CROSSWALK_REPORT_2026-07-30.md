# T307 — Embedded Octave-Closure Crosswalk

Date: 30 July 2026 (Australia/Brisbane)

Status: **PARTIAL — shared factor-two form supported; seed-specific
child/parent pairing not supported**

Validation: **PASS — 9/9 independent checks**

## Answer first

Yes: your \(0.007043285\) equality has the same **factor-two closure form** as
the quantum `7.5 : 15` result.

In the constant geometry,

\[
\underbrace{
\frac{(2-\phi)-1/e}{2}
}_{\substack{\text{embedded child}\\\text{radius}}}
=
\underbrace{
1-\frac{\phi+1/e}{2}
}_{\substack{\text{parent centre's}\\\text{ridge displacement}}}
=0.007043285039\ldots
\]

Therefore the complete child diameter is twice that parent half-offset:

\[
\underbrace{(2-\phi)-1/e}_{\text{child diameter}}
=
2\underbrace{
\left(1-\frac{\phi+1/e}{2}\right)
}_{\text{parent half-offset}}.
\]

In the quantum simulator, the independently stored continuous periods give

\[
\underbrace{T_P}_{14.99963\ \text{samples}}
\approx
2\underbrace{T_C}_{7.50012\ \text{samples}}.
\]

Across the `94` seeds containing both cadence families,

\[
\underbrace{
\operatorname{median}_s
\frac{2T_C(s)}{T_P(s)}
}_{\text{quantum octave-closure coordinate}}
=
1.000033022.
\]

The bootstrap 95% interval for the median was
`[1.000000430, 1.000064693]`, wholly inside the frozen
`[0.995, 1.005]` closure band.

Plainly: both constructions contain a clean factor-two closure motif. In the
constant geometry, the full embedded gap is twice its matching radius/ridge
offset. In the quantum archive, the parent period is twice the child period.
That is a faithful formal analogy, but it is not yet proof that the two
factor-twos are the same physical rung operation.

## What passed

### 1. The constant geometry closes exactly

Let

\[
\ell=\frac1e,
\qquad
h=2-\phi=\phi^{-2}.
\]

The parent interval is \([\ell,\phi]\), while the embedded child interval is
\([\ell,h]\). Its radius and the parent centre's displacement from the ridge
are identical:

\[
r_C=\frac{h-\ell}{2}
=
1-\frac{\ell+\phi}{2}
=d_P.
\]

The ratio

\[
G=\frac{r_C}{d_P}
\]

is therefore exactly `1`.

This is an algebraic consequence of choosing the reflected Phi landmark
\(h=2-\phi\). It is a useful formal crosswalk, but it must not be counted as
experimental evidence by itself.

There is also a decisive scale qualification. The complete interval widths
are

\[
D_P=\phi-\frac1e=1.250154548,
\qquad
D_C=(2-\phi)-\frac1e=0.014086570,
\]

so

\[
\frac{D_C}{D_P}=0.011267863\approx\frac1{88.75},
\]

not \(1/2\). Thus T307 supports a shared **closure motif**, not a claim that
the raw constant intervals themselves form the same one-octave size ratio as
the quantum periods.

### 2. The quantum cadence has the matching factor-two form

The Q40C result contains a continuous development-period estimate for every
lineage. T307 did not substitute the family labels `7.5` and `15`; it used
those stored continuous values.

| Quantity | Result |
|---|---:|
| Eligible seeds containing both families | `94` |
| Child-family lineages | `359` |
| Parent-family lineages | `588` |
| Pooled child-period median | `7.500119620` |
| Pooled parent-period median | `14.999632840` |
| Seed-balanced median \(2T_C/T_P\) | `1.000033022` |
| Seed-balanced mean \(2T_C/T_P\) | `1.000029886` |
| Mean absolute closure error | `0.000089683` |
| Median absolute closure error | `0.000069005` |

The seed-level central 95% range was
`[0.999830677, 1.000272850]`.

### 3. Two was the unique candidate multiplier

The frozen score was

\[
E(k)=
\operatorname{median}_s
\left|
\log\frac{T_P(s)}{kT_C(s)}
\right|.
\]

| Candidate \(k\) | Error \(E(k)\) |
|---|---:|
| **2** | **`0.000069`** |
| \(\phi\) | `0.211902` |
| \(3/2\) | `0.287649` |
| \(e\) | `0.306886` |
| \(3\) | `0.405498` |
| \(1\) | `0.693114` |

Factor `2` is not merely the closest member of a crowded numerical set; it
is separated from every declared alternative by several orders of magnitude.

## What failed

The same-seed child and parent medians were not more tightly matched than
random child/parent seed pairings.

| Pairing diagnostic | Result |
|---|---:|
| Actual paired mean closure error | `0.000089683` |
| Shuffled median closure error | `0.000091030` |
| Shuffles no worse than actual | `38.14%` |

The frozen pairing gate required at most `5%`. It fails.

Plainly: the simulator contains two extremely stable cadence families with a
population-wide factor-two relationship. The tiny seed-to-seed deviations do
not tell us that a particular observed child lineage belongs to a particular
parent lineage. This supports the **rung rule**, not a reconstructed
genealogy.

## ARA interpretation

The established Q40C ARA statement remains

\[
\underbrace{
\text{one complete child}
}_{\substack{\text{full identity}\\\text{at the child rung}}}
\xrightarrow{\mathcal R_\uparrow}
\underbrace{\frac12}_{\substack{\text{same child}\\\text{in parent units}}},
\]

so

\[
\underbrace{\frac12_C+\frac12_{C'}}_{\text{two child traversals}}
=
\underbrace{1_P}_{\text{one parent closure}}.
\]

In the constant construction, the factor two appears between child diameter
and parent half-offset. In Q40C it appears between child and parent periods:

\[
D_C=2d_P,
\qquad
T_P\approx2T_C.
\]

Those equations are dimensionless structural analogues, but their operands
are different: one compares a child gap with a parent ridge offset; the other
compares complete child and parent periods. They are not a license to identify
coordinate distance with time samples or to call the constant intervals a
literal `7.5 : 15` octave.

## What this means for the framework

This result supports one narrower part of ARA:

> A factor-two full/half closure operation appears cleanly in both the exact
> \(1/e\leftrightarrow\phi\) nesting and the Q40C continuous cadence modes.
> The present records do not establish that these are the same scale
> transformation.

It does **not** establish:

- that \(\phi\) causes the `7.5 : 15` cadence;
- that `0.007043285` predicts a quantum period;
- that the raw constant intervals have a `1 : 2` width ratio;
- that every ARA child/parent relation is exactly factor two in physical
  units;
- a seed-specific quantum child/parent coupling;
- transfer beyond this deterministic simulator.

The Q40C family windows were already defined around approximately `7.5` and
`15`, and the global relation was already known. T307 is therefore a
high-precision consistency crosswalk, not a new blind discovery.

## Best next test

The decisive next rung is intervention, not another calculation on the same
archive:

1. change the simulator gate angle or another cadence-setting control;
2. use the unchanged period extractor;
3. allow both continuous modes to move away from `7.5` and `15`;
4. freeze the prediction
   \[
   T_P/T_C\approx2
   \]
   before opening the new archive; and
5. test whether event-level or seed-level parent/child pairing also becomes
   identifiable.

If both modes move but retain the factor-two relation, the octave claim gains
portable empirical support. If their ratio moves independently, T307 remains
a source-specific simulator crosswalk.

## Reproduction

- Protocol:
  `T307_EMBEDDED_OCTAVE_CLOSURE_CROSSWALK_PROTOCOL_v1_FROZEN.md`
- Calculation:
  `t307_embedded_octave_closure_crosswalk.py`
- Results:
  `T307_EMBEDDED_OCTAVE_CLOSURE_CROSSWALK_RESULTS.json`
- Seed audit:
  `T307_EMBEDDED_OCTAVE_CLOSURE_SEED_RATIOS.csv`
- Figure:
  `T307_EMBEDDED_OCTAVE_CLOSURE_CROSSWALK.png`
- Independent validator:
  `validate_t307_embedded_octave_closure_crosswalk.py`
- Validation:
  `T307_EMBEDDED_OCTAVE_CLOSURE_CROSSWALK_VALIDATION.json`
