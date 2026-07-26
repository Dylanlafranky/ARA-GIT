# Q31 source selection addendum — v2 frozen before candidate-5 outcomes

**Frozen:** 2026-07-26 20:02 AEST  
**Parent files:** `Q31_LATTICE_TO_TRAVERSAL_PROTOCOL_v1_FROZEN.md`, `Q31_SOURCE_SELECTION_v1_FROZEN.md`

## Candidate 4 data-gate result

The Lin et al. photonic quantum-walk workbooks are authentic experimental sphere-resolved data, but their schemas expose only:

- three experimental three-axis trajectories in each of three system configurations;
- nine measured trajectory units in total;
- matching theoretical comparison curves that are not independent experimental units.

The source therefore fails the frozen minimum of 30 independent trials, devices, trajectories or repeated sweeps and cannot provide 30 untouched evaluation units. Q31 does not calculate or interpret its flip metrics. The candidate is classified:

**Ineligible for Q31 v1 by source-size gate; scientifically useful for a later descriptive sphere-trajectory crosswalk.**

## Candidate 5

**Source:** Dalmasso et al., *Quantum trajectory simulation of two-dimensional non-equilibrium steady states with a trapped ion quantum processor*  
**Experimental platform:** Quantinuum System Model H1 trapped-ion quantum processor  
**Public record:** Zenodo record `20075236`  
**Paper:** arXiv `2605.08350`

Public metadata state that the repository contains:

- experimental quantum trajectories, not only classical simulations;
- a two-dimensional `4 × 4` lattice;
- stochastic particle injection at one corner and removal at the opposite corner;
- persistent source-to-drain current;
- HDF5 result files separating hardware, noisy-emulator and classical data;
- trajectory-running and plotting code;
- a 12,091,540-byte public archive.

## Provisional eligibility decision

Candidate 5 is selected provisionally because its externally declared source/drain events supply a possible handover anchor, the 16-site state is a multi-coordinate relation object, and the experiment directly links lattice persistence with traversal across that lattice.

Before any ARA outcome calculation, its schema must confirm:

1. which HDF5 files are hardware measurements;
2. at least 30 independently identifiable hardware trajectories for evaluation after the deterministic split;
3. at least 500 eligible evaluation transitions;
4. at least 25 ordered samples around an externally recorded injection/removal or protocol handover;
5. at least two non-zero spatial/transverse coordinates above measurement resolution.

Failure of any item makes candidate 5 ineligible. No simulator or classical trajectory may be relabelled as experimental to rescue a gate.

## Frozen local ARA orientation

For this candidate only:

- `2` = persistent occupation/connection structure across the lattice;
- `1` = source/drain handover ridge;
- `0` = coherent information/particle traversal away from the local lattice relation.

The 16-site state vector is the relation object. Source/drain records or the published circuit schedule locate handovers. Q31 metrics may not move those anchors.

The author-supplied labels—particle occupation, source, drain and current—will remain beside the ARA labels. ARA does not replace or rename the underlying measurement.

## Evidence boundary

The experiment implements trajectories of a model on a quantum processor. A positive result would support recurrence of the registered ARA geometry in this measured implementation. It would not by itself prove that every microscopic quantum system undergoes the proposed universal singularity flip.
