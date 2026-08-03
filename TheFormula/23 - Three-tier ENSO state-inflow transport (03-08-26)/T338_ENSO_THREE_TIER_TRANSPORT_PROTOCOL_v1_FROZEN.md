# T338 — ENSO three-tier state/inflow transport

**Frozen:** 3 August 2026, before numerical scoring  
**Geometry:** supplied and approved by Dylan La Franchi  
**Purpose:** test causal transport through the confirmed ARA hierarchy before
attempting an ENSO forecast

## Confirmed identity tree

```text
ENSO parent
├─ La Niña child (0-side)
│  ├─ oceanic expression (Phase A grandchild)
│  └─ atmospheric expression (Phase B grandchild)
└─ El Niño child (2-side)
   ├─ oceanic expression (Phase A grandchild)
   └─ atmospheric expression (Phase B grandchild)
```

Neutral conditions are a parent ridge neighbourhood, not a third pole and not
automatically an exact `1.0` month.

## Primary state cuts

- Oceanic grandchild: monthly Niño 3.4 SST anomaly, oriented positive toward
  El Niño.
- Atmospheric grandchild: monthly SOI, sign-reversed so that positive is
  oriented toward El Niño.
- Independent atmospheric replication: central-equatorial-Pacific OLR,
  sign-reversed because negative OLR denotes enhanced convection.

No series is simultaneously used as a state and an inflow.

Each source keeps its raw monthly anomaly. To compare unlike physical units,
the scale of each series is estimated once from the development interval only
and then held fixed. No rolling normalization, spectral decomposition, Fourier
transform, smoothing or retrospective event alignment is allowed.

Let the fixed-scale ocean and atmosphere readings be `O_t` and `A_t`, both
positive toward El Niño. The four non-negative grandchild strengths are

\[
L_O=\max(-O_t,0),\quad L_A=\max(-A_t,0),
\]

\[
E_O=\max(O_t,0),\quad E_A=\max(A_t,0).
\]

The two within-child ARA readings are

\[
x_L=2\frac{L_A}{L_O+L_A},
\qquad
x_E=2\frac{E_A}{E_O+E_A},
\]

when the denominator is non-zero. Here `0` is ocean-led, `2` is
atmosphere-led and `1` is their local equal-strength ridge. These are two
separate child relations and must not be averaged together.

The La Niña and El Niño child strengths are

\[
S_L=L_O+L_A,\qquad S_E=E_O+E_A,
\]

and the ENSO parent coordinate is

\[
\boxed{x_P=2\frac{S_E}{S_L+S_E}}.
\]

This is a declared ARA compression of the four retained grandchildren. The
uncompressed values remain in every output row.

## Primary inflow cuts

### Oceanic inflow

East and west warm-water-volume anomalies are retained separately. Their
directed redistribution coordinate is

\[
R_t=WWV_{east,t}-WWV_{west,t}.
\]

The monthly inflow cut is the unsmoothed change

\[
F_O(t)=R_t-R_{t-1}.
\]

Positive `F_O` is eastward/El-Niño-directed redistribution; negative `F_O` is
westward/La-Niña-directed redistribution. Basin-total WWV is not substituted
for this spatial transport cut.

### Atmospheric inflow

The CPC 850-hPa trade-wind anomaly indices for the western, central and eastern
equatorial Pacific are retained as three separate spatial cuts. CPC defines
positive values as easterly anomalies, so each is sign-reversed for the common
El-Niño-positive orientation:

\[
F_{AW}=-W_{850},\quad F_{AC}=-C_{850},\quad F_{AE}=-E_{850}.
\]

The three cuts must be reported separately. Their median may be used only as a
labelled parent-flow coarse grain after the uncompressed results have been
scored.

MJO/RMM is excluded from the primary test: it is not a direct westerly-wind-
burst measurement and its published processing changes in 2014. It remains a
candidate nearby/Other coupling for a later test.

## Frozen causal questions

The test follows the declared path rather than asking only for same-month
correlation.

1. Does `F_O(t)` predict the signed movement of the oceanic state
   `O(t+h)-O(t)`?
2. Do the western, central and eastern atmospheric inflow cuts predict the
   signed movement of the atmospheric state `A(t+h)-A(t)`?
3. Does the relation of oceanic and atmospheric inflow predict movement of the
   parent ARA coordinate `x_P(t+h)-x_P(t)`?
4. Are La-Niña-directed and El-Niño-directed results both present, or is an
   apparent whole-record result carried by only one pole?
5. Does the ordering support a transport chain rather than only a simultaneous
   state description?

## Time split and lag selection

- Common monthly record begins no earlier than January 1980.
- Development: January 1980 through December 2004.
- Untouched holdout: January 2005 through the latest complete common calendar
  year, expected to be December 2025.
- Candidate positive leads: `h = 1..18` months.
- For each primary path, choose one lead on development data by maximum
  balanced directional accuracy; ties choose the shortest lead.
- The chosen lead and orientation are then applied once to holdout.
- Lead zero is descriptive only and cannot pass the causal gate.

## Scores

For every uncompressed path report:

- balanced directional accuracy;
- signed Spearman association with future state change;
- El-Niño-directed and La-Niña-directed recall separately;
- sample count and missing-data count;
- a moving-block bootstrap 95% interval using 24-month blocks.

The parent coarse grain is supplementary until all component paths are shown.

## Pass, mixed and fail gates

A primary path passes only if, on holdout:

- balanced directional accuracy is greater than `0.55`;
- its 95% moving-block-bootstrap lower bound is greater than `0.50`;
- its signed Spearman direction agrees with the frozen orientation;
- both phase-direction recalls exceed `0.50`.

The architecture is **supported** only if the ocean path passes and at least two
of the three atmospheric spatial cuts pass. It is **mixed** if some individual
paths pass but that joint gate does not. It is **not supported** if neither
branch provides a passing path.

No threshold may be relaxed after holdout scoring.

## Controls and falsifiers

The following are mandatory:

- wrong orientation for each flow;
- time-reversed flow;
- month-preserving shuffled years;
- persistence/no-inflow direction baseline;
- OLR replacement of SOI as an atmospheric-state replication;
- central-Pacific 0–300 m heat content as an ocean-reservoir replication, kept
  distinct from east/west WWV redistribution.

Evidence against the proposed transport geometry includes:

- holdout performance at chance despite development selection;
- reversed or shuffled controls matching the frozen direction;
- a result confined to only El Niño or only La Niña;
- simultaneous association with no positive-lead transport;
- success appearing only after averaging away the three wind cuts.

## Claim boundary

This test can support or falsify the declared **transport crosswalk**. It cannot
by itself establish that ARA is fundamental, prove a physical energy budget,
or constitute a competitive ENSO forecast. Forecasting is authorized only
after the state/inflow route survives untouched holdout data.

