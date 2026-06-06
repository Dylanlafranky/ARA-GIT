# ARA Five-Axis Neighbourhood Model

Date: 2026-06-03

This note records the prediction architecture implied by the ARA coordinate sphere in `3D models/ara_sphere_coordinate_3d.html`.

## Core Claim

The measured system is not a single isolated oscillator. It is a sphere with its own recursive ARA terrain, sitting inside a local contact neighbourhood.

The sphere we measure needs surrounding systems along five axes:

| Axis | Meaning | Negative direction | Positive direction |
|---|---|---|---|
| X | Mapping / ARA | space-side | time-side |
| Y | Rung / scale | lower/faster rung | upper/slower rung |
| Z | Coupling / mix | connection/contact | information traversal |
| Phi | efficient valley line | phi-back | phi-forward |
| Anti-phi | mirror/counter valley line | anti-phi-back | anti-phi-forward |

For prediction, each axis must be sampled three deep in both directions:

`5 axes x 2 directions x 3 depths = 30 surrounding contact systems`

plus the measured home sphere.

This is the first faithful shape of the full local environment. Earlier predictors mostly used only:

- home wave memory
- one lower/fast feeder block
- one upper/slow pressure block
- a first-order terrain/ridge term

That is useful, but incomplete. It sees only the first or second layer of the surroundings.

## Contact Depth

Depth means how far away the neighbouring system is from the measured sphere along an axis.

| Depth | Role | Example |
|---|---|---|
| 1 | direct contact | immediate lower feeder, direct counter, direct upper pressure |
| 2 | feeder of feeder / second contact | system driving the direct feeder, or pressure behind the upper constraint |
| 3 | terrain background | the environment deciding whether the depth-1 and depth-2 contacts are clean, delayed, cancelled, or amplified |

Depth is not just "more inputs." Each contact has its own terrain and spin state.

## State Per Contact

Each contact should carry:

- axis
- direction
- depth
- observed series if available
- period / rung
- current ARA coordinate
- sub-ARA / sub-sub-ARA address
- spin / phase velocity
- pressure / amplitude
- terrain slope toward local phi valley
- ridge or spillover resistance
- alignment with the home sphere
- parity flip from layer contact

If an observed series is unavailable, the contact is not empty. It should be read from the recursive ARA terrain grid.

## Formula Shape

The measured sphere receives a roll vector from all contacts:

```text
contact_force(axis, direction, depth)
  = direction_vector(axis, direction)
  * observed_or_terrain_pressure
  * spin_alignment
  * parity(depth)
  * depth_weight(depth)
  * terrain_gate
```

Then:

```text
home_roll_vector
  = floor_motion
  + sum(contact_force over 30 contacts)
  - upper_brake / ridge_resistance
```

The future coordinate is:

```text
future_pose = current_pose + integrate(home_roll_vector, wobble, horizon)
```

The prediction is not "average historical neighbours." It is:

```text
future_pose
  -> read recursive ARA terrain at that coordinate
  -> combine with carried home-wave energy
  -> output forecast
```

## Weighting

Depth should decay logarithmically. The first working default is:

```text
depth_weight(depth) = phi ^ -depth
```

Layer contact should flip spin parity:

```text
parity(depth) = -1 for odd depth, +1 for even depth
```

This matches the layered sand/contact idea:

lower layer rolls the layer above in the opposite direction, then the next layer flips again.

## Why This Matters

The current `home_plus_ara` predictor is a real useful extension of the framework, but it only approximates the local contact environment. A full ARA-native predictor should read the five-axis surroundings around the measured sphere, three deep in both directions, and let those contacts determine how the sphere rolls.

This should especially matter when:

- a lower feeder appears present but is itself depleted or cancelled
- an upper pressure surface is arriving from an unexpected direction
- the system sits near a ridge / boundary / spillover point
- the home wave looks right but occurs too early or too late
- paired/coupled systems turn in opposite directions like contact layers

## Implementation Fence

This note is architecture, not yet a validated forecast result. The next implementation should be tested against the current local proxy baselines and should report:

- ARA + home memory
- pure five-axis ARA
- one-axis/three-axis/five-axis ablations
- depth 1 vs depth 2 vs depth 3 ablations
- shuffled-contact null
- ordinary lag/seasonal/harmonic baselines

