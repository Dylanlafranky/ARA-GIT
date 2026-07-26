# Q6B physical CHSH coherence ladder

**Date:** 24 July 2026  
**Ledger:** `T265`  
**Verdict:** `SUPPORTED — 20/20 FROZEN GATES`  
**Independent validation:** `PASS — 26/26`

## Outcome

After correcting the raw tomography estimates into physical density matrices, the same parent/child geometry
cleanly recovered an established quantum coherence ladder:

```text
three strong relation axes   → one strong relation axis → no strong relation axes
coherent Bell parent         → classical correlation    → fully mixed parent
CHSH above 2                 → CHSH below 2             → near-zero relation
```

All four physically prepared Bell states crossed the established CHSH boundary in every one of `5,000`
record-bootstrap draws. Both reconstructed classical controls stayed below `2.1` in every draw, and the
reconstructed uniform mixture stayed below `0.6` in every draw.

## The mathematics

The nine parent cuts form

\[
\underbrace{T}_{\substack{\text{standard: two-qubit}\\\text{correlation tensor}\\
\text{ARA: full parent relation}}}
=
\begin{pmatrix}
\langle XX\rangle&\langle XY\rangle&\langle XZ\rangle\\
\langle YX\rangle&\langle YY\rangle&\langle YZ\rangle\\
\langle ZX\rangle&\langle ZY\rangle&\langle ZZ\rangle
\end{pmatrix}.
\]

Its singular values

\[
\underbrace{s_1\ge s_2\ge s_3}_{\substack{\text{standard: independent}\\\text{correlation strengths}\\
\text{ARA: retained relation axes}}}
\]

say how many independent directions of the two-child relation survive. The established Horodecki result is

\[
\underbrace{S_{\max}}_{\substack{\text{maximum CHSH value}\\\text{of the physical parent}}}
=
2\sqrt{
\underbrace{s_1^2+s_2^2}_{\substack{\text{two strongest independent}\\\text{parent-relation cuts}}}
}.
\]

Plainly: one strong correlation direction can be classical. A Bell parent retains at least two mutually
independent directions strongly enough that their joint CHSH account exceeds `2`.

## Physicality correction

Q6 first applied the formula directly to unconstrained raw tomography coefficients. That exposed
\(S_{\max}=2.88579>2\sqrt2\), proving that the raw linear estimate was not a valid physical state.

Q6B was then frozen before correction. It reconstructed

\[
\rho_{\mathrm{lin}}
=
\frac14\sum_{i,j}\langle ij\rangle\,\sigma_i\otimes\sigma_j
\]

and projected its eigenvalues onto the nonnegative, unit-sum simplex while preserving its eigenvectors. Every
resulting state was Hermitian, trace one and positive semidefinite, and every \(S_{\max}\) respected the
Tsirelson limit.

## Results

| Entity | Source type | Local-child mean \(|\langle P\rangle|\) | \(s_1,s_2,s_3\) | \(S_{\max}\) | 95% interval | Strong axes |
|---|---|---:|---|---:|---|---:|
| \(\Phi^+\) | physically prepared | `0.0322` | `0.975, 0.930, 0.908` | `2.694` | `[2.598, 2.730]` | 3 |
| \(\Phi^-\) | physically prepared | `0.0455` | `0.983, 0.910, 0.893` | `2.678` | `[2.512, 2.735]` | 3 |
| \(\Psi^+\) | physically prepared | `0.0363` | `0.924, 0.887, 0.811` | `2.561` | `[2.500, 2.608]` | 3 |
| \(\Psi^-\) | physically prepared | `0.0651` | `0.927, 0.872, 0.830` | `2.545` | `[2.475, 2.604]` | 3 |
| \(\Phi\)-classical | equal-weight reconstruction | `0.0252` | `0.937, 0.060, 0.033` | `1.878` | `[1.785, 1.907]` | 1 |
| \(\Psi\)-classical | equal-weight reconstruction | `0.0328` | `0.897, 0.076, 0.053` | `1.801` | `[1.746, 1.851]` | 1 |
| uniform mixed | equal-weight reconstruction | `0.0172` | `0.117, 0.021, 0.006` | `0.238` | `[0.177, 0.352]` | 0 |

The mean Bell-minus-classical \(S_{\max}\) gap was `0.7798`, exceeding the frozen `0.40` gate.

## ARA reading in plain language

All seven rows look locally quiet: the two children, inspected separately, sit close to the ARA `1.0` ridge.
That local view cannot tell coherent Bell identity, ordinary classical correlation and complete mixing apart.

The difference appears only after reconstructing the parent relation:

- **Bell:** the relation closes strongly in three independent directions. The parent contains phase-sensitive
  structure unavailable in either child alone.
- **Classical mixture:** only one parity/connection direction survives. The other two cancel when opposite Bell
  phases are mixed.
- **Uniform mixture:** all four parent orientations cancel, leaving no strong relation direction.

This is a precise established-quantum example of Dylan's non-flattening rule:

> Two children can each read near a `1.0` ridge while their parent identities remain radically different because
> the missing information lives in how the children are coupled.

It also sharpens `Information³`. The informative third is not “another child.” It is the stateful relation whose
independent directional content can be counted.

## What this adds and what it does not

It adds a deeper standard-physics crosswalk than Q5:

- Q5 recovered **which** Bell parent was prepared from ordered signs.
- Q6B recovers **what kind of closure** the parent has: coherent multi-axis, classical one-axis, or mixed zero-axis.

This is still established Bell/Pauli/Horodecki physics in ARA coordinates. The physically prepared rows are real;
the contrast controls are reconstructed. Therefore this result does not discover entanglement, prove universal
fractal spheres, or show superiority over quantum tomography.

## Next trodden-path rung

The next strong test is a **physically prepared decoherence trajectory**:

1. start with a Bell state;
2. increase a documented noise/dephasing control;
3. freeze the prediction that two phase-sensitive relation axes collapse before or faster than the surviving
   classical parity axis;
4. test whether the retained-axis ladder changes `3 → 1 → 0`;
5. predict the sample at which \(S_{\max}\) crosses `2` before opening later points.

That would turn this static calibration into a genuine time-ordered accumulation/release test and move one rung
closer to unknown quantum outcomes.

## Reproduction

From `analysis/quantum`:

```powershell
python q6b_physical_chsh_coherence_test.py
python q6b_physical_chsh_coherence_validate.py
```

Primary artifacts:

- `Q6B_PHYSICAL_CHSH_COHERENCE_RESULTS.json`
- `Q6B_PHYSICAL_CHSH_COHERENCE_STATES.csv`
- `Q6B_PHYSICAL_CHSH_COHERENCE_BOOTSTRAP.csv`
- `Q6B_PHYSICAL_CHSH_COHERENCE_VALIDATION.json`

