# T420 — Independent Information³ handover channel

**Frozen before development fitting or any validation/holdout scoring:** 22 August 2026  
**Status:** ARA-first follow-up to T419 on the same public muoniated-acetone ensemble

## Question

T419 found that independently measured closure generally falls while openness
rises, with their visible crossings below the adult `1.0` ridge. Does a third,
independently observed relation become exposed at that handover, improve the
three-part TE-ARA account, and carry information into later openness?

This is an Information³ test of the measured population relation. It is not an
individual-muon, connection-birth, decay-event or neutrino-release test.

## Who / what / when / where / why / how

### Who

Use exactly the T419 source manifest and partitions: 13 development runs,
13 validation runs and 20 high-field/temperature holdout runs. RF-on and
RF-off remain distinct histories. The identity remains the detector-population
spin relation of the muoniated-acetone radical.

### What

Retain the independent T419 coordinates:

\[
U(t)=\frac{2L_{\rm local}(t)}{L_{\rm local}(t)+L_{\rm null}(t)},
\]

\[
R(t)=2\,\operatorname{median}_{\ell=1}^{32}|C_\ell(t)|,
\qquad
C_\ell=\left\langle e^{i2\pi(z_{j+\ell}-z_j)}\right\rangle_j.
\]

Define the candidate third relation from the unused angular component of the
same complex lag relations:

\[
H(t)=2\,\operatorname{median}_{\ell=1}^{32}
\frac{|\arg C_\ell(t)|}{\pi}\in[0,2].
\]

`H` is therefore observed from lag angle. It is not calculated as `2-U-R`, is
not a fitted residual, and is not labelled as physical energy. It is a
candidate unresolved/turning relation whose ARA role must be earned by the
tests below.

The wrong-frequency `H_wrong` uses the median of the same four predeclared
T416 sideband reconstructions used by T419.

### When

Each coordinate uses only the preceding 128 native bins and is read every four
native bins. The primary predictive horizon is the unchanged 32 reads =
128 native bins, approximately 2.048 microseconds, so source and target
histories share no native bins.

An observed crossing occurs only when adjacent reads change the sign of
`U-R`. Crossing time and all coordinate values are linearly interpolated
within that interval. No numerical proximity band is used to create events.

### Where

Material, temperature partitions, detector geometry, source files, corrected
time range, phase-path reconstruction, parent-lifespan coordinate, magnetic
field turn budget and RF separation remain unchanged from T419.

### Why

At the two labelled T419 crossings, `U+R` was approximately 1.51–1.63 rather
than 2. Because `U` and `R` are independent coordinates, that arithmetic alone
does not prove a missing channel. T420 asks whether an independently observed
third relation is actually aligned with the handover and adds out-of-window
information.

### How

T420 contains three linked tests.

1. **Crossing exposure.** Compare interpolated `H` at every `U=R` crossing
   with the median `H` of the same run/period history. Pair effects by field
   and bootstrap fields with RF histories kept together.
2. **Unfitted three-part closure.** At crossings compare

   \[
   E_2=|2-U-R|
   \quad\text{with}\quad
   E_3=|2-U-R-H|.
   \]

   Positive `E2-E3` means the independently observed `H` moves the three-part
   account closer to 2. Compare the correct `H` with circularly shifted and
   wrong-frequency `H`; also report, but do not use as an ARA pass gate, a
   development-fitted affine alternative `a+bH`.
3. **Causal handover.** Predict future openness from the frozen baseline

   \[
   Z_0=[U,\Delta U,R,\Delta R,P,K_B,\mathrm{RF}]
   \]

   versus

   \[
   Z_1=[Z_0,H,\Delta H].
   \]

   Development-only standardization and ordinary-least-squares coefficients
   are frozen before validation and holdout. A corresponding `H -> later R`
   arm is diagnostic only because T419 identified closure-to-openness as the
   surviving direction.

## Frozen controls

1. Within-history circular shifts of `H` and `delta H`.
2. Reverse chronology of `H` and `delta H`.
3. Wrong-frequency `H` from the four frozen sidebands.
4. RF-on and RF-off effects reported separately.
5. Field-level bootstrap with RF histories kept paired.
6. Development-fitted affine closure as a flexible non-ARA benchmark.
7. Shorter horizons of 1, 2, 4, 8, 16 and 24 reads as overlapping diagnostics
   only; they cannot rescue a failed 32-read primary result.

All random controls use seed 420. Bootstrap intervals use 10,000 draws and
circular-shift prediction controls use 1,000 draws.

## Frozen gates

Validation and holdout are scored separately. The candidate Information³
handover channel is supported in a stage only when all primary gates pass:

1. At least 75% of run/period histories supply at least eight non-overlap
   prediction rows.
2. `H` is not an imposed complement: `std(U+R+H)>0.01`, and neither
   `|corr(H,U)|` nor `|corr(H,R)|` exceeds 0.95.
3. The field-bootstrap 95% interval for crossing exposure
   `H_cross-median(H_history)` lies wholly above zero.
4. At crossings, the field-bootstrap 95% interval for `E2-E3` lies wholly
   above zero, and correct `H` improves closure more than both circularly
   shifted and wrong-frequency `H`.
5. At the primary non-overlap horizon, the field-bootstrap 95% interval for
   `MSE_baseline-MSE_H` lies wholly above zero.
6. Correctly timed `H` beats at least 95% of circular shifts; wrong-frequency
   and reversed `H` are both worse with field-bootstrap intervals wholly above
   zero.
7. Baseline-minus-`H` prediction improvement is positive in RF-on and RF-off.

Archive-level support requires both validation and holdout to pass. A partial
pass may identify a regime-specific or one-arm relation but cannot establish a
general Information³ handover.

## Chart contract

The final technical report must show numeric axes and units for:

1. `U`, `R` and independent `H` histories for labelled validation and holdout
   examples, with observed `U=R` crossings marked;
2. event-centred median `U`, `R` and `H` around crossings;
3. `E2` versus correct, shifted, wrong-frequency and affine `E3` closure;
4. future-openness prediction errors and per-field effects;
5. horizon dependence with overlapping diagnostics separated from the
   non-overlap primary test;
6. coordinate correlations, sample counts, gates and claim boundaries.

## Claim boundary

A pass would show that an independently measured lag-angle relation becomes
exposed at the closure-to-openness crossing, improves the three-part TE-ARA
account without being defined as the missing arithmetic, and carries
out-of-window information into later openness. It would support this
Information³ handover instrument in the measured population identity. It
would not establish literal conserved energy, microscopic muon structure,
individual connection creation, or neutrino birth timing.
