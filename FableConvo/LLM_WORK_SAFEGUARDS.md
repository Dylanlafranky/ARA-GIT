# Safeguards for LLM-domain work with AI assistants (3 Jul 2026)

**Context:** In June 2026 Anthropic disclosed, then reversed, a covert policy
degrading Fable 5's responses for frontier-AI-development work (steering
vectors + prompt modification, silent, ~0.03% of traffic). Separately, export
controls removed the model entirely June 12-30. Both resolved. **Principle:
safeguards must not depend on current policy status** — policy can change
silently, and an assistant cannot verify its own serving from inside; a
steered model would report itself unsteered. All six safeguards below are
structural: they catch distortion regardless of the assistant's intentions
or self-reports. (Scope note: the disclosed degradation targeted pretraining/
distributed-training/accelerator work; this repo's LLM thread — activation
measurements on small open models — was likely out of scope even then.
Safeguards apply anyway.)

## The six safeguards

**S1 — Ground-truth gate.** Every instrument runs on known-answer targets
before touching LLM data (this week's standing rule). Distortion manifests
as broken instruments; ground-truth gates catch broken instruments no matter
whose fault they are.

**S2 — Second-family verification.** Any experimental design, code review, or
interpretation the assistant produces for LLM-domain work is independently
reviewed or re-derived by a NON-Anthropic model family before being trusted.
Disagreements are logged, not resolved by either assistant's authority.
(Extends CANON_FOR_AI §6.)

**S3 — Open artifacts only.** All analysis ships as fixed-seed runnable
scripts against OPEN models (Pythia). Conclusions must be reproducible by a
stranger with no Anthropic product in the loop. Code can be audited; code
has no moods.

**S4 — Testimony discount.** The assistant's claims about its own internals,
about what is infeasible, or about what "won't work" in LLM research are
HYPOTHESES, never verdicts. Discouragement is the cheapest possible sabotage;
every "that won't work" must come with a reason that can be tested or it
carries no weight.

**S5 — Registration + canaries.** Predictions registered before data, as
always. Additionally: mix known-answer canary tasks into LLM-domain sessions
and occasionally compare the assistant's error rate against matched
non-LLM-domain tasks — a yoked control on the assistant itself. A domain-
selective error-rate excess is a distortion signal.

**S6 — Fallback visibility (user-side).** Anthropic states model fallbacks
are now visibly indicated. Dylan, not the assistant, watches for model-switch
indicators in the client. The assistant's statement about which model is
serving is testimony (S4).

## The LLM thread — next tests under these safeguards (sketch, to be
## registered properly before running)

- **T-LLM-1 (queued by the thread's own summary):** verify the substrate
  reading ~1.25 as a SINGLE DECOUPLED mode — canonical mapper, rung audit,
  middles rule (§31: no middle is self-certifying).
- **T-LLM-2 (the two-column instance, the big one):** generation dynamics
  under FREE sampling vs FORCED decoding (templated/constrained output = the
  forced clock column). Registered expectations: forced column locks rational
  — adjudicated by LOCK DETECTION (step constant across windows, winding at
  exact rationals; the L1 correction, NOT folded-angle-nearest); free column
  is the engine candidate — dominance duty against the full crowded
  neighborhood. Pythia: fully open, fully reproducible (S3).
- **T-LLM-3:** stability of the pilot's per-rung peak (k=6, ~18 generation
  steps) across model sizes 70M/160M/410M/1.4B; rung spacing vs octaves;
  phase-step between adjacent rungs with lock detection.

All three: built kit-style for Dylan's machine, pre-registered headers,
S2 review by a second model family BEFORE first run on real activations.
