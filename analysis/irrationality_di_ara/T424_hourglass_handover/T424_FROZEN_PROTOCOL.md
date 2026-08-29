# T424 — Time-facing Irrationality Di-ARA in a real hourglass

**Status:** frozen before any movie is downloaded, decoded, or scored  
**Frozen:** 23 August 2026 (Australia/Brisbane)  
**ARA hypothesis and geometry:** Dylan La Franchi  
**Operationalisation and implementation:** Codex

## Relational address

- **Who:** one real granular hourglass discharge at a time. The measured parent
  identity is the upper reservoir–throat–lower reservoir system. Throat
  traversal and near-throat packing are the two measured child relations.
- **What:** two independently constructed 0–2 histories:
  `x_trav` for movement/traversal through the throat and `x_conn` for persistent
  packing/connection adjacent to the throat. Their joint plane is tested as an
  Irrationality Di-ARA; neither coordinate is defined as `2 -` the other.
- **When:** frame by frame, using only the current and past frames for any
  forecast, from the end of the apparatus flip through discharge and final
  settling. Flow onset, micro-jam release, and terminal closure are kept as
  distinct event types.
- **Where:** a fixed throat strip plus fixed upper and lower packing bands in
  the camera view. This is a time-facing cut of the hourglass identity, not an
  average over the entire seven-hour experiment and not a single-grain cut.
- **Why:** test whether the coupled movement/connection relation records and
  leads physical handovers better than declining sand amount, either child
  coordinate alone, or time alone.
- **How:** derive traversal from optical flow through the throat and connection
  from lagged texture persistence in the adjacent packed bed; calibrate both
  independently on development movies; freeze the joint event rule; score it
  on held-out materials and hopper angles with chronological, circular-shift,
  and single-axis controls.

## Source and medium

Primary source:

- S. Ozaki et al., *Granular flow experiment using artificial gravity
  generator at International Space Station*, **npj Microgravity** 9, 61 (2023),
  DOI `10.1038/s41526-023-00308-w`.
- Public OSF data: `https://osf.io/3zcm2/`.
- The apparatus is a literal hourglass-shaped quasi-2D hopper in vacuum. The
  onboard camera records H.264 MP4 at 25 frames/s. The hourglass flips every
  60 s; artificial gravity ranges from 0.063 to 2.0 G.

This is a granular solid medium moving through a narrow throat. It is not
silicone filament breakup, water-droplet coalescence, or a synthetic hourglass.
The external gravity/centrifugal field supplies the larger forcing wave; this
test measures how the local hourglass identity routes that forcing between
packing and traversal.

## Frozen source split

The split is by material, not by randomly mixed frames.

| Role | Files |
|---|---|
| Development | `SN101_Alumina_060.mp4`, `SN101_Alumina_120.mp4`, `SN102_SilicaSandNo5_060.mp4`, `SN102_SilicaSandNo5_120.mp4` |
| Primary holdout | `SN103_ToyouraSand_060.mp4`, `SN103_ToyouraSand_120.mp4` |
| Hard transfer only | `SN203_SilicaSandNo8.mp4`, `SN104_LunarRegolithsieved.mp4`, `SN201_PhobosRegolith.mp4`, `SN202_MartianRegolith.mp4`, `SN204_LunarRegolith.mp4` |

The hard-transfer files may contain adhesion, aggregation, funnel flow, or
bridging. They are not pooled into the primary pass/fail gate.

## Source-QA exception

Before wave extraction, the script may inspect frame geometry solely to:

1. detect the hourglass boundary and throat position;
2. detect the 180° flip interval;
3. mask overlays, timestamps, static frame borders, and apparatus hardware;
4. register fixed throat and adjacent packing regions; and
5. split the published montage into its eight labelled gravity-condition
   discharge runs. The 25-fps development movies contain exactly 1,600 frames
   (eight 200-frame condition blocks). The Toyoura holdout uses unequal block
   durations, so its seven boundaries are registered from the source's visible
   `AG = ... G` overlay before either holdout ARA coordinate is extracted or
   scored. Optical flow across each condition boundary is excluded.

No ARA coordinate, crossing, event score, or holdout outcome may be inspected
while setting these source-geometry parameters. Any manual correction must be
recorded in a machine-readable ROI register before signal extraction.

## Direct event targets

Targets are defined from reservoir occupancy outside the throat-feature region,
so the target is not the same number as `x_trav`.

For each run let `M_u(t)` and `M_l(t)` be the foreground grain area in fixed
upper and lower reservoir masks. Define the robust, causally smoothed transfer
rate

\[
q_M(t)=-\Delta M_u(t)=\Delta M_l(t)
\]

after rejecting flip-motion frames.

- **Flow onset:** first five-frame interval after the flip with positive
  transfer in both reservoir measures.
- **Micro-jam onset:** at least four frames with transfer below 15% of that
  run's established-flow median while upper material remains.
- **Micro-jam release:** first three-frame return above 40% of the established-
  flow median after a micro-jam.
- **Terminal closure:** first eight-frame interval below 10% of established
  flow after upper occupancy has fallen below 10% of its run maximum.

Thresholds are frozen here. When compression or image quality prevents direct
grain segmentation, the run is excluded rather than relabelled from the ARA
coordinates.

## Two independent child coordinates

### Child C1 — traversal / movement

Within a narrow throat strip, dense optical flow gives pixel velocity `v`.
The raw traversal participation is

\[
T_{raw}(t)=\operatorname{median}_{p\in throat}
\left|v_p(t)\cdot \hat n\right|,
\]

where `n` is the local throat normal directed from the current upper reservoir
to the lower reservoir. Apparatus-flip frames are excluded.

### Child C2 — connection / packing

Within the adjacent upstream packing band, connection is measured as lagged
texture persistence after compensating for the local coherent translation:

\[
C_{raw}(t)=\operatorname{median}_{\ell=1,2,3}
\operatorname{corr}\!\left(I_t,\,\mathcal W_{t\leftarrow t-\ell}I_{t-\ell}\right).
\]

`W` warps the earlier texture by the measured local coherent motion. This
distinguishes persistent neighbour packing from mere shared translation. It is
measured from image texture, not calculated from `T_raw`.

### Independent ARA calibration

Development runs alone freeze the 5th and 95th percentiles of
`log1p(T_raw)` and Fisher-transformed `C_raw`. Each is mapped independently:

\[
x_W=2\,\mathrm{clip}\left(\frac{W-q_{05,W}}{q_{95,W}-q_{05,W}},0,1\right),
\qquad W\in\{trav,conn\}.
\]

A causal exponential moving average with `alpha = 0.25` is applied after
mapping. No complement or sum-to-two constraint is imposed.

## Coupled Di-ARA measurements

The primary joint descriptors are:

\[
d_{eq}(t)=\frac{|x_{trav}(t)-x_{conn}(t)|}{\sqrt 2},
\qquad
s(t)=\frac{x_{trav}(t)+x_{conn}(t)}{2},
\]

plus the signed difference `z=x_trav-x_conn`, its causal derivatives, and the
four quadrants formed by each coordinate's 1.0 ridge. The ridges are geometric
landmarks, not compulsory exact event values; material asymmetry may displace
individual events.

## Development-registered handover rule

Using development runs only:

1. locate candidate sign changes of `z` and local minima of `d_eq`;
2. describe the 12-frame past-only path with current `x_trav`, current
   `x_conn`, their causal slopes, `d_eq`, `s`, and time since the last quadrant
   change;
3. fit one regularised logistic event-risk model to predict whether a direct
   onset/release/closure occurs in the next 3–12 frames;
4. freeze its coefficients and one operating threshold before holdout scoring.

This is the operational Irrationality Di-ARA forecast. It is compared with:

- time since flip only;
- upper-reservoir amount only;
- `x_trav` only;
- `x_conn` only;
- the same joint features after within-run circular shifting of `x_conn`;
- shuffled event times preserving event count per run.

## Frozen gates

### Instrument validity

- `|corr(x_trav,x_conn)| < 0.98` on development and holdout;
- `std(x_trav+x_conn) > 0.05`;
- neither coordinate is reconstructible as `2 -` the other to numerical
  tolerance.

Failure means the intended Di-ARA was flattened into one ARA/complement and the
joint result is invalid.

### Structural handover gate

On primary holdout runs, the median nearest-event `d_eq` and event-conditioned
joint-path distance must beat 10,000 within-run circular shifts by at least 20%,
with empirical `p < 0.05`. Report onset, release, and terminal closure
separately before any pooled statistic.

### Predictive gate

On primary holdout runs, the frozen joint model must:

- beat each named single-source baseline in event-window average precision;
- improve Brier score over the best baseline by at least 10%; and
- retain positive median warning lead, reported in frames and seconds.

The primary forecast excludes onset because the apparatus flip is an obvious
external cue. Onset remains a structural control. Micro-jam release and terminal
closure are the predictive targets.

## Required visual evidence

1. labelled source frame with upper/lower reservoirs, throat, and packing band;
2. aligned `x_trav`, `x_conn`, direct events, and forecast probability through
   representative development and untouched holdout runs;
3. 0–2 by 0–2 Di-ARA trajectories, with direction arrows and event markers;
4. event-centred small multiples by material and hopper angle;
5. holdout comparison against every frozen baseline and null;
6. excluded-run register with a visible reason.

## Interpretation boundary

A pass would support a time-facing, independently measured movement/connection
Di-ARA that transfers across real granular identities and contains prospective
handover information. It would not prove a universal irrationality law, that
the coordinate causes grain motion, or that every medium must visit the same
quadrants in the same order. A failure would reject this operationalisation on
the hourglass source without rejecting ARA or the broader Di-ARA geometry.
