# T430 — Remaining traversal versus accumulated connection

Frozen before downloading or scoring the four confirmation events. T427–T429
remain unchanged.

## Question

T429 separated frequency/chirp activity from received connection-facing signal,
but then tested whether both rose together. That is not the same-rung ARA claim.
For two opposing waves of one identity, accumulated connection should increase as
the remaining traversal budget decreases. Does that inverse gradient appear in
binary-black-hole strain more strongly than in matched off-source histories?

## ARA identity, ownership, and orientation

- One binary-black-hole event is one measured identity. Events are never pooled
  into one ARA path.
- H1 and L1 are independent detector views of that identity. V1 is descriptive
  where available and never substitutes for a missing primary detector.
- `M_rem` is the remaining movement/traversal child, oriented from 2 toward 0.
- `C_acc` is the independently observed connection/concentration child, oriented
  from 0 toward 2.
- Pure TE-ARA predicts `M_rem + C_acc = 2`; the test measures deviation from that
  relation and never defines one coordinate as the complement of the other.
- Labels state this cut's direction. Reversing both labels leaves the relational
  result unchanged.

## Development and untouched confirmation

Previously inspected events are development/exploration only:

- GW150914, GW170104, GW170608, GW170809, GW170814, GW170818.

The frozen confirmation set contains four GWTC-1 binary-black-hole events absent
from T427–T429:

- GW151012, GW151226, GW170729, GW170823.

No confirmation event may alter a feature, threshold, time interval, orientation,
gate, or figure definition.

## Time windows and native landmark

- Context: -1.50 to +0.25 seconds relative to official event GPS.
- Primary inverse-gradient window: -0.50 to -0.03 seconds.
- Wide sensitivity window: -1.25 to -0.03 seconds, reported separately.
- Off-source calibration: [-12,-4] and [4,12] seconds.
- The official event time is an independent native handover label. It selects the
  crop and endpoint but does not select an ARA crossing.
- STFT: 64 ms Hann window, 4 ms hop, 30–512 Hz, unchanged from T427–T429.

## Independently constructed coordinates

### Remaining traversal `M_rem`

For each detector, obtain the power-weighted frequency history from the fixed
STFT. Align L1 to H1 with the same bounded +/-8 ms amount lag used previously and
average the detector frequency histories. Smooth only with the frozen nine-frame
median filter.

Within each scored window, calculate remaining observed phase cycles:

    N_rem(t_i) = sum_{j=i}^{end} f_consensus(t_j) * hop_seconds

and orient the identity-specific movement budget as:

    M_rem(t_i) = 2 * N_rem(t_i) / N_rem(t_start)

This fixes the stated 2-to-0 orientation but does not use connection data. A
matched off-source window receives the identical construction, so a decreasing
movement axis alone cannot pass the test.

A secondary non-cumulative check uses the independently observed local period
`1/f_consensus`, projected to 0–2 from detector off-source values. It must agree
in sign with the primary result to support a scale-length interpretation.

### Accumulated connection `C_acc`

Connection is not defined from `M_rem`. For each detector:

1. `C_amount`: log 30–512 Hz spectral amount, independently mapped to 0–2 by
   that detector's off-source empirical CDF.
2. `C_density`: one minus normalized spectral entropy, independently mapped to
   0–2 by that detector's off-source empirical CDF.

After the frozen detector lag, H1 and L1 are averaged within each component and:

    C_acc = mean(C_amount, C_density)

H1/L1 amount agreement remains a validation channel and is not part of `C_acc`.

## Relations scored

For each event and matched off-source window:

- inverse-gradient Spearman association `rho(M_rem, C_acc)`;
- connection growth `rho(time, C_acc)`;
- TE-ARA residual `abs(M_rem + C_acc - 2)`;
- fraction of samples within residual <= 0.50;
- order and time of the first persistent `C_acc >= 1` ridge crossing;
- H1/L1 connection-history agreement;
- secondary association between local-period ARA and `C_acc`.

The primary event p-values use circular block shifts of the complete `C_acc`
history relative to the fixed `M_rem` history. Matched off-source windows use the
same duration, features, movement-budget construction, and scoring.

## Frozen confirmation gates

Support requires all of the following:

1. At least 3/4 confirmation events have `rho(M_rem, C_acc) <= -0.30` with
   lower-tail circular-block-shift `p <= 0.05`.
2. At least 3/4 have event median TE-ARA residual lower than at least 90% of their
   matched off-source windows.
3. At least 3/4 have positive connection growth `rho(time, C_acc) >= 0.30` with
   upper-tail circular-block-shift `p <= 0.05`.
4. At least 3/4 spend at least 60% of the primary window within
   `abs(M_rem + C_acc - 2) <= 0.50`, and exceed the 95th percentile of matched
   off-source occupancy.
5. At least 3/4 show positive H1/L1 connection agreement and beat 95% of bounded
   circular detector shifts.

Gate 1 tests opposition; gates 2 and 4 test approximate closure; gate 3 tests the
expected direction; gate 5 tests whether the relation belongs to the shared
source rather than one detector.

## Controls

1. Equal-duration sliding windows from both off-source intervals.
2. Circular block shifts of `C_acc` relative to `M_rem`.
3. Circular shifts of L1 relative to H1 for detector agreement.
4. Reverse chronology, descriptive only because `M_rem` has a stated direction.
5. Wide-window sensitivity, which cannot rescue the primary window.
6. Established-physics separation/binding calculated only after ARA histories
   are frozen; it is a crosswalk and cannot rescue a failed model-free gate.

## Visual contract

The technical report must show, with 0–2 axes and numerical labels:

- `M_rem`, `C_acc`, and their sum through chronological time;
- the chronological ARA plane with the ideal inverse line `M+C=2`;
- TE-ARA residual and ridge crossing;
- the event path beside matched off-source paths on identical scales;
- all untouched confirmation events as identical-scale small multiples;
- exact gate metrics and detector agreement;
- ARA reading, established-physics crosswalk, and unresolved boundary.

## Interpretation boundary

A pass supports this operational inverse-gradient instrument in public event-
locked strain. It does not prove that black holes literally contain the named
ARA children, replace general relativity, or provide a blind merger forecast.
A failure rejects this coordinate construction and scale, not the general ARA
framework. Development results remain exploratory regardless of their strength.
