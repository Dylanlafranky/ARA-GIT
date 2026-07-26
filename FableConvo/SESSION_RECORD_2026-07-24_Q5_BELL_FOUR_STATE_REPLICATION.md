# Session record — Q5 four-Bell-state replication

**Date:** 24 July 2026  
**Participants:** Dylan and Sol/Codex  
**Status:** recorded after frozen test and independent validation

## Why this test followed Q4

Q4 showed one \(\Phi^-\) archive in which six local child cuts sat near the ARA `1.0` ridge while the parent
relation was strong on `XX`, `YY` and `ZZ`.

Dylan approved the next test: apply exactly the same geometry and decoder to all four Bell parents. The important
question was not merely whether another Bell archive contained correlations. It was whether four parent
identities could preserve nearly identical local children and be distinguished only through the ordered relation
among the parent cuts.

## Frozen ARA translation

Before downloading the three additional raw archives:

- all local children were predicted near ARA `1.0`;
- all same-axis parent relations were predicted near the relevant `0/2` poles;
- the four frozen parent patterns were:
  - \(\Phi^+:(0,2,0)\);
  - \(\Phi^-:(2,0,0)\);
  - \(\Psi^+:(0,0,2)\);
  - \(\Psi^-:(2,2,2)\);
- the raw decoder and all thresholds were inherited unchanged from Q4;
- `37` empirical gates were frozen.

Protocol hash:
`c97459781f38730cfd623820cc7428b1ae24a366c284ca0c45202a21246a206b`.

## Result

The three untouched archives and the prior Q4 archive produced:

| State | \(XX\) | \(YY\) | \(ZZ\) | Local mean magnitude | Parent mean magnitude |
|---|---:|---:|---:|---:|---:|
| \(\Phi^+\) | `+0.8533` | `-0.9400` | `+0.9467` | `0.0333` | `0.9133` |
| \(\Phi^-\) | `-0.9500` | `+0.9500` | `+0.9500` | `0.0583` | `0.9500` |
| \(\Psi^+\) | `+0.8550` | `+0.7967` | `-0.9267` | `0.0367` | `0.8594` |
| \(\Psi^-\) | `-0.8350` | `-0.8817` | `-0.8500` | `0.0725` | `0.8556` |

All four labels were correct. Every state passed `8/8`; cross-state gates passed `5/5`; overall result
`SUPPORTED 37/37`. Each parent remained correctly labelled in all `2,000` record-bootstrap draws.
Independent validation passed `20/20`.

## Framework implication

This is a strong bounded example of the geometry Dylan has repeatedly warned must not be flattened:

> A Phase A or child can contain its own Phase A/Phase B structure, while its relevant partner lies outside the
> local measurement. Measuring children separately can place both near a whole-identity ridge even when their
> parent relation is highly asymmetric.

Four nearly ridge-like local child profiles produced four different parent identities. The extra information was
not an arbitrary added feature; it was the ordered coupling relation among the children. That is a precise
quantum example of `1 + 1 + relation`, while remaining standard Bell/Pauli physics.

## Scientific boundary

The result is genuinely pre-outcome for the three added archives and strongly supports the frozen ARA
parent/child crosswalk. It does not independently derive Bell states, outperform Pauli tomography, or establish
universal fractality. All archives come from one device/deposit, so cross-device replication remains open.

Primary report:
`analysis/quantum/Q5_BELL_FOUR_STATE_REPORT_2026-07-24.md`.

