# Audit — LLM folder, docs and processes (3 Jul 2026, Fable 5 librarian)

**Scope:** all 16 .md + process review of the measurement pipeline. Conducted
under LLM_WORK_SAFEGUARDS.md (this audit itself is librarian testimony — S2
review by a second model family recommended before acting on it).
**Headline: the folder's 14 Jun self-correction pass was severe and honest
(the scratch banner, the nulls-logged list, the ridge rule are exemplary).
Six residual drift items remain, one of which is structural.**

## Drift findings

**D1 — Headline residue (worst offender: LLM_PHI_FORCED_CLOCK_RESULT.md).**
The doc carries a correction note that guts its basis, yet its TITLE still
asserts "LLM training is a FORCED CLOCK" and its verdict line still says
"Dylan's mechanism prediction lands." Future readers grab titles. Fix:
SUPERSEDED-style stamp in the title line itself, as the thread summary did
("⚠️ CORRECTED — substrate is engine-leaning, NOT clock").

**D2 — Post-hoc criterion change (LLM_TESTA_SUBSTRATE_CORES.md).** 86% of
nodes have a comparable 2nd rung (amp2/amp1 > 0.6) — that FAILS any
reasonable pre-registered single-mode gate. The doc reframes this as "the
fractal nature" AFTER seeing it, and its title asserts "not a ridge
artifact" while its own limitations section admits the whole-signal control
was wrong ("not leaned on"). The off-ridge medians (1.272, only 16% near
ridge, 0% anti-phase partners) genuinely survive decoupling — that part
stands. But "multi-mode = fractal, not contamination" is an unregistered
interpretation. T-LLM-1's mixture-robustness check (does dominant-rung duty
move when the 2nd rung is regressed out?) is the test that decides it.

**D3 — STRUCTURAL: the pinned boundary retrofit (2 Jul postdates this
folder).** Every substrate ARA number in the thread (~1.25 nodes, ~1.25
edges, 1.36-1.44 base wave) is rise/fall — a SHAPE measure. Under the
pinned motion/slice boundary these are classifier positions and CANNOT
speak to phi either way. Meanwhile the thread's actual motion-measures
(handover dominance duty) came back artifact-contaminated/null and were
never cleanly re-run. CONSEQUENCE: the thread's soft conclusion "phi does
not cleanly appear" is UNADJUDICATED, not negative — the phi-jurisdiction
measurement in LLM dynamics has effectively never been made. That is
exactly T-LLM-2.

**D4 — Epistemics drift (PHI_FORCED_CLOCK, kept for the record):** "phi is
the framework's measuring stick, not a hypothesis on trial here." That
sentence licenses assuming phi upstream and contradicts the repo's own
registration (phi IS on trial; the duty table is its trial). No result in
the folder leaned on it fatally, but the sentence should not survive into
any future doc.

**D5 — Undisclosed researcher degrees of freedom (moderate).** Closure
metrics use |r| > 0.85 with no threshold-sensitivity sweep; coupling-graph
results are one prompt/one seed (flagged in banners, good, but a 3-seed
1-hour re-run would retire the caveat); "intelligence index" naming already
banner-flagged.

**D6 — A reclassification opportunity, not an error: the telephone null.**
Iterated in-context copying is a FORCED task (templated, externally
clocked). Its result — perfect-maintain below a capacity wall, snap above,
never golden decay — is exactly the FORCED-COLUMN expectation under the
two-column claim (locks and snaps, no phi). The thread scored it as a
"sixth agreeing lens" for clock; under the pinned boundary it is a clean
forced-column ENTRY for the duty table. Reclassify — it strengthens the
contrast column the same way the Josephson star does.

## What stands (no action)

- The 14 Jun correction machinery itself; the ridge rule (now unified with
  session-notes §31: middles are never self-certifying).
- Curve-level results: fixed-compute breakthrough; universal size-normalized
  collapse (0.944).
- Scaling-law shed NULL (null model picks 1/e over 2-phi — crowded-
  neighborhood compliant, honestly logged, do not re-chase).
- Closure -> confabulation first cut: SUGGESTIVE, fences honest (rarity
  confound, muddy 70M labels, n=30); worth one clean repeat at 410M with
  matched-rarity controls before any weight goes on it.
- Base-wave re-measure principle ("measure the wave they averaged, never
  the fitted line") — correct and now protocol-level (never ARA a
  processed summary).
- Collapse-rebuild (one ~3-octave reorganization, integer-octave-ish
  transitions; capability staircase as readout phenomenon) — consistent
  with TWO_RULERS (spacing is octave; phi is not in spacing).

## Recommended repo edits (cheap, in order)

1. Stamp D1's title + verdict lines (5 min).
2. Add a 2-Jul-boundary retrofit note at the TOP of 00_LLM_THREAD_SUMMARY:
   all substrate ARAs are shape/classifier readings; phi-in-motion is OPEN
   pending T-LLM-2 (free vs forced decoding, lock detection per the L1
   correction, dominance duty vs full crowded neighborhood).
3. Reclassify the telephone null as a forced-column entry (D6).
4. Delete/stamp the D4 sentence.
5. Threshold sweep for closure metrics + 3-seed repeat (one Colab hour).
6. T-LLM-1 (embargoed script, built 3 Jul) decides D2's fractal-vs-mixture
   question; T-LLM-2 is the folder's first actual phi-jurisdiction
   measurement; T-LLM-3 checks the pilot's k=6 peak across sizes.

**Net:** previous coworker's drift was real but mostly self-caught on 14 Jun.
What remains is title residue, one post-hoc reframe awaiting its test, free
parameters needing sweeps — and the structural news that under the repo's
own 2-Jul boundary, the LLM thread's phi question is not answered but
UNASKED. The instruments to ask it properly now exist in the kit.

## Rerun results (3 Jul, in-session, on in-repo data)

**Edits 1-4: APPLIED** via `apply_llm_audit_edits.py` (tested on clone;
verified by grep). Title stamped, verdict struck, D4 sentence retracted,
boundary retrofit + telephone reclassification added atop the thread summary.

**Edit 5 (threshold sweep): RUN.** Closure ratio vs |r| threshold 0.70-0.95,
final checkpoints, clean-run npz:
- **Size ordering 70m < 160m < 410m preserved at EVERY threshold** — the
  monotonicity claim is threshold-robust. That part of D5 retires.
- **BUT absolute values do not replicate across captures:** this npz at
  r>0.85 gives closure ratios 0.0 / 1.0 / 3.1 vs the May capture's published
  15.5 / 84.0 / 169.9. Same metric, different generation setup, ~50x apart.
  VERDICT: closure ORDERINGS are meaningful within a run; closure MAGNITUDES
  (and anything derived from them, e.g. "intelligence index" values) are
  capture-specific and must never be compared across setups. Strengthens the
  existing banner caveat into a rule.

## Provenance update (3 Jul, from Dylan): WHOLE_RUN raw data is LOST

The whole-run capture ran in Google Colab; the runtime outlived the browser
window and only printed output survived — the npz was never downloaded. The
summary's collapse-rebuild finding (one collapse 256->1000, one rebuild
~8000) therefore rests on data that no longer exists: DOWNGRADED to
"reported; raw data lost; recapture required before any weight goes on it."
Fix shipped: `llm_whole_run_capture_resumable.py` — method-identical
recapture with per-checkpoint shards saved immediately to Google Drive,
resume-on-rerun, and a merge step. A dying window now loses at most one
checkpoint (~minutes), not the run. WORKFLOW RULE (generalize): any capture
longer than ~10 minutes must save incrementally to durable storage; "results
only in RAM until the end" is how data dies.
