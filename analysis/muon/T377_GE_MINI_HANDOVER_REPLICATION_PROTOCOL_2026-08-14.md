# T377 - Ge-Mini muon-handover replication protocol

**Frozen:** 14 August 2026, after source/schema inspection and before numerical vector extraction or model scoring  
**Status:** registered protocol; outcomes remain unread at the extracted-data level

## Identity and boundary

- **Who:** the prompt `nu_mu` branch released by stopped-pion decay and the
  delayed `nu_e + anti-nu_mu` branch released by subsequent muon decay.
- **What:** their ensemble two-branch handover. This is not an event-linked
  prediction of an individual muon's daughter time.
- **Where:** the COHERENT Ge-Mini solid-germanium detector, SNS Campaign 2
  (21 June to 15 August 2023). This is a different detector, material, campaign
  and reconstruction from the T371/T372 CsI[Na] record while retaining the
  same stopped-pion source identity.
- **When:** beam-relative reconstructed arrival time, retaining recoil energy
  as the second measurement cut.
- **Why:** determine whether the ordered two-release ARA geometry recovered in
  T371/T372 survives an independent connection-heavy solid detector.
- **How:** reconstruct the publication's vector timing projections and exact
  integer on/off-beam count cells; refit fixed prompt and delayed timing shapes;
  compare the pair with named controls; solve branch equality; integrate the
  release to that time on the 0-2 ARA coordinate.

## ARA definitions

For non-negative fitted branch yields `P` and `D`,

```text
x_prompt  = 2 P / (P + D)
x_delayed = 2 D / (P + D)
```

Their sum is exactly 2 by construction and is bookkeeping, not evidence.

At the instantaneous branch-equality time `t_H`,

```text
r_prompt(t_H) = r_delayed(t_H)
```

and the cumulative handover coordinate is

```text
x_H = 2 * integral(start..t_H)[r_prompt + r_delayed]
          / integral(start..end)[r_prompt + r_delayed].
```

The pure proposed child landmark `x_H = 0.5` remains distinct from the
identity-specific physical coordinate. The pre-existing T372 CsI interval
`[0.1787, 0.6916]` is a frozen compatibility reference, not a fit target.

## Frozen comparisons

1. ordered prompt + delayed pair;
2. prompt-only;
3. delayed-only;
4. zero-release/null timing model;
5. time-reversed or branch-swapped control where identifiable;
6. off-beam projection under the same fitting procedure;
7. raw on-minus-off count projection as a coarser independent crosscheck.

## Gates

- **G1 provenance:** official arXiv source archive, local SHA-256 recorded, and
  all consumed figure hashes recorded.
- **G2 identity:** independent detector/campaign and same stopped-pion source
  relation are documented explicitly.
- **G3 ordered branches:** the prompt crest precedes the delayed crest and a
  finite branch-equality point exists.
- **G4 pair necessity:** the ordered pair improves information criterion over
  each single-branch control. Exact threshold and finite-sample correction
  (`AICc`) will be reported rather than changed post hoc.
- **G5 observed support:** the on-beam timing projection supports the pair more
  strongly than the identically processed off-beam control.
- **G6 ARA placement:** report `x_H`, uncertainty, displacement from 0.5, and
  compatibility with the frozen T372 interval. Exact 0.5 is not claimed unless
  independently resolved.
- **G7 robustness:** extraction/calibration uncertainty, leave-one-bin-out
  stability and the coarse raw-count crosscheck do not reverse the ordering.

## TE-ARA/coupling audit

The prompt/delayed normalization forces a two-part total and cannot establish
physical closure by itself. Coupling evidence must instead come from the
observed timing-energy structure: pair-vs-single improvement, chronological
ordering, on-vs-off separation, and residual/uncertainty behaviour. Detector
drift time, low-energy timing loss, background subtraction, finite counts,
energy threshold, excluded cosmogenic lines and source-model dependence will
be carried as explicit `Other`/confound terms rather than hidden inside the
ARA coordinate.

## Interpretation boundary

A pass would independently support the ensemble ordered-handover geometry in a
new solid detector. It would not prove universal ARA, exact 0.5 placement,
event-level sibling linkage, or advance warning of one muon's decay.
