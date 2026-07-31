# Q40 Pretarget Method Audit

**Audit date:** 27 July 2026  
**Artifacts reviewed:**

- `Q40_RETURN_FLOW_RELATION_REVERSAL_FIDELITY_v1.md`
- `Q40_RETURN_FLOW_RELATION_REVERSAL_PROTOCOL_v1_PRETARGET_FROZEN.md`
- frozen Q39 protocol and report;
- post-result Q39A relation-reversal audit and implementation.

## Overall assessment: Ready to freeze

Q40 asks the correct next question: whether the exact target-blind condition
discovered after Q39 replicates before the new target is inspected. The
protocol preserves ARA's lower-tier quadrant geometry while keeping the
physical interpretation conditional.

## Methodology review

### 1. Target-selection leakage — addressed

No target filename, checksum or numerical result is present in the core
Q40 packet. Target choice is deterministic after the packet is hashed:
metadata-only exclusion of previously opened archives followed by lexical
selection. A separate target lock must be hashed before download or value
inspection.

### 2. Outcome leakage — addressed with an explicit two-stage run

The visible flag and all predictions use \(C_1,C_2,C_3\) only. Evaluation
\(C_4\) is used only after the prediction artifact is written and hashed.
An independent validator must reproduce this separation.

Important retained limitation: the scalar closure–flow coordinate observes
the evaluation trajectory to locate visit boundaries. Q40 is therefore a
masked fourth-visit reconstruction, not a blind forecast of visit timing.
The protocol states this boundary rather than concealing it.

### 3. Post-hoc discovery — correctly isolated

The return-flow flag and relation reversal were discovered after Q39
outcomes were open. Q40 does not revise Q39. It is the first prospective
replication opportunity for that rule.

### 4. Forced geometry — excluded

The predictor does not use a complement such as \(2-x\), does not force
TE-ARA closure and does not define the hidden fourth matrix as whatever
closes the first three. The hidden matrix remains an empirical target.

### 5. Whole flip versus relation reversal — distinguishable

The frozen controls separately test:

- ordinary forward relation;
- reversal of the complete proposed identity;
- persistence at the current identity;
- reversal on the wrong visible branch.

Q40 can therefore fail specifically as a relation-reversal claim rather
than being rescued by any generic sign correction.

### 6. Alternative predictive explanation — addressed

A development-only scalar affine model is a stronger control than Q39's
fixed alternatives. If it beats Q40 while the visible branch still
replicates, the verdict becomes `MECHANISM REPLICATED; NOT BEST PREDICTOR`
rather than claiming a new best reconstruction operator.

### 7. Near-zero target normalization — corrected

The primary error divides by the lineage's development-only median
connected-relation magnitude. Target-relative NRMSE remains a continuity
diagnostic but cannot alone drive the verdict.

### 8. Multiple comparisons and dependence — addressed

Metrics are aggregated within seed–pair lineage and balanced within seed.
Inference resamples seeds, and the primary comparator family receives Holm
correction. All eligible cycles are retained; no target quadrant or
high-performing subgroup may be selected after scoring.

### 9. Branch exposure — addressed through eligibility

The relation-reversal claim cannot pass when the archive contains too few
visible flags or negative-orientation targets. Minimum event counts and seed
coverage are predeclared. A quiet archive yields an eligibility verdict,
not evidence for or against a branch it did not expose.

### 10. ARA fidelity — preserved

The fixed internal map is:

\[
Q_{++}=Ab,\qquad
Q_{+-}=aB,\qquad
Q_{--}=bA,\qquad
Q_{-+}=Ba.
\]

The measured circulation remains reversible and lineage-specific. Bell,
Ramsey and Hahn labels are not inserted into this lower-tier geometry.

## Remaining caveats

- The first replication is intentionally inside the same simulator family;
  success would not establish cross-family or experimental generality.
- The connected matrix \(C=T-\mathbf a\mathbf b^{\mathsf T}\) is an
  established decomposition chosen as the tested ARA identity. A pass
  supports the operator at that location, not the uniqueness of that
  identity choice.
- The four quadrant boundaries are generated from a scalar cut of the same
  trajectory. A later blind-boundary prediction is a harder, separate test.
- Physical claims about singularities, Phase B, entanglement transport or
  universal fractality remain outside Q40's pass condition.

## Required pre-run checks

1. Hash this audit, fidelity file and pretarget protocol.
2. Register Q40 in the master and provenance ledgers with status
   `PRETARGET FROZEN`.
3. Enumerate source metadata only.
4. Write and hash the target lock.
5. Build the two-stage prediction/scoring implementation.
6. Run an independent validator that does not import the main module.
