# T455 frozen protocol — two clocks and geographic polar motion

Frozen after verifying the official IERS file structure, before inspecting the
T455 outcome.

## Who / what / where / when / why / how

- **Who:** Earth is the measured parent identity.
- **What:** a uniform atomic day and Earth's observed rotation day are the two
  clocks. Geographic polar motion is an independently recorded child of the
  same Earth system.
- **Where:** the primary relation is the difference between Earth-rotation
  progression and atomic progression. The polar-motion child is retained as a
  two-dimensional path, not added to the clock ledger as though arcseconds and
  seconds were the same unit.
- **When:** daily IERS EOP C04 observations from 1 January 1984 onward. All
  development, validation and holdout divisions are chronological.
- **Why:** test whether an ARA/Irrationality-Di-ARA description of the moving
  rotation pole contains prospective information about the next Earth-clock
  deviation, and whether the result survives changes in temporal grain.
- **How:** rebuild the same dimensionless geometry at 1, 7, 30 and 90 day
  grains; predict the next complete window from past and present information
  only; compare clock-only and clock-plus-pole models against false-time
  controls.

## Source and physical observables

Source: IERS Earth Orientation Centre, EOP 20u24 C04 0 h UTC daily series.

- `LOD`: observed excess of the Earth's rotation day over 86,400 SI seconds.
- `UT1-UTC`: observed Earth-rotation phase relative to civil UTC. It is shown
  for traceability but not used as the continuous model target because leap
  seconds insert human-made steps.
- `x_pole`, `y_pole`: geographic rotation-pole coordinates in arcseconds.
- `x_rate`, `y_rate`: reported pole-coordinate rates in arcseconds per day.

The uninterrupted two-clock rate is

\[
s_T=\frac{86400+\overline{LOD}}{86400},\qquad
u_T=\log s_T,\qquad
x_T=\frac{2s_T}{1+s_T}.
\]

`x_T=1` is an Earth day equal to the atomic day. The exact coordinate will be
extremely close to the ridge; plots must therefore show both the honest 0–2
location and a labelled ridge-centred magnification.

## Geographic-pole child and its Irrationality Di-ARA

At each temporal grain `tau`, form non-overlapping complete windows. Let

\[
P_k=\overline{x}_{p,k}+i\overline{y}_{p,k},\qquad
\Delta P_k=P_k-P_{k-1}.
\]

The child's amount relation and signed turn are

\[
s_{P,k}=\frac{|\Delta P_k|}{|\Delta P_{k-1}|},\qquad
x_{P,k}=\frac{2s_{P,k}}{1+s_{P,k}},
\]

\[
\delta_k=\operatorname{wrap}(\arg\Delta P_k-\arg\Delta P_{k-1}),\qquad
y_{P,k}=1+\frac{\delta_k}{\pi}.
\]

Thus `(x_P, y_P)` is the typed geographic-pole Irrationality Di-ARA:
reciprocal change in displacement amount crossed with signed traversal. It is
not silently relabelled as Time.

## Frozen prediction question

For each grain, predict next-window mean `LOD` at horizons 1, 2 and 4 windows.

1. **Persistence:** current window mean `LOD`.
2. **Clock-only:** fixed ridge regression using three causal clock lags,
   current clock slope and current clock ARA/log coordinate.
3. **Clock + raw pole:** clock-only terms plus current/past `x_pole`, `y_pole`
   and their causal displacements.
4. **Clock + pole Di-ARA:** clock-only terms plus `x_P`, `y_P`, `log(s_P)`,
   signed turn and displacement amount.
5. **Full child:** raw-pole and pole-Di-ARA terms together.

Every linear model uses development-only standardisation and a fixed ridge
penalty `alpha=1`. No outcome-selected landmark, offset or lag is fitted.

## Chronological partitions

- Development: 1984–2008.
- Validation: 2009–2016.
- Untouched holdout: 2017 through the final complete source window.

Rows requiring prehistory or a future target stay outside scoring. Models are
fit on development only. Validation describes calibration transfer; the
holdout is opened once for the frozen result.

## Scale-invariance tests

The coordinate equations are identical at 1, 7, 30 and 90 day grains. Scale
is represented only by how raw observations are aggregated into complete
windows. The following are reported separately:

1. shape and quadrant occupancy at every grain;
2. holdout forecast error at every grain and horizon;
3. sign and size of the pole-child improvement over clock-only;
4. coefficient-direction similarity across grains after development-only
   standardisation;
5. a pooled model trained on development rows from three grains and tested on
   the omitted grain after within-grain development scaling.

Numerical equality across grains is not required. Scale invariance means the
same declared geometry retains directionally useful structure when the window
is changed, without redefining its axes.

## False-time and geometry controls

- circularly shift the polar child by 365 days before aggregation;
- reverse the polar chronology while retaining the clock chronology;
- reflect the traversal coordinate `y_P -> 2-y_P`;
- retain the clock history but randomly permute whole calendar-year pole
  blocks with a fixed seed.

Controls are evaluated with the same model size. A control cannot be called a
new phase after the result.

## Frozen gates (secondary to the full geometry)

1. Full child improves 1-window holdout MAE over clock-only at at least three
   of four grains.
2. Median 1-window improvement across grains is positive.
3. At least one child model beats persistence at every grain.
4. The real child beats all four false-time/control versions in median
   cross-grain improvement.
5. Leave-one-grain-out transfer improves clock-only at at least three of four
   omitted grains.
6. The exact Earth-clock ARA remains near its physically expected ridge and is
   not rescaled to manufacture visible 0–2 excursions.

Passing would support a scale-transportable relational child for the
Earth-clock deviation. It would not prove that polar motion causes time, that
the child is Time itself, or that all systems share Earth's coefficients.

## Deferred magnetic child

Magnetic-pole drift is not included in T455. Its public historical record is
much coarser than daily EOP C04 and represents the geomagnetic field rather
than the geographic rotation axis. It can be added later as an independently
timed deep-Earth child after a same-grain or explicitly cross-rung protocol is
frozen.

