# Q27 — ARA^9 Network Reconstruction or Larger-Wave Phase B

**Date:** 26 July 2026  
**Ledger:** T283  
**Strict registered verdict:** **INCONCLUSIVE**  
**Conditional claim verdict:** **NOT SUPPORTED**  
**Geometry verdict:** **A weaker ordered network-transfer relation is supported inside this simulator**

## Orientation signature

- **Object:** connected two-parent relation \(C=T-\mathbf a\mathbf b^\mathsf T\).
- **ARA amplitude:** \(h=|\det C|^{1/3}\).
- **Diameter:** \(x=2h/s\), where \(s\) is the exposed-half Q95 for the same
  local pair.
- **0:** local trough / unresolved closure.
- **1:** local handover or ridge region.
- **2:** exposed local crest.
- **Up one rung:** the surrounding network-parent relation assembled from
  local pair children.

## Outcome first

Q27 does **not** support the registered simple reconstruction claim.

Local crest-to-trough-to-crest recurrence was common: `88.20%` of `10,519`
eligible pair trajectories returned to a sustained crest. But recurrence alone
was not the registered larger-wave result. Only `31.82%` of returning pairs
landed within the frozen mirrored-time tolerance, and the mirrored waveform
forecast was substantially worse than both persistence and a no-return
contraction control.

The registered strong Phase-B alternative also failed. Only `2.58%` of
non-returning sources produced a sustained crest in a direct active neighbour,
far below the frozen `50%` gate.

There is nevertheless a narrower relational result worth retaining. The exact
source-release to active-neighbour-accumulation overlap was `0.27677`, compared
with a pair-shuffle null median of `0.20721` and circular-time null median of
`0.22606`. It beat all `999` draws of both nulls and reproduced in both
predeclared seed halves. In ARA language, release is coupled to ordered
accumulation in the surrounding web, but it is distributed rather than closing
as one dominant neighbour crest.

## Why the strict verdict is inconclusive

One frozen source-integrity gate failed:

- `5,000` raw density matrices were sampled independently.
- Maximum trace error was `2.5342e-05`.
- The runner's frozen pass threshold was `1e-05`.
- Maximum Hermiticity error was `0`.
- Minimum eigenvalue was `-3.1154e-07`.
- No matrix failed the reported PSD tolerance of `-1e-06`.

Because the trace gate was frozen before numerical values were read, it cannot
be relaxed after seeing the result. The strict protocol verdict is therefore
**INCONCLUSIVE**. This does not prevent reporting the registered branch metrics.
If the source gate were accepted at its observed numerical precision, neither
substantive branch would pass and the conditional verdict would be
**NOT SUPPORTED**.

## Frozen hypotheses and results

| Registered question | Frozen success rule | Result | Verdict |
|---|---:|---:|---|
| Does a local trough reconstruct as the next crest? | At least 50% | `88.20%` | Pass descriptively |
| Does it return on the mirrored larger-wave clock? | At least 50% within tolerance | `31.82%` | Fail |
| Does the mirror beat persistence and no-return? | Both, with bootstrap probability at least 95% | `1.37830` MAE versus `0.70753` and `0.51933`; bootstrap `0%` | Fail |
| Does a non-returning source create one direct-neighbour crest? | At least 50% | `2.58%` | Fail |
| Is release-to-accumulation tied to exact adjacency? | Beat at least 95% of pair-shuffle null | Beat `999/999` | Pass |
| Is release-to-accumulation tied to exact time order? | Beat at least 95% of circular-time null | Beat `999/999` | Pass |
| Does the larger relation show a stable orientation flip? | At least 50% of reliable reconstructions | `0/9,278` | Fail |

## Results by connectivity stratum

| Metric | 2-local (`c2`) | 4-local (`c4`) | Pooled |
|---|---:|---:|---:|
| Trials | 100 | 100 | 200 |
| Eligible sources | 5,311 | 5,208 | 10,519 |
| Local reconstruction | 88.80% | 87.60% | 88.20% |
| Mirrored timing hit | 32.78% | 30.82% | 31.82% |
| Direct-neighbour crest | 2.86% | 2.32% | 2.58% |
| Mirror MAE | 1.36822 | 1.38858 | 1.37830 |
| Persistence MAE | 0.69872 | 0.71650 | 0.70753 |
| No-return MAE | 0.51116 | 0.52766 | 0.51933 |
| Exact ordered overlap | 0.26534 | 0.28842 | 0.27677 |
| Stable orientation flip | 0% | 0% | 0% |

The pooled local-reconstruction cluster-bootstrap 95% interval was
`[87.60%, 88.79%]`. The result is therefore stable across trials and both
connectivity strata, even though it does not satisfy the registered timing and
forecast requirements.

## ARA interpretation

### What survived

The connected ARA^9 cut is not behaving like arbitrary noise. It repeatedly
contracts from a local crest through a trough and commonly expands again.
Release from the source also lines up with accumulation in the exact active
neighbour web more than it does after either relational or temporal
misalignment.

This supports a modest statement:

> The ARA-compressed pair identity retains information about ordered,
> network-structured transfer beyond the pair itself.

### What did not survive

The data reject the simplest version of a clean doubled resonance:

- the return time is not the mirror of the exposed crest-to-trough half;
- the mirror is worse than both simple controls;
- the release does not generally reappear as one neighbour's crest;
- no stable determinant-orientation flip appears.

The surrounding response is therefore better represented, for this dataset, as
a distributed and delayed coupling web. Calling that web a confirmed Phase B
would overstate the result. It is a candidate direction for a newly frozen test.

## Established-physics crosswalk

| ARA reading | Established description |
|---|---|
| Local ARA^9 child | Connected correlation tensor of a reduced two-qubit pair |
| Crest-to-trough contraction | Loss or redistribution of that pair's connected correlation volume |
| Neighbour accumulation | Growth of connected correlation magnitude in currently interacting adjacent pairs |
| Distributed Phase-B candidate | Correlation spreading through several network relations rather than one recipient |
| No stable flip | Determinant orientation did not reverse reliably during reconstructed returns |

This side-by-side translation does not replace the ARA geometry with established
quantum language. It keeps the two coordinate systems aligned so each result can
be audited from either side.

## Data, controls and provenance

The complete public source was:

- Akhouri, Shandera and Henry, *Dataset for 6–14 qubits evolving on network
  with varying connectivity*.
- Zenodo DOI: `10.5281/zenodo.16753415`.
- Archive: `unnati_submit_12_pure_random.hdf5.zip`.
- Archive MD5: `06b6b278c4ce1e8ce14d2d662f0dc9dc`.
- Extracted HDF5 SHA-256:
  `0e10afb6e5c7bcc3b469a9bb18a9bcae9469bfae165d5da5add93eeeb1972eeb`.
- Total matrices used: `6,600,000`.
- Development times: `0–249`.
- Hidden evaluation times: `250–499`.

The implementation manifest was frozen after schema inspection but before any
density-matrix value was read. The first extracted-HDF checksum was accidentally
calculated on a command-window-truncated file; the primary runner detected the
mismatch and stopped before reading numerical values. The complete file was
then extracted, checksum-corrected in the ledger, and used without changing the
registered analysis.

## Independent validation

`q27_ara9_network_reconstruction_validate.py` independently reopened the raw
HDF5, rebuilt the frozen 5,000-matrix quality sample, checked the derived cache,
and recomputed the headline metrics, controls, gates and strict verdict without
importing the primary runner.

**Validation result: PASS, 46/46 checks.**

The executed notebook contains 12 cells, including 5 code cells; every code
cell has an execution count and no error output.

## Reproduction

From `analysis/quantum`:

```powershell
python q27_ara9_network_reconstruction_test.py all --workers 6
python q27_ara9_network_reconstruction_validate.py
python q27_build_notebook.py
```

The primary runner restores and checksum-verifies the public archive
automatically when it is absent. Large source and cache files are excluded from
Git.

## Evidence boundary

Q27 uses complete public simulated network trajectories, not quantum-hardware
measurements. It tests whether the predeclared ARA compression and
trajectory/adjacency rules survive a larger dataset. It does not establish a
new quantum law, a universal Phase B, or universal fractality.

