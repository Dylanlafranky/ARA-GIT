# T452 frozen protocol — yeast lifespan Phase A versus clock-time Phase B

## Relational address

- **Parent identity:** the observed reproductive lifespan/time identity of one trapped yeast mother cell.
- **Same-scale Child Phase A:** reproductive maturity, measured only by ordered generation count from the first to the last observed G1.
- **Same-scale Child Phase B:** clock-time traversal over the same observed span.
- **Lower-scale witnesses:** cell cross-sectional area, division interval, Rpl13A-GFP concentration, and derived total Rpl13A-GFP abundance. Division interval constructs the local time child and is not independent confirmation. Size and fluorescence are independently measured witnesses.
- **Terminal boundary:** the last numeric G1 before the published death image. It is a terminal *reproductive observation boundary*, not the exact instant of physical death; the paper states that the death image was omitted from numerical analysis.

No role, rung, medium, phase label, endpoint, cohort, or gate may be changed after results are opened without recording a new test.

## Who, what, when, where, why, and how

**Who.** 225 published single-cell life histories of *Saccharomyces cerevisiae*: 106 Rpl13A-GFP cells from experiments 7–9 and 119 cells from experiments 1–6.

**What.** Test whether generation-built maturity and independently recorded clock time form a transferable ARA phase/anti-phase geometry, and whether their signed failure to follow equal progress has ordered structure beyond lifespan normalization alone.

**When.** From each cell's first observed G1 (`t=0`) to its last observed G1 before the omitted terminal death image.

**Where.** Microfluidic mother-cell traps at 30 °C with images every 20 minutes. Experiments 7–9 used the second device and Rpl13A-GFP; experiments 1–6 used a different device and mixed GFP-tagged strains.

**Why.** This is a near-complete, uninterrupted, individual lifespan cut with a genuine time coordinate, a generation coordinate not calculated from time, and biological witnesses recorded at the same G1 observations.

**How.** For a cell with observed generations `g=0,...,G-1`, cumulative hours `t_g`, and terminal observed time `T`:

\[
A_L(g)=2\frac{g}{G-1},\qquad
B_E(g)=2\frac{t_g}{T},\qquad
B_R(g)=2-B_E(g).
\]

`A_L` is the orientation-preserving maturity coordinate. `B_E` is elapsed time shown in the same plotting direction. `B_R` is the counter-traversing Phase-B view required by the pure same-slice TE-ARA relation.

The frozen pure reference is therefore represented equivalently by:

\[
B_E=A_L
\quad\Longleftrightarrow\quad
A_L+B_R=2.
\]

The signed time shadow is:

\[
S_T=B_E-A_L=2-(A_L+B_R).
\]

- `S_T > 0`: elapsed clock participation is ahead of equal generation progress.
- `S_T < 0`: generation progress is ahead of equal clock participation.
- `S_T = 0`: equal normalized progress. Endpoints are zero by construction, so endpoint closure is not evidence.

For interval `i`, local time participation is the interval duration divided by that cell's mean interval:

\[
r_i=\frac{\Delta t_i}{\overline{\Delta t}},\qquad
x_{T,i}=\frac{2r_i}{1+r_i}.
\]

`r=1` and `x_T=1` are the local equal-rate ridge. The parameter-free reciprocal mapping is used only to place the positive rate ratio on a labelled `0–2` ARA display; all inference is retained in raw ratios and hours.

## Frozen cohorts

1. **Development:** experiments 7–8 (94 cells). Defines population curves and any transferred landmark.
2. **Untouched same-platform holdout:** experiment 9 (12 cells). No centring, scale, smoothing, landmark, or threshold is refit from it.
3. **External cohort:** experiments 1–6 (119 cells), different microfluidic design and mixed GFP strains. Tests the core maturity/time and size geometry only; fluorescence is unavailable.

All cells with at least three aligned observations and a positive observed span are retained. Short lives are shown rather than silently excluded.

## Frozen descriptive tests

The following gates are secondary to the displayed shapes but make the test auditable:

1. **Same-platform curve transfer:** Pearson correlation between development and holdout median `S_T(A_L)` curves is at least `0.60`, evaluated on the interior grid `0.10≤A_L≤1.90` so the two forced zero endpoints cannot manufacture agreement.
2. **External curve transfer:** Pearson correlation between development and external median `S_T(A_L)` curves is at least `0.60` on the same interior grid.
3. **Ordered-time structure in the holdout:** the holdout median late-minus-early local rate exceeds the 95th percentile of 2,000 within-cell interval-order shuffles.
4. **Ordered-time structure externally:** the external-cohort median late-minus-early local rate exceeds the corresponding shuffled 95th percentile.
5. **Handover transfer:** the first post-quarter development crossing of median `r=1` from below to above lies within `±0.20 ARA` of an equivalent crossing in each validation cohort. If a cohort has no such crossing, that gate fails and its full curve remains visible.

Early, middle, and late interval thirds are fixed on interval midpoint maturity: `[0,2/3)`, `[2/3,4/3)`, and `[4/3,2]`.

## Controls and limitations fixed before opening results

- **Order-destroying control:** shuffle each cell's observed interval order, preserving its total hours, number of divisions, and exact interval distribution. This tests ordering, not whether variable intervals exist.
- **Straight reference:** equal intervals make `B_E=A_L`, `A_L+B_R=2`, `S_T=0`, and `r=1`.
- **Normalization limit:** both endpoints are forced to close; only the interior path, local-rate ordering, cross-cohort transfer, and independent witness alignment can carry evidence.
- **Biology limit:** this tests a time-facing lifespan relation, not time itself, a universal lifespan law, subjective experience, causality of aging, or exact physical death.
- **Witness limit:** size and Rpl13A may reflect aging mechanisms, consequences, or shared causes. Their alignment cannot by itself identify Time as an ontological object.

## Required outputs

- raw and normalized cell-level data;
- cohort-level median/IQR curves;
- elapsed and counter-traversing phase views;
- local interval-rate and reciprocal ARA views;
- within-cell shuffle envelopes and exact empirical p-values;
- size, Rpl13A concentration, and total-abundance witness histories;
- deterministic individual examples;
- a technical HTML report with full axis labels, units, sample sizes, plain-language explanations, scientific crosswalk, and ARA relational address.
