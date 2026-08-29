# T428 — Paired-phase spacetime Di-ARA

Frozen before scoring the five T427 holdouts. T427 remains unchanged.

## Question

Did T427 plot two leading-side observables, rather than the Phase A and Phase B
of one ARA identity? If so, do separately measured opposing behaviours recover
two paired ARAs whose relation forms a more faithful time-facing Di-ARA?

## ARA identity and scale

- Observed parent: the received binary-black-hole strain history at one detector.
- Replicates: H1, L1 and V1 detector streams; H1/L1 form the primary network
  comparison and V1 is a secondary independent view when available.
- Time window: -1.50 to +0.25 seconds relative to the published event GPS. The
  GPS is used only to retrieve and crop the data.
- Calibration population: the same off-source intervals as T427,
  [-12,-4] and [4,12] seconds.
- Development event: GW150914 only.
- Untouched holdouts: GW170104, GW170608, GW170809, GW170814 and GW170818.

## Four separately measured candidate wave sides

Every feature is calculated from the same fixed 64 ms STFT with a 4 ms hop and
30–512 Hz band used in T427. The pairs are not forced to sum to 2.

1. Traversal candidate A, `T_A`: native spectral power plus spectral change
   (Hellinger displacement and ridge-frequency motion). This is the corrected
   name for T427 C1.
2. Traversal candidate B, `T_B`: adjacent-frame complex spectral persistence,
   measured as normalized complex overlap after removing the deterministic STFT
   hop phase. It asks how much of the waveform remains coherently carried into
   the next time slice.
3. Connection candidate A, `K_A`: spectral concentration, measured as one minus
   normalized spectral entropy. This is the corrected name for T427 C2.
4. Connection candidate B, `K_B`: normalized effective spectral width around the
   power-weighted centroid. It measures independently exposed dispersion rather
   than defining `K_B = 2-K_A`.

`T_B` and `K_B` are independent functionals of the measured complex spectrum.
They are expected to oppose their named partners in some regimes, but no sign,
sum or crossing is imposed.

## Local child ARA projection

Each raw feature is mapped independently to 0–2 by its detector-specific
off-source empirical cumulative distribution:

    x = 2 * F_off(raw feature)

The off-source median is therefore the local child ridge x=1. Event values may
approach either pole. This deliberately expands the child-scale basin that T427
compressed beneath a parent 3-sigma ridge. It does not force two features to be
complements.

## Relations to score

For each detector and pair:

- TE-ARA closure residual: `abs(A + B - 2)`.
- Pair opposition: Spearman correlation between A and B.
- Handover proximity: `abs(A-B)` and its local minima.
- Traversal around the pair plane: chronological path length and signed angular
  travel around (1,1).

For the coupled Di-ARA:

- simultaneous pairedness: root-mean-square of the two closure residuals;
- coupled handover: both pair gaps fall below the development-frozen threshold;
- phase ordering: whether the two pair crossings occur in the same order in H1
  and L1;
- network agreement: four-coordinate H1/L1 distance after a frozen +/-10 ms
  lag search on `T_A` only.

## Development-only freezing

GW150914 determines:

- the coupled-handover gap threshold: the 20th percentile of its event-window
  coupled gap;
- the closure-improvement threshold: its event median closure must be lower than
  at least 75% of equal-duration off-source windows;
- the network-agreement threshold: the 25th percentile of its H1/L1 agreement.

These numeric values are written to `T428_DEV_FREEZE.json` before holdout scoring.

## Primary holdout gates

The paired-phase hypothesis is supported only if all are true:

1. At least 4/5 holdouts have event-window median simultaneous closure better
   than at least 75% of their own off-source windows.
2. At least 4/5 contain a persistent coupled-handover run of three frames using
   the development-frozen gap threshold.
3. At least 4/5 have median H1/L1 four-coordinate agreement above the frozen
   development threshold.
4. Matched-event H1/L1 agreement beats wrong-event pairings in at least 75% of
   comparisons.
5. The same result is not reproduced by more than 5% of 1,000 circular time
   shifts per holdout.

No requirement is placed on an absolute (0.5,1.5) address or on the published
event peak. Failing a universal gate does not erase descriptive geometry; it
keeps it at exploratory tier.

## Visual contract

The report must show:

- the four measured histories with 0, 1 and 2 landmarks;
- Traversal ARA (`T_A` vs `T_B`) and Connection ARA (`K_A` vs `K_B`) side by side;
- the coupled four-coordinate history and closure residuals;
- detector-separated and H1/L1-consensus paths;
- holdout small multiples on identical 0–2 scales;
- off-source and time-shift controls;
- native onset labelled as native onset, never as opening unless the paired gate
  independently passes.

## Interpretation boundary

A pass would support a reproducible paired relational instrument in these strain
data. It would not by itself identify the four coordinates with literal internal
black-hole components or establish ARA as a new gravitational law. A failure
would falsify this particular four-feature pairing and local projection, not the
general ARA framework.
