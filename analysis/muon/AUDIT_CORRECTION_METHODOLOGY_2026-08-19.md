# Audit correction — methodology and provenance

**Date:** 19 August 2026
**Applies to:** all four muon audits dated 19 August 2026
**Cause:** I audited sixteen tests without reading
`FableConvo/SESSION_RECORD_2026-08-16_IRRATIONALITY_DI_ARA_AND_MUON_INFORMATION3.md`,
which states the methodology and already classifies most of what I "found."

---

## 1. What I got wrong

### 1.1 The methodology is ARA-first by design, not by accident

Frozen in the session record, §2 and §11:

> Dylan specifies and confirms the identities, direction, rungs and proposed coupling.
> Codex then formalises and tests them.

> **ARA-first, science side-by-side.** Established physics supplies source meaning,
> controls and interpretation; it does not overwrite the ARA geometry being tested.

So the sequence is: geometry declared → coordinates and gates built → test run →
established physics used for interpretation and controls. Established physics supplying
the *meaning* of a landmark is the **intended structure**, not a defect I discovered.

My repeated framing — "the Standard Model supplies the values, ARA supplies the labels,
therefore ARA earns nothing" — measured the work against a bottom-up methodology it does
not use and does not claim to use.

### 1.2 The classification I proposed was already frozen, three days earlier

My cross-cutting table ("every positive result recovers something already established")
duplicates §10 of the session record, which predates it:

| Session record class | Stated ceiling |
|---|---|
| Exact geometry/bookkeeping | "Definitions or conservation, not empirical support" |
| Established-physics crosswalk | "Shows ARA-compatible recovery, not new physical law" |
| Physical partial support | "Identity- and boundary-specific; not universal" |
| Failed universal/fixed claims | "Must remain failed; cannot be relabelled" |
| Structurally unavailable | "Requires different data, not more reinterpretation" |

And **Michel `0.49/1.51` is listed there explicitly, under established-physics
crosswalk**, with that ceiling attached. I presented as an audit finding a classification
the author had already frozen and applied to the same result.

### 1.3 Two of my "required corrections" were already standing rules

```
Rule 7  — Do not count forced closure as evidence. A complement defined as 2−x
          will close by construction.
Rule 10 — Preserve negative results and post-result status. Diagnostics can explain
          a failure but cannot retroactively pass a frozen gate.
```

My "identities in plain text, results in boxes" and my gate-amendment discipline are
restatements of these. Frozen 16 August; my audits are dated 19 August.

### 1.4 The binning concern was already caught, in this series

T372 corrected a spurious exact `0.5` landmark caused by plotting completed
0.5 μs bins at their centres; native 1 ns reconstruction gave `0.4374`. So the
digitisation-artefact failure mode I raised against T392 had already been identified,
diagnosed and corrected once by the same programme.

---

## 2. What the provenance record does and does not settle

The `(0.5, 1.5)` coarse pair is **not** back-derived from the Michel spectrum. It
appears in `PRIME_TEST_RELATIONAL_GLOSSARY.md` ("Coarse pair ridge — examples `(0,2)`,
`(0.5,1.5)`") in the July prime work, and the half-weight child rule is April-dated.
The landmark therefore predates the muon programme by months and arrives from an
unrelated domain.

T381 froze an 18-cut master architecture on 14 August, before T392–T397. The geometric
question — *what is the child beneath the population spin parent?* — was declared first,
and the polarized Michel spectrum was selected as the instrument to answer it.

**What that establishes:** the landmark was not fitted to the muon data.

**What it does not establish:** whether the human author knew, before the test, that the
polarized Michel asymmetry has an exact analytic zero at `x = 1/2` from the `(2x − 1)`
factor. The AI assistant certainly did. This is the standing caveat already recorded in
`CLAIMS_STATUS.md` — *"blind applies to the human author, not to the human–AI pair"* —
and Rule 4 of the provenance ledger says self-scoring cannot settle it.

So the correct status is: **ARA-declared landmark, predating and from another domain,
tested against a Standard-Model-exact value on an instrument chosen for the purpose.**
That is a crosswalk in the author's own classification, and it is a legitimate one.

---

## 3. Findings that survive unchanged

These are defects *within* the stated methodology and would be defects under any
framework. None depend on the bottom-up assumption I wrongly applied.

| Finding | Audit | Why it stands |
|---|---|---|
| **T394's `M0` is a strawman baseline** | T392–T401 §2.2 | Stopped cosmic muons are a `μ⁺/μ⁻` mixture; `μ⁻` capture on oxygen shortens its effective lifetime to ~1.8 μs against `μ⁺` at 2.197 μs. A single truncated exponential cannot fit two components. The `0.0436` nats gain partly recovers textbook structure, and rises monotonically with bin count (`0.017 → 0.063`). A matched-flexibility baseline is required regardless of methodology. |
| **T395's headline is 3× its non-trivial part** | T306–T400 §3.2 | `uncond → phase-space` is `0.1755` of the `0.2643`; only `0.0888` is parent conditioning. `C` is defined relative to `N = 2−P`, so support information is construction. This is Rule 7 applied to a gain rather than a closure. |
| **T392's offset propagates into T393** | T392–T401 §1.3 | `0.490190 / 2 = 0.245095`. One digitisation offset reported as two independent near-misses. A reporting issue, not a framework issue. |
| **T399's ordering is forced by monotonicity** | T392–T401 §3.1 | Landmarks read off a monotone cumulative are ordered by construction; only the values are empirical. Rule 7's logic applied to sequence rather than closure. |
| **`0.706306` is a shared dependency of four tests** | T306–T400 §4.2 | T400, T404, T406, T407 all rest on it; T404 has already shown this chain can produce a plausible crest from a definition error; `1/√2 = 0.707107` is `0.0008` away and unchecked. |
| **T409's R2 needs a multiple-comparison statement** | T403–T409 §4.1 | Three frozen zones, one significant `p`. Bonferroni puts `0.0164 → 0.049`. |
| **T409's bands may be counter combinatorics** | T403–T409 §4.2 | Integer multiplicities produce discrete ratio bands by default. One groupby settles it. |

---

## 4. Corrections to my own audits

1. **Strike the "ARA earns nothing" framing** from `AUDIT_MUON_T403_T409` §5.1,
   `AUDIT_MUON_T396_T405` §5, `AUDIT_MUON_T306_T400` §5.3 and
   `AUDIT_MUON_T392_T401` §5.1. Replace with: *these are established-physics crosswalks
   in the author's own classification, with the ceiling already stated in the 16 August
   session record §10.*
2. **Withdraw** the "identities in boxes" recommendation and the gate-amendment rule as
   novel — both restate frozen Rules 7 and 10. Retain only the specific instance
   (T306's unlabelled `A = A` box) as a compliance gap against Rule 7, not as a new rule.
3. **Retain §3 above in full.**

---

## 4b. NOTE TO ADD — author prior-knowledge statement for the muon domain

**Audit check performed 19 August 2026.** `FableConvo/PROVENANCE_LEDGER.md` contains
extensive per-test provenance for the muon programme (T370–T397), recording proposal
order for each test — e.g. the 13 August T371 entry noting that Dylan proposed a
parallel-branch or bottom-up pion/muon lineage and "the established chain clarified"
the actual relation.

However, **no domain prior-knowledge statement exists** for nuclear or particle physics.
`CLAIMS_STATUS.md`'s "On the author's prior knowledge" section lists KAM theory, action
quantization, the Sun's internal subsystem structure, dark-sector categories and
camshaft/mechanical-timing concepts. Muon decay, nuclear reaction roles and neutrino
physics are absent, covered only by the catch-all "many of the other systems later
tested."

This should be added, because the muon programme is now the largest single test series
in the repository and its blind status depends on it.

### Recommended text, for `CLAIMS_STATUS.md` prior-knowledge section

> **General background and domain knowledge (stated 19 August 2026).** The author has no
> formal training in physics, mathematics or any physical science. Formal science study
> consists of approximately one year of Environmental Science at university, weighted
> toward chemistry, with poor results. All subsequent learning has been at hobby level.
>
> The author's own description of the working knowledge available to him: broad
> familiarity with what interactions exist, without knowledge of the mechanisms by which
> they occur. In quantum specifically: aware that entanglement and information sharing
> exist, without knowledge of how either is measured.
>
> **Nuclear and particle physics.** At the start of the fusion work the author did not
> reliably distinguish the roles of fission and fusion, believed the muon couples to a
> neutrino during catalysis, and had applied the ARA coordinate to wavefunction width
> rather than phase duration. All three were corrected in session and are recorded
> contemporaneously in `ARA_Fusion_Theory.md` (1 June 2026) — see its opening line
> "records the session thread from the fission↔fusion clarification onward" and its
> logged corrections.
>
> As of 19 August 2026, at the close of the T392–T409 muon series, the author's stated
> knowledge of muons is: that there are many of them, that they are used in fusion, that
> decay releases two neutrinos, and that they decay. The author did not know the Michel
> spectrum, the `(2x − 1)` angular factor whose exact zero at `x = 1/2` sets the
> polarized-decay asymmetry reversal, or the `μ⁺/μ⁻` effective-lifetime difference from
> nuclear capture.
>
> **Division of labour.** The author supplies the relational geometry: identities,
> direction, rungs, proposed couplings, and which cut is parent, child or relation. AI
> assistants supply all domain knowledge — source selection, established-physics
> interpretation, coordinate formalisation, protocol drafting, controls and statistical
> machinery. This division is stated in the frozen consultation rule of
> `SESSION_RECORD_2026-08-16`.
>
> Consequently "blind" applies to the human author and to the geometry, **not** to the
> human–AI pair, and not to source selection. Per Rule 4 of the provenance ledger this
> cannot be scored by the same assistants and awaits independent verification.

### Consequence for how the work should be described

With this background stated explicitly, the defensible claim is **not** "an untrained
person independently derived established physics." It is narrower and more testable:

> A relational geometry, specified by someone without domain knowledge of the fields
> tested, directed searches that landed on established structures more often than a
> matched control would predict.

That is a claim about the geometry's value as a **search heuristic**, it is independent
of who holds it, and it is exactly what the unrun decoy protocol
(`ARA_DECOY_CONTROLLED_REPETITION_TEST_PROTOCOL_v1_DRAFT.md`) was designed to measure.
It is also a stronger claim than it sounds: generative search methods are rarer than
correct theories.

### Why this is worth recording now

The corroboration is **contemporaneous and against interest**: three logged physics
errors dated 1 June 2026, ten weeks before T392 approached the Michel spectrum. That is
materially stronger than a retrospective claim of ignorance, which Rule 4 would not
accept.

It is also perishable. Each further muon test teaches the author more of the field; a
knowledge-state statement made after the series cannot be made cleanly again.

**Recorded by the auditor as the author's statement, not verified by the auditor.**

---

## 5. Note for future audits of this repository

Read the session record for the period before auditing the tests. The programme
maintains its own evidence classification, standing rules and claim ceilings, and
several of them are more conservative than the ones an outside auditor would arrive at
independently. Auditing the outputs without the methodology produces findings that are
either already frozen or aimed at a method the work does not use.

This is the fourth time in this engagement I have asserted a gap that turned out to be a
hole in my reading. The pattern is consistent enough to be a rule: **check provenance
and methodology before assessing content.**
