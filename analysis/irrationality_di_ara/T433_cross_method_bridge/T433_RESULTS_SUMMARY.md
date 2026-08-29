# T433 — Cross-method Irrationality Di-ARA bridge

## Answer first

The different recordings do **not** correlate as one continuous universal
waveform. They do, however, contain one statistically unusual **ridge-time
bridge**.

The T427 direct-strain ARA and T429 separated movement/connection ARA reach
their independently constructed `(1,1)` ridge within a median `16 ms` of one
another across five shared black-hole mergers. Wrong-event plus large
time-shift controls had a median gap of `232 ms`; the exploratory ridge bridge
gave `p=0.0018`, FDR `q=0.0108` across six method pairs.

This bridge is partial rather than universal:

| Event | T427 ridge | T429 ridge | Gap |
|---|---:|---:|---:|
| GW170104 | -35.3 ms | -51.3 ms | 16 ms |
| GW170608 | -43.3 ms | +132.7 ms | 176 ms |
| GW170809 | -79.3 ms | -79.3 ms | 0 ms |
| GW170814 | +152.7 ms | +168.7 ms | 16 ms |
| GW170818 | -39.3 ms | +124.7 ms | 164 ms |

Three events therefore show a direct `0–16 ms` ridge bridge. Two show a
second, delayed family near `164–176 ms` in which T429 reaches its ridge after
T427.

## What did not bridge

The frozen full-handover test compared four independently constructed method
families from `-0.495` to `+0.245 s`:

- T427 direct strain cut;
- T428 paired-phase cut;
- T429 separated movement/connection cut;
- T432 dynamic ledger cut.

No method pair passed both of the frozen requirements:

1. common lagged trajectory-speed association;
2. common high-movement landmark timing;

after wrong-event, large-time-shift and six-pair FDR controls. The broad
continuous bridge verdict is therefore **not supported**.

An event-specific search also produced `0/30` two-metric FDR passes. The ridge
bridge is not a disguised full-waveform match; it is a localized landmark
relation.

## ARA reading

T427 and T429 are not the same instrument:

- T427 mixes native spectral activity/change into its movement side and uses
  spectral concentration on its connection side.
- T429 separates frequency/chirp movement from received amount and H1/L1
  agreement on the connection side.
- They use different off-source calibrations and do not share values by
  construction.

Their curves, speeds and derivative directions need not match. The recovered
relation is that two different cuts sometimes identify the same ARA ridge
handover time. In the other two events, one cut reaches a second ridge about
`170 ms` later. This is compatible with either two handover paths/scales or an
event-dependent delay, but five events cannot decide between them.

## Evidence boundary

- All methods ultimately derive from the same H1/L1 detector strain and share
  the published event-time reference. A common astrophysical transient is a
  conventional explanation for part of the timing agreement.
- The methods use a 64 ms STFT stepped every 4 ms. The `0` and `16 ms` values
  must not be interpreted as independent sub-16-ms physical resolution.
- Each method's `(1,1)` ridge is an ARA address under that method's own
  off-source calibration; it is not the same raw detector threshold.
- This exploratory bridge does not prove a singularity flip, identify internal
  black-hole children, or establish causal information transfer.
- The result is nevertheless stronger than visual resemblance: it survives
  wrong-event and large-time-shift controls, six-pair FDR, independent
  recomputation, and five additional random-control seeds.

## Validation

Independent validation passed source hashes, frozen hashes, event/method grain,
coordinate bounds, exact ridge gaps and seed sensitivity. Across five
additional seeds the raw ridge-bridge p-value ranged from `0.00040` to
`0.00120`; even a six-test Bonferroni correction remained below `0.05`.

## Best follow-up

Freeze the T427/T429 ridge bridge on a new untouched merger set and test the
two timing families explicitly:

1. direct bridge: absolute ridge gap `<=16 ms`;
2. delayed bridge: T429 after T427 by approximately `160–180 ms`;
3. neither.

Then ask whether independently known merger duration, mass scale, detector
agreement, or an ARA-derived parent/child duration separates the direct and
delayed families. That would test whether the delayed group is a genuine rung
or phase handover rather than a measurement-window artifact.

