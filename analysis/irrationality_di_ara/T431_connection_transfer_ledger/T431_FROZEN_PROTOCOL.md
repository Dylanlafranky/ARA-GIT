# T431 — Connection-transfer ledger in binary-black-hole strain

Frozen before downloading or scoring the four confirmation events. The ten
events inspected in T427–T430 are development-only. T431 does not alter any
earlier result.

## Who / what / when / where / why / how

- **Who:** each binary-black-hole event is one ARA identity. H1 and L1 are two
  independent detector views of that identity, not two black holes and not two
  ARA children.
- **What:** test the ordered local relation
  `old connection -> mobile/unresolved handover -> new connection` without
  defining any coordinate as the complement of another.
- **When:** score -0.22 to +0.16 seconds around the published event GPS. Search
  old connection in [-0.22,-0.04], mobile structure in [-0.08,+0.04], and new
  connection in [+0.04,+0.16].
- **Where:** public 4 kHz, 32 second H1/L1 strain. Off-source calibration uses
  [-12,-4] and [+4,+12] seconds. Identical matched controls are cut from those
  intervals.
- **Why:** T430 showed local connection excursions but rejected a smooth
  remaining-traversal/connection closure. T431 asks the narrower ARA question:
  does connection visibly break, become movement-heavy, and re-form?
- **How:** use the unchanged T427 whitening and 30–512 Hz, 64 ms Hann STFT with
  4 ms hop. Build independent movement, amount, spectral concentration and
  H1/L1 complex spectral-coherence coordinates. Compare the event ledger with
  every matched off-source ledger and with the two detectors separately.

## Frozen coordinates

All scalar inputs are projected to 0–2 from detector off-source empirical CDFs.

- `C`: mean of network spectral amount, spectral concentration and H1/L1
  complex spectral coherence. This is the connection-facing cut.
- `M`: spectral movement from adjacent-frame Hellinger change plus ridge
  frequency movement. This is the traversal/movement-facing cut.
- `L = M-C`: an independently constructed selection contrast used only to
  locate the most movement-heavy central frame.
- `H = max(0,2-C-M)`: unresolved participation, reported descriptively. It is
  not added back to force closure.

The old and new connections are not assumed to be different feature-space
identities. They are the same connection-facing coordinate on opposite sides
of a handover.

## Frozen landmark selection

Within every event and every matched control:

1. old landmark = maximum `C` in [-0.22,-0.04];
2. mobile landmark = maximum `M-C` in [-0.08,+0.04];
3. new landmark = maximum `C` in [+0.04,+0.16].

The windows impose chronological ownership but do not impose the required
amplitude relations. The primary relations are:

    connection_break = mean(C_old,C_new) - C_mobile
    movement_excursion = M_mobile - mean(M_old,M_new)
    ledger_strength = connection_break + movement_excursion

The same optimization is performed in controls, so selecting local extrema
cannot by itself make the event significant.

## Development boundary

Ten previously inspected events were used only to choose the fixed instrument:
GW150914, GW151012, GW151226, GW170104, GW170608, GW170729, GW170809,
GW170814, GW170818 and GW170823.

The frozen development result is deliberately retained: 9/10 showed the local
network shape, but only 1/10 beat matched off-source windows at p<=0.05 and only
1/10 reproduced all component directions in both detectors. Thus morphology
alone is insufficient; source specificity is the confirmation target.

## Untouched confirmation events

- GW190412-v2
- GW190521_074359-v1
- GW190727_060333-v1
- GW190828_063405-v1

No confirmation value may alter a coordinate, interval, smoothing rule,
eligibility rule, control, gate or figure definition.

## Frozen controls

1. Half-overlapping matched windows from both off-source intervals.
2. Separate H1 and L1 component-direction replication.
3. H1/L1 complex spectral coherence calibrated against off-source values.
4. Time reversal, descriptive only because the old/new labels have declared
   chronological ownership and the primary ledger strength is symmetric.
5. The abandoned three-prototype classifier remains a documented development
   failure and cannot rescue the ledger result.

## Frozen gates

Support requires all of the following:

1. At least 3/4 events have positive connection break and positive movement
   excursion (`network_shape_pass`).
2. At least 3/4 events have ledger strength above at least 95% of their own
   matched off-source windows (empirical p<=0.05).
3. At least 2/4 events reproduce both positive relations separately in H1 and
   L1 (`detector_replication_pass`).
4. At least 3/4 events have larger unresolved `H` at the mobile landmark than
   the mean at the old/new landmarks.
5. At least 3/4 events have event-window median H1/L1 phase coherence above at
   least 90% of their matched off-source windows.

Failure of gate 1 rejects the proposed local shape. Failure of gates 2 or 5
means the shape is not demonstrably tied to the astrophysical event. Failure of
gate 3 means the network result is not robustly visible in each detector's
separate children. Failure of gate 4 rejects the proposed unresolved/mobile
interpretation. A failed T431 rejects this operational instrument, not ARA in
general.

## Interpretation boundary

A pass would support a source-specific connection-break/movement/reclosure
sequence in event-locked public strain. It would not show literal material
connections between black holes, establish a conserved energy ledger, replace
general relativity, or prove the universal ARA proposal. Established black-hole
inspiral/merger/ringdown language is a post-test crosswalk only.
