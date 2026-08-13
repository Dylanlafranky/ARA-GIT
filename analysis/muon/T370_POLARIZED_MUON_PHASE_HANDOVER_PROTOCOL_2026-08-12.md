# T370 — Polarized-muon parent-phase handover

## Frozen scope

This test asks whether a relation already present in a polarized muon before
decay predicts the two-sided directional allocation observed after decay.

### Who

An ensemble of positive surface muons stopped in the EMU instrument. The
incoming beam is polarized. The public raw acquisition is recorded by 96
positron detectors.

### What

Two distinct statements are tested and must not be conflated:

1. **Decay closure crosswalk:** in the rest frame of a stopped muon, the
   detected positron and the combined two-neutrino packet exhaust the daughter
   energy-momentum budget.
2. **Parent-phase handover:** the pre-decay muon-spin phase predicts which
   detector direction receives more visible positron flow at a given delay.

The neutrino pair is treated as one hidden combined packet. It is not treated
as two separately reconstructed neutrinos.

### When and where

The handover occurs at muon decay. The empirical cut is made in the detector
plane of the same stopped-muon ensemble, from 0.25 to 6.0 microseconds after
the corrected pulse origin. Raw 16 ns channels are predeclared to be summed in
groups of four (64 ns) before fitting.

### Why

The earlier stopped-muon archive exposed only decay time and electron momentum.
It could not observe a parent directional phase. EMU supplies an independent
pre-handover phase carrier and many opposing directional cuts, allowing the
parent relation to be estimated without defining the hidden side from the
visible result after the event.

### How

For detector `d` and time bin `t`, let `N[d,t]` be raw positron counts and

```text
S[d,t] = N[d,t] / sum_d N[d,t]
```

be its share of the live detector sphere. A detector-specific development
baseline `b[d]` is calculated from the first half of the time interval, and

```text
Y[d,t] = S[d,t] / b[d] - 1
```

is the measured directional child departure.

The minimal ARA parent-phase model is one common circular phase with
detector-specific two-sided projections:

```text
Y_hat[d,t] = c[d]
           + exp(-lambda t)
             * (A[d] cos(2 pi f t) + B[d] sin(2 pi f t)).
```

The shared `f` and `lambda`, and every detector coefficient, are chosen using
only the development interval `0.25 <= t < 3.0 us`. The untouched holdout is
`3.0 <= t < 6.0 us`.

The same detector-specific development baselines are used for all candidates.

## Frozen controls

- **No-phase:** each detector remains at its development mean.
- **Persistence:** each detector remains at its final development value.
- **Wrong orientation:** reverse the handedness of the fitted circular phase
  by changing the sign of the sine coordinate while retaining all fitted
  coefficients.
- **Independent acquisitions:** repeat the identical frozen procedure on all
  downloaded runs; no result from one acquisition selects parameters for
  another.

## Frozen primary gates

The parent-phase handover is supported on an acquisition only if, on holdout:

1. the ARA phase model has lower count-weighted RMSE than no-phase;
2. it has lower count-weighted RMSE than persistence;
3. it has lower count-weighted RMSE than wrong orientation; and
4. predicted and measured detector departures have positive Pearson
   correlation.

Cross-acquisition support requires at least three of four acquisitions to pass
all four gates. Median detector-level bootstrap and circular detector-shift
controls are reported as sensitivity checks.

## Claim boundary

The exact positron ↔ combined-neutrino closure is conservation bookkeeping and
cannot validate ARA by itself. The empirical result is whether a common parent
phase predicts untouched visible directional allocation. Even a pass is a
crosswalk/recovery result unless ARA outperforms the established polarized
muon-decay phase model; here their simplest mathematical forms coincide.

