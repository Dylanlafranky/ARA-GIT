# Q5 public four-Bell-state ARA parent/child replication

**Ledger:** `T263`  
**Protocol:** `Q5-BELL-FOUR-STATE-v1`  
**Result:** **SUPPORTED — 37/37 frozen gates**  
**Independent validation:** **PASS — 20/20 checks**  
**Public source:** [Madzik and Asaad, Figure 2 — Bell states tomography](https://doi.org/10.6084/m9.figshare.14160476.v2)

## Answer first

The Q4 parent/child result replicated across all four public prepared Bell states without changing the raw-current
decoder or any threshold.

All four states had local child cuts close to the ARA `1.0` ridge. Their parent identities were nevertheless
strong, distinct and correctly identified by the frozen ordered relation among `XX`, `YY` and `ZZ`:

| Declared parent | Observed \((XX,YY,ZZ)\) | Parent ARA \((x_{XX},x_{YY},x_{ZZ})\) | Local mean \(|\langle P\rangle|\) | Parent mean \(|\langle P\rangle|\) | Bell margin |
|---|---|---|---:|---:|---:|
| \(\Phi^+\) | \((+0.8533,-0.9400,+0.9467)\) | \((0.1467,1.9400,0.0533)\) | `0.0333` | `0.9133` | `1.1956` |
| \(\Phi^-\) | \((-0.9500,+0.9500,+0.9500)\) | \((1.9500,0.0500,0.0500)\) | `0.0583` | `0.9500` | `1.2667` |
| \(\Psi^+\) | \((+0.8550,+0.7967,-0.9267)\) | \((0.1450,0.2033,1.9267)\) | `0.0367` | `0.8594` | `1.1011` |
| \(\Psi^-\) | \((-0.8350,-0.8817,-0.8500)\) | \((1.8350,1.8817,1.8500)\) | `0.0725` | `0.8556` | `1.1233` |

Each untouched archive independently produced its filename-declared parent. Each state passed all `8/8`
per-state gates, and all `5/5` cross-state gates passed.

## What was frozen

Before the three additional archives were downloaded or opened, Q5 fixed:

- the four expected parent sign patterns;
- the Q4 current decoder and all thresholds;
- six local children, three same-axis parent relations and six mixed controls;
- all `32` per-state and `5` cross-state failure gates;
- checksum, bootstrap and independent-validation requirements.

Frozen protocol SHA-256:

`c97459781f38730cfd623820cc7428b1ae24a366c284ca0c45202a21246a206b`

The three untouched replications were:

- `UPUP+DOWNDOWN.zip` → \(\Phi^+\);
- `UPDOWN+DOWNUP.zip` → \(\Psi^+\);
- `UPDOWN-DOWNUP.zip` → \(\Psi^-\).

All source sizes and MD5 checksums matched the frozen Figshare manifest.

## Parent discrimination

The minimum Euclidean distance between any two observed parent vectors was `2.3830`, above the frozen `1.00`
gate. The mean parent-vector distance was `2.5325`; the mean distance between the six-component local-child
profiles was only `0.2143`. The resulting approximately `11.82×` descriptive contrast should not be treated as
a dimension-free physical constant because the two vectors have different lengths. It does show that this
deposit's state label resides overwhelmingly in the parent relation rather than the local marginals.

A separate `24`-permutation control matched all four observed parents to all four declared labels. The correct
identity assignment ranked `1/24`, with mean state error `0.1054`; the runner-up error was `0.6668`, a margin of
`0.5614`.

## Bootstrap stability

Q5 independently resampled the acquisition records within each of the nine measurement orientations:

| Parent | Records per orientation | Correct label in 2,000 draws |
|---|---:|---:|
| \(\Phi^+\) | `300` | `100%` |
| \(\Phi^-\) | `80` | `100%` |
| \(\Psi^+\) | `600` | `100%` |
| \(\Psi^-\) | `600` | `100%` |

This quantifies record-level stability. It is not a cross-device confidence interval.

## Plain-language ARA reading

If each qubit is viewed separately, all four prepared identities look nearly alike: the child cut rests close to
the quiet `1.0` ridge. That does not mean the whole two-qubit identity is quiet.

The parent identity is stored in how the two children relate. Three ordered cuts through that relation place one
coordinate near each required pole. Changing the pole pattern changes the parent while leaving the local children
almost unchanged. In the user's sphere language, the same-looking child diameters belong to four different
parent spheres because their cross-child coupling directions differ.

This is the cleanest current numerical example of the rule:

\[
\text{children compressed near ridge}
\;\not\Rightarrow\;
\text{parent relation near ridge}.
\]

## Standard-physics control

Quantum mechanics already predicts that all four ideal Bell states have maximally mixed local marginals and
distinct joint Pauli correlations. The ARA coordinates are exactly

\[
x_P=1-\langle P\rangle.
\]

Consequently, ARA and the same-information Pauli account are losslessly affinely equivalent. Q5 does not
outperform tomography and does not discover entanglement. Its empirical contribution is narrower: the
parent/child geometry, coordinate orientation and thresholds were frozen before three raw state archives were
opened, and that same crosswalk recovered all three untouched parents.

## Validation report

### Overall assessment: Share with caveats

The independent validator:

- rechecked all four archive sizes and checksums;
- verified `56,880` unique saved record rows;
- reconstructed all `64` expectation values including normalization;
- verified all `60` Pauli/ARA projection rows;
- independently reproduced all `8,000` bootstrap draws;
- recalculated all `37` gates and the `24`-assignment control.

All `20/20` validation checks passed.

### Required caveats

1. The four archives are different prepared states from one experiment, device and public deposit.
2. Record bootstrap is not independent device/day replication.
3. Bell/Pauli identities are established physics.
4. This supports the frozen ARA relational-parent and non-flattening crosswalk; it does not prove universal
   fractality, Information³, quantum gravity or a new quantum law.

## Reproduction

Run:

```powershell
python q5_bell_four_state_test.py
python q5_bell_four_state_validate.py
```

Derived artifacts:

- `Q5_BELL_FOUR_STATE_RECORDS.csv`
- `Q5_BELL_FOUR_STATE_PROJECTIONS.csv`
- `Q5_BELL_FOUR_STATE_BOOTSTRAP.csv`
- `Q5_BELL_FOUR_STATE_PAIRWISE.csv`
- `Q5_BELL_FOUR_STATE_RESULTS.json`
- `Q5_BELL_FOUR_STATE_VALIDATION.json`

