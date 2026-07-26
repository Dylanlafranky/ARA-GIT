# Session record — Q26 ARA^9 larger connection-space wave

**Date:** 26 July 2026  
**Participants:** Dylan La Franchi and Sol/Codex  
**Test:** `Q26-ARA9-LARGER-WAVE-v1`  
**Ledger:** `T282`

## Why this test was run

Q25 rejected a static rule that tried to recover one hidden ARA^9 cut from the other eight. Before Q25 target
values were opened, Dylan proposed that the local object might instead be only a crest of a larger
connection-space wave:

> “I think this is also just the crest of a larger wave in connection space. We might find the whole shape
> flips and becomes a trough in the next ARA^9.”

The correction was architectural: stop treating one complete local ARA^9 as the whole envelope; observe repeated
complete ARA^9 matrices and ask whether the whole relation moves across a larger ARA diameter.

## Frozen translation

For every complete connected relation,

\[
C(t)=T(t)-\mathbf a(t)\mathbf b(t)^\mathsf T,
\qquad
h(t)=|\det C(t)|^{1/3},
\qquad
x_h(t)=2h(t)/h(t_0).
\]

The frozen geometry was:

- crest: \(x_h\ge1.5\);
- handover: \(0.5<x_h<1.5\);
- trough: \(x_h\le0.5\);
- stable orientation flip: determinant sign reversal for two consecutive reliable samples above the trough.

The protocol and all later predictions were hashed before target reveal.

## Result

The larger-wave amplitude prediction landed:

- `25/28` primary trajectories completed crest-to-trough movement;
- median closure-versus-wait Spearman was `-0.9364`;
- ridge timing was within one sample on `21/22` eligible trajectories;
- trough timing was within one sample on `25/28`;
- exact time order beat all `999` permutations.

The direction-flip prediction did not:

- only `1/28` trajectories showed a stable reliable orientation reversal;
- the angular ARA predictor was worse than no rotation;
- ARA beat no rotation in cut MAE by only `0.00130`, with bootstrap win probability `0.6344`.

## Shared interpretation

The result supports Dylan's “crest of a larger wave” reading in amplitude. It does not support the stronger idea
that the next ARA^9 generally becomes a trough by turning into the opposite orientation. The data look more like
the complete relation shrinking through the larger ARA coordinate while retaining its broad orientation.

In plain terms: the whole nine-cut connection web gets quieter in an ordered and predictable way. It does not
usually turn inside out.

## Scientific boundary

This is a strong staged result because:

- the complete matrices, not selected cells, were predicted;
- the final four time steps were withheld;
- simple controls were run;
- timing, amplitude, orientation, and source quality were separated;
- an independent implementation passed `282/282` checks.

It remains one public experimental trajectory family in an established decoherence setting. It does not prove
universal fractality, a new quantum law, or an ARA singularity flip.

## Durable files

- `analysis/quantum/Q26_ARA9_LARGER_WAVE_TRAJECTORY_PROTOCOL_v1_FROZEN.md`
- `analysis/quantum/Q26_ARA9_LARGER_WAVE_TRAJECTORY_REPORT_2026-07-26.md`
- `analysis/quantum/Q26_ARA9_LARGER_WAVE_TRAJECTORY_FIDELITY_v1.md`
- `analysis/quantum/Q26_ARA9_LARGER_WAVE_RESULTS.json`
- `analysis/quantum/Q26_ARA9_LARGER_WAVE_VALIDATION.json`

