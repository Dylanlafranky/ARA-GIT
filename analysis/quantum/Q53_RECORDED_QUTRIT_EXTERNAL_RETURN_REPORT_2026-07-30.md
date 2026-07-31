# Q53 — recorded trapped-qutrit external-return report

**Date:** 30 July 2026  
**Frozen verdict:** **NOT SUPPORTED — 1/4 substantive gates**  
**Validation:** **PASS — 22/22 independent checks**  
**Source class:** recorded hardware measurements from one trapped-ion qutrit

## Answer first

Q53 replaced Q52's generated simulator futures with a large already-recorded
experimental trajectory:

```text
53,459,987 valid sequential measurements
53,301 retained source subsequences
1,062 source-flagged purged subsequences
13 fixed physical measurement directions
```

The test asked only whether the whole-direction vector repeatedly completed:

\[
\frac1e
\longrightarrow
\phi
\longrightarrow
\frac1e,
\]

mapped locally as:

\[
0\longrightarrow2\longrightarrow0.
\]

The answer on this coordinate is **no**.

Strict returns occurred occasionally:

```text
cut (ψ0,ψ1): 7
cut (ψ1,ψ2): 3
cut (ψ2,ψ0): 3
```

But their order did not beat shuffled versions of the same recorded
directions. In every cut and chronological third, the observed return count
was below the shuffled `99th` percentile. The declared
\(1/e\leftrightarrow\phi\) arc also did not consistently contain more
headings or more returns than its three equal-width quarter-turn rotations.

Thus the record contains chance-compatible endpoint crossings, not an
identified ordered whole-vector wobble along the declared landmarks.

## What was recorded rather than generated

The public ETH Zürich source contains one physical \(^{40}\mathrm{Ca}^+\)
qutrit subjected to a continuous sequence of projective measurements. Each
stored pair gives:

1. one of the 13 published Yu–Oh measurement rays;
2. the raw detected photon count.

The next ray was selected in real time by a quantum random-number generator.
The experiment's retained subsequences can be concatenated because each new
subsequence restarts from the last ray of the previous retained one.

Source:

- paper: <https://arxiv.org/pdf/1706.07370>;
- data page:
  <https://tiqi.ethz.ch/publications-and-awards/public-datasets.html>;
- local immutable source SHA-256:
  `5410775C307EDEA9F68E95133CF0A733B6CD34E7D9D774B6509472FACE74D55D`.

No simulated continuation, interpolated sample or generated future entered
Q53.

## ARA measured object

The 13 published rays were retained in their declared real three-dimensional
geometry. The source threshold classified each photon response as bright or
dark:

- bright: the recorded state closes onto the selected ray;
- dark: the preceding state is projected into the plane perpendicular to the
  selected ray.

This reconstructs a recorded post-measurement direction; it does not invent
an observation.

The sphere was read using all three fixed coordinate cuts:

\[
(\psi_0,\psi_1),\qquad
(\psi_1,\psi_2),\qquad
(\psi_2,\psi_0).
\]

In each cut, four ordered quadrants defined a complete internal circuit.
Every complete circuit was fitted as one circle. The centre-to-centre tangent
between neighbouring whole circuits supplied the external direction carrying
the complete circuit through recorded time, retaining the earlier Q49
construct.

Extraction produced:

| Fixed sphere cut | Complete circuits | Whole-centre events |
|---|---:|---:|
| \((\psi_0,\psi_1)\) | `196,066` | `168,399` |
| \((\psi_1,\psi_2)\) | `196,763` | `169,035` |
| \((\psi_2,\psi_0)\) | `196,011` | `168,456` |

At the primary active-movement threshold, `167,842–168,493` events survived
per cut. Median fitted-circle residual was approximately `0.126`; the
90th percentile was approximately `0.186`.

## Frozen directional results

The declared arc ran from:

\[
L=\frac1e=0.367879441\ldots
\]

to:

\[
R=\operatorname{frac}(\phi)=\phi-1=0.618033989\ldots
\]

with width:

\[
R-L=0.250154548\ldots\ \text{turns}.
\]

### Heading occupancy

| Cut | Declared | Rotated 1 | Rotated 2 | Rotated 3 | Declared wins? |
|---|---:|---:|---:|---:|---|
| \((\psi_0,\psi_1)\) | `41,910` | `42,051` | `42,036` | `41,973` | no |
| \((\psi_1,\psi_2)\) | `41,912` | `42,223` | `42,109` | `42,351` | no |
| \((\psi_2,\psi_0)\) | `42,095` | `42,061` | `42,076` | `41,808` | yes |

Only one of three cuts preferred the declared location. The occupancies are
close to the approximately one-quarter share expected from four matched
quarter-turn locations.

### Complete `0 → 2 → 0` returns

| Cut | Declared | Rotated 1 | Rotated 2 | Rotated 3 |
|---|---:|---:|---:|---:|
| \((\psi_0,\psi_1)\) | `7` | `5` | `3` | `2` |
| \((\psi_1,\psi_2)\) | `3` | `3` | `1` | `3` |
| \((\psi_2,\psi_0)\) | `3` | `2` | `2` | `3` |

The first cut placed the declared arc above its controls. The second did not;
the third tied a rotated control. Landmark specificity therefore failed.

### Time-order control

Each chronological third contained approximately `56,000` active
whole-centre events per cut. The observed declared returns per cell ranged
from `0` to `3`. Shuffling headings inside fixed `10,000`-event blocks gave:

```text
mean shuffled returns: 2.398 to 2.648
99th percentile:       7 in every cell
observed returns:       0 to 3
```

No cut beat its shuffled `99th` percentile in any chronological third.
Therefore the observed direction order supplies no evidence for the proposed
back-and-forth pathway.

## Frozen gates

| Gate | Result |
|---|---|
| G0 — source and reconstruction integrity | **PASS** |
| G1 — declared directional location | **FAIL** |
| G2 — at least one complete return in the required strata | **PASS** |
| G3 — time order beats shuffle | **FAIL** |
| G4 — declared landmarks beat rotated controls | **FAIL** |

Existence alone passed G2 because two cuts contained at least one return in
every chronological third. The shuffled control shows why that is not enough:
randomized order commonly produced at least as many returns. With only one of
four substantive gates passing, the frozen verdict is **NOT SUPPORTED**.

## Integrity and limitations

- All `53,459,987` expected valid measurements were processed.
- All `1,062` source-flagged rows were excluded exactly as instructed.
- No reconstructed unit-vector norm failed the `1e-9` check.
- `15,742` dark results were incompatible with an exactly aligned preceding
  ray under the ideal reconstruction. They were not repaired. Each ended the
  local circuit lineage until the next recorded bright result fixed the state
  direction again.
- The experiment is physically recorded but externally driven: the QRNG
  changes the measurement coupling direction at every step. Q53 therefore
  tests whether the proposed whole-vector carrier survives that recorded
  environment. It is not a test of a freely evolving autonomous qutrit.
- The physical state direction is reconstructed using the experiment's
  published projective-measurement rule. The observed photon outcomes
  themselves remain untouched.

## Scientific interpretation

This is a useful negative result.

Q50–Q51 found a half-turn external reversal inside deterministic simulator
archives. Q52 could not decide whether that reversal returned because its
future had to be generated. Q53 supplied the missing long hardware record and
tested the exact return claim without using the already-known parent-ridge
behaviour.

On this recorded qutrit coordinate:

\[
\boxed{\text{ordered }1/e\rightarrow\phi\rightarrow1/e
\text{ whole-direction wobble is not supported}.}
\]

The test does not falsify ARA's general sphere or phase-pair claims. It
rejects this specific identification of the whole external direction with
the \(1/e\leftrightarrow\phi\) path in this randomly driven qutrit record.

## Reproduction

From `analysis/quantum`:

```powershell
node q53_extract_recorded_qutrit_external_return.mjs

& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' `
  -u q53_recorded_qutrit_external_return.py

& 'F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe' `
  -u q53_validate_recorded_qutrit_external_return.py
```

Primary artifacts:

- `Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_PROTOCOL_v1_FROZEN.md`
- `Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_EXTRACTION.json`
- `Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_RESULTS.json`
- `Q53_RECORDED_QUTRIT_EXTERNAL_RETURN.png`
- `Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_VALIDATION.json`
- `q53_extract_recorded_qutrit_external_return.mjs`
- `q53_recorded_qutrit_external_return.py`
- `q53_validate_recorded_qutrit_external_return.py`

