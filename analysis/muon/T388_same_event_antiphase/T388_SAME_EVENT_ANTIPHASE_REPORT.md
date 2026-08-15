# T388 — same-event anti-phase identification result

## Outcome

**DIRECT DETECTOR REPETITION**

T388 compared the ARA detector loop around the chronological stopped-muon
pulse with the later charged-daughter pulse in the same liquid-scintillator
record. It did not directly observe either neutrino.

## Population

- Eligible evaluation events before pair filtering: `1,148`
- Complete, non-overlapping paired loops: `650`
- Native sample cadence: `8 ns`
- ARA window: `128 ns`
- Scored interval: `-256 ns` to `+512 ns` from each pulse minimum

## Frozen mapping scores

| Mapping | Median paired RMSE | 95% bootstrap CI |
|---|---:|---:|
| Direct repeat | 0.192393 | [0.188215, 0.198334] |
| Full reversal | 1.332082 | [1.329720, 1.333780] |
| x_R-only reversal | 0.741836 | [0.739222, 0.744742] |
| x_H-only reversal | 1.126791 | [1.124730, 1.128772] |

### Reversal minus direct repetition

| Reversal | Median difference | 95% bootstrap CI |
|---|---:|---:|
| Full reversal | +1.136194 | [+1.131144, +1.141672] |
| x_R-only reversal | +0.539525 | [+0.534457, +0.546283] |
| x_H-only reversal | +0.932658 | [+0.927347, +0.938958] |


The lowest-error mapping was **Direct repeat**. The two pulse loops
retained the same handedness in **100.0%** of paired events.

## Strict pre-daughter guard

At `-128 ns` relative to each pulse minimum:

- first-pulse median `(x_R,x_H)` = `(1.000000, 0.157395)`;
- daughter-pulse median `(x_R,x_H)` = `(1.000000, 0.157395)`;
- paired direct distance = `0.183153` ARA units, 95% CI
  `[0.174740, 0.194260]`.

T388 does not pass the advance-handover gate. T385 had already found no held-
out advance contribution outside the final `128 ns` visible-pulse guard.

## Meaning

This test identifies what the visible T387 opposite belongs to at the measured
boundary. A direct-repeat result says the expansion/opening and later
contraction/reclosure are principally the detector's response to an energy
deposit, repeated after both pulses. A reversal result would instead nominate
an anti-phase candidate for independent physical-lineage testing.

Even a clean reversal here would remain Class D. The muon's proposed retained-
connection child and the neutral-daughter release require a source that measures
their physical lineage rather than only the scintillator voltage response.
