# T305 — ARA Phi Temporal Carrier: Known Calibration and Muon-Fusion Schedule

**Frozen:** 30 July 2026, 12:48 AEST  
**Status at freeze:** unrun  
**Target exposure:** the earlier muon pulse-schedule result is open. The
specific multi-prefix carrier comparison and its values have not been
calculated. The plant source and T302 result are already open and are used
only as an empirical calibration, not a discovery target.

## Prior ARA claim

The local sphere/cycle may close while its complete identity is transported
through a larger ordered frame. Dylan proposes that this larger **Time-side
carrier** may advance by the Phi handover:

\[
\alpha_\phi=\phi^{-2}=0.381966011250105\ldots
\]

on a directed `0 -> 1` turn, with reverse direction
`1-alpha_phi = phi^-1`. On the ARA `0 -> 2` diameter these are the paired
landmarks `0.381966...` and `1.618034...`.

The engineering claim is not that Phi is the best arrangement when the final
number of pulses and target phase are known. It is that Phi is a robust
non-repeating temporal carrier when the final prefix and production phase are
unknown, every prefix must remain usable, and pulse resources are matched.

## ARA-first coordinate

For carrier step \(\alpha\), placement \(k\) is
\(\theta_k=\operatorname{frac}(k\alpha)\). The directed observed step is
\(\widehat\alpha_k=\operatorname{frac}(\theta_{k+1}-\theta_k)\).
The exact synthetic control must recover its generating \(\alpha\). This is
an implementation check, not evidence for Phi.

Each prefix is evaluated in its own unit parent cycle. No Fourier fitting or
learned parameter creates the placements.

## Known comparisons

### K0 — exact mathematical controls

Generate noiseless ordered carriers at exact Phi, `3/8`, `sqrt(2)-1` and
`1/3`. The estimator must recover every supplied carrier to absolute error
`<=1e-12`. Reverse Phi must recover `phi^-1`.

### K1 — public empirical calibration

Reuse, without changing its verdict, T302's public ordered Arabidopsis
phyllotaxis calibration: confirmation wild type is within `0.01` of
`phi^-2`, and exact Phi is the best already-tested fixed cumulative-position
carrier. This system is already known to inhabit the golden-angle
neighbourhood, so this is calibration rather than discovery or Fusion
evidence.

## Fusion target

The target is the external-field overlap
\[
f_X=\int_0^1g(t)C(t)\,dt
\]
from the public Kou-Chen muon-reactivation rate-network formulation
(`arXiv:2606.07077`). This tests only the scheduling part of \(f_X\), not
microscopic stripping or post-stripping recycling.

### Matched conditions

- `N_max=64`, with every prefix `N=4,...,64` scored;
- fixed pulse width `0.15/64` of the normalized window;
- identical pulse count, width, peak and delivered energy per prefix;
- circular wrapping; overlapping coverage saturates at `1`;
- unknown source phase swept over `128` equally spaced values.

The width remains fixed as the prefix unfolds. Recomputing it from the final
observed `N` would leak knowledge of the stopping time.

### Arrival families

1. stationary `flat` null;
2. `beam7`, a seven-cycle periodic source;
3. `beam7_cycle23`, coupled seven- and twenty-three-cycle source;
4. `beam7_decay`, seven-cycle source under a muon-decay envelope with
   normalized lifetime `tau=0.45`.

These are idealized public-formula stress tests, not laboratory muon data.

### Fixed carrier candidates

Exact Phi `phi^-2`, reverse Phi `phi^-1`, `3/8`, `8/21`, `1/e`, `2/5`,
`sqrt(2)-1`, `1/3` and `pi-3`.

An evenly spaced schedule recalculated for every `N` is an **oracle
known-horizon ceiling**. It is ineligible for the fixed-carrier winner.

## Frozen metrics and gates

### G0 — implementation

All K0 checks pass; interval integration agrees with a dense numerical spot
check to absolute error `<=5e-4`; all overlaps lie in `[0,1]`.

### G1 — geometric prefix robustness

For every fixed candidate and prefix, calculate circular largest gap,
one-dimensional circular star discrepancy and repeat/overlap loss. Rank
candidates separately within every prefix for largest gap and discrepancy,
then average both ranks over all prefixes. Phi passes only if it is the unique
best eligible fixed candidate and ranks below `3/8`. The oracle is ineligible.

### G2 — Fusion robust overlap

For every non-flat family, candidate and prefix, calculate the fifth
percentile of \(f_X\) over unknown phase. Average equally across all three
families and `61` prefixes. Phi passes only if it is the unique best forward
fixed carrier, beats `3/8`, and beats `3/8` in at least `60%` of the `183`
family-prefix cells. Reverse Phi cannot rescue the forward prediction.

### G3 — unknown-horizon tail robustness

Take each candidate's fifth percentile across the `183` non-flat
family-prefix robust-overlap cells. Phi passes only if it is the unique best
forward fixed carrier and beats `3/8`.

### G4 — stationary null

On `flat`, no non-overlapping irrational schedule may differ from another by
more than `5e-4` at matched prefixes. Rational repeat losses are recorded as
expected schedule collisions. Phi gets no credit for merely matching null.

## Verdict

- **Supported for this scheduling model:** G0, G1, G2, G3 and G4 pass.
- **Mixed:** G0/G4 and at least two of G1-G3 pass.
- **Not supported:** fewer than two of G1-G3 pass.
- **Invalid:** G0 or the non-repeating portion of G4 fails.

The empirical calibration cannot change the Fusion verdict.

## Interpretation boundary

Even full support would mean only that Phi is an effective fixed,
prefix-robust carrier in this idealized overlap model. It would not prove that
natural muon-catalyzed Fusion has a Phi time vector, or that Phi improves
\(P_X\) or \(\eta_X\). Those require time-resolved experimental or validated
transport data.

