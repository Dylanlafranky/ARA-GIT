# Q52 — whole-sphere continuation protocol v1 (frozen)

**Frozen before continuation outcomes were generated:** 2026-07-30  
**Measured object:** the external centreline carrying each complete internal
ARA circle through time  
**Question:** does the previously observed external
`0 → 2` reversal complete an active `0 → 2 → 0` traversal?

## 1. Construct boundary

Q52 does **not** test the local \(\pi/15\) pair rotation, the internal quadrant
turn or the 7.5/15 cadence.

It retains the Q49/Q50 external directional coordinate:

\[
x_{\rm ext}
=
1-
\frac{
\sum_i \mathbf d_i\cdot\widehat{\mathbf e}_{1/e\rightarrow\phi}
}{
\sum_i\|\mathbf d_i\|
}.
\]

Here \(\mathbf d_i\) is the movement of a fitted whole-circle centre between
neighbouring complete internal cycles.

- `x = 0`: movement along the declared \(1/e\rightarrow\phi\) orientation;
- `x = 1`: directional ridge / axial cancellation;
- `x = 2`: exact opposite orientation.

The target sequence is:

\[
0\rightarrow2\rightarrow0.
\]

## 2. Immutable history and source calibration

- Archive: `unnati_submit_12_pure_strongmax.hdf5`
- Archive deposited MD5:
  `11b5f14ba185a9901f6a85bd31497d71`
- Branch: `c2_2local connectivity`
- Ordering rule in the immutable history: `strongest_maximizes`
- Source seeds: `0–49`, chosen before continuation generation
- Original stored slices: `0–499`
- Existing Q39 closure values supply slices `0–499`.

The continuation state is reconstructed from the complete set of slice-499
two-qubit reductions. The source is a pure single-excitation state, so the
populations and pair coherences identify its 12 complex amplitudes up to an
irrelevant global phase. Every reconstructed state must regenerate all 66
stored slice-499 pair reductions with maximum absolute error no greater than
`5e-6`.

The public QuNet source was separately calibrated against the random archive:
the full source replay matched all 66 slice-499 reductions with maximum and
RMS error `0.0`. See
`Q52_SOURCE_EXTENSION_CALIBRATION_2026-07-30.md`.

## 3. Continuation generator

The local interaction remains unchanged:

\[
U_{\pi/15}=
\begin{pmatrix}
\cos(\pi/15)&-\sin(\pi/15)\\
\sin(\pi/15)&\cos(\pi/15)
\end{pmatrix}.
\]

Each continuation uses only the two pair partitions declared by the public
`c2_2local` rule:

```text
A = [(9,10), (1,2), (3,4), (0,11), (5,6), (7,8)]
B = [(0,1), (10,11), (2,3), (6,7), (4,5), (8,9)]
```

Eight continuation families are fixed:

1. `fixed_A`;
2. `fixed_B`;
3. `alternating_AB`;
4. `alternating_BA`;
5. `random_520101`;
6. `random_520102`;
7. `random_520103`;
8. `random_520104`.

The four random families use `numpy.random.default_rng(seed)` to select A or B
with equal probability at each continuation step. Each family uses the same
predeclared order sequence across all 50 source seeds, isolating source-state
variation from future-order variation.

Continuation length: `1,500` transitions, producing total slices `0–1,999`.

The original Python random-generator state was not deposited. These families
are therefore a declared ensemble of valid possible futures, not a claim to
recover an unrealized historical future.

## 4. Exact extraction retained from Q49/Q50

For every source seed, pair identity and continuation family:

1. convert the trajectory to the Q39 closure coordinate;
2. calibrate its state/change plane on immutable slices `0–249`;
3. require development circulation coherence at least `0.80`;
4. require minimum development quadrant occupancy at least `0.05`;
5. identify ordered four-quadrant internal cycles;
6. fit each complete cycle as a circle;
7. obtain external centre movements from the preceding and following fitted
   cycles;
8. normalize centre movement by the local mean circle radius;
9. project the resulting external vectors onto the unchanged
   \(1/e\rightarrow\phi\) axis.

No \(\pi/15\) quantity enters the external ARA score.

## 5. Fixed lineage and bin rules

- Bin width: `50` source slices.
- A fixed lineage must contain:
  - at least three external events ending before slice `250`;
  - at least three external events starting at or after slice `500`.
- Family eligibility:
  - at least `20` represented source seeds;
  - at least `100` fixed pair lineages;
  - at least three finite continuation bins.

The same rules are also applied separately to each source seed when sufficient
pair lineages exist.

## 6. Frozen outcome definitions

### Complete geometric return

A family has a geometric `0 → 2 → 0` witness when its ordered finite bins
contain:

1. `x ≤ 0.5`;
2. a later `x ≥ 1.5`;
3. a later continuation bin, beginning at or after slice `500`, with
   `x ≤ 0.5`.

### Active return

Let \(M_0\) be the median mean external movement per event in finite historical
bins ending by slice `250`. A geometric return is active when movement in the
return bin is at least:

\[
0.25M_0.
\]

Sensitivity ratios `0.10` and `0.50` are reported but do not replace the
primary `0.25` gate.

### One-way settling

A family is classified as one-way settling when:

- no continuation return to `x ≤ 0.5` occurs;
- the median of its last three finite bins is at least `1.5`;
- their median movement is at most `0.10M_0`.

### Cycle extinction

Insufficient continuation cycles or finite bins are reported as
`CYCLE EXTINCTION / NOT DIRECTIONALLY TESTABLE`; they are not silently counted
as settling.

### Driver dependence

Driver dependence is supported when at least two eligible families have an
active return and at least two eligible families satisfy one-way settling.

## 7. Ensemble gates

For each family, source-seed bootstrap intervals use `5,000` draws and the
fixed seed `520052 + family_index`.

- **Complete return supported:** at least five eligible families show an
  aggregate active return, including at least one fixed, one alternating and
  one random family, and their pooled source-seed active-return fraction has a
  bootstrap 95% lower bound above `0.50`.
- **One-way settling supported:** at least five eligible families satisfy the
  aggregate settling rule and their pooled source-seed settling fraction has a
  bootstrap 95% lower bound above `0.50`.
- **Driver-dependent:** the frozen driver-dependence rule is met.
- Otherwise: **unresolved/mixed**.

## 8. Required controls and reporting

- regenerate all slice-499 pair reductions from each reconstructed amplitude
  state;
- report norm drift during every continuation;
- retain circle, centroid and extrema centre estimators;
- report family and source-seed classifications;
- show `x`, movement and eligibility through all 2,000 slices;
- do not relabel an orientation-only return as an active return;
- do not interpret a simulator result as a hardware quantum measurement;
- report the local \(\pi/15\) parameter as source machinery, not as an ARA
  prediction.

## 9. Falsification value

- Persistent active `0 → 2 → 0` across allowed continuation families supports
  the whole-sphere wobble interpretation in this simulator.
- Persistent settling supports a one-way relaxation interpretation instead.
- Strong family dependence says the future coupling environment determines
  whether return occurs.
- Cycle extinction leaves the directional question unresolved but establishes
  that the selected observable no longer supplies a complete rotating identity.

No continuation outcome was inspected before this protocol was written.
