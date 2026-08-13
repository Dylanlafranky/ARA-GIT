# T368 frozen protocol v1 - muon decay handover information test

**Frozen:** 12 August 2026, after source-schema inspection and before downloading or reading event values  
**Evidence class:** event-level physical data; development/holdout split fixed independently of values  
**Status at freeze:** `EXACT ENOUGH TO TEST`

## Question

Does the duration of a stopped muon's open parent interval contain measurable
information about the daughter electron observed when that interval closes?

In ARA language, the proposed relation is

\[
\text{open parent duration}
\longrightarrow
\text{decay handover}
\longrightarrow
\text{daughter state}.
\]

The decisive distinction is between:

1. **pre-handover imprint:** the parent waiting coordinate predicts some part
   of the daughter's observable state; and
2. **closure only at/beyond the handover:** the waiting coordinate and daughter
   state are independent even though both have organised population-level
   distributions.

This is not a test for a visible microscopic ramp immediately before one
decay. The source does not continuously measure an individual muon between its
stop and its decay.

## WHO

The source is the Super-Kamiokande Collaboration data release
`10.5281/zenodo.15081911`, containing one row for each of 1,986,465 stopped
cosmic-ray muons observed during SK-VI (2020-2022).

Each row contains:

- tagged decay-electron momentum in MeV (`0` when absent);
- tagged decay-electron time after the stopping muon in microseconds (`0` when
  absent);
- zero or more tagged neutron detection times after the stopping muon.

The **primary population** is high-energy tagged decay-electron events:

\[
p_e>15\ \mathrm{MeV},\qquad 1.1\leq t_e\leq5.0\ \mu\mathrm{s}.
\]

The momentum threshold follows the source paper's boundary separating decay
electrons from lower-energy de-excitation gamma candidates. The time window is
the paper's published usable electron/gamma interval; the lower boundary
avoids detector dead time and the upper boundary limits flat accidental
background.

Neutron-bearing capture candidates are retained for descriptive post-handover
QA only. They are not treated as daughters of the same electron decay.

## DATA SPLIT

Before any values are inspected, assign every one-based source row to a split
by the first eight bytes of

```text
SHA256("T368|<row number>")
```

interpreted as an unsigned integer modulo 10:

- residues `0`-`5`: development (60% expected);
- residues `6`-`9`: untouched holdout (40% expected).

The split is deterministic, value-independent and reproducible. Development
defines all empirical coordinate maps and bin edges. Holdout values cannot
alter the frozen instrument or gates.

## NATIVE ARA COORDINATES

### Parent waiting coordinate

Let `F_T` be the development empirical CDF of eligible decay times. For each
event,

\[
x_P=2F_T(t_e),\qquad 0\leq x_P\leq2.
\]

This is the released-versus-still-surviving ensemble coordinate. It does not
claim that clock time itself is an intrinsic 0-2 diameter. The ridge `x_P=1`
is the empirical half-released/half-surviving point of this declared
population.

### Daughter coordinate

Let `F_E` be the development empirical CDF of eligible electron momentum. For
each event,

\[
x_D=2F_E(p_e),\qquad 0\leq x_D\leq2.
\]

This preserves raw rank information without forcing an unobserved neutrino
energy budget into the coordinate. It is an observable daughter coordinate,
not a complete TE-ARA decomposition of all decay products.

### Irrationality Di-ARA cut

The joint cut is `(x_P,x_D)`. Its four coarse quadrants are the combinations
of each coordinate lying below or above its ridge. Finer structure uses eight
fixed equal-width bins on each 0-2 axis.

If longer open-parent duration progressively determines the daughter, then
the conditional daughter distribution should narrow and become more
predictable as `x_P` advances. If daughter closure is created only at the
handover, `x_D` should remain independent of `x_P`.

## PRIMARY MEASUREMENTS

All primary values are calculated on holdout only after the development maps
are frozen.

1. **Predictive information:** eight-bin daughter cross-entropy from the
   development `P(x_D-bin | x_P-bin)` table, compared with the development
   unconditional daughter distribution. Laplace pseudocount `1` is fixed.
2. **Conditional entropy:** Shannon entropy of the eight daughter bins within
   each of eight parent bins.
3. **Late-versus-early narrowing:** relative entropy change between the final
   and first parent quartiles.
4. **Quadrant dependence:** Cramer's V for the 2x2 ridge-quadrant table.
5. **Continuous dependence:** Spearman correlation between `x_P` and `x_D`.
6. **Shape audit:** empirical survival/release curve and binned empirical
   hazard, compared descriptively with the source paper's known
   positive/negative-muon exponential mixture. This is a baseline, not an ARA
   success criterion.

## CONTROLS

1. **Mismatched daughters:** circularly shift daughter momenta within holdout
   by `floor(N/3)+17` rows.
2. **Permutation null:** 1,000 fixed-seed (`368`) permutations of daughter-bin
   labels relative to parent bins.
3. **Reversed parent direction:** replace `x_P` by `2-x_P`; this tests the
   claimed direction but is not an independence control.
4. **Inner detector window:** repeat on `20<p_e<50 MeV` and
   `1.3<t_e<4.5 microseconds`.
5. **Independent hash halves:** repeat the holdout calculation separately for
   even and odd SHA256-derived 64-bit hashes.
6. **Smooth time baseline:** development-only multinomial logistic regression
   of daughter bin on raw `t_e`, evaluated on holdout. This asks whether the
   coarse ARA relation adds predictive value beyond a generic smooth trend.

## UNCERTAINTY

- Use a deterministic 1,000-replicate row bootstrap (`seed=368`) for primary
  effect intervals.
- Because the archive is very large, statistical significance alone is not a
  gate. Minimum effect sizes are frozen below.
- Report missing, zero, non-finite and out-of-window rows before filtering.

## FROZEN GATES

1. **Source and implementation QA:** DOI, file MD5 and SHA256 are recorded;
   parsed row count agrees with the release; all coordinates use development
   maps only.
2. **Coverage:** at least 100,000 eligible holdout electron-decay events.
3. **Predictive imprint:** the ARA conditional table improves holdout
   cross-entropy over the unconditional model by at least 1%, with a bootstrap
   95% interval above zero.
4. **Not a shuffled relation:** no more than 10 of 1,000 permutation effects
   equal or exceed the observed improvement.
5. **Progressive determination:** final-parent-quartile daughter entropy is at
   least 5% below first-parent-quartile entropy, with a bootstrap 95% interval
   below zero.
6. **Nontrivial quadrant effect:** holdout Cramer's V is at least 0.05.
7. **Robustness:** Gates 3 and 5 retain direction in the inner detector window
   and both independent hash halves.
8. **Added relational value:** the ARA conditional table is no worse than the
   smooth raw-time baseline in holdout cross-entropy.

`OBSERVABLE PRE-HANDOVER IMPRINT SUPPORTED IN THIS RECORD` requires Gates 1-8.

If dependence exists without progressive narrowing, the verdict is
`PARENT-DAUGHTER DEPENDENCE WITHOUT PREFORMATION SUPPORT`.

If the primary effects are absent, the verdict is
`NO OBSERVABLE PREFORMATION IN THE RELEASED VARIABLES`.

## REQUIRED OUTPUTS

- source and population QA;
- development maps and frozen bin edges;
- parent/daughter quadrant and 8x8 mixing heatmaps;
- daughter entropy and momentum distribution across parent phase;
- survival/release and empirical hazard panels;
- mismatch, permutation, inner-window and hash-half controls;
- machine-readable results, event-level derived coordinates, report,
  executable notebook and independent validation record.

## SCIENTIFIC BOUNDARY

The record begins when a muon stops and next records a tagged decay electron;
it contains no continuous internal muon measurement during the waiting
interval. A null result therefore means that **waiting duration does not carry
detectable information about the released electron momentum under this
instrument**. It cannot prove that no unmeasured internal pre-decay geometry
exists.

The two neutrinos are unobserved, electron direction is absent, muon charge is
not labelled per event, detector efficiency is time- and energy-dependent, and
the source mixes positive-muon decay, negative-muon decay and negative-muon
nuclear capture. No result may be described as a complete decay TE-ARA or as a
test of all daughter information.
