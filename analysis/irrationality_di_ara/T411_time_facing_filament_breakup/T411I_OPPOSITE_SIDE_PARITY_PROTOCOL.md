# T411I — opposite-side rung-parity diagnostic

## Question

Are S1 and S2 unusual because their grandchild coordinate is coupled to the
opposite side of the parent ARA ridge?

## Frozen ARA translation

T411H supplies centered coordinates

\[
v=x_P-1,\qquad u=x_C-1,\qquad w=x_G-1.
\]

Opposite-side coupling means negative orientation around the ridge:

\[
v\,w<0
\quad\text{or, equivalently,}\quad
x_G\mapsto 2-x_G.
\]

The direct child is tested in parallel with `v u`; this distinguishes a
grandchild inversion from the ordinary rung-to-rung singularity flip.

## Outcome protection

Orientation is measured only on the quiet incoming trajectory. Two causal
guards are reported:

- `lead > 1 × child horizon`;
- `lead > 2 × child horizon`.

The decay/handover window is therefore excluded and cannot select which
coordinate is flipped.

## Unit of analysis

Each filament identity contributes one event-balanced orientation estimate.
The primary measures are:

- cosine alignment of centered ARA position;
- the fraction of snapshots occupying opposite sides of the 1.0 ridge;
- cosine alignment of ARA movement as a secondary check.

Fluid summaries use event medians and event-bootstrap 95% intervals. The
S1/S2 grouping is compared with S3/S4, but fluid and archive partition remain
confounded and are not treated as independent randomized groups.

## Interpretation rule

- negative parent–grandchild alignment and opposite-side occupancy above 0.5
  support the proposed grandchild inversion;
- negative parent–child alignment with positive parent–grandchild alignment
  instead supports one alternating rung flip:

\[
P\;\longrightarrow\;-C\;\longrightarrow\;+G.
\]

No predictive model or outcome label is used in this diagnostic.

