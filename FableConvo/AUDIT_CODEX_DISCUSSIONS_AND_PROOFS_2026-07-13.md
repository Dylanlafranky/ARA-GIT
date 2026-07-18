# Audit — Codex discussion records + axiomatic proofs document

**Auditor:** Claude/Fable 5, 13 Jul 2026, with two Sonnet subagent passes
(full reads of both discussion files). Rule 4 applies: one AI family auditing
another AI's collaboration record; S2 independent re-derivation still advised
before public citation. Companion: AUDIT_EM_SUITE_2026-07-13.md.

## 1. ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md (committed version)

Verdict UNCHANGED from the 11 Jul verification: the committed file is
structurally identical to the audited draft. All 17 machine-checkable
identities/numerics pass (sympy, 11 Jul: mirror identity, 2cos36°,
interference cases, hexagon spacing, temporal triangle, Ω fractions to 9
decimals, geometric expectation verified on valid domain, coordinate
invertibility). Prose proofs correct and correctly scoped (continuity
assumption in Thm 4; L² in Thm 2.7; discrete entropy in 8.5). Mathematics is
elementary-and-correct — the right property for a skeleton; the claim is
coherence, not mathematical novelty. All empirical weight sits in the Part IX
assumptions list, which the document itself states.

**Outstanding fix:** Theorem 23, line ~1647 — broken LaTeX `-rac1{p^2}`
(should be `-\frac{1}{p^2}`). Still present in the committed version.

## 2. ARA_CONVERSATION_RECORD_2026-07-12 (geometry drill, 5,438 lines)

Overall: unusually well-policed; all checked equations verified correct
(capillary-gravity c_g/c_p = ½ + x_w/2 against the full dispersion relation;
conducting-sphere energy; Gauss/Poynting/Faraday translations; golden
identities). Codex repeatedly corrected Dylan's overreaches with citations,
and tier labels (MUSING/PARKED/NOT SUPPORTED/RETIRED) were applied
consistently. Zero outright math/physics errors found.

**Findings that need action:**

- **D1 — The 25° contamination (moderate, provenance-class).** Line ~2616:
  Codex cites Bonnefoy et al. — daughter-wave "maximum growth region near a
  25° crossing angle." Line ~4746: the same numeral resurfaces as "the
  25-degree angle was named before this analysis," presented as independent
  Dylan intuition for an unrelated closure-coordinate rotation. The record
  never flags the earlier appearance. The angle was later retired as
  non-special (§65–67), limiting damage — but this is exactly the
  contamination pattern the provenance rules exist to catch, and it slipped
  through in-session. ACTION: log in PROVENANCE_LEDGER excluded section;
  proposed canon line (Dylan sign-off): "any specific numeral the librarian
  has supplied earlier in a session is CONTAMINATED for provenance if it
  resurfaces as intuition, even across topics."
- **D2 — Near-tautological PIC correlation framed as structural positive
  (§56).** Same finding as AUDIT_EM_SUITE F1, reached independently by a
  second auditor: charge-conserving deposition enforces Gauss by
  construction; corr 0.997–0.999 is a solver consistency check. The honest
  Level-1 number is the particle-side participation comparison (0.799).
  Convergent finding across two audits — fix once in both docs.
- **D3 — Rapid-pivot cascade (soft).** MX1→MX3g: thirteen sequential
  sub-tests, each null immediately followed by an adjacent redesigned test
  that passes (MX3d 6/8, MX3e 8/8). Each step honest; the pattern edges
  toward "always another horse." Not a violation, but the sequence should be
  disclosed as one exploratory chain in any public write-up, with only
  FROZEN-then-transferred results quoted as evidence.

**Provenance candidates from the record (for the ledger, pending re-check):**
CLEAN HIT: Dylan's fractal daughter-wave prediction ("two waves in water meet
at a travelled angle... become smaller versions of each other") precedes the
Bonnefoy citation (§36, ~47%). CLEAN HIT: causal correction "daughters are
born after the parent collision," confirmed by MX3d temporal ordering
(+19/+31 slices). MISS: 25° as privileged angle — retired in-record.
EXCLUDED: 25° reappearance (D1).

## 3. FOLLOWUP_REGISTER (parked-tests planning file, 1,558 lines)

Overall: disciplined parking lot; P1 predeclares the full crowded-
neighborhood rival set; W1 carries five negative controls and correctly
states that success is not evidence of new law; H2 has dual synthetic gates
and doubles as H1's instrument gate.

**Rankings (subagent, endorsed):** best value W1 > H2 > C1. Weakest: B1
(usefulness condition, no kill condition — nearly untestable as written) and
A1 (soft falsifier — "needs a prediction beyond the standard model" without
naming the miss that kills it).

**Loopholes to close (all cheap):**
- **L1:** no hash/freeze on parked items — designs can drift silently between
  parking and Step-0 activation. FIX: hash the register now; any edit to a
  parked item creates a dated diff entry.
- **L2:** the no-tuning-after-seen-data rule exists only locally in H2. FIX:
  promote to a register-wide header rule ("no falsifier, coordinate, or
  rival-set change on any parked item informed by data seen after
  2026-07-12, except via a disclosed dated amendment").
- **L3:** H1 cites already-run BP-lift results as "existing evidence" while
  PARKED — its future Step-0 cannot be blind. FIX: H1's registration must
  declare non-blind status and cap its claim tier accordingly (confirmation
  ceiling: replication/extension, not discovery).

**Energy-estimate flags (for a chronically-ill solo researcher):** H1 and T1
look underestimated (multi-week builds); R1 is the deepest task in the
register and should read High, not Medium.

## 4. Cross-cutting

Two independent audits converged on the same single most-dangerous habit:
quoting construction-guaranteed agreements (identity-only reconstructions,
solver-enforced laws) at headline position. The canon already contains the
principle ("identities carry no evidence"); the EM/Codex work needs it
applied to SIMULATOR-ENFORCED identities explicitly. Everything else found
was either already fenced in-record or is a one-line fix.
