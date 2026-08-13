# T369 frozen protocol v1 - muon-capture daughter closure

**Frozen:** 12 August 2026, after T368 and source-paper/schema inspection but
before calculating prompt/delayed daughter relationships  
**Evidence class:** event-level physical recovery test with an untouched
value-independent holdout  
**Status at freeze:** `EXACT ENOUGH TO TEST`

## Question

When a stopped negative muon is captured by an oxygen nucleus, does the prompt
low-energy daughter signal retain measurable information about the delayed
neutron branch from the same handover?

In ARA language:

\[
\text{stopped-muon parent}
\longrightarrow
\text{capture handover}
\longrightarrow
\begin{cases}
\text{prompt gamma-like child},\\
\text{neutron child detected later}.
\end{cases}
\]

This goes one rung deeper than T368. T368 asked whether the open parent's
waiting duration predicted a later electron. T369 asks whether two observable
children of a muon-capture handover retain their common relation.

## WHO

The same checksum-locked Super-Kamiokande release used by T368:
`10.5281/zenodo.15081911`, one row per stopped cosmic-ray muon.

The paper reports that de-excitation gamma signals are reconstructed in the
same prompt channel as decay electrons, and uses a high-energy gamma signature
as a predominantly single-neutron reference. It also states that removing
prompt signals above 15 MeV yields a capture-enriched sample with 99.88%
simulated selection efficiency for capture events.

## WHAT

### Capture-enriched population

Use every finite row with prompt momentum `p <= 15 MeV`. This includes rows
without a prompt tag (`p=t=0`) because absence is part of the released child
record.

### Prompt child

Define:

- `prompt_present = 1` when `0 < p <= 15 MeV` and `1.1 <= t <= 5 microseconds`;
- `prompt_present = 0` otherwise.

Within prompt-present rows, development ECDFs map prompt time and momentum to
native 0-2 coordinates `x_GT` and `x_GE`.

### Delayed neutron child

For each row, retain all positive neutron-tag times in columns three onward.
Define:

- observed neutron multiplicity `m_N in {0,1,2+}`;
- `neutron_present = 1[m_N > 0]`;
- within neutron-present rows, first-neutron detection time mapped through the
  development ECDF to `x_N in [0,2]`.

Neutron detection time is a delayed detector/capture coordinate, not the time
of neutron emission at the muon handover.

## SPLIT

Before relationship values are calculated, assign source rows by

```text
SHA256("T369|<one-based row number>")
```

using the first eight bytes modulo ten:

- residues `0`-`5`: development;
- residues `6`-`9`: untouched holdout.

## PRIMARY PREDICTIONS

### P1 - common-parent information

The prompt child predicts the delayed neutron child on untouched rows:

1. development conditional tables improve holdout cross-entropy for
   `neutron_present` and `m_N` relative to unconditional development
   distributions;
2. prompt-present rows are enriched for neutron tags relative to prompt-absent
   capture-enriched rows;
3. same-row performance exceeds mismatched-child and permutation controls.

This is primarily a known-science recovery because the source experiment uses
prompt gamma candidates as a neutron reference.

### P2 - continuous ARA value

Among prompt-present rows, the **primary continuous instrument** is the frozen
8x8 `(x_GT,x_GE)` Di-ARA address. Separate eight-bin `x_GT` and `x_GE` models
are simple time-only and energy-only baselines. The joint continuous ARA
instrument must improve holdout prediction beyond the single binary
`prompt_present` label to count as added relational information; a baseline
winning after inspection cannot replace the declared joint instrument.

### P3 - within-neutron timing relation

Among same-row prompt-present and neutron-present events, test whether prompt
coordinates predict first-neutron coordinate `x_N`. This is exploratory but
frozen: improvement must survive shuffled-neutron timing and the stricter
`5 < p <= 15 MeV` prompt-gamma window.

## CONTROLS

1. Circularly shift whole neutron packets within each split by
   `floor(N/3)+19` rows.
2. Run 1,000 fixed-seed (`369`) permutations of neutron packets relative to
   prompt rows.
3. Preserve neutron multiplicity but shuffle first-neutron times within each
   multiplicity class.
4. Repeat the continuous test on `5 < p <= 15 MeV` prompt candidates.
5. Repeat holdout on even and odd SHA256-derived hashes.
6. Compare ARA models with simple baselines: prompt presence alone, raw prompt
   momentum quantiles alone, and raw prompt time quantiles alone.

## FROZEN GATES

1. **Source QA:** exact row count and hashes agree with T368/Zenodo.
2. **Coverage:** at least 5,000 prompt-present holdout rows and at least 1,000
   prompt-plus-neutron holdout rows.
3. **Common-parent recovery:** prompt presence improves neutron-presence
   cross-entropy by at least 1% with bootstrap 95% interval above zero.
4. **Same-row specificity:** no more than 10 of 1,000 packet permutations equal
   or exceed Gate 3's effect.
5. **Replication:** Gate 3 retains direction in both hash halves.
6. **Continuous added value:** the frozen joint prompt Di-ARA address improves
   holdout cross-entropy by at least 0.5% relative to prompt presence alone.
7. **Multiplicity information:** a frozen prompt ARA table improves holdout
   three-class multiplicity cross-entropy by at least 0.5% relative to the
   unconditional model.
8. **Timing relation:** the prompt ARA table improves first-neutron-bin
   cross-entropy by at least 0.5%, survives multiplicity-preserving timing
   shuffle, and retains direction in the `5-15 MeV` window.

Verdicts:

- Gates 1-8: `DAUGHTER CLOSURE AND ADDED ARA RELATION SUPPORTED`;
- Gates 1-5 only: `COMMON-PARENT RELATION RECOVERED WITHOUT ADDED ARA VALUE`;
- failure of Gates 3-5: `COMMON-PARENT RELATION NOT RECOVERED`.

## REQUIRED OUTPUTS

- source/population QA;
- prompt-versus-neutron contingency and effect;
- continuous daughter mixing heatmaps;
- multiplicity and timing panels;
- mismatch, permutation, hash-half and strict-window controls;
- machine-readable results, visual report, reproduction script and
  independent validation.

## SCIENTIFIC BOUNDARY

This archive does not label each row as true nuclear capture or free decay.
Prompt absence includes detector non-detection, and neutron absence includes
both true zero-neutron events and missed tags. The paper estimates neutron
detection efficiency near 50%, and false tags occur. T369 therefore tests
information retained in the **released detector record**, not the complete
physical daughter state.

Because prompt gamma/neutron association is part of the source experiment's
established method, recovering P1 is a validation/crosswalk, not a novel
discovery. Only frozen added performance from the continuous ARA coordinates
would be a new empirical result from this analysis, and even that would require
independent replication before a physical mechanism claim.
