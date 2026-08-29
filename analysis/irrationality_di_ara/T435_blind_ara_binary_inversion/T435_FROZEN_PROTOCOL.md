# T435 — blind ARA binary-identity inversion

Status before scoring: **FROZEN**

## Question

Can the processed parent waveform of one binary-black-hole simulation be separated, using ARA geometry alone for the primary reconstruction, into two unordered child identities and their relation before the individual-horizon histories are revealed?

This is a single-simulation falsification/calibration test. It cannot establish a universal physical law.

## Who / what / when / where / why / how

- **Who:** child identities `B1` and `B2`, their relation `R12`, and the combined waveform parent `P`.
- **What:** infer `B1_hat`, `B2_hat`, and `R12_hat` from `P`; then compare them with hidden individual horizons A/B and common horizon C.
- **When:** late inspiral through first common-horizon formation and early ringdown, wherever all required waveform modes overlap.
- **Where:** SXS:BBH:0305, Lev6. The inference source is only `Lev6:Strain_N4.h5`. `Lev6:Horizons.h5` and `Lev6:metadata.json` are answer keys and remain unopened until the prediction artifact is written and hashed.
- **Why:** this directly tests the ARA claim that a compressed parent relation can retain enough structure to recover two constituent identities plus the relation between them; it does not treat the observed waveform as `h1 + h2`.
- **How:** use the parent phase, octave halving, polar opposition, odd/even modal asymmetry, and cadence tightening to construct a waveform-only ARA inversion. Reveal horizons only for scoring.

## Frozen identity map

The dominant complex quadrupole mode is the parent carrier:

`P(t) = h_22(t)`.

Its unwrapped phase is `phi_22(t)`. The ARA child orientation is frozen as

`theta_hat(t) = phi_22(t) / 2`.

The two child axes are antipodal:

`B1_angle = theta_hat`, `B2_angle = theta_hat + pi`.

No horizon information may choose the time-varying phase. During scoring only a constant rotation, a global handedness reversal, and an A/B label swap are allowed because these are coordinate and unordered-pair symmetries.

## Frozen child asymmetry

For every available complex mode `h_lm` on the common time support:

`P_even = sum |h_lm|^2 for (l + m) even`

`P_odd  = sum |h_lm|^2 for (l + m) odd`.

The raw child contrast is

`a_raw = sqrt(P_odd / (P_even + P_odd + eps))`.

It is mapped to `[0, 1]` using waveform-only 5th and 95th percentiles, clipped outside that interval. The unordered child shares are

`s_near = (1 - a_hat) / 2`, `s_far = (1 + a_hat) / 2`.

This does not assume which named horizon is heavier. The label is selected only by the minimum total scoring error.

## Frozen relation / closing coordinate

Let

`omega_hat = abs(0.5 * d(phi_22)/dt)`.

After a fixed Savitzky-Golay smoothing rule chosen solely from waveform cadence, the primary ARA remaining-relation coordinate is the reverse empirical-rank transform of `omega_hat`, mapped to `[0, 2]`. Faster cadence therefore means less remaining relation scale, without inserting a domain-specific orbital-radius law.

The inferred child radii are

`r1_hat = R12_hat * s_near`, `r2_hat = R12_hat * s_far`.

The inferred planar child positions follow from these radii and the antipodal angles.

For a side-by-side established-science crosswalk only, not for the ARA gate, also compute `R_science proportional to omega_hat^(-2/3)`.

## Frozen common-horizon landmark

The waveform-only handover estimate is the median time of three parent landmarks:

1. maximum total modal power;
2. maximum positive derivative of the smoothed cadence;
3. maximum absolute derivative of modal concentration `P_22 / sum(P_lm)`.

No horizon time enters this estimate. The comparison uses the time coordinates stored in the two SXS products. If the products require an undocumented propagation offset, the timing gate is reported **unscorable**, not fitted post hoc.

## Hidden scoring quantities

After the prediction file and SHA-256 hash exist, reveal:

- individual coordinate centers A and B;
- individual Christodoulou/areal masses and spins where available;
- first valid common-horizon C sample.

The actual relation is the A–B center separation. The actual child radii are measured about the instantaneous mass-weighted center. The orbital plane is identified from the hidden centers only for scoring, not inference.

## Frozen metrics and gates

1. **Orientation:** circular coherence of predicted half-phase against the hidden A–B direction, allowing only constant rotation, handedness and label symmetry. Gate: `>= 0.80` and at least `0.10` better than the unhalved-phase control.
2. **Relation:** Spearman correlation between `R12_hat` and actual A–B separation. Gate: `>= 0.70` and at least `0.20` better than the phase-scrambled control.
3. **Child radii:** best-label median Spearman correlation across the two inferred and actual child radii. Gate: `>= 0.50`.
4. **Handover timing:** absolute error no larger than one inferred parent cycle at the predicted handover. If the SXS product clocks are not directly comparable, mark this gate unscorable.

Overall result:

- **SUPPORTED:** all four gates pass.
- **PARTIAL:** orientation and relation pass, but radius or timing does not.
- **NOT SUPPORTED:** either orientation or relation fails.
- **UNSCORABLE:** required answer-key fields or clock relation are absent.

## Frozen controls

- unhalved parent phase (`theta = phi_22`);
- phase-scrambled/circularly shifted mode histories;
- one-identity parent (no antipodal child split);
- shuffled odd/even contrast;
- established-science `omega^(-2/3)` relation crosswalk.

Equal-mass/equal-spin systems are reserved as a later symmetry control: only the unordered pair is recoverable there.

## Evidence class

SXS is a numerical-relativity simulation generated within established general relativity. A pass is therefore an exact/empirical **crosswalk and inversion calibration**, not independent proof that ARA is the bedrock physical generator.
