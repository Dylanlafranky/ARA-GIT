# ARA Cross-Rung Recycling Model

**Status:** working framework equation, not yet empirically validated.

## Correction

Recycling is not primarily a same-junction feedback loop.

The base geometry is a **Space pipe of width 2** attempting to hand flow into a
**Time pipe of width phi**:

```text
Space pipe:  2
Time pipe:   phi
Gap:         G = 2 - phi = 0.381966...
```

`G` is the geometric mismatch or diversion landmark. It is not automatically
the amount permanently lost by a real system.

If the incoming Space-pipe flow is normalized to `1`, distinguish the absolute
ARA-width gap from the normalized diverted share:

```text
G = 2 - phi                  # ARA-width mismatch
g = (2 - phi) / 2            # normalized one-pass diverted share
tau = phi / 2                # normalized direct Time-pipe share
g + tau = 1
```

Both conventions are useful, but they must not be conflated.

## Cross-Rung Flow

There is one underlying octave ladder read along two axes. Do not confuse the
intrinsic rung size with its projected reading:

```text
intrinsic octave ladder:  x2, x4, x8, ...
Space-axis reading:       2              # viewed head-on
Time-axis reading:        2 cos(36 deg)  # viewed through the shear
                        = phi
```

The Space-axis reading controls the head-on capacity or density change when a
packet falls between differently sized systems. The Time-axis reading controls
the effective relational handoff sequence as recycled energy works through the
return path. Its observed step is `phi`, but the underlying rung is still an
octave. The `2 - phi` gap exists because one `x2` octave read head-on is being
handed into the same octave read through a `36 degree` shear:

```text
phi = 2 cos(36 deg)
```

The trigonometric identity is exact mathematics. Treating physical Time as the
octave viewed through that fixed shear is the framework conjecture.

### Static projection versus recursive handoff

Keep one additional distinction explicit:

```text
static projection of an x4 length:     4 cos(36 deg)
two staged projected handoffs:         (2 cos(36 deg))^2 = phi^2
```

These are not numerically identical. The Time-ladder sequence
`phi, phi^2, phi^3, ...` therefore requires the `36 degree` projection to recur
at each handoff. That recursive re-projection fits the fractal gate picture,
but it is a physical framework conjecture to test, not a consequence of the
single trigonometric identity alone.

## Fractal Gate Invariant

The stronger framework claim is that the local handoff geometry repeats at
every scale. There is not one special foundational gate followed by unrelated
mechanics. Each subsystem contains the same Space-to-Time transfer shape at its
own size:

```text
intrinsic Space step at gate k:     S_(k+1) = 2 * S_k
projected Time step at gate k:      T_(k+1) = 2 cos(36 deg) * T_k
                                   = phi * T_k
local width mismatch at gate k:     gap_k = (2 - phi) * scale_k
```

After `n` repeated handoffs:

```text
Space-axis scale:  2^n
Time-axis scale:   (2 cos(36 deg))^n = phi^n
```

The same local transfer proportions recur:

```text
direct share:    phi / 2
diverted share:  (2 - phi) / 2
```

The geometry repeats, but the realized outcome does not have to be numerically
identical at every rung. Each scale has its own:

```text
available energy
reservoir fill
permanent dissipation
phase position
terrain address
gate openness
contact orientation
external forcing
```

That distinction matters for prediction. The repeated rule supplies the
architecture. The measured local state determines what the architecture does
on this tick.

### Recursive reservoir form

For scale `k`, write:

```text
Q_k(t)          available flow at the current gate
D_k(t)          direct projected Time flow
V_k(t)          diverted flow entering the lower reservoir route
L_k(t)          permanently lost flow
R_k(t)          recyclable lower-rung deposit

D_k(t) = (phi / 2) * Q_k(t)
V_k(t) = ((2 - phi) / 2) * Q_k(t)
L_k(t) = lambda_k(t) * V_k(t)
R_k(t) = (1 - lambda_k(t)) * V_k(t)
```

The lower rung applies the same rule again after rescaling and delay. Its
release is not automatic: it returns upward only when its local gate opens.

This gives the next predictor a compact target:

```text
one repeated gate equation
+ measured state at each rung
+ causal gate-opening rule
+ cross-rung delay
```

Do not replace the hierarchy with a single global recycling coefficient.

At rung `k`, let:

```text
Q_k(t)        available incoming flow
lambda_k(t)   irrecoverable-loss fraction of the diverted flow
C_k           characteristic capacity or scale of rung k
```

The idealized handoff becomes:

```text
direct_time_k(t) = tau * Q_k(t)
diverted_k(t)    = g * Q_k(t)
lost_k(t)        = lambda_k(t) * diverted_k(t)
recyclable_k(t)  = (1 - lambda_k(t)) * diverted_k(t)
```

The recyclable part falls into a smaller, faster rung below the current
system. It may fall one rung or two rungs before returning:

```text
deposit_(k -> k-m)(t) = recyclable_k(t) * gate_(k,m)(t)

m = 1  adjacent lower rung
m = 2  two rungs down, if same-spin matching is required
```

## Density Across Scale

A packet falling from a larger rung into a smaller rung does not create energy.
It becomes **larger relative to the capacity of the receiving rung**:

```text
relative_density_(k -> j)(t)
    = deposit_(k -> j)(t) * C_k / C_j

j < k
```

For exact octave spacing, `C_k / C_(k-m) = 2^m`. For a real measured system,
use the observed scale relationship rather than assuming an exact octave. The
return timing is the same octave geometry read along the Time axis, so its
effective projected step is `phi^m` rather than the head-on density multiplier
`2^m`.

This is the whale-corpse or falling-leaf effect:

* the falling packet may be modest relative to the large system that shed it;
* the same packet can be a dense forcing event for the smaller system below;
* the lower system processes that forcing at a faster cycle rate;
* some processed energy works upward again through the rung stack.

## Lower Reservoir and Return

Let `B_j(t)` be the stored recyclable energy in lower rung `j`:

```text
B_j(t+1)
    = decay_j * B_j(t)
    + sum_k deposit_(k -> j)(t) * C_k / C_j
    - release_j(t)
```

The lower rung returns energy upward when its phase, terrain, and contact gate
allow release:

```text
upflow_(j -> j+1)(t)
    = eta_j(t)
    * release_j(t)
    * orientation_j
```

where `eta_j(t)` is the realized transfer efficiency after local turbulence and
propulsion losses.

## Spin Parity

Physical rolling contact flips orientation between adjacent layers:

```text
orientation_(j -> j+1) = -orientation_j
```

After crossing two layers:

```text
orientation_(j -> j+2) = +orientation_j
```

This gives a concrete reason that some recyclable flow may need to descend two
rungs before it can return through a same-spin gate. It also explains why a
single global minus sign failed in the first joint ENSO test: different edges
have different roles.

Do not conflate:

* physical layer-to-layer rolling parity;
* a matched-rung anti-phase relation;
* an upper-shell brake or grip;
* the sign convention of an observed index such as SOI.

### Contact transfer versus coherent absorption

One refinement remains open:

```text
contact transfer is not automatically coherent absorption
```

Adjacent counterspinning layers can still pass force into each other, like
touching gears. But a recyclable packet may settle cleanly only in a layer with
matching orientation:

```text
orientation_k       = +1
orientation_(k - 1) = -1    # adjacent contact: pressure / turbulence
orientation_(k - 2) = +1    # same-spin candidate: coherent storage
```

In that reading, a dense falling packet can pass through the adjacent layer
and settle two physical rungs down before working upward again. The
intermediate layer still changes timing, direction, and wobble.

First ENSO ablation:

```text
TheFormula/Claude4.8/ARA_ENSO_LEAF_SAME_SPIN_ROUTE_RESULT.md
```

The strict-causal monthly test does not establish this law. It gives a small
compatible hint: one-rung storage is slightly better around `3-6 months`,
while two-rung same-spin storage is slightly better around `9-18 months`.
The frozen `30-60 month` extension also does not isolate a distinct two-rung
return. The effect is too small to claim confirmation. It may already be
partly encoded in the ordinary recursive equation, or the monthly proxy may be
too coarse. A measured lower-lower coordinate or a finer target is needed.

## Prediction State

A proper predictor needs cross-rung reservoirs, not one recycling scalar:

```text
state_k(t) = {
    pose_k,
    own_spin_k,
    local_ARA_terrain_k,
    incoming_lower_upflow_k,
    outgoing_diverted_flow_k,
    lower_reservoirs,
    upper_pressure_k,
    irrecoverable_loss_k
}
```

Then:

```text
available_flow_k(t)
    = external_input_k(t)
    + incoming_lower_upflow_k(t)
    + carried_storage_k(t)

future_pose_k
    = advance_pose(
        pose_k,
        available_flow_k,
        lower_contact_direction,
        upper_pressure_k,
        recursive_ARA_terrain_k
      )
```

## What Must Be Measured

The model separates quantities that previous prototypes compressed together:

| Quantity | Meaning | Possible empirical proxy |
| --- | --- | --- |
| `G = 2 - phi` | idealized handoff-width mismatch | defined landmark |
| `lambda_k` | permanently lost share | residual dissipation / unexplained loss |
| `B_j` | lower-rung stored recyclable energy | reservoir measurement |
| `eta_j` | realized return efficiency | causal feeder-to-target transfer |
| `C_k / C_j` | relative density multiplier | measured scale or period relationship |
| `gate_(k,m)` | one-rung versus two-rung return route | phase alignment and spin parity |
| delay | time required for energy to work upward | causal lead-lag measurement |

Autocorrelation can help diagnose recycling, but it is not automatically equal
to any one of `lambda`, `B`, or `eta`.

## Next Test

The next implementable ablation is a **two-reservoir feeder model**:

```text
direct lower feeder        -> one-rung return path, orientation flip
delayed lower-lower feeder -> two-rung return path, same-spin return
upper slow shell           -> pressure / large falling-packet forcing
```

For ENSO:

```text
WWV west/east   lower-rung reservoirs
SOI             matched-rung atmospheric partner
PDO             upper slow pressure
IOD             external or lateral feeder candidate
```

The test should compare:

```text
no reservoir
one-rung reservoir
one-rung + two-rung reservoir
shuffled-reservoir null
```

Score direction first, then correlation and MAE. Keep all reservoir updates
strictly causal.

## First ENSO Reservoir Ablation Result

Implemented:

```text
TheFormula/Claude4.8/ara_enso_cross_rung_reservoir_test.py
```

Full result:

```text
TheFormula/Claude4.8/ARA_ENSO_CROSS_RUNG_RESERVOIR_RESULT.md
```

The minimal fixed-duty reservoir proxy did **not** improve held-out
correlation over the raw joint ENSO topology. The two-rung latent return did
not separate from a causal randomized-prior null. This rejects the tested
shortcut, not the cross-rung architecture.

The next test needs a dynamic release gate and, ideally, an observed candidate
for the lower-lower reservoir. Releasing a fixed fraction every tick is too
blunt for the stated tube-and-gate geometry.

## Measured WWV Leaf-Fall Signature Diagnostic

The next clean diagnostic avoided synthetic leaf injection entirely:

```text
TheFormula/Claude4.8/ara_enso_leaf_to_wwv_abnormality_test.py
```

Full result:

```text
TheFormula/Claude4.8/ARA_ENSO_LEAF_TO_WWV_ABNORMALITY_RESULT.md
```

The test asks whether a causal NINO-derived brown leaf marker is followed by
unusual behavior in the measured WWV west/east lower rung, after subtracting a
training-only WWV-history baseline.

A weak held-out candidate ridge appears around 31 to 34 months, especially in
the combined WWV battery abnormality. The two held-out halves place the battery
peak near 31 and 34 months. The earlier visible period peaks nearer 15 months.

This is not yet a stable recycling law or causal proof. The marker is inferred
from NINO, is periodic, and is not independently observed. The result supports
the next empirical direction:

```text
upper falling-packet marker
    -> measured lower-rung abnormality
    -> later upward return
```

Test this correspondence in measured data before adding any new deposited
energy term to the predictor.

## Frozen Two-Flow Window Diagnostic

The first follow-up froze two possible WWV response windows before scoring:

```text
12 to 18 months -> possible smaller/faster upflow already below WWV
30 to 34 months -> possible slower recycled return after brown leaf-fall
```

Implemented:

```text
TheFormula/Claude4.8/ara_enso_two_flow_window_test.py
```

Full result:

```text
TheFormula/Claude4.8/ARA_ENSO_TWO_FLOW_WINDOW_RESULT.md
```

The visible pre-cutoff period contains a broad directional `12 to 18 month`
WWV pulse (`battery corr +0.424`, `orientation corr +0.459`) aligned with
measured MJO candidate activity (`+0.277`) and especially IOD lateral activity
(`+0.573`). In the held-out period that early branch disappears. Instead, a
broad `30 to 34 month` WWV battery pulse appears (`corr +0.296`) without the
same contemporaneous MJO/IOD alignment.

This is compatible with two different flow shapes:

```text
active lower feeder upflow
slower battery disturbance / recycled return
```

It is not yet proof of their physical identities. The rung directly below WWV
is not independently measured in the present record, the brown marker is
inferred from NINO, and the public MJO RMM series changes processing method in
2014. Keep the distinction as a measured candidate and test it next with
independent thermocline, wind-burst, trade-wind, or upper-ocean measurements.

## Release-Gate and Native WWV-Motion Diagnostic

The next diagnostic asked whether the early pulse concentrates near a
transparent lower-cycle release/end state and whether it is smaller than the
later disturbance:

```text
TheFormula/Claude4.8/ara_enso_release_gate_energy_ratio_test.py
```

Full result:

```text
TheFormula/Claude4.8/ARA_ENSO_RELEASE_GATE_ENERGY_RATIO_RESULT.md
```

In the visible pre-cutoff era, the `12 to 18 month` pulse behaves like a
sustained WWV discharge episode. The WWV battery-discharge gate is open `1.712x`
more often around the marker-weighted pulse than normally, and native WWV
motion is `1.242x` larger while the gate is open. The signed battery movement
is toward discharge.

That exact release-gate signature does not repeat in held-out time. The
diagnostic therefore does not establish a universal release law or a fixed
logarithmic energy fraction.

WWV is a volume proxy, not energy in joules. The observed early/late ratios
measure warm-water-volume motion, not the share passed upward versus retained
as substrate. A direct finer-grain measurement beneath WWV is still needed.

## Raw WWV Bedrock Versus Packet Flow

The next diagnostic separated a real raw discharge shape from the amount of
WWV motion riding over it:

```text
TheFormula/Claude4.8/ara_enso_wwv_bedrock_packet_test.py
```

Full result:

```text
TheFormula/Claude4.8/ARA_ENSO_WWV_BEDROCK_PACKET_RESULT.md
```

The geometric bedrock is a single real train-only medoid event, not a smoothed
or averaged waveform. The March 1992 raw WWV medoid has four falling months
followed by recovery:

```text
[-1.054, -0.711, -0.961, -0.590, +0.355, +0.273, +0.118]
```

Held-out discharge events reproduce the first `3 to 5` months of the raw
falling front much more closely than season-and-level-matched ordinary months.
The longer recovery tail varies more.

This supports a narrower decomposition:

```text
observed response
    = recurring handoff geometry
    x packet size
    x available gap
    x gate / alignment state
```

The packet-size ordering is suggestive but not established. Freeze the short
raw falling-front bedrock and test its variable tail next with direct
wind-burst, trade-wind, thermocline, or upper-ocean measurements.

## Forward Packet-in-Transit Ablation

The retrospective travel-time candidate was turned into a strict-causal
forward ablation:

```text
TheFormula/Claude4.8/ara_enso_leaf_transit_forward_ablation.py
```

Full result:

```text
TheFormula/Claude4.8/ARA_ENSO_LEAF_TRANSIT_FORWARD_RESULT.md
```

The simple version does not hold cleanly: a leaf marker seen now does not
generalize as a fixed `30 to 34 month` WWV-soil amplitude predictor. The direct
marker-to-soil association changes sign between training and held-out eras.

A narrower correction channel is worth preserving. A causal arrived-packet
state, calculated only from markers observed `30 to 34 months` earlier,
improves held-out NINO shape correlation at the `30 month` horizon:

```text
raw topology state          -0.223
raw state + arrived packet  +0.062
lift                        +0.285
```

The lift appears in both held-out halves and beats the declared wrong-time
controls at that horizon. It is localized around roughly `29 to 31 months`.
MAE and direction do not improve, so this is a possible route/timing
correction, not a solved amplitude formula.

The transit window was discovered from this historical record. Keep this
channel exploratory until an independent physical marker or new data
confirms it.

## Rare Large-Drop and Temporal-Shape-Loss Diagnostic

The next descriptive refinement tested whether larger visible drops occur near
one-cycle or three-cycle recurrence points and whether raw temporal shape
degrades before the drop:

```text
TheFormula/Claude4.8/ara_enso_large_leaf_shape_loss_test.py
```

Full result:

```text
TheFormula/Claude4.8/ARA_ENSO_LARGE_LEAF_SHAPE_LOSS_RESULT.md
```

Eight causal-marker peaks appear after warmup, spaced `47.3 +/- 5.4 months`.
That is consistent with one brown-cycle shedding opportunities, but not
independent proof because the marker contains a declared `48 month` brown
geometry.

A separate raw-shape reader compares the recent NINO trajectory against the
same portion of the previous brown cycle. Over `12 to 24 month` raw segments,
shape loss correlates moderately with visible marker size (`+0.573` to
`+0.650`). It does not predict the later WWV soil amount. The `144 month`
three-cycle comparison is unstable with only seven completed soil outcomes.

Preserve the January 2024 inferred event prospectively. Its frozen WWV soil
observation window is July through November 2026. Do not tune the marker or
window after that outcome arrives.

The packet-ratio conjecture for that event is frozen separately:

```text
TheFormula/Claude4.8/ARA_ENSO_2024_PACKET_RATIO_PROSPECTIVE_NOTE.md
```

Keep `G = 2 - phi = 0.381966...` distinct from the normalized one-pass
diverted share `g = (2 - phi) / 2 = 0.190983...`. WWV alone is not an energy
meter, so a ratio test also requires an independently declared incoming-flow
proxy.

### Gross shed versus net same-spin return

The January 2024 prospective refinement distinguishes the packet shed at the
upper handoff from the amount that later becomes usable recycled flow.

The adjacent counterspinning layer is not merely an empty pipe. It can consume,
cancel, scatter, or dissipate some of the packet before a remainder reaches a
same-spin reservoir two physical rungs down:

```text
V_k(t)     gross diverted packet from rung k
C_k(t)     adjacent-rung local use, absorption, or anti-phase cancellation
L_k(t)     irrecoverable dissipation before coherent storage
P_k(t)     surviving same-spin deposit

V_k(t) = C_k(t) + L_k(t) + P_k(t)

usable_return_(k-2)(t + delay)
    = gate_(k-2)(t + delay)
    * recycle_(k-2)(t + delay)
    * P_k(t)
```

This preserves `2 - phi` as a gross geometric landmark without requiring a
later measured proxy to equal it. The same-spin return is expected to be
smaller unless another measured feeder adds flow during the route.

Historical monthly-WWV proxy check:

```text
TheFormula/Claude4.8/ARA_ENSO_INTERMEDIATE_TO_SAME_SPIN_SEQUENCE_RESULT.md
```

The simple measured sequence is not isolated by monthly WWV. The earlier
orientation disturbance is approximately ordinary (`0.432` versus `0.439`
for matched controls). The later battery proxy has only a small excess
(`0.119` versus `0.111`). Later native WWV battery motion is not reliably
smaller than earlier motion (`2 / 7` events below one).

Do not use WWV as both the adjacent anti-phase layer and the lower-lower
same-spin reservoir. A distinct finer or deeper coordinate is required.
