# Q24 ARA^9 connected Bell relation

**Date:** 26 July 2026  
**Ledger:** `T280`  
**Verdict:** `CALIBRATED — 16/16 FROZEN GATES`  
**Independent validation:** `PASS — 860/860 checks`

## Outcome first

The older ARA^9 idea has an exact mathematical home in the two-parent Bell relation:

\[
\underbrace{3\ \text{cuts of parent A}}_{X,Y,Z}
\times
\underbrace{3\ \text{cuts of parent B}}_{X,Y,Z}
=
\underbrace{9\ \text{relation slots}}_{\text{ARA}^9}.
\]

After subtracting what the two local children would produce independently, the public raw-current reconstruction
returned the exact frozen closure ladder:

```text
Bell records:          3, 3, 3, 3 retained relation directions
classical mixtures:    1, 1       retained relation direction
uniform mixture:       0          retained relation directions
```

The established positive-density companion returned the identical `3,3,3,3 / 1,1 / 0` ladder. All raw bootstrap
classifications were stable in `100%` of `2,000` draws per entity, and every Bell determinant remained negative
in `100%` of draws.

This is a strong calibrated identification of the pre-existing ARA^9 coupling object. It is not a blind Bell
prediction, a new entanglement witness, or proof that ARA is universal.

## The ARA and standard objects side by side

The two separate parent cuts are

\[
\underbrace{\mathbf a}_{\substack{\text{standard: first local}\\\text{Bloch/Pauli vector}\\
\text{ARA: three cuts of parent A}}}
=
(\langle XI\rangle,\langle YI\rangle,\langle ZI\rangle)^\mathsf T,
\]

\[
\underbrace{\mathbf b}_{\substack{\text{standard: second local}\\\text{Bloch/Pauli vector}\\
\text{ARA: three cuts of parent B}}}
=
(\langle IX\rangle,\langle IY\rangle,\langle IZ\rangle)^\mathsf T.
\]

The full pair account is

\[
\underbrace{T_{ij}}_{\substack{\text{standard: Pauli}\\\text{correlation tensor}\\
\text{ARA: nine joint cuts}}}
=
\langle\sigma_i\otimes\sigma_j\rangle.
\]

Q24 froze the informative third as

\[
\boxed{
\underbrace{C}_{\substack{\text{standard: connected}\\\text{correlation/covariance tensor}\\
\text{ARA: parent relation beyond}\\\text{the two separate children}}}
=
\underbrace{T}_{\text{joint nine-slot field}}
-
\underbrace{\mathbf a\mathbf b^\mathsf T}_{\text{separate-child completion}}.
}
\]

The ARA diameter reading in every slot is

\[
\boxed{
\underbrace{X^{(9)}_{ij}}_{\text{ARA}^9\text{ coordinate}}
=1-C_{ij}.
}
\]

Thus connected values `+1, 0, -1` become ARA `0, 1, 2`. No raw value was clipped or physically projected before
forming the primary ARA^9 object.

## Results

Let \(s_1\ge s_2\ge s_3\) be the singular values of \(C\). They are the strengths of three independent relation
directions. Q24 also used

\[
h=|\det C|^{1/3}
\]

as three-direction closure strength,

\[
b=s_3/s_1
\]

as weakest/strongest directional balance, and

\[
D_R=
\frac{\|C\|_F^2}{\|C\|_F^2+\|\mathbf a\|^2+\|\mathbf b\|^2}
\]

as the share of the measured parent/local account carried by the connected relation.

| Entity | \(s_1,s_2,s_3\) | Retained | \(h\) | Balance \(b\) | Relation share \(D_R\) | \(\det C\) |
|---|---|---:|---:|---:|---:|---:|
| Phi-plus | `0.992, 0.944, 0.893` | 3 | `0.942` | `0.900` | `0.9963` | `-0.8367` |
| Phi-minus | `1.078, 0.957, 0.855` | 3 | `0.959` | `0.793` | `0.9899` | `-0.8824` |
| Psi-plus | `0.993, 0.956, 0.745` | 3 | `0.891` | `0.751` | `0.9954` | `-0.7074` |
| Psi-minus | `0.954, 0.882, 0.819` | 3 | `0.883` | `0.858` | `0.9842` | `-0.6888` |
| Phi-classical | `0.951, 0.079, 0.020` | 1 | `0.114` | `0.021` | `0.9946` | `-0.0015` |
| Psi-classical | `0.924, 0.109, 0.025` | 1 | `0.135` | `0.027` | `0.9874` | `-0.0025` |
| Bell-uniform-mixed | `0.122, 0.048, 0.015` | 0 | `0.044` | `0.120` | `0.8504` | `+0.0001` |

The relation-share number should not be read alone: a classical one-axis relation can also dominate tiny local
marginals. What distinguishes Bell closure is that the relation remains strong and balanced in **all three**
independent directions.

## What the nine cells show

In the aligned Bell basis, the four prepared records place three strong cells near opposite ARA poles while the
other six sit nearer the `1.0` ridge. Which three pole directions and signs occur distinguishes the four Bell
identities.

The classical mixtures preserve one strong relation direction but cancel the other two. The uniform mixture
cancels all three, leaving all nine cells near the ridge.

This is precisely the non-flattening point:

> The two local children are nearly quiet in every case. Their parent identities differ because the information
> is stored in the full ordered relation between their three cuts.

## Controls

- **Raw versus physical:** both layers returned the exact same seven-entity closure ladder.
- **Bootstrap:** every entity retained its expected number of directions in `2,000/2,000` draws.
- **Orientation:** all four Bell determinants were negative in `2,000/2,000` draws.
- **Proper rotations:** rotating the parent coordinate frames changed individual cells but preserved the frozen
  relation invariants to maximum residual `5.55e-16`.
- **Rank-one destruction:** keeping only the strongest singular direction reduced every Bell tensor from three
  retained directions to one and made its determinant zero to numerical precision.
- **Independent reconstruction:** a separate validator rebuilt the raw tensors from the Q5 projection CSV,
  rebuilt the physical tensors from Q6B, recomputed all tables, intervals and gates, and passed `860/860`.

## What is genuinely important

The important result is not merely that both descriptions contain the number nine. It is that:

1. the older ARA^9 object was explicitly a three-axis coupling structure;
2. the Bell parent has an independently defined three-by-three coupling object;
3. subtracting the separate children leaves a coherent full-rank relation for Bell records;
4. controlled phase mixing reduces that object from three directions to one and then zero;
5. the result survives raw resampling, physical-state correction and coordinate-frame rotation.

That makes ARA^9 a faithful structural crosswalk here, not a decorative relabelling of nine arbitrary values.

## Evidence boundary

This cannot be scored as a fresh provenance hit. Q6 had already opened the same correlation tensors and singular
values; Q24 identifies and formalizes their connection to the older ARA^9 object after that fact.

The result does establish a clean next test. A genuinely new ARA^9 claim should freeze a transformation,
missing-slot reconstruction, noise trajectory, or untouched-state outcome before opening new quantum data.

It does **not** establish that:

- ARA predicted or discovered Bell states, Pauli tomography, CHSH or entanglement;
- nine is uniquely preferred among every possible representation;
- all nine slots are independent;
- universal fractality, phi, TE-ARA ontology or quantum gravity is proved.

## Reproduction

From `analysis/quantum` with the bundled scientific Python:

```powershell
python q24_ara9_bell_relation_test.py
python q24_ara9_bell_relation_validate.py
```

Primary artifacts:

- `Q24_ARA9_BELL_RELATION_PROTOCOL_v1_FROZEN.md`
- `Q24_ARA9_BELL_RELATION_RESULTS.json`
- `Q24_ARA9_BELL_RELATION_MATRICES.csv`
- `Q24_ARA9_BELL_RELATION_METRICS.csv`
- `Q24_ARA9_BELL_RELATION_BOOTSTRAP.csv`
- `Q24_ARA9_BELL_RELATION_GEOMETRY.png`
- `Q24_ARA9_BELL_RELATION_GEOMETRY.svg`
- `Q24_ARA9_BELL_RELATION_VALIDATION.json`

