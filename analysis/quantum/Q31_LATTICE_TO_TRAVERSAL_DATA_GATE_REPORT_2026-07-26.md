# Q31 lattice-to-traversal singularity-flip data-gate report

**Date:** 26 July 2026  
**Ledger:** T285  
**Frozen protocol:** `Q31_LATTICE_TO_TRAVERSAL_PROTOCOL_v1_FROZEN.md`  
**Verdict:** **INCONCLUSIVE — DATA/ELIGIBILITY GATE**  
**Outcome metrics calculated:** **No**

## Answer first

The proposed test is mathematically specified, timestamped, checksum-pinned and
ready to run, but none of the first eight public experimental sources inspected
contains the complete measurement object required by the frozen protocol.

The closest sources split into two groups:

1. rich two- or three-coordinate paths without enough independent units or an
   externally imposed lattice-to-release crossing; and
2. many externally detected transitions without a two-coordinate path on both
   sides of the transition.

Therefore Q31 has **not failed** and has **not passed**. It did not reach its
registered ARA outcome calculation. Changing the source criteria after seeing
this would weaken the test, so the protocol remains unchanged.

## Scope correction after user clarification

Q31 is **not** the first test of whether an ARA singularity flip exists. It is
a narrower quantum-domain replication attempt: does the already-declared
conditional flip rule appear here specifically as
`persistent lattice -> handover -> coherent non-closing traversal`?

The relevant earlier lineage is mixed:

| Earlier line | Result | Boundary |
|---|---|---|
| Formula/engine tests | Flip-at-low-energy/null and transit-to-later-coherence patterns were positive in several systems; per-rung phase locking was null, QBO was an exception, and inserting the flip value directly hurt prediction | Soft/geometric and conditional evidence, not one universal constant |
| Prime PN30 | The dynamic `x -> 2-x` flip improved unresolved-composite discrimination from AUC `0.5301` to `0.5663` | Directional support, but the frozen one-sided result was `p=0.06199`, so not a confirmatory pass |
| Quantum Q14 | Same-rung observations were consistent with no flip until a completed seam crossing | A consistency check, not independent proof |
| Quantum Q22B | A strict three-boundary odd-parity flip representation passed only `1/13` gates | That particular transported-lineage implementation was not supported |
| Quantum Q31 | No public source passed the frozen data gate | The lattice-to-traversal quantum appearance remains unmeasured |

Accordingly, the honest status is: the broader conditional flip proposal has
prior test history, including both supportive and adverse results; Q31 does not
re-adjudicate that whole history.

## The ARA question in plain language

The registered geometry asks whether a strongly connected quantum relation
behaves as follows:

1. **Before the handover:** the same neighbours or relation directions persist
   from slice to slice. This is the local ARA connection/lattice side near `2`.
2. **At the handover:** an experimental control or detector—not the ARA
   calculation—marks the crossing near `1`.
3. **After the handover:** the path keeps coherent local direction for a short
   distance but does not settle back into the same partners or a short repeating
   loop. This is the proposed traversal side toward `0`.

That produces a falsifiable distinction between a flip and three ordinary
alternatives:

- **decay:** connection disappears but structured traversal does not appear;
- **random diffusion:** movement appears but has no short directional memory;
- **another lattice:** the post-side closes repeatedly onto stable partners.

## Frozen measurement

For the source-native relation vector \(v_r(t)\):

\[
C_r(t)=
\frac{\langle |v_r(t)|,|v_r(t+1)|\rangle}
{||v_r(t)||\,||v_r(t+1)||},
\]

\[
D_r(t)=
\min\left(1,\frac{||\Delta v_r(t)||}{a_r(t)+a_r(t+1)}\right)
\]

\[
P_r(t)=
\frac{1+\operatorname{Re}
\langle\widehat{\Delta v_r(t)},\widehat{\Delta v_r(t+1)}\rangle}{2},
\]

\[
T_r(t)=D_r(t)P_r(t),
\qquad
x_r(t)=\frac{2C_r(t)}{C_r(t)+T_r(t)}.
\]

The proposed flip requires `C` to fall, `T` to rise at the same externally
located crossing, and `x` to move from above `1` to below `1` on untouched
evaluation units.

## Public-source audit

The following sequence was inspected without calculating a Q31 outcome on an
ineligible source.

| Order | Public experimental source | Useful content | Frozen-gate result |
|---:|---|---|---|
| 1 | Vaartjes et al., nuclear-spin-qudit precession, Dryad `10.5061/dryad.547d7wmj0` | Density-matrix tomography and off-diagonal precession | No externally declared lattice-to-release handover and no clearly identified 60-unit split |
| 2 | Jiang et al., Fermi-Hubbard charge/spin dynamics, Dryad `10.5061/dryad.crjdfn32v` | Measured lattice spreading | Advertised records are primarily density/spreading summaries, not a native non-diagonal relation path |
| 3 | Yen et al., Floquet Landau–Zener tunnelling, Zenodo `10.5281/zenodo.18860416` | External drive and tunnelling | Repository metadata does not establish the required relation path and independent units |
| 4 | Lin et al., photonic quantum walks, Zenodo `10.5281/zenodo.18264638` / Dryad `10.5061/dryad.3ffbg79vk` | Experimental three-axis sphere trajectories | Only 9 measured trajectories; theoretical curves were not counted as trials |
| 5 | Dalmasso et al., Quantinuum H1 2D trajectories, Zenodo `20075236` | 1,280–1,480 H1 shots and 16-site lattice | Hardware paths contain only 10, 14, 14, 16 and 18 ordered steps; the 600–1,000-step paths are numerical |
| 6 | Farid et al., fluxon decay, Zenodo `8004359` | Repeated detector-anchored tunnelling events | Fig. 8c is scalar monitoring ending at tunnelling; no two-coordinate post-handover path; insufficient transitions |
| 7 | NIST digital qubit control, DOI `10.18434/mds2-2932` | Public I/Q-derived parameter sweeps | Published CSVs are averaged sweeps, not at least 60 independent crossing paths |
| 8 | Larsen et al., 2D photonic cluster state, Figshare `8647211` | Long public \(x/p\) homodyne traces of a large lattice | Suitable stable-lattice control, but no externally switched lattice-to-release crossing |

## Candidate 6 exact audit

Candidate 6 was the closest event-based source. Its 297,216,848-byte archive
matched the published MD5:

`ced1ed4af893ad064045900903e19a17`

Following the authors' notebook filters:

| Flux condition | Tunnelling events | Events with at least 25 pre-samples | Median time | Maximum time |
|---|---:|---:|---:|---:|
| `6.6507` | 64 | 51 | 2,760 s | 15,420 s |
| `6.6641` | 51 | 45 | 8,250 s | 27,570 s |
| `6.7057` | 85 | 48 | 810 s | 7,110 s |
| **Total** | **200** | **144** | — | — |

A deterministic half split leaves at most 72 evaluation events with 25
pre-handover samples. The frozen gate requires 500 eligible evaluation
transitions. More decisively, monitoring stops when tunnelling is detected, so
there is no post-handover relation path. The Fig. 8c raw records also do not
retain fixed I and Q coordinates throughout the event. I/Q mentioned elsewhere
in the repository belongs to different measurements and cannot be joined to
these transition records.

This corrects the provisional v3 source note, which had inferred that candidate
6 might carry raw I/Q through the transition before the archive schema was
opened.

## Why no exploratory “flip score” was reported

Using a scalar pre-transition trace would make every fall in persistence look
like traversal simply because the detector value changed. Without a
two-coordinate post-path:

- direction memory is undefined;
- return to the same partner cannot be distinguished from amplitude decay;
- the stable-lattice and phase-randomised controls do not have equal
  information;
- the claimed `2 → 1 → 0` orientation could be created by the measurement
  design itself.

That would test a different, easier claim. Q31 therefore stops at the data gate.

## What data would make the test decisive

The smallest useful release should contain:

- at least 60 independent trajectories, so 30 remain untouched for evaluation;
- at least 25 ordered samples surrounding every externally marked crossing;
- two fixed-basis signed or complex coordinates before and after the crossing;
- at least 500 eligible evaluation transitions;
- the experimental pulse or detector label locating the crossing;
- a matched no-crossing condition;
- native magnitude and precision metadata.

A suitable experiment could repeatedly prepare a stable two-coordinate
relation lattice, apply a predeclared release pulse, and record both quadratures
for at least 12 samples after release. The existing formulas and gates then run
without alteration.

## Reproduction

From `analysis/quantum/`:

```powershell
python q31_data_gate_audit.py
python q31_build_notebook.py
```

Outputs:

- `Q31_DATA_GATE_AUDIT_RESULTS.json`
- `Q31_LATTICE_TO_TRAVERSAL_DATA_GATE_AUDIT_NOTEBOOK.ipynb`

The audit script verifies the local published checksums, enumerates the H1
hardware paths, applies the candidate-6 event filters and asserts that no
confirmatory Q31 outcome statistic was calculated.

## Scientific status

**Claim verdict:** **INCONCLUSIVE** because `D1–D3` cannot all be evaluated on
one eligible public source.

**Geometry verdict:** not measured. The proposed lattice → handover →
short-memory/non-closing-traversal package remains a registered, falsifiable
quantum-domain ARA hypothesis.

**What this work did establish:** the hypothesis now has a precise relation
object, a scale orientation, an external crossing rule, ordinary-physics rival
models, negative controls, an untouched holdout, numeric pass gates and explicit
data requirements. That is a substantial methodological advance, but not
evidence that the flip exists.

## Does the missing public measurement count as evidence?

Only in a limited methodological sense. The source audit found a recurring
measurement split: public records often preserve either a rich relation path
without a controlled handover, or many handovers without the same relation
coordinates continuing on the far side. That is a useful
**measurement-ecology clue** and is consistent with Dylan's expectation that
the counter-side is difficult to retain in the current observation cut.

It is not, by itself, physical evidence for the flip. The same absence can be
caused by experimental purpose, destructive detection, averaging, storage
choices or publication practice. Promoting selective absence to empirical
evidence would require a separate frozen availability study that predicts in
advance which seam-crossing experiments should omit the far-side coordinates,
then compares them with matched non-seam experiments. Q31 makes no such
availability claim.
