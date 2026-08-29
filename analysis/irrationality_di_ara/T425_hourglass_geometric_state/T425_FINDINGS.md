# T425 — Hourglass Irrationality Di-ARA comparison

## Question

Does the older geometric/state Irrationality Di-ARA recover additional
structure when applied to the same held-out hourglass histories used by T424?

This is an instrument comparison, not a new-event prediction test.

## Matched inputs

- Same 16 held-out Toyoura-sand discharges as T424.
- Same T424 pre-closure windows and state coordinates.
- No video re-extraction and no refitting of the T424 instrument.
- Frozen T425 protocol SHA-256:
  `BA48F5066E4B237031A7A25305A81EBD96F076B9B9CEE1F910531DBF4665AFFD`.

## The two cuts

### T424 dynamic/state cut

T424 describes the current relation between:

- `C1`: movement / traversal;
- `C2`: connection / packing.

It answers: **what kind of state is the hourglass occupying now?**

### T425 geometric movement-of-state cut

T425 first centres the same T424 state plane:

\[
z_t=(C1_t-1)+i(C2_t-1),
\]

then measures the quotient between consecutive states:

\[
q_t=\frac{z_{t+1}}{z_t}=s_t e^{i\Delta\theta_t}.
\]

The two ARA coordinates are:

\[
X_t=\frac{2s_t}{1+s_t},
\qquad
Y_t=1+\frac{\Delta\theta_t}{\pi}.
\]

It answers: **how did the state move between these two slices?**

## Primary result

Equal-run mean quadrant occupancy was:

| Instrument | Quadrant / sector | Share |
|---|---|---:|
| T424 current state | connection-heavy | 79.03% |
| T424 current state | movement-heavy | 16.21% |
| T424 current state | both-low | 2.64% |
| T424 current state | both-high | 2.12% |
| T425 movement of state | expanding forward | 59.16% |
| T425 movement of state | contracting reverse | 27.55% |
| T425 movement of state | expanding reverse | 11.53% |
| T425 movement of state | contracting forward | 1.77% |

All 16 runs entered the expanding-forward and contracting-reverse sectors.
Eight of 16 runs entered all four geometric sectors at least once; seven did
so with at least 1% occupancy in every sector.

Therefore the apparent one-quadrant concentration in T424 does **not** carry
over unchanged to the second instrument. The sand state is mostly
connection-heavy, while the movement of that state is predominantly
expanding-forward with a substantial contracting-reverse return component.

## Sampling-scale finding

At the primary one-frame separation, the equal-run median `X` and `Y`
histories lie extremely close to the 1.0 ridge. This is not the same claim as
"no movement": each densely sampled transition is small, while the signs of
its radial and angular changes still assign sectors.

A post-freeze sensitivity view retained the same quotient and changed only
the temporal separation:

| Lag | Expanding forward | Contracting reverse | Expanding reverse | Contracting forward |
|---:|---:|---:|---:|---:|
| 1 frame | 59.16% | 27.55% | 11.53% | 1.77% |
| 3 frames | 51.04% | 30.11% | 14.26% | 4.59% |
| 6 frames | 48.28% | 27.64% | 16.38% | 7.70% |
| 12 frames | 48.41% | 25.17% | 16.85% | 9.56% |

The coordinate cloud opens progressively with longer cuts, and the rarer
contracting-forward sector becomes more visible. This is scale sensitivity,
not a selected winning lag and not a new frozen gate.

## Event boundary

Seventeen direct closure events had a preceding valid geometric state. Their
median coordinate was approximately:

\[
(X,Y)=(1.000012,\ 1.000009).
\]

Sixteen of those events are terminal closures, so the near-ridge value is
partly expected: once the observed state stops changing, the quotient tends
toward the identity relation `q = 1`. This result describes the resolved
closure and must not be presented as advance prediction.

## Interpretation boundary

- Supported as an exact application of the frozen geometric instrument: the
  two hourglass cuts expose different relational information.
- Descriptively supported: the second cut has multi-sector directional
  structure that is hidden by the connection-heavy state concentration.
- Unresolved: whether the sector histories can forecast closure causally.
- Not supported here: universal `e`, `1/e`, `phi`, or reciprocal-`phi`
  landmarks. Those coordinates remain historical references, not gates.

