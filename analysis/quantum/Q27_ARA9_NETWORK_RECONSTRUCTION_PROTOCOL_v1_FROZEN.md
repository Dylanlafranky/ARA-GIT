# Frozen protocol — Q27 ARA^9 network reconstruction

**Protocol ID:** `Q27-ARA9-NETWORK-RECONSTRUCTION-v1`  
**Ledger ID:** `T283`  
**Frozen:** 26 July 2026, before downloading or opening the target HDF5 values  
**Test class:** public-data, prospective half-record holdout  
**Source:** Akhouri, Shandera and Henry (2025), *Dataset for 6–14 qubits evolving on network with varying
connectivity*, Zenodo DOI `10.5281/zenodo.16753415`

## Registered question

Q26 observed `25/28` complete local connected ARA^9 trajectories move from a crest to a trough, but the records
ended before a later return could be tested. Dylan proposed that the structure may reconstruct as a larger
resonance or may be the Phase B of a larger wave.

Q27 asks:

1. after a complete local ARA^9 reaches a trough, does it reconstruct locally;
2. if it does not return locally, does its release align with accumulation in directly coupled neighbouring
   pair relations;
3. does any amplitude return also carry a reliable orientation reversal;
4. do the exact network adjacency and time order add information beyond matched controls?

## Target fixed before download

- file: `unnati_submit_12_pure_random.hdf5.zip`;
- expected MD5: `06b6b278c4ce1e8ce14d2d662f0dc9dc`;
- advertised content: `12` qubits, `500` time steps, `100` trials, all two-qubit density partitions, and
  connectivity by time step;
- development/exposed times: indices `0–249`;
- sealed target times: indices `250–499`.

The `pure_random` branch was selected before numerical inspection because it uses a pure initial-condition family
and the neutral random ordering rule, rather than a connectivity-maximising rule selected for an anticipated ARA
outcome.

## Schema boundary

The Zenodo description fixes the scientific content but not the internal HDF5 key names. After opening:

- a schema-only adapter may identify trial, time, pair-density and connectivity arrays;
- no values may be plotted, summarized or used to change the split, thresholds, target file or formulas during
  that adaptation;
- exact discovered key paths, shapes and dtypes must be written to a schema manifest;
- if the advertised `100 x 500` records or all pair partitions are not present, the run becomes
  `INCONCLUSIVE — SOURCE SCHEMA`, not an alternative target hunt.

## ARA object

For each pair density matrix \(\rho_{uv}(t)\), calculate

\[
a_i=\operatorname{Tr}\!\left[\rho(\sigma_i\otimes I)\right],\quad
b_j=\operatorname{Tr}\!\left[\rho(I\otimes\sigma_j)\right],
\]

\[
T_{ij}=\operatorname{Tr}\!\left[\rho(\sigma_i\otimes\sigma_j)\right],\quad
C=T-\mathbf a\mathbf b^\mathsf T,
\]

\[
h=|\det C|^{1/3},\qquad o=\operatorname{sign}(\det C).
\]

The local scale is frozen to the exposed-record `95th` percentile:

\[
s_{uv} = Q_{0.95}\{h_{uv}(t):0\le t<250\},
\qquad
x_{uv}(t)=2h_{uv}(t)/s_{uv}.
\]

Pairs with \(s_{uv}<10^{-10}\) are recorded as unresolved and excluded from class denominators.

Classes:

- crest: \(x\ge1.5\);
- handover: \(0.5<x<1.5\);
- trough: \(x\le0.5\);
- sustained state: the class persists for at least `5` consecutive samples.

## Local reconstruction prediction

An eligible source pair must, using exposed times only:

1. contain a sustained crest;
2. later enter a sustained trough;
3. have its mirrored return centre fall in the sealed interval.

Let \(t_c\) be the final sample of the last sustained crest preceding the qualifying trough and \(t_\tau\) the
first trough sample. The ARA half-cycle prediction is

\[
\widehat t_{\rm return}=t_\tau+(t_\tau-t_c).
\]

A local reconstruction is a sustained hidden crest. Its timing is a hit when its first sample lies within

\[
\max\{10,\lceil0.25(t_\tau-t_c)\rceil\}
\]

samples of \(\widehat t_{\rm return}\).

## Larger-parent / Phase-B transfer prediction

For each eligible source pair \((u,v)\), its direct network neighbourhood is the set of other deposited pairs
sharing \(u\) or \(v\) and connected through the deposited graph at that time. The child-neighbour closure is

\[
G_{uv}(t)=\sum_{(i,j)\in\mathcal N_{uv}(t)}h_{ij}(t).
\]

Normalize \(G\) by its own exposed `95th` percentile onto `0–2`. A transfer event requires:

- source \(x_{uv}\) in a sustained trough;
- direct-neighbour \(x_G\) entering a sustained crest within `25` later samples;
- positive release-to-accumulation coupling between
  \(\max(0,-\Delta h_{uv})\) and \(\max(0,\Delta G_{uv})\).

This is the registered Phase-B recipient test. Network-wide movement without an adjacency advantage is reported
as generic parent motion, not direct Phase-B transfer.

## Orientation rule

A stable flip requires determinant sign reversal with at least `5` consecutive samples on each side while both
sides have \(x>0.5\). Sign changes confined to the trough are quiet-region observations, not reliable flips.

## Controls and rivals

1. **No-return contraction:** once the exposed trough is reached, the relation remains at that level.
2. **Persistence:** hidden relation equals the final exposed matrix.
3. **ARA mirror:** reverse the exposed crest-to-trough amplitude path about \(t_\tau\); this is the registered
   local reconstruction waveform.
4. **Exact-adjacency transfer:** deposited neighbour set and exact time order.
5. **Pair-shuffled adjacency:** `999` deterministic matched neighbourhood permutations.
6. **Circular-time transfer:** `999` deterministic nonzero circular offsets within trial.

Seed: `27027`.

No Fourier transform is used to define or detect the ARA wave. A Fourier or autoregressive fit may be added only
as a labelled established-method rival without changing the registered ARA calculation.

## Primary metrics

- eligible source-pair and trial counts;
- sustained local reconstruction fraction;
- return-timing hit fraction and absolute timing error;
- hidden amplitude MAE for ARA mirror, no-return contraction and persistence;
- exact-adjacency release-to-accumulation coupling and its pair-shuffled percentile;
- exact-time coupling and its circular-time percentile;
- fraction of non-returning local sources with a qualifying direct-neighbour crest;
- stable orientation-flip fraction;
- trial-cluster bootstrap intervals and split-half results;
- complete ARA geometry tables for local sources, neighbours and controls.

## Frozen gates

Data:

1. `D1`: archive MD5 matches.
2. `D2`: schema exposes `100` trials and `500` ordered time steps.
3. `D3`: all advertised two-qubit partitions can be mapped to qubit-pair identities.
4. `D4`: sampled density matrices are finite, trace-one and Hermitian; the PSD tolerance and any violations are
   reported rather than silently repaired.
5. `D5`: protocol hash predates target download and numerical opening.

Local reconstruction:

6. `R1`: at least `30` eligible source trajectories spanning at least `20` trials.
7. `R2`: at least `50%` of eligible sources reconstruct locally in the sealed half.
8. `R3`: at least `50%` of locally reconstructing sources land within the frozen timing tolerance.
9. `R4`: ARA-mirror hidden amplitude MAE is lower than both persistence and no-return contraction.
10. `R5`: trial-cluster bootstrap probability that ARA mirror beats both controls is at least `95%`.

Phase-B / larger-parent transfer:

11. `B1`: among eligible sources without local reconstruction, at least `50%` have a qualifying direct-neighbour
    crest.
12. `B2`: exact-adjacency release-to-accumulation coupling beats at least `95%` of pair-shuffled controls.
13. `B3`: exact time order beats at least `95%` of circular-time controls.
14. `B4`: both trial halves have the same signed adjacency advantage.

Orientation:

15. `O1`: stable orientation flips occur in at least `50%` of local reconstructions.

## Verdicts

The two branches receive separate verdicts.

- **LOCAL RECONSTRUCTION SUPPORTED:** `D1–D5`, `R1`, and at least four of `R2–R5`.
- **PHASE-B TRANSFER SUPPORTED:** `D1–D5`, `R1`, and all `B1–B4`.
- **MIXED:** both branches supported.
- **NOT SUPPORTED:** instrument is adequate but neither branch passes.
- **INCONCLUSIVE:** source/schema failure or fewer than the required eligible sources.

`O1` is reported independently and cannot rescue either amplitude branch.

## Evidence boundary

The data were generated by a quantum-network simulator, so the Schrödinger/unitary machinery and partial traces
are built into the source. Q27 tests whether the predeclared complete connected ARA^9 geometry compresses and
predicts the simulated trajectories and network transfer better than its controls. It is not evidence by itself
that physical quantum hardware, all ARA^9 objects, or the universe must follow the same rule.

