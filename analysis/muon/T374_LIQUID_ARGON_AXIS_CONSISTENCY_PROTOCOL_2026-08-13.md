# T374 — frozen liquid-argon axis-consistency test

**Frozen:** 13 August 2026 (Australia/Brisbane), before calculating any
projection-specific branch mixtures.

## Identity boundary

T374 does **not** change medium or physical identity. It uses the same
CENNS-10 liquid-argon event record, the same stopped-pion / stopped-muon
neutrino source, and the same CEvNS interaction as corrected T373. Only the
measurement cut changes.

The working ARA lead is therefore left unchanged:

\[
x_H = 1 + \frac{0.5}{2} = 1.25.
\]

This is the movement-heavy liquid-parent reading proposed after T373. It is a
post-T373 hypothesis but a pre-T374 prediction.

## Plain-language axis map

- **Energy:** how much recoil energy the argon event deposits.
- **Pulse shape (`F90`):** how much of the argon scintillation light arrives in
  its first 90 nanoseconds. It helps distinguish different kinds of recoil and
  background.
- **Arrival time:** when the event arrives after the accelerator pulse. It is
  the most direct cut between the prompt pion-lineage branch and the delayed
  muon-lineage branch.

These are three views of the same liquid parent, not three independent event
samples.

## Who / what / when / where / why / how

- **Who:** the prompt pion-lineage and delayed muon-lineage CEvNS branches
  inside the CENNS-10 liquid-argon parent response.
- **What:** their fitted mixture and the cumulative ARA coordinate at their
  rate-equality handover.
- **When:** over the released ten half-microsecond arrival-time bins; axes that
  omit time infer the mixture from the remaining released template shapes and
  then use the same frozen native timing bases to locate the handover.
- **Where:** the collaboration's released `12 energy × 8 F90 × 10 time` event
  cube.
- **Why:** a genuine parent handover should not be created solely by one
  plotting axis. Consistent cuts should remain compatible with the same
  location, while their precision reveals which observable actually carries
  the distinction.
- **How:** fit the same five non-negative components used in T373 after
  projecting the data and templates onto each declared cut.

## Frozen cuts

The complete 3D fit is retained as a reference. Six additional cuts are run:

1. energy × time (remove F90);
2. F90 × time (remove energy);
3. energy × F90 (remove arrival time);
4. time only;
5. energy only;
6. F90 only.

For every cut, profile the prompt share. Convert the best-fit share to the
same native-time handover coordinate used in T373. Calculate the profile
penalty at the exact share that places the handover at `x_H = 1.25`.

## Frozen gates

### Geometry compatibility

For each cut separately:

1. the fit must converge;
2. the best-fit mixture must produce a finite prompt/delayed equality;
3. exact `x_H = 1.25` is called *compatible* when its one-parameter profile
   penalty is `Delta NLL <= 1.920729` (the conventional 95% diagnostic);
4. the central estimate is called *movement-side* when `1 <= x_H <= 1.5`.

The main axis-consistency gate passes only if both time-bearing 2D cuts
(`energy × time`, `F90 × time`) are compatible with `1.25` and have central
estimates on the movement-side interval. The time-free `energy × F90` cut is
reported as a diagnostic and is not required to pass, because removing arrival
order may erase the handover distinction.

### Arrival-order control

For every time-bearing cut (3D, energy × time, F90 × time and time only), keep
the observed data and published backgrounds fixed but circularly shift the two
CEvNS source templates together by each of the nine non-zero native time-bin
offsets. Refit every shifted model.

The correct source order passes its control when its fitted NLL is lower than
the median shifted-source NLL. The exact rank and all nine control values are
reported. This is a negative control for source ordering, not an independent
validation of `1.25`.

## Evidence boundary

- All cuts reuse the same events and therefore cannot be multiplied into an
  independent replication count.
- Compatibility from an uninformative cut is not evidence of convergence;
  profile width and central location must be shown.
- T374 can support or weaken the statement that `1.25` is stable across cuts
  through this liquid parent. A new same-identity event record is still needed
  to confirm the law prospectively.
- No claim is made that energy, F90 and time are themselves ARA phases. They
  are measurement axes used to inspect one proposed relational handover.

