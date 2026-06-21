# Closure → hallucination, causal within-model first cut (14 Jun 2026)

**Dylan La Franchi & Claude.** The causal within-model test the closure work flagged but never ran: does
lower closure / more looseness predict WHICH generations confabulate (not just which model size)?
Dylan's prediction: confab = looser / lower-closure (held loosely — "I've been surprised by LLMs").

## Setup
pythia-70m-deduped (sandbox; 160M throttled), greedy, 32 gen steps, n=30 per group.
- **ground**: answerable within-knowledge completions ("The capital of France is").
- **confab**: false-premise / fictional-entity prompts where ANY fluent answer is a hallucination
  ("The capital of Zorbland is", "The element Flubberium is used to"). Clean guaranteed-hallucination label.
Per generation: closure = `trace(A³)`/active node; loose_frac = nodes not in a closed triangle. Script
`halluc_closure.py`, data `halluc_results.json`.

## Result
| metric | GROUND median[IQR] | CONFAB median[IQR] |
|---|---|---|
| closure | 0.182 [0.141, 0.182] | **0.136** [0.127, 0.182] |
| loose_frac | 0.909 [0.909, 0.909] | 0.909 [0.909, 0.909] |

- **Closure SEPARATES in the predicted direction** — confab lower. Mann-Whitney **p=0.017**, **AUC 0.64**.
  Significant but MODEST (0.64, not a clean detector).
- **loose_frac does NOT separate** (both 0.909, saturated) — on 70M nearly every node is loose regardless;
  can't discriminate. That half is untestable on a model this tiny.

## Honest fences (first cut, not a clean result)
1. **70M hallucinates on everything** — "grounded" outputs are also garbage. Muddy labels (Dylan predicted).
   Closure still separating through that mud is mildly encouraging, but it's a weak model.
2. **Token-rarity confound:** confab prompts contain rare/fictional tokens (Flubberium, Vorbinghast); rare
   INPUT tokens could lower closure independent of hallucination. Part of the 0.64 could be vocabulary.
3. n=30, one model, greedy, single setting.

## Verdict
Closure↓ for confabulation: SUPPORTED, significant, modest (p=0.017, AUC 0.64). loose_frac: undecided
(saturated). A promising first signal, NOT yet clean. Connects to this session's "one-sided lossy flywheel"
(time-side flow, space-side never closing) = the unclosed/hallucination side.

## Next to make it real
- **Bigger model** (160M/410M): grounded prompts actually grounded; loose_frac no longer saturated.
- **Rarity-controlled prompts**: true-but-obscure facts vs false premises with MATCHED token rarity, so the
  contrast is hallucination, not vocabulary.
- **Per-token**: which exact tokens go low-closure mid-confabulation.

---

## Gemini behavioral shadow (closed model, can't see closure) — 14 Jun
Gemini's internals are inaccessible, so test the framework's BEHAVIORAL prediction: closed→consistent,
loose→indeterminate. gemini-2.5-flash, N=6 samples/question at temp 1.0, n=10 rarity-matched pairs.
Script `gemini_consistency_hallucination.py`.

| metric | GROUND mean | CONFAB mean | predicted |
|---|---|---|---|
| **self-consistency** | **0.65** | **0.33** | confab lower ✓ |
| uncertainty rate (detector) | 0.00 | 0.02 | confab higher — detector FAILED |

- **Self-consistency separates ~2× (0.65 vs 0.33), predicted direction.** Real questions → samples converge
  (Tolstoy, Ulaanbaatar, W); false-premise → samples diverge (can't pin a non-existent fact). = "loose
  structure allows indeterminacy." Metric is crude (first-sentence norm) so it DEFLATES grounded — true gap wider.
- **Uncertainty number is a measurement failure, not a null:** confab previews ("I'm…","It looks like…","There
  is no…","That's…") show Gemini WAS flagging the false premises; the 60-token truncation + narrow marker list
  missed the completed hedges. Re-run without truncation + broader markers would capture it.

## Cross-model synthesis (the satisfying part)
The SAME "unclosed structure" shows up two ways depending on the model's closure:
- **Pythia-70M (low closure):** confabulates confidently, with low INTERNAL closure (trace(A³), p=0.017).
- **Gemini-2.5 (high closure):** does NOT confidently confabulate — the unclosed fact surfaces as **low
  self-consistency + hedging** (behavioral).
This matches the prior φ-deep×φ-wide prediction exactly: *"out-of-knowledge questions surface as honest
uncertainty rather than confident fiction."* Internal closure (weak model) and behavioral consistency (strong
model) are the **same signal from inside vs outside.** Fences: n=10, crude consistency metric, broken uncertainty
detector. Bigger-Pythia rarity-matched run (`colab_closure_hallucination.py`) still pending for the internal side.

### Second Gemini run (gemini-3.5-flash) — signal shifts channels
| metric | GROUND | CONFAB | (2.5-flash run) |
|---|---|---|---|
| self-consistency | 0.53 | 0.42 | (0.65 / 0.33) |
| uncertainty rate | 0.00 | **0.20** | (0.00 / 0.02) |

- This run the **uncertainty channel fired** (confab 0.20 vs ground 0.00) while the consistency gap shrank.
  Several confab prompts now get **consistent honest refusals** ("There is no country called Zorbland",
  flubberium: consistency 0.83 AND uncertainty 0.83) — which RAISES confab consistency while flagging uncertainty.
- **Uncertainty = precise flag:** fired on 0/10 ground, 4/10 confab → when the model says "There is no X" it's
  always a false premise (100% precision, ~40% recall).
- **Channels trade off:** catch-and-refuse → high consistency + high uncertainty; wobble → low consistency +
  low uncertainty. Either way ≠ grounded (always high-consistency + zero-uncertainty). The shift toward
  consistent honest "there is no" = the closure→uncertainty trajectory (more closure → uncertainty not fiction).
- **Robust claim (both runs):** grounded = consistent AND certain; confabulation leaks via consistency,
  uncertainty, or both. **NOT robust:** the specific channel split (n=10, temp-1 variance, one run/model —
  could be model difference or noise; "gemini-3.5-flash" internals unknown).

---

## ⚠️ Bigger-model rarity-matched run — INTERNAL CLOSURE FAILS (scratches the detector claim, 14 Jun)
Ran `colab_closure_hallucination.py` on 160M/410M/1B/2.8B, rarity-matched prompts (the confound control).

| model | closure: confab vs ground | closure AUC | loose AUC |
|---|---|---|---|
| 160M | confab HIGHER (1.70 vs 1.41) — wrong dir | 0.39 | 0.60 |
| 410M | confab HIGHER (151 vs 11) — wrong dir | 0.37 | 0.33 |
| 1B | confab HIGHER (1.94 vs 1.40) — wrong dir | 0.48 | 0.56 |
| 2.8B | confab LOWER (30 vs 201) — RIGHT | **0.82** (p<0.001) | 0.64 |

**~~Internal closure → hallucination as a robust detector~~ — SCRATCHED. NOT supported.** 3 of 4 sizes point the
WRONG way (confab has HIGHER closure). Only 2.8B shows the predicted direction.
- **Mechanism for the failure:** small/mid models confabulate by **repeating the made-up token** (echoing),
  which RAISES coupling/closure. So confabulation reads as HIGH closure — opposite to "loose indeterminacy."
  The `trace(A³)` closure metric **conflates grounded structure with repetitive echoing**; small-model
  hallucination is full of echoing.
- **The earlier 70M positive (p=0.017, AUC 0.64) does NOT generalise** — likely the rarity confound (removed by
  matched prompts) + this repetition artifact aligning by chance. Do not cite it as evidence.
- **The lone 2.8B win is intriguing but unclaimable** (one point vs three contradicting sizes). Charitable
  hypothesis — at scale, confabulation stops being repetitive-echo and goes genuinely loose — is TESTABLE
  (does 6.9B/12B flip right too?), not yet a result.

## Net (honest)
- **Internal `trace(A³)` closure metric: NOT a reliable hallucination instrument** (repetition pollutes it; fails
  3/4 sizes rarity-controlled). Logged as a NEGATIVE.
- **Behavioral signal (Gemini consistency/uncertainty): HOLDS** across runs. The phenomenon (false premise →
  indeterminacy/honest-uncertainty) is real; the internal closure metric just doesn't track it robustly.
- Open: does the 2.8B right-direction flip continue at 6.9B/12B (loose emerges past repetitive-echo)?

---

## NEXT TEST (Dylan, 14 Jun) — KEYSTONE looseness, not aggregate looseness
The aggregate test failed partly because **total loose count is the wrong quantity.** Dylan's refined hypothesis:

> **Hallucination spikes when a KEYSTONE — a foundational, load-bearing piece of information — is a loose thread.**
> NOT "more loose threads = more hallucination," and NOT the threads near the *end* of the response. It's whether
> the *foundation* is loose. A loose peripheral/late thread is harmless; a loose **keystone** makes everything
> built on it ungrounded (arch with a loose keystone → collapses; loose edge stone → fine).

**What to measure (vs the failed aggregate version):**
- Don't count total loose_fraction. Instead **identify the keystone / foundational nodes** and ask whether
  *those specifically* are loose (not closed into the structure), then see if keystone-looseness predicts
  hallucination.
- Candidate definitions of "keystone / foundation" (test which one carries it):
  1. **Centrality** — the highest-degree / hub nodes that the rest of the graph depends on.
  2. **Foundation = early/base** — early-layer or base-rung nodes (the foundation of the computation), and/or
     the early-generation tokens (the subject/premise the later answer is built on) — explicitly NOT the
     late/peripheral ones.
- **Test:** keystone-loose → hallucination, **controlling for total loose count** (which, per the failed run,
  should NOT predict). Ideally per-response: when the load-bearing fact node is loose, the answer confabulates.
- **Must still control the repetition confound** (define keystone by role/centrality, not raw coupling, since
  repetition inflates coupling).

**Status:** proposed, not run. This is the position/role-weighted successor to the (negative) aggregate-closure
test. The aggregate metric is dead; this is the live direction for the internal side.
