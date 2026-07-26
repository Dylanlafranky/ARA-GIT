# H1 Fidelity Packet — Public Hydraulic Two-Cut ARA

**Frozen orientation:** accumulator connection pressure, `130 bar → 90 bar`  
**Measured identity:** one complete 60-second hydraulic load cycle  
**Cuts:** synchronized spatial pressure histories `PS1`–`PS6`

## Dylan's framework claim being tested

The preceding Q2 result suggested a boundary: a strongly information/traversal-aligned output may be represented
by one dominant cut, whereas a connection-heavy identity should more often require several cuts to retain its
distributed structure.

For H1, the hydraulic accumulator is treated as the connection/storage identity. The surrounding pressure network
is not flattened into a single global average. Each pressure sensor is one diameter-like line reading through the
same 60-second parent cycle.

## Exact ARA translation used

For pressure sensor `s` in cycle `i`, the raw 60-second trace is divided into twelve fixed five-second windows.
Each window contributes:

- its arithmetic mean: local accumulated pressure level;
- its standard deviation: local release/response movement around that level.

The resulting 24-number vector is one decompressed pressure cut. No Fourier, wavelet, PCA, learned embedding or
source-provided feature is applied before this construction.

Every feature is mapped using outer-training data only:

\[
\underbrace{x_{ij}}_{\substack{\text{ARA coordinate}\\\text{for feature }j}}
=
1+
\underbrace{o_j}_{\substack{\text{training pole}\\\text{orientation}}}
\frac{
\underbrace{f_{ij}-m_j}_{\substack{\text{distance from}\\\text{training centre}}}
}{
\underbrace{s_j}_{\substack{\text{training robust}\\\text{scale}}}
}.
\]

Here `m_j` is the outer-training median, `s_j` is the outer-training interquartile range divided by `1.349`
with a standard-deviation fallback, and `o_j` is the sign of the difference between the outer-training `90 bar`
and `130 bar` class means. Thus `1.0` is the training-centred ridge and direction is fixed from the optimal
accumulator pole toward the near-failure pole.

The map is affine and reversible for every retained feature. Values are allowed outside `0–2`; clipping would
discard overshoot information and is prohibited.

## One cut, two cuts and parent relation

- **One cut:** one selected pressure sensor's 24 ARA coordinates.
- **Two cuts:** the 48 coordinates from two distinct selected pressure sensors.
- **Selection:** best sensor and best pair are selected inside each outer-training fold by nested grouped
  cross-validation only.
- **Parent target:** the four accumulator-pressure states `130`, `115`, `100`, `90 bar`.

The two-cut claim is supported only if the selected pair improves untouched whole-cycle classification over the
best selected single sensor. This does not assert that the classifier itself is new physics.

## Fidelity boundaries

H1 can test:

- whether distributed real pressure cuts retain complementary accumulator-state information;
- whether the 0–2 ARA coordinates preserve the same information as raw standardized pressure features;
- whether pole reversal changes representation without changing classification;
- whether the result survives whole-block holdout and repeated label-permutation controls.

H1 cannot establish:

- universal fractality;
- a universal Space/Time ontology;
- TE-ARA as a physical energy unit;
- phi, hexagon/pentagon leakage or a universal singularity law;
- superiority over all structural-health or predictive-maintenance methods;
- causation beyond the accumulator states imposed by the source experiment.

## Authorial fidelity decision

The test deliberately uses a connection/storage-heavy system after the information-heavy Q2 boundary. The
interpretation is faithful only if the result is reported in two parts:

1. information gain from a second real pressure cut;
2. exactness of the reversible ARA/raw coordinate bridge.

Those conclusions must not be merged.

