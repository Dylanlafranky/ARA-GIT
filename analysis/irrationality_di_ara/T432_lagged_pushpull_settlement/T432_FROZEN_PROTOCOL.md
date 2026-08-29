# T432 — Lagged Push/Pull, Corner Avoidance and Settlement

Frozen before the six confirmation event files were downloaded or inspected.

## ARA identity and scope

**Who.** Each gravitational-wave merger is one parent event. `C` is the measured connection-facing child coordinate; `M` is the measured movement-facing child coordinate. H1 and L1 are independent detector views of the same event, not the two black holes. `H=max(0,2-C-M)` is an unresolved residual in this projection and is not promoted to a third physical identity.

**What.** Test whether the measured children behave as a delayed push/pull pair: when one rises, the other tends to fall, with an allowed timing offset. Separately test whether the trajectory settles as the waveform loses form and whether the nominal low-movement/high-connection corner is avoided.

**When.** The event window is -0.50 to +0.75 seconds relative to the published event GPS. The active interval is -0.15 to +0.15 seconds and the late-settlement interval is +0.35 to +0.75 seconds. Matched controls use identical windows in the same 32-second detector files.

**Where.** All trajectories use one fixed plane: horizontal `M` from 0 to 2 and vertical `C` from 0 to 2. The nominal top-left pure corner is therefore `(M=0,C=2)`. No axis rotation or event-specific remapping is allowed.

**Why.** T430–T431 showed useful inverse/transfer shapes but weak event specificity. T432 asks a more precise dynamic question: whether the source window contains a lagged opposing relation and subsequent settlement that is uncommon in its own off-source strain.

**How.** Preserve the existing lens: public GWOSC 4 kHz strain, off-source whitening, 30–512 Hz bandpass, 64 ms Hann STFT, 4 ms hop, seven-frame median smoothing and off-source empirical-CDF mapping to 0–2. Connection is the mean of network spectral amount, spectral concentration and H1/L1 phase coherence. Movement is spectral redistribution. No `C+M=2` constraint is imposed.

## Frozen dynamic measurements

1. Compute `dC/dt` and `dM/dt` after the fixed smoothing.
2. Search lags from -64 to +64 ms in 4 ms increments. The same lag search is applied to every matched control.
3. The lagged opposition is the maximum of `-Spearman(dC(t),dM(t+lag))`.
4. Opposition occupancy is the fraction of aligned steps with `dC*dM<0` at that lag.
5. Push/pull score is `max(0, opposition) * occupancy`.
6. Signed loop area and orientation are descriptive geometry, not a gate.
7. Settlement is tested two ways: reduction in trajectory speed and contraction toward the late centroid from the active interval to the late interval.
8. Corner avoidance is the full-window occupancy of `M<=0.5 and C>=1.5`, plus the 10th-percentile distance to `(0,2)`.
9. H mobility is the active-to-late change in the unresolved residual, reported descriptively.

## Matched controls and detector replication

- Use all identical 1.25-second windows wholly contained inside the two off-source reference regions, with centers separated by 0.25 s.
- Convert each event metric to an empirical within-file percentile against its controls.
- Repeat the push/pull test independently for H1 and L1 using detector-local connection `(amount+concentration)/2` and detector-local movement.

## Frozen gates

- **G1 dynamic source specificity:** at least 4 of 6 confirmation events have network push/pull percentile >= 0.95.
- **G2 settlement specificity:** at least 4 of 6 have both speed-settlement and radius-settlement percentiles >= 0.90.
- **G3 detector replication:** at least 3 of 6 have H1 and L1 push/pull percentiles >= 0.90.
- **G4 corner avoidance:** at least 4 of 6 have top-left occupancy at or below the 10th control percentile. This is a secondary gate because the boundary may arise from the coordinate construction.
- The dynamic handover claim is supported only if G1 and G2 pass. Other combinations are reported as component results, not rescued post hoc.

## Data limits frozen with the test

- The source is calibrated detector strain: astrophysical response plus instrumental/noise contributions.
- `C`, `M` and `H` are constructed 0–2 coordinates, not joules, masses, forces, literal spacetime density or black-hole surface positions.
- H1/L1 coherence is a detector relation after preprocessing, not direct access to the merger's internal phase.
- A 64 ms STFT cannot resolve structure shorter than its window without temporal smearing; the 4 ms hop is display/step spacing, not independent 4 ms resolution.
- The absolute -0.50 to +0.75 s window does not normalize for source mass or intrinsic merger timescale.
- Off-source controls test source-window specificity within each file. They do not prove a universal physical mechanism.

