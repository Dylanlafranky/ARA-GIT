# Q52 source-extension calibration — 2026-07-30

## Purpose

This is a source-reproduction check, not an ARA hypothesis test.

Q50 and Q51 found a same-lineage external ARA orientation change from near the
declared `0` direction to near the opposite `2` direction. The existing public
archives end after 500 recorded time slices, so they cannot decide whether the
trajectory later returns toward `0` or merely settles after a one-way reversal.

Before extending those trajectories, the public generator must reproduce the
immutable archive exactly.

## Public sources

- Generator repository: `UnnatiAkhouri/QuNet`
- Calibrated source commit:
  `2b49f27420b8ce8a12b4e6afac4ce5fe62664c68`
- Immutable archive:
  `unnati_submit_12_pure_random.hdf5`
- Archive SHA-256:
  `0e10afb6e5c7bcc3b469a9bb18a9bcae9469bfae165d5da5add93eeeb1972eeb`
- Branch checked:
  `12 qubits/c2_2local connectivity/unitary energy subspace 1/unitary seed 0/ordering seed random`

## Recovered generator state

The archive begins with one excitation on qubit `4`:

```text
[0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
```

The analysis notebook records a Haar two-qubit angle denominator of `15`, so
the repeated two-qubit rotation is:

\[
\theta=\frac{\pi}{15},
\qquad
U_1=
\begin{pmatrix}
\cos\theta&-\sin\theta\\
\sin\theta&\cos\theta
\end{pmatrix}
\]

inside the single-excitation subspace. This is independently visible in the
first archive transition:

\[
\cos^2(\pi/15)=0.9567727288,
\qquad
\sin^2(\pi/15)=0.0432272712.
\]

The saved `previous_order/orders_list/data` array supplies the exact pair
ordering used at each archived transition.

## Calibration result

Using the public generator, the recovered initial state, the
\(\pi/15\) operator and the archived pair order:

- all 66 two-qubit density matrices matched exactly at every one of the first
  20 checked slices;
- replaying all 499 transitions produced all 66 slice-499 density matrices
  with:
  - maximum absolute error `0.0`;
  - root-mean-square error `0.0`.

This is bit-for-bit source reproduction for the checked stored observables.
The longer continuation can therefore start from the exact full generated
state rather than attempting to reconstruct a many-body state from pairwise
reductions.

## Remaining continuation choice

The archived `random` branch does not store the Python pseudorandom-generator
state used after slice 499. A continuation therefore cannot claim to recover
the one unrealized future that the original process would have generated.

The clean test is a **predeclared continuation ensemble**:

1. replay slices `0–499` exactly;
2. branch the exact full state into fixed, published continuation seeds;
3. use only the two public `c2_2local` orderings and the unchanged
   \(\pi/15\) operator;
4. evaluate every continuation with the unchanged Q50 external ARA
   coordinate.

This tests whether return, settling or repeated reversal is robust to the
allowed future coupling order. It does not treat any chosen future ordering as
the missing historical truth.

## Exact next-test object requiring re-confirmation

After the context-compaction fidelity rule, Q52 must be re-confirmed before it
is frozen or run.

Proposed measured object:

> From the exactly reproduced slice-499 full state, do independently seeded
> valid coupling-order continuations show a complete active external ARA
> traversal `0 → 2 → 0`, or do they remain near `2` with collapsed movement?

The test must retain three separate outcomes:

- **complete return:** crosses from the declared half to the opposite half,
  later crosses back, and movement recovers;
- **one-way settling:** remains on the opposite half while movement stays
  collapsed;
- **driver-dependent/undetermined:** different permitted continuations produce
  materially different outcomes.

No Q52 outcome has been inspected or scored at the time of this calibration
record.
