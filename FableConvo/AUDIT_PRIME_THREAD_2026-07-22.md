# Audit — prime thread PN1–PN36, focus 20–22 Jul work

## PART 2 (added same date, after the PN24–PN36 push of 22 Jul 23:27)

### PN35 / PN36 — internals independently verified

Recomputed from the shipped PN35/PN36 REPORT_SOURCE.sqlite artifacts:
- Headline numbers match the reports exactly (PN35 golden AUC 0.497180,
  capture 24.475%; PN36 converted AUC 0.499851, all five gates FAIL in both).
- **Physics-grade sanity check passes:** per-rung prime rates match
  PNT-on-wheel theory (k=26 observed 0.2027 vs 30/8 × 1/ln N ≈ 0.201, and
  the correct 1/ln decline across rungs). The instrument is measuring what it
  claims to measure.
- **The nulls are deep, not marginal:** PN35's distance-to-crossing octiles
  are flat (0.1508–0.1563 with n=24,576 each) — no gradient toward the
  registered crossings at any resolution. PN36's boundary Spearman per rung
  oscillates around zero (−0.023..+0.017).
- Full rival tables confirmed: nothing beats chance; PN35's best rival is
  "shear 36deg" at 0.5031 (~1σ, noise); in PN36 the registered flip actively
  HURT (difference CI [−0.0074, −0.0006]) — an informative negative for the
  flip operator on this domain.
- Hash chains present (freeze manifest → primary receipt → predictions →
  scored → results). REPRODUCIBILITY FLAG: validate_pn35/36 scripts require
  PN*_PREDICTIONS.csv, which is NOT committed — the validator cannot run
  from a fresh clone. Commit the CSVs or add a regeneration path; otherwise
  the recorded VALIDATION.json is the only witness.

**23 Jul resolution:** the CSVs are intentionally untracked because the four PN35/PN36 products total about
485 MB. `analysis/primes/reproduce_pn35_pn36_csvs.py` now reconstructs the label-free and scored CSVs through the
original frozen builders and validators, checks the exact recorded hashes, and leaves the compact receipts as the
Git-tracked anchors. See `analysis/primes/PN35_PN36_CSV_REPRODUCTION.md`. This closes the fresh-clone pathway gap;
it does not change either scientific verdict.

### PN27 — the arc's one live positive is likely mechanical (main finding)

The rule P̂ = N + 29 − a (a = largest of {1,3,5,9,11,13} dividing N) claims
+0.233pp over uniform offsets, permutation p = 0.0144, graded "partial
predictive support." AUDIT FINDING: because 29 is prime, the chosen candidate
is NEVER divisible by its own a (N ≡ 0 mod a ⟹ candidate ≡ 29 mod a ≠ 0).
The rule therefore carries a built-in small-prime-avoidance guarantee that
the uniform control lacks. Magnitude check (this audit, MC at the middle
scale): conditioning uniform-offset candidates on the same avoidance class
lifts the hit rate 8.08% → 9.48% — the coprimality channel is worth ~1.4pp,
roughly 6× the claimed lift. The permutation control's p = 0.0144 is exactly
what breaking the N-divisibility↔offset correlation would show, and that
correlation IS the bookkeeping.

RECOMMENDATION: before PN27 is cited anywhere, run the wheel-corrected null —
expected hit probability computed in closed form per (N mod 3·5·11·13,
offset) cell (Hardy–Littlewood small-prime correction). Prediction of this
audit: the corrected null absorbs the entire lift and PN27 regrades from
"partial predictive support" to "exact bookkeeping crosswalk" (the
real-but-not-mysterious class, same as PN19's 93.2%). If any residue
survives the corrected null, THAT would be genuinely interesting — which is
why the test is worth running either way.

### PN24–PN34 — verdict-label check

Statuses are honestly graded throughout (PARTIAL/NULL/geometric-only;
PN28 correctly voids itself as testing a superseded interpretation; PN33
carries the dual verdict "SUPPORTED SPACING EXPRESSION / NO DISTINCT
ADVANTAGE OVER PNT"; PN34's full support blocked by a 0.20pp cohort swap on
a deliberately strict frozen endpoint — correctly not rescued).

### Axis-map note

PN35 + PN36 add two sealed, at-power φ-nulls in the maximally space/rational
domain — the strongest-instrumented conforming outcomes yet for the domain
map's negative half (with PN11/12/13: five prime-domain φ-nulls total).
Queue for RETROSPECTIVE_125_DOMAIN_SORT.

---

## PART 1 (original audit of the same date, PN1–PN23)

**Auditor:** Claude/Fable 5, 22 Jul 2026, with one Sonnet subagent full-read
pass over PN14/17/19/20/21/23 reports+protocols, the resonance-locks doc, and
the closure validator. Rule 4 applies; S2 re-derivation advised before public
citation. Capstone arithmetic independently machine-verified (sympy, this
date).

## Verdict in one line

The prime thread is the most disciplined arc in the repository: 23 tests, a
sealed-prediction protocol that held, an honest terminal null on its own
headline hope, exact crosswalks retained at the correct tier, and a
self-imposed parking order with precise resume conditions — no overselling
found anywhere in the audited reports.

## Machine-verified (this audit)

- PN17/18/19 sealed anchors: 400,000,000,019 / 700,000,000,009 /
  900,000,000,013 are all prime AND are the FIRST primes after their declared
  bases — the sealed offsets (+19, +9, +13) are exactly right.
- Capstone probe factorizations correct: 169,765 = 5·19·1787;
  339,529 = 163·2083; 194,017 prime (and the capstone correctly notes 2n+1
  carries no prime-specific enrichment).
- PN23's 92,160 child residues = φ(510510) exactly (primorial through 17);
  the 2:1 compression maps to 46,080 stored lanes.

## Subagent findings (full reads)

1. **Seal integrity: SOUND.** PN17/19 protocols declare the anchor and "no
   target candidate has been calculated" at freeze; procedure was
   freeze→hash→run builder without primality calls→hash prediction→validate.
   No evidence of anchor selection after peeking.
2. **No overselling — the reports police themselves in-body:** PN17: "the
   standard segmented sieve written as a complete ARA child-phase field...
   does not yet improve established prime-search complexity." PN23: "It is
   also established modular arithmetic... validates the implementation and
   the ARA interpretation, not a previously unknown prime theorem." PN14
   self-flags its r=0.999910 as the known autocorrelation of centered
   sawtooths — "should not be advertised as a new number-theory waveform."
   PN19's 93.2% is headed EXPLORATORY, written after the sealed result, and
   attributed honestly: "real but not mysterious" (Phase A is a near-complete
   partial sieve; weak 28% wheel baseline noted).
3. **Nulls are clean:** PN20 (0/7), PN21 (zero retained variance, chance
   AUC) — both explicitly DEVELOPMENT NULL, protected anchors unopened.
4. **Resonance-locks doc is MORE conservative than the capstone** — tier
   "POST-HOC / NOT A PRIME-PREDICTION RESULT," disclaims its own musical
   labels and the 510≈512 coincidence explicitly.
5. **No contradictions** between individual verdicts and the capstone
   lineage table.

## Flags (all minor)

- **F1:** `validate_prime_thread_closure_docs.py` is a documentation-
  consistency checker (files exist, fence strings present, ledger entries
  unique, forbidden-overreach phrases absent) — useful hygiene, but it must
  never be cited as mathematical re-validation. One line in its header would
  prevent that misread.
- **F2:** PN19's quoted 28% baseline is weak; any public quote of 93.2%
  should carry the report's own "near-complete partial sieve" attribution in
  the same sentence, or better, quote the pair (93.2% vs what a matched
  partial-sieve control scores) if ever revisited.
- **F3:** The forbidden-phrase check in the validator is a nice innovation —
  consider generalizing it repo-wide (a lint that greps public-facing docs
  for known overreach phrasings from the corrections table).

## What the thread actually bought (endorsed reading)

- The capstone's closing statement is exactly right and quotable: exact
  prime-sieve geometry in three information stages, but "the repository does
  not currently contain a three-cheap-operation next-prime algorithm or a
  new prime theorem."
- The missing-object formulation — a bounded-size recursively computable
  sufficient statistic Z(N) preserving first-quiet location — is a
  WELL-POSED open problem statement, and the thread correctly discovered the
  wall's shape (PN20/21 reject the two cheap candidates) rather than
  claiming to breach it. This is "look for the cracks, and certify the wall
  when it holds" executed at scale — the lotto discipline, in number theory.
- "Completion and prediction are different" (capstone carry-item 3) is the
  classifier/generator distinction appearing in pure mathematics — worth
  cross-referencing to the minimal statement.
- Grain-relative ridge now EXACT in one domain (children (0,2)/(2,0)/(1,1)
  coarse-graining to the same parent ridge) — the first fully rigorous
  instance of a middles-rule phenomenon; worth a pointer from CANON §1's
  ridge definitions.

## Bottom line

Park stands, exactly as written. The thread ends with the framework's
strongest credential pattern: it went hunting for a shortcut through one of
mathematics' hardest walls, instrumented the hunt properly, caught its own
near-misses, and wrote "wall certified, here is its precise shape" instead
of a discovery claim. Quote the capstone verbatim in any public account —
it cannot be improved on for honesty.
