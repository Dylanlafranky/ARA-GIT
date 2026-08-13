# T346 temporal Di-ARA storage-handover-release

**Date:** 9 August 2026  
**Status:** frozen post-T345 mechanism test; primary claim not supported  
**Frozen protocol SHA-256:** `205f48d722b80e59f3d0c766790c1ecfeabbf7eac50f3f644590301e1fdda512`

## Answer first

The frozen temporal mechanism was **not supported**.

- The laboratory primary rung was formally ineligible: it recovered `192`
  coherent-recurrence anchors, just below the frozen floor of `200`. Its Gates
  A-C therefore fail without calculation or threshold relaxation.
- The numerical primary rung was eligible with `9,072` coherent anchors across
  the longer numerical trajectories. Its mean connection build, release and
  centre peak all overlapped zero, so Gate A failed.
- Larger movement closing/opening was associated with *smaller*, not larger,
  connection-ledger build/release. Both frozen rank correlations were strongly
  negative and worse than the matched broken-lineage null, so Gate B failed.
- Coherent recurrence nevertheless had a much more positive connection-peak
  contrast than crooked curvature in all three numerical conditions. Gate C
  passed strongly.
- Laboratory/numerical signs and Gate A-C verdicts did not transfer. Gate D
  failed.

Thus T346 supports a narrower statement: **coherent recurrence and crooked
curvature have different temporal connection profiles**. It does not support
the registered claim that the amount of ordered-connection concentration
released determines the magnitude of the next Phase-A opening.

## What was actually tested

Every contiguous trajectory was divided into non-overlapping triples of
`W`-step blocks. A primary handover anchor was selected from movement alone:

\[
D_{pre}\ge0.75,
\quad D_c\le0.75,
\quad G_c\ge0.75,
\quad D_{post}\ge0.75.
\]

Connection concentration did not participate in event selection. Only after
the `open -> recurrent -> open` movement event had been identified did T346
read

\[
S_{build}=I_c-I_{pre},
\quad
S_{release}=I_c-I_{post},
\quad
S_{peak}=I_c-\frac{I_{pre}+I_{post}}2.
\]

`I_conn` is the concentration of the 16 observed ordered Di-ARA transition
channels. It is a proxy for the organisation of Phase-B children, not the full
Phase B, total information or stored energy.

## Primary W=15 results

| component | laboratory | numerical estimate [95% whole-track CI] | numerical result |
|---|---:|---:|---|
| connection build `S_build` | ineligible | `-0.005644 [-0.017039, +0.006178]` | FAIL |
| connection release `S_release` | ineligible | `+0.007904 [-0.004389, +0.020183]` | FAIL |
| centre connection peak `S_peak` | ineligible | `+0.001130 [-0.009023, +0.011100]` | FAIL |
| approach/build magnitude `rho_in` | ineligible | `-0.089977 [-0.110051, -0.067811]` | FAIL; broken `p=1.0` |
| release/open magnitude `rho_out` | ineligible | `-0.106357 [-0.127807, -0.084030]` | FAIL; broken `p=1.0` |
| circle minus crooked `S_peak` | ineligible | `+0.214743 [+0.198696, +0.231335]` | PASS in `3/3` conditions |

Primary Gates A/B/C were:

- laboratory: **FAIL / FAIL / FAIL**;
- numerical: **FAIL / FAIL / PASS**;
- representation Gate D: **FAIL**.

The numerical primary construction used `237,600` non-overlapping triples,
`12,068` total anchors and `3,905` trajectories. The laboratory construction
used `52,312` triples, `905` total anchors and `758` trajectories.

## Scale-dependent lead

The sensitivity rungs do not rescue the primary result, but they reveal a
clean post-result lead.

| representation/rung | `S_peak` [95% CI] | Gate A | circle minus crooked `S_peak` |
|---|---:|---|---:|
| laboratory `W=8` | `+0.173534 [+0.129497, +0.216002]` | PASS | `+0.221978 [+0.162686, +0.278223]` |
| laboratory `W=15` | ineligible (`192<200` circle anchors) | FAIL | ineligible |
| laboratory `W=30` | ineligible (`26<200`) | FAIL | ineligible |
| numerical `W=8` | `-0.089238 [-0.097627, -0.081236]` | FAIL | `+0.154382 [+0.137626, +0.170637]` |
| numerical `W=15` | `+0.001130 [-0.009023, +0.011100]` | FAIL | `+0.214743 [+0.198696, +0.231335]` |
| numerical `W=30` | `+0.109845 [+0.094347, +0.125415]` | PASS | `+0.258317 [+0.238512, +0.279301]` |

In the numerical representation the connection profile changes from a trough
at `W=8`, through neutral at `W=15`, to a clear peak at `W=30`. The laboratory
representation already has a clear peak at `W=8`. Because these scales were
inspected after the primary freeze, this is not evidence for an octave law or
a fitted rung. It motivates a new test in which the operative rung is selected
from movement geometry alone before the connection ledger is opened.

## Visual audit

The figures faithfully show the frozen outcomes, including the empty primary
laboratory inference panels caused by ineligibility.

The raw exemplars also expose an important measurement boundary. The
laboratory exemplar is a compact coherent turn. The numerical maximum-
circularity exemplar is almost a one-dimensional reversal: it leaves, reverses
smoothly and returns along nearly the same line. This is not disqualified
merely because it is not a closed orbit. Under ARA, a locally recurrent child
is normally transported by a larger parent wave; in the observer's frame the
expected path is therefore open--a spiral, helix, cycloid, U-turn or displaced
arc--rather than a literal circle. Exact indefinite closure would instead be a
resonance limit at the declared rung.

The actual boundary is narrower and more important: `C=(1-D)G` recovers
coherent recurrence/curvature, but it does not resolve the recursive handover

\[
A_k \rightarrow B_{k-1}^{\rm children}
\rightarrow A_{k-1}^{\rm children}
\rightarrow B_k \rightarrow A_k.
\]

The children feed back into the adult cycle; they are not simply added to an
independent parent carrier. The next test must first recover the smoother
direction one rung above the target, then descend and test the same direction
at the target rung together with any asymmetric handover gap. Intact ordering
must beat reversed, shuffled and wrong-lineage controls.

## What this means for the framework

T346 does not falsify generic ARA or Di-ARA. It falsifies a particular
translation of the temporal mechanism:

> more concentration lost from the observed ordered-connection ledger should
> produce a proportionally larger next directional opening.

That translation treated concentration as if it were a quantity or energy
budget. The data show that it is not safe to do so. `I_conn` describes how
unevenly the observed connection children occupy their channels; redistribution
can reduce concentration without specifying how much total Phase B exists.

The robust surviving result is relational: coherent recurrence has a different
connection profile from crooked recurrence, and the sign of its absolute peak
depends strongly on the declared rung. The next admissible question is
therefore about **cross-rung recirculation, rung alignment and distribution
shape**, not a post-hoc positive-energy ledger. The scale dependence may have
arisen because the frozen single-window statistic compressed different stages
of the child-to-adult return. That is a post-result hypothesis and does not
repair T346.

The broader proposal that temporal Di-ARA is an ever-present coherent
carrier/source wave analogous in role to light or gravity remains hypothesis
tier. This one controlled-weir result neither establishes nor identifies such
a source.

## Validation and artifacts

The saved-artifact validator independently reconstructed Gates A-C, all
eligible summary estimates, all `1,000`-member broken-lineage p-values,
official source-hash flags and the Gate-D comparison. Validation passed.

- `T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_PROTOCOL_v1_FROZEN.md`
- `T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_FIGURE.png`
- `T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_NUMERICAL_REPLICATION_FIGURE.png`
- `T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_RESULTS.json`
- `T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_NUMERICAL_REPLICATION_RESULTS.json`
- `T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_VALIDATION_2026-08-09.md`
- `T346_TEMPORAL_DI_ARA_STORAGE_HANDOVER_VALIDATION.json`
- `t346_temporal_di_ara_storage_handover.py`
- `validate_t346_temporal_di_ara_storage_handover.py`
