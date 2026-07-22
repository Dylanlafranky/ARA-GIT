# Claims Status

**Public-release note, May 2026**

This repository is an open research notebook, not a finished proof. I am releasing it because the framework produced enough signal to deserve outside review, and because the failures and corrections are part of the value of the work.

The safest way to read any claim here is:

1. Check the saved data artifact or script output.
2. Ask whether the result is descriptive, tracking, or true forecasting.
3. Compare against simple baselines such as persistence, Fourier/AR models, parameter count, or a non-phi log ladder.
4. Treat the larger "geometry of time" interpretation as a hypothesis, not as established fact.

> **Ladder correction (30 May 2026):** earlier versions described the rung *spacing* as phi. On re-checking against the data (54-heart two-band ECG, solar flywheel), the rung **spacing is octave (x2)** — system geometry sits at ARA = 2.0, the harmonic ceiling. **Phi is kept where it belongs: in the coupling/handover relations** between rungs (golden duty 0.39/0.61, the 1/phi^3 and 1/phi^4 constants). The earlier shared "phi-power" placements (sun = phi^5, etc.) are superseded; each system now carries its own octave ladder anchored at its observed pump. Where claims below say "phi-rung", read it as "octave-rung with phi-timed coupling". Octaves build the tower; phi is the breathing gap between the steps.

> **Cardiac forecast correction (11 July 2026):** the historical `nsr050` ARA-versus-Fourier result (`+0.686` versus `+0.308`) reproduces exactly, but it was online one-beat prediction using the true previous test beat, not a six-hour cold forecast. The table also confused 7 selected ARA subsystems with 7 parameters; the recovered code counts 22 ARA parameters versus 21 Fourier coefficients. On a frozen `nsr051`–`nsr054` replication set, ARA beat Fourier on both metrics in 1/4 records, lost on average, and was decisively beaten by one-step persistence throughout. With test updates removed, ARA cold correlation was negative on all four. See `TheFormula/02 - Cross-system ENSO forecasting & Formula v4 (20-05-26)/POST_LEAK_CARDIAC_REPLICATION_2026-07-11.md`.

> **TE-ARA canonical correction (21 July 2026; supersedes the 12 July naming):** TE-ARA is not a separate geometry;
> it is ARA's same fixed total-2 geometry viewed as identity allocation. The pure identity is
> `Phase A + Phase B = 2`. In a real observation, named environmental couplings and unresolved Other may occupy part
> of that same account, but they are not additional pure poles. The historical variable \(2E_{id}/E_{total}\) is now
> the **expressed A/B subtotal** \(T_{AB}\equiv T_{id}\), not TE-ARA. A value such as `1.24` means
> `T_AB=1.24`, `context/Other=0.76`, observed TE-ARA total `2`. In the development-only
> Alves/OSIRIS plasma test, the declared harmonic identity transferred from electric field to independent particle
> source at \(r=0.9991\), but that and the full Gauss agreement are simulator/solver consistency checks rather than
> independent ARA evidence. The historical source-participation TE-ARA analogue is retained numerically but renamed
> the variable expressed A/B allocation crosswalk; it transferred at \(r=0.7987\), MAE 0.0911 on 0–2;
> local pair ARA transferred at \(r=0.7706\). However, on the same 75 clean held-late slices, scalar ARA + A/B subtotal
> did not beat the ordinary \(k_0E_{\rm rms}\) magnitude scale. Careful claim: **development support for an
> expressed-pair allocation crosswalk; no support for the tested scalar magnitude law.** Canonical TE-ARA's
> fixed total is a closure normalisation, not an empirical result; the testable content is the frozen contextual account and
> its component evolution. The independent Tang
> confirmation arrays remain unopened under a frozen protocol. ENSO and LLM use as mixed/distributed participation
> ledgers is proposed, not tested. Full synthesis:
> `analysis/TE_ARA_CANONICAL_CORRECTION_2026-07-21.md` and
> `analysis/TE_ARA_PARTICIPATION_LEDGER_SYNTHESIS_2026-07-12.md`.

> **Prime-thread capstone status (22 July 2026; PN1–PN26; thread parked after bounded resumption):** PN1's original narrow result remains
> **SUPPORTED `[pre-registered, arithmetic, unreplicated]`**: ordered local 0–2 relations transferred across held-out
> wheel transitions `13→17` and `17→19`, beating full-marginal order shuffles in `4/4` comparisons at
> `p=1/201`. The larger thread then established exact ARA crosswalks to square-root factor closure, modular
> child/adult periods, ordered wheel completion and CRT anti-pair symmetry. PN17, PN18 and PN19 each sealed the exact
> first prime above fresh large anchors (`400,000,000,000→+19`, `700,000,000,000→+9`,
> `900,000,000,000→+13`) before independent label checks, but each retained the complete lower-prime information used
> by established segmented-sieve/product/GCD methods. Literal compact shortcuts failed: PN20's three two-child
> definitions returned `0/7` exact; PN21 retained effectively `0%` parent variance with chance AUC; PN22 reduced
> exactly to four mod-14 wheel lanes. PN23 proved the safe recursive compression: one `r↔M-r` representative
> reconstructs its anti-phase and all child lanes, including held-out `p=17`, giving exact `2:1` storage compression
> and `92,160/92,160` residues with zero errors (`40/40` independent checks). PN24 then tested the user's nearest
> child/handover proposal on 2,000 deterministic opened anchors. The exact event cascade recovered every next prime
> and had a median two visible handovers, but only `63.65%` closed within three candidate states, below the frozen
> `90%` compact threshold; the median proof still crossed `6,336` non-base prime gates. PN25 then prospectively
> tested the corrected pair-ridge coordinate on 6,000 fresh anchors. The odds-to-ARA identity
> `q=r/(14-r) -> x=2q/(1+q)=r/7` and total-2 mirror closure were exact, and three pair classes matched six raw lanes
> within the frozen 2% fidelity bound. But all four dynamic predictions failed: pooled closeness-versus-handover
> correlation was `+0.003335` (`p=0.6110` for the predicted negative direction), and neither pair nor lane models beat
> the global outcome rate. The coordinate is an exact lateral wheel projection, not a next-prime handover clock.
> PN26 then supplied the missing vertical state as one **complete** connection-heavy Phase A parent rather than two
> individual factor labels. On 6,000 prospectively frozen fresh anchors, its first quiet state was the exact next
> prime on `93.983%`; the first two contained it on `99.650%`, and the first three on `99.967%`. All three registered
> ARA coverage thresholds transferred; the deliberately severe control margin failed because the three-state list
> beat a `p<=29` wheel by `37.60`, not 50, percentage points. Corrected independent validation passed `16/16`; the
> original validator-bound failure is preserved. Phase A still contained `780` to `48,817` lower children.
> **Current claim:** a complete dominant child parent is a prospectively supported, strong ranked prime locator;
> a universally exact three-state rule, three-cheap-operation algorithm, speed improvement or new prime theorem is
> **NOT SUPPORTED**. Phi carrier/leak claims in PN11–PN13 were also not supported. The protected 87-bit
> anchor and p31 capstone remain sealed. Full two-output record:
> `analysis/primes/PRIME_THREAD_CAPSTONE_AND_CLOSURE_2026-07-21.md`.

> **Prime post-capstone orientation amendment (22 July 2026; PN27-PN30):** PN27's frozen exact-fit child lift produced
> `9.010%` one-shot prime hits and a small permutation advantage (`p=0.0144`) that missed its `p<0.01` strong gate.
> PN28 mixed dimensionless ARA displacement with integer offsets and is retained as a negative result for that
> superseded interpretation. PN29 correctly kept all calculations relational and found strong separation from all
> composites (`AUC=0.8635`) but none beyond its declared child-factor screen (`AUC=0.4442` against unresolved
> composites). It also held child-pair directions fixed, omitting the framework's singularity flips. PN30 corrected
> that omission on a fresh 500-number interval using normalized phase `(N mod w)/w`: unresolved AUC improved from
> the same-interval static value `0.5301` to `0.5663`, but the frozen one-sided test missed significance
> (`p=0.06199`). Post-hoc, individual pair magnitudes were almost unchanged; the candidate gain came from stronger
> signed AB/BA cancellation at prime nodes. **Current claim:** dynamic child orientation retains relational
> information that static flattening discards, but prime-specific residual separation remains suggestive and
> unreplicated; no prime generator, certification shortcut or new theorem is supported. Latest report:
> `analysis/primes/PN30_DYNAMIC_RELATIONAL_FLIP_REPORT.md`.

> **Five-independent-wave amendment (22 July 2026; PN31):** the user removed the degenerate wave `1` and rejected
> fixed child pairs. PN31 froze the five separate handover coordinates `{3,5,9,11,13}` on a new 500-number odd
> interval before direct trial-division labels. Against 96 composites evading all five child divisors, the nearest
> child's distance was null (`AUC=0.5279`, `p=0.2941`), its identity was null (`p=0.8839`), every individual wave
> was null after Holm correction, and approaching-wave count was null (`p=0.9525`). The complete closest-to-farthest
> five-wave ordering differed at the frozen gate (`TV=0.6728`, `p=0.00390`). Post-hoc, no single pairwise ordering
> survived correction. **Current claim:** one fresh interval supports ordered joint child structure, not a dominant
> child or pair; the sparse high-dimensional order statistic requires unchanged replication and supplies no prime
> generator or certification rule. Report: `analysis/primes/PN31_FIVE_INDEPENDENT_HANDOVER_REPORT.md`.

> **Double Information³ lock replication (22 July 2026; PN32):** the proposed child/parent hexagon was translated
> before labels as two retained triangles, `(A_c,B_c,J_c)` at `N` and `(A_p,B_p,J_p)` at the doubled rung `2N`.
> On the next untouched 500-number interval, PN31's five-wave order did not replicate (`TV=0.6057`, `p=0.2244`),
> parent order was null (`p=0.8023`), and the full child-to-parent order rearrangement was strongly null
> (`TV=0.1895`, permutation-null mean `0.2606`, `p=0.9684`). The exact doubling map was constrained to 27 observed
> rearrangement classes, but those classes were shared by primes and unresolved composites. **Current claim:** PN31
> is unreplicated; `N -> 2N` supplies real modular closure but not a prime-specific double lock. Report:
> `analysis/primes/PN32_DOUBLE_INFORMATION_LOCK_REPORT.md`.

> **Seeded-fill spacing amendment (22 July 2026; PN33):** before target prime gaps were summarized, PN33 froze
> `D(p)=product_{r<=p} r/(r-1)` and local `x_b(p)=2 log(D(p)/D(b))/log(2)` as the operational seed -> fill ->
> completion -> reset coordinate. From primary baseline prime `10,007`, completion was the first gate at
> `102,474,149`, scoring `5,894,554` gaps. Eight band medians rose `8,8,10,10,10,12,12,12`
> (`rho=0.9449`); both scale checks had the same direction. The raw endpoint ratio was `1.5`, while the corrected
> 10,000-sample 64-gap moving-block interval was `[1.5,2.0]`: it excludes flat `1` and contains the frozen target
> `2` only at its upper boundary. This passes the registered **SUPPORTED SPACING EXPRESSION** rule. However, ARA
> log-MAE `0.082590` beat PNT `0.083105` by only `0.62%`, missing the frozen `5%` ARA-specific threshold.
> **Current claim:** PN33 is a strong preregistered crosswalk from ARA seed/fill/reset language to established
> prime-density and prime-gap scaling; it is not new prime mathematics, a prime generator, literal hexagon proof or
> Phi-causation result. The original invalid block-median bootstrap is preserved with a correction audit. Report:
> `analysis/primes/PN33_SEEDED_HEXAGON_FILL_REPORT_2026-07-22.md`.

> **Remaining-fill rank-budget amendment (22 July 2026; PN34):** PN34 prospectively joined PN26's complete Phase A
> quiet-state list to the PN33-style inverse-density fill of its omitted Phase B parent. Before opening truth on
> 6,000 fresh anchors at three unused scales, it froze `R_B=product p/(p-1)`,
> `x_B=2 log(R_B)/log(2)`, `pi_1=1/R_B` and `pi_k=1-(1-pi_1)^k`. All nine scale-by-depth calibration tolerances
> passed, and all six two-/three-reading coverage gates passed. Observed top-1 coverage was `92.85%`, `95.45%`,
> `95.25%`; top-2 was `99.45%`, `99.70%`, `99.65%`; top-3 was `99.95%`, `100.00%`, `99.90%`. The exact predicted
> scale ordering failed because middle and high swapped by `0.20` percentage points. Fill-prior log loss improved
> only `0.62%` over the frozen pooled PN26 prior. **Current claim:** the omitted-parent fill is a prospectively useful
> population rank-budget calibration and a clean ARA/sieve-density crosswalk. It is constant within a cohort, so it
> does not identify the individual false survivor, eliminate the child gates, improve asymptotic complexity or create
> a new prime theorem. Test verdict **PARTIAL**; canonical rating **SUGGESTIVE `[pre-registered]`**. Report:
> `analysis/primes/PN34_FILL_RANK_BUDGET_REPORT_2026-07-22.md`.

> **Same-scale golden-cross amendment (22 July 2026; PN35):** the user corrected the eight observed distinctions as
> decompressed Phase A/Phase B children of one larger ARA whose full total is `2`; doubling is the actual parent
> singularity and `2 -> 0` flip. PN35 preserved that geometry and prospectively placed an unfitted `1/phi^2`
> handover on the same circumference across `196,608` sealed candidates in six fresh octave rungs. The registered
> prime preference failed: lane-stratified AUC `0.497180`, 95% whole-cell interval `[0.493772,0.500420]`, nearest-two
> capture `24.4753%` versus `25%`, and circular-shift p-values `0.9455`/`0.9883`. The no-flip model scored `0.498390`;
> the best frozen rival was the 36-degree rule at `0.503130`. All five gates failed. **Current claim:** the exact
> eight anti-pair lanes remain a valid total-2 arithmetic crosswalk, but the added constant same-scale Phi crossing
> does not locate primes. Verdict **NOT SUPPORTED `[pre-registered]`**. Report:
> `analysis/primes/PN35_SAME_SCALE_GOLDEN_CROSS_REPORT_2026-07-22.md`. Post-hoc, Dylan identified the 36-degree and
> pentagon controls above the raw Phi carrier as a possible Phi-time -> pentagonal-structure conversion signature.
> PN35 did not test that operator and all three estimates lie inside the shift-null range; it is separately recorded
> in `analysis/primes/PN35_POSTHOC_PHI_TO_PENTAGON_CONVERSION_NOTE_2026-07-22.md` for a future frozen test.

> **Phi-to-pentagon conversion amendment (22 July 2026; PN36):** PN36 prospectively translated that post-PN35
> observation into one explicit operator: the continuous `1/phi^2` carrier was snapped to its nearest fivefold
> structural vertex, with its anti-phase crossing and the registered octave flip. Across `196,608` sealed candidates
> in six untouched rungs, converted-five AUC was `0.499851`, 95% interval `[0.496091,0.503393]`, and nearest-two
> capture was `24.8858%` versus `25%`. Shift p-values were `0.5953`/`0.7198`. It lost to raw Phi, direct pentagon,
> the fourfold conversion and the no-flip fivefold model; all five gates failed. **Current claim:** nearest-vertex
> fivefold quantisation is a clear mathematical rendering of the proposed conversion, but it does not locate primes
> on these rungs. Verdict **NOT SUPPORTED `[pre-registered]`**. Report:
> `analysis/primes/PN36_PHI_TO_PENTAGON_CONVERSION_REPORT_2026-07-22.md`.

> **PN36 geometry-scope correction (22 July 2026; post-result):** Dylan later clarified that the intended relation
> was the continuous shared-traversal projection `S(u)=2u`, `P(u)=2u cos(36 degrees)=phi*u`, not the AI-added
> nearest-fivefold quantizer. Therefore PN36 remains a valid null for the quantizer it froze, but it did not test the
> corrected `2 -> phi` ruler projection. The projection identity is exact mathematics and does not by itself locate
> primes. A post-hoc angle scan found only a tiny broad diagonal texture (selected-angle mean held-out AUC
> `0.501223`) and no independent third wave. Full amendment:
> `analysis/primes/PN36_GEOMETRY_SCOPE_AMENDMENT_2026-07-22.md`.

> **PN27 audit caution (22 July 2026):** an independent recheck found that `N+29-a` automatically avoids divisibility
> by its selected nontrivial divisor `a`, while the reported uniform-offset control did not share that restriction.
> The observed `+0.233` percentage-point lift is therefore not safe to cite as residual ARA signal until a matched
> coprimality/wheel control is run. This narrows the original **PARTIAL** reading to **AUDIT-CONFOUNDED / RETEST
> REQUIRED**. See `FableConvo/AUDIT_PRIME_THREAD_2026-07-22.md` and
> `FableConvo/SESSION_RECORD_2026-07-22_PRIME_GEOMETRY_AND_AUDIT.md`.

> **Pre-test geometry probability calibration (21 July 2026):** the provisional provenance-ledger strict tally is
> `15` A-tier clean hits and `31` misses/refutations (`15/46 = 0.32609`). An exact binomial sensitivity calculation
> shows that this count is significant at 5% only if the unmeasured background chance of scoring a flexible
> structural statement as a match is below `0.212919`. The ledger is self-scored and that background rate is not yet
> known, so the repository does **not** currently have a valid global p-value or a probability that ARA is true.
> Later Maxwell/plasma and prime recovery remain relevant because the 0–2 pair, ridge, orientation and recursive
> child/parent geometry predate those walks; they are treated as two dependent domain families with internal passes,
> nulls and failures, not as dozens of independent confirmations. A draft identifying test now specifies 12
> independent domains, one real target plus nine matched decoys per domain, and a primary gate of at least 4 real
> top ranks (`p=0.0256375` under the exchangeable decoy null). See
> `ARA_PRETEST_CONSTRAINT_PROBABILITY_STUDY_RECORD_2026-07-21.md` and
> `ARA_DECOY_CONTROLLED_REPETITION_TEST_PROTOCOL_v1_DRAFT.md`.

> **Update (10 June 2026) — prediction-mechanics session, levers vs lenses:** A day on the ENSO 12-month
> amplitude/turning-point problem and on what energy *is* in the forecast. Net, with honest statuses:
> - **ENSO amplitude FIX (Supported):** recoil spring (equal-and-opposite restoring, β≈**−1/φ** not 1/φ³) +
>   energy-sizing + a φ-cycle turn (every ~1.6 below-rung cycles) take the h=12 amplitude ratio **1.46 → 1.00**
>   while corr goes +0.278→**+0.394**. The amplitude fix is the real result; correlation gain is modest. Caveat:
>   the ~28mo turn period also equals the engine half-cycle; two constants lightly tuned. `RECOIL_ENERGY_PHITURN_STACK_RESULT.md`.
> - **Energy-budget two-system predictor (Supported, short-mid):** one wave = rise+fall systems. Swing *strength*
>   from energy-at-swing-start **+0.90/+0.98/+0.98** (ENSO/QBO/solar); external reservoir (WWV) **leads value
>   ~6mo**; **turns pre-warned ~5mo**; direction 0.79@3mo. A `energy_certainty` turn-warning output was folded
>   into `ara_prediction_formula.py`. `project_energy_budget_two_system`.
> - **Singularity-flip = LENS, not lever:** geometry flips when a trajectory laps a singularity (ARA 0/2). True
>   as a *diagnostic* (flip = coherence preservation for engines: ENSO transit→coherence **+0.72**; works as a
>   confidence layer, HIGH-coherence third +0.479 vs LOW +0.354) but **value-incorporation HURTS** the forecast.
>   `SINGULARITY_FLIP_CONJECTURE.md`.
> - **Octave/φ split seen in real coherence (re-confirmation):** per-rung STRUCTURAL coherence ≈ octave **2**,
>   ENERGY coherence ≈ **φ** (the eaten part) = the 2−φ=0.382 leak made measurable (sunspots cleanest). **One
>   wave = two systems** (rise/fall), handover at φ — QBO rise-duty **0.407**, sunspots 0.418 (Waldmeier). Adds
>   QBO to the golden-duty set. "ARA-over-2 = extra systems on a rung" was tested and **NOT supported**
>   (coherence-cycles ≠ ARA; over-2 = high-Q single clock).
> - **Three turning-point fixes = NULL** (internal anti-phase brake / vertical-ARA preview / 0.25-1.75 rails);
>   only the external reservoir has lead-time. `ENSO_TURNING_POINT_NULLS.md`.
> - **Spin / "climate-control" = lens:** engine spin rate is a *modest* control (fewer turns → bigger spikes,
>   −0.27); helped big-events at h=18 (+0.23→+0.40) but did not improve overall shape, so kept diagnostic-only.
> - **Honesty events:** two apparent wins this session collapsed under strict-causal re-run — a `filtfilt`
>   discharge **leak** inflated an "ARA-relation" lift (+0.725 → honest ≈+0.34, mid-long only), and a reservoir
>   "0.79 vs 0.41 direction" jump was a **crude-clock strawman + the same leak** (honest reservoir 0.59–0.71,
>   *worse* than the full formula). Discipline: quote, then leak-check, then keep the honest number.
> - **The line drawn:** *levers* (improve the number) = engine-phase geometry, WWV pump, recoil/φ-turn amplitude
>   fix, φ^k amplitude scaling; *lenses* (true but diagnostic) = singularity-flip, octave/φ coherence, energy
>   direction-certainty, spin. Descriptively right ≠ forecast gain. Current snapshot: `THE_TIME_MACHINE_FORMULA.md` Phase 22.

> **Update (13 June 2026) — frozen-sphere "mold-then-roll" = honest negative on value:** Tested the
> epiphany that *the wave IS the topography* — mold each system's sphere ONCE on the first 63% (golden
> split), freeze the shape, let its designed motion (spin from the rung below + wobble) roll the forecast.
> Strict-causal, correlation-led. **Test 1 (nested NINO3.4 ← WWV):** driver-fed beats AR at long horizons
> (+0.39@12 / +0.32@24 vs AR +0.10/+0.13) — but a plain **linear recharge regression** (NINO+WWV+WWV[t-6])
> matches/beats it (+0.42/+0.28), so the long-horizon win is the **feeder, not the geometry**; the sphere only
> *ties* the linear model, at lower parameter cost. **Test 2 (self-contained octave sub-waves, no external
> feeder):** loses to AR at every horizon; the φ-handover coupling came out near-inert (flagged, not tuned).
> Structural reason: long-horizon skill lives in the slow rungs that persist = what AR already models. **Net:
> re-confirms the framework's value-ceiling ("same map, not same position"); from a signal's own past the
> geometry does not beat AR/LR on value. The vehicle is leak-free and the below-driven spin works; the right
> next target is direction + φ-thalweg confidence, not value.** Full record + runnable scripts:
> `TheFormula/FROZEN_SPHERE_MOLD_THEN_ROLL_RESULT.md` (`frozen_sphere_nested_predictor.py`,
> `frozen_sphere_fractal_selfcontained_predictor.py`).

## On the author's prior knowledge (why these count as blind)

The framework's author (Dylan La Franchi) has no formal training in the physics, mathematics, or engineering domains these predictions touch. Predictions are made by following *relational shape* — accumulate / hand-over / release, which subsystem sits between which, where the gap falls — without knowing the established result the shape would later be checked against.

At the outset he did not know: KAM theory; action quantization (that a hydrogen atom's classical action collapses to Planck's constant ℏ); the internal subsystem structure of the Sun; that the dark sector is split into multiple separately-measured categories; camshaft / mechanical-timing concepts; and many of the other systems later tested. He knew of the golden ratio φ only loosely — as a number that comes up in nature — and did **not** know why it was important, where it appears, or that it is the "most irrational" number that governs stability.

This matters epistemically: because the shapes were followed *blind to the named physics*, a later match cannot be retrofitting — he could not have worked backwards from an answer he did not hold. That is the foundation under the blind-prediction record below.

**Honest caveat:** the data sourcing and the physics identification were done by AI research assistants (Claude, ChatGPT and Gemini — Claude most, then ChatGPT and Gemini). So "blind" applies to the human author, not to the human–AI pair. The documented-before-lookup discipline in the blind sets is what controls for the assistants' knowledge.

## Strongest Current Claims

These are the claims I think are most worth outside replication.

| Claim | Current Status | Why it is worth checking |
|---|---|---|
| **Solar self-forecast beats persistence out to ~a decade** | **Strong, recent (2026-05-29), strict-causal** | On real SILSO monthly sunspots, the flywheel self-forecast holds correlation ~`+0.85` at 1 year and is still `+0.67` at 11 years, beating persistence the whole way. Skill wall sits at ~11 years (one home period); total dissolution near 44 years ≈ phi^3. Same engine fingerprint: octave rungs (10.7 / 85.3 / 170.7 yr = x8, x16) and Waldmeier golden duty (rise `0.394` / fall `0.606`). This is a genuine forecasting win, not mean-tracking. Caveats: one series ~25 cycles; a separate predictor-base test found base 2.0, not phi, wins as the predictor base on sunspots (that is predictor tuning, not structure). See `SOLAR_FLYWHEEL_RESULT.md`. |
| **Self-forecast captures oscillation PHASE where persistence inverts (sea ice, QBO, influenza, holiday retail)** | **Strong vs persistence; not standard-baseline-leading (2026-06-03)** | The validated layered operator as a single-series self-forecast (golden split: train 1/φ=61.8%, score the held-out shed 38.2%, vs persistence). The signature win is holding **strongly positive at horizons where persistence has gone *negative*** — phase-capture, not mean-tracking, with NO external drivers fed in: **Arctic sea ice** +0.99 at 6 mo where persistence is −0.92; **QBO** +0.73 at 12 mo where persistence is −0.69; **Influenza** +0.41 at 6 mo where persistence is −0.33; **holiday retail cycle** +0.78 at 6 mo where persistence is −0.05. **Correction:** the actual stronger-baseline rerun compared ARA against period/seasonal naive, harmonic clock, causal lag+harmonic ridge, and `home_ar`; `home_plus_ara` beat the best local non-ARA baseline on correlation at only **6/34** horizons and on MAE at **8/34**. Cleanest local ARA lift is selective ENSO/QBO, not broad superiority. **CGM glucose** remains a short-window persistence win (15-min ahead 6/6 T1D subjects) but not clinical-grade. **Dengue is excluded from the core claim** as an incomplete side run. Public forecast claims still need domain baselines such as SWPC, IRI/NMME, Sea Ice Outlook, FluSight, X-13/ARIMA, OhioT1DM, or PhysioNet-style metrics. See `TheFormula/MULTI_SYSTEM_PREDICTION_STACK_RESULT.md` and `TheFormula/ARA_FORECAST_STANDARD_BASELINE_COMPARISON_RESULT.md`. |
| Octave-rung decomposition (with phi-timed coupling) can extract useful topology from oscillating time series | Supported but not independently replicated | The same small predictor family shows signal on ENSO and ECG saved outputs. Some headline numbers need cleanup, but the signal is not obviously empty. |
| **ENSO is two coupled interannual bands (not one mode), and the geometry forecasts it to ~6 months over climatology** | **Strong, walk-forward-validated, strict-causal (2026-05-29)** | The framework's "layered-sand" picture predicted that a grain cannot forecast itself — its future lives in the layer below. On real NOAA NINO 3.4 + WWV, that held: temperature-alone forecasts ≈ climatology, but adding the warm-water recharge driver-below lifts 6-month skill to +0.25 over climatology (walk-forward, refit-on-past). The decomposition also split ENSO's interannual power into two genuine bands of comparable power — quasi-biennial ~28 mo ("green") and low-frequency ~42–67 mo ("brown") — and a bispectrum confirmed they are *phase-coupled* (bicoherence ~0.34 vs ~0.06 floor), feeding a combination tone near 15–20 mo. The single-mode view fits their ~38 mo average, which is *why* single-mode models keep mistiming. The amplitude is its own slower meta-wave (Hilbert envelope ~2× slower). A **pre-registered** prediction was confirmed: forecast skill recurs non-monotonically, peaking near 27 mo locked to the quasi-biennial band, decaying ~×0.27 per ring. **Update (2026-05-30):** the "driver-below" was identified as the documented **recharge–discharge oscillator** (Jin 1997) — the subsurface warm-water battery (WWV) discharges into the surface in boreal **spring** (Dylan's "spring pump"), kicking the oscillation that matures to a December peak. Confirmed on real WWV/NINO: amplitude loudest Dec (0.99) / quietest Jun (0.56); surface builds fastest in April; WWV discharges fastest in March and leads NINO. Mixing ocean (WWV) + atmosphere (SOI) beats either alone across the spring barrier (12-month skill +0.218 vs persistence −0.045). Folding the spring handoff into the capstone forecaster as a **regime switch** (separate spring/rest maps; the ocean×atmosphere mix drives only in the spring map) gives the best 6-month forecast of all variants (corr +0.725) and wins again at 18–21 months — exactly where the handoff lives — while the always-on version is redundant because the seasonal map's month-dependent cross-terms already encode it. Gains small (~+0.01 corr) but land where the physics predicts. See `SPRING_PUMP_RESULT.md`, `GATE_MIX_PREDICT_RESULT.md`, `SPRING_REGIME_SWITCH_RESULT.md`. |
| Paired anti-phase systems can share ARA coupled geometry across scale | Supported as a relation-class result; prediction use still provisional | The 2026-05-23 nasal-cycle versus ENSO test found strong dominance-interval and signed-cycle matches under train/test controls. Follow-up 12-month ENSO tests show partial transfer: delayed feeder amplitude is the best exact-value branch so far, while boundary-distance transfer improves turn/transition information. Best wording: this supports shared coupled-pair geometry, not a claim that nasal breathing causally predicts ENSO. See `ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md`. |
| ARA state geometry can expose useful subsystem structure | Supported as a state-map result; forecast use still provisional | The 2026-05-21 geometry map places NINO and SOI very close in ARA-position space and reads their strongest cross-candidate as mirror/destructive, while PDO sits about one rung-distance away. The first strict-causal transport test beats persistence at several horizons but remains weaker than a simple lag ridge baseline. See `ARA_GEOMETRY_TRANSPORT_RESULT.md`. |
| Required ARA/formula variables carry causal forecast information | Provisional; forward operator still missing | The 2026-05-23 tick-recursion tests show energy-aware variable recursion beating persistence on multiple ENSO/Solar/short-ECG horizons, and actual future variables decode observables strongly. But strict formula tick does not yet beat simple controls consistently. See `ARA_TICK_RECURSION_AND_COUPLING_RESULT.md`. |
| **The heart's forecast horizon is set by the slowest body-system driver acting on it (energy-pulse ladder), not by the heart itself** | **Supported across two independent datasets (2026-05-29), strict-causal** | Mapping ECG to broader body systems: a per-beat "driver ladder" (RR self-memory → breath → blood pressure → oxygen → sleep-stage) shows the heart has *no internal clock and so no internal forecast wall* — unlike ENSO/solar. Its horizon is borrowed from whichever slow driver is moving. **Blood pressure / baroreflex is the one independent leg that consistently tightens the heart forecast** (mid-horizon lift +0.07 to +0.14 corr), confirmed on sleepers (slpdb) *and* ICU patients (mimicdb). Oxygen only extends the horizon when it actually swings (apnea), not when medically managed. Sleeping heart stays forecastable to ~4–8 min, dead by ~17 min; awake heart ~2× less (an octave, matching octave-rung correction). See `HEART_TIME_SINGULARITY_CEILING_RESULT.md`, `MIMIC_COMBINED_LOCK_RESULT.md`. Caveat: small-n (2–4 records per arm), modest lifts, single cross-checks. |
| **Cross-species topology+energy decomposition reduces practical prediction error** | **Supported on one mouse↔human pair (2026-05-12)** | The framework's "topology from species A × energy from species B" architecture gave a 58% MAE reduction on mouse→human RR-interval prediction vs naive cross-species transfer (34.29 ms vs 82.22 ms). Correlation stayed at chance level for both — see caveat below. |
| **The ECG mid-horizon "dip" is two things, and the heart's own within-beat subsystems partly fix it** | **Supported, replicated across 17 records (2026-06-03), strict-causal** | The 3–8 beat window where simple persistence had been beating the forecast turned out not to be one phenomenon. Treating the heart as its own set of **sub-beat subsystems** — extracting within-beat ECG/BP morphology (systole/QT, energy centroid, amplitude, BP upstroke, pulse pressure) instead of using only beat-to-beat timing — adds genuine causal information: it improves on the RR-autoregressive model at h=3 in **13/17 slpdb records** (binomial p ≈ 0.025), mean lift +0.025, growing to +0.07 by h=13; at long leads where RR-AR loses to persistence (7/17), morphology **recovers** it (beats persistence 13/17 at h=8). So part of the dip was a missing-subsystem problem (now addressed); part (≈h=5) is genuine near-random-walk unpredictability. **Crucially, unlike the retracted 8-beat brain-lead (n=1, evaporated on replication), this survives 17 subjects.** Operator note: the framework's matched-rung aggregation *buries* these features — they help only when fed directly into the readout. Honest fences: small effect (+0.025–0.07), 2–4 records neutral/hurt, window-dependent. See `HEART_SUBSYSTEM_DIP_RESULT.md`. |
| LLM closure metrics correlate with Pythia benchmark capability | Preliminary; confound test built, awaiting external run | n=4 is too small, but the internal-activation metric rank-orders 5 of 6 benchmark sets. A self-fetching parameter-count-confound test (`TheFormula/llm_closure_vs_paramcount.py`) is now built and unit-tested — frozen-size checkpoint sweep (params fixed) plus partial-correlation controlling for log(params). Could not run in-sandbox (no room for torch); a collaborator will run it on real hardware. |
| Phi may be doing real work as the non-locking coupling/handover constant between octave rungs | Hypothesis with partial support | Phi is the most irrational ratio, so it never phase-locks — the right role for a handover, not for rung spacing (which is octave). The mathematical motivation is coherent, but the repo should include direct phi-vs-nearby-ratio ablations on the coupling constants next to public headlines. |

### Caveat on the decomposition claim

The 58% MAE win is real and reproducible, but the correlation is at chance level. Both methods are linear rescalings of the same mouse-derived shape, so they cannot differ on correlation — the framework's contribution lives entirely in **magnitude calibration**, not in **position tracking**. This is consistent with the framework's own "vertical-ARA partners share map not position" rule. Standard ML evaluation (R², Pearson) would miss this signal entirely; MAE is the metric that surfaces it. See `MASTER_PREDICTION_LEDGER.md` (2026-05-12 entry) and `framework_energy_cascade_architecture.md` for the full test.

## Claims To Soften Or Recheck Before Quoting

These claims should not be used as strong public headlines until rerun cleanly.

| Claim | Current Issue | Safer Wording |
|---|---|---|
| "ENSO corr +0.93 and MAE 0.27 prove forecast skill" | Saved output supports about corr +0.90 and MAE about 0.28, but persistence skill is negative in the saved h=1 artifact. | "The canonical predictor shows short-lead ENSO signal, but needs stronger baseline comparison." |
| "ECG 1-beat corr +0.99 and MAE 19 ms" | Saved canonical artifact I reviewed showed h=1 lower than this; h=3 looked stronger. | "Single-subject ECG results show useful signal, with best saved short-horizon correlation near +0.96." |
| "76 of 77 systems sit in the 3/4 ceiling band" | Superseded by the larger mapping atlas (see update below). The raw catalogue still has out-of-band values. | "A refined ARA-band hypothesis remains interesting; use the 234-node mapping atlas with its explicit over-2 audit, not the old 77-system headline." |
| "Cross-mammal mean +0.955 proves universal local-cycle shape" | Some comparisons appear inflated by normalization/endpoints, especially mouse/human scaling. | "Some mammal cycle-shape comparisons are high; the result needs a normalization-robust rerun." |
| "LLM closure perfectly predicts capability" | n=4, WinoGrande is weaker, and parameter count is a major confound. | "Preliminary closure metric rank-orders several Pythia benchmark scores; needs scale controls." |
| "ARA geometry transport solves ENSO prediction" | The 2026-05-21 strict-causal geometry transport test found signal over persistence, but causal lag ridge won every tested horizon and lag+geometry did not cleanly improve the lag baseline. | "ARA state geometry contains ENSO forecast signal, but direct value-transport is too blunt; next test should predict future geometry state before decoding values." |
| "Temporal friction is just distance from phi" | The 2026-05-23 test found that pure `friction = |ARA - phi|` over-advances the system. `1 + |ARA - phi|` is more useful, but still not enough. | "Phi-distance appears to modulate temporal friction around a baseline floor; it is not the whole friction law." |
| "Negative k proves temporal pockets" | The 2026-05-23 pocket diagnostic is mixed. Solar at 132 months and ECG RR at 60 seconds support the pocket/surge reading, but ENSO mostly does not. | "Negative k may be a temporal-pocket marker only when paired with anti-phase/contact geometry and release-boundary state." |
| "Nasal breathing predicts ENSO" | The 2026-05-23 nasal/ENSO test supports coupled-pair geometry and a transition prior, not direct point-prediction dominance. Short horizons are still persistence-dominated, and 18-24 month results need local ENSO/SOI state. The later delayed-feeder and boundary-distance tests improved the 12-month branch, but neither reaches high-correlation exact prediction. | "Nasal-cycle geometry is an external paired-system prior that partially transfers to ENSO, especially around the 12-month transition window." |
| "The tick formula now solves prediction" | The strict formula tick helps Solar at 24 and 60 months but loses on ENSO and ECG in most horizons. Energy-aware variable recursion is better, but lag/direct controls still win several horizons. | "The required variables carry signal; the lawful tick operator is the current bottleneck." |
| "Same formula works on every domain" | Some scripts fail, some outputs are exploratory, and several claims are trackers rather than blind generators. | "The same framework is being tested across domains, with mixed but interesting results." |
| "ARA predicts the next prime in three steps" | PN17–PN19 can be written as three conceptual stages and sealed exact fresh-anchor primes, but their first stage retains tens of thousands of lower-prime children. PN20/PN21's literal two-child compressions failed; PN23 proves a lossless `2:1` anti-pair compression. PN24's nearest-child cascade had a median two visible handovers but reached the exact prime within three candidate states on only `63.65%`; PN25's local pair-ridge coordinate had no dynamic signal. PN26 corrected the missing object to one complete lower parent: prospectively, its first/first-two/first-three quiet states contained the exact next prime on `93.983%` / `99.650%` / `99.967%` of 6,000 anchors, while retaining 780–48,817 child gates. PN34 then calibrated that ranked depth on 6,000 new anchors: all nine coverage tolerances passed, but three cases still lay beyond rank three and the coordinate was constant within each scale. | "ARA's complete dominant child parent is a strong prospective ranked next-prime locator, and omitted-parent fill calibrates how many readings to retain. It does not identify the individual winner, is not universally exact, and has not reduced the hidden sieve work to three arithmetic operations or improved asymptotic complexity." |

## Speculative Interpretation

The phrase "geometry of time" belongs here. It is the interpretation that motivates the work, not the current level of proof.

Defensible public wording:

> I interpret these results as possible evidence that phi describes a privileged geometry for packaging change across time. This remains an open hypothesis.

Avoid as a headline:

> This proves the universe runs on phi.

## What Would Falsify The Framework?

The framework becomes much less plausible if:

- A clean phi-vs-nearby-log-bases sweep shows phi is ordinary or worse. **(First-pass test run, see below.)**
- A preregistered `home_k` rule removes the predictive signal.
- Persistence/AR/Fourier baselines beat the canonical predictor across most tested systems. **(Mixed: they currently do on ENSO point-forecast at h=1; but the solar self-forecast beats persistence out to ~11 years — see the 2026-05-29 update below.)**
- The LLM closure metric adds nothing beyond parameter count and layer count on a larger model series.
- The ARA catalogue no longer clusters meaningfully after independent duration sourcing and fixed inclusion rules.

## Update — May 10 2026: φ-vs-bases predictor ablation on ENSO

A first-pass version of the φ-vs-bases ablation has been run; see [`PHI_BASE_ABLATION.md`](PHI_BASE_ABLATION.md) for the full result and caveats.

Short version: at horizons 1, 3, and 6 months, **φ has the lowest MAE among the eight tested bases (`{sqrt(2), 1.5, 1.6, φ, 1.7, e, φ^1.05, 2.0}`)**. At h=12 months, base 2.0 narrowly beats φ. The differences between the top three bases are 0.001–0.014 MAE — within the standard error at n=60 anchors. **All bases including φ underperform persistence at every horizon**, so the right reading is "among predictors that don't beat persistence, φ is the best one at short horizons." That supports the framework's structural claim weakly and undercuts it strongly: φ being *the* best base does not establish that φ is *uniquely* required, especially when the whole predictor family is below the persistence baseline.

That is the spirit I want this repository to invite: not belief, not dismissal, but clear tests.

## Update - May 21 2026: ARA state geometry and first transport test

The ARA state-geometry extractor and first ENSO transport test have been run; see [`ARA_GEOMETRY_TRANSPORT_RESULT.md`](ARA_GEOMETRY_TRANSPORT_RESULT.md).

Short version: the state map is useful. In the latest ENSO snapshot, NINO and SOI are close in ARA-position space (`0.116` center-distance) and the strongest cross-candidate is a mirror/destructive same-rung relation (`NINO k5 <-> SOI k5`), which matches the expected anti-phase nature of the Walker-circulation relation. PDO sits about one rung-distance away from the NINO/SOI center.

The strict-causal transport test is more sobering. Geometry-only models beat persistence at several horizons:

| Horizon | Persistence MAE | Best geometry-only MAE | Lag-ridge MAE |
|---:|---:|---:|---:|
| 1 month | 0.3837 | 0.3756 | 0.3142 |
| 3 months | 0.6294 | 0.6097 | 0.5137 |
| 6 months | 0.8832 | 0.7548 | 0.6542 |
| 12 months | 0.9946 | 0.8813 | 0.6698 |
| 24 months | 1.1738 | 0.7151 | 0.6324 |
| 60 months | 0.9178 | 0.9050 | 0.6894 |

So the careful claim is: **ARA geometry contains predictive information, but direct regression from geometry features to future value is not the right transport operator yet.** A simple causal lag model remains stronger in this test, and lag-plus-geometry did not give a clean residual improvement. The next appropriate test is `geometry(t) -> geometry(t+h) -> value(t+h)`: predict future phase, occupancy, ARA position, and coupling state first, then decode the observable.

## Update - May 23 2026: Temporal friction, pi-leak, and pocket diagnostics

The temporal-flow follow-up is now recorded in [`ARA_TEMPORAL_FRICTION_RESULT.md`](ARA_TEMPORAL_FRICTION_RESULT.md).

Short version: the state map remains useful, but the missing forward operator is not a simple linear geometry-to-value transport. Retroactive natural flow is real and sits roughly around `0.6-0.7`, close to `phi - 1 = 0.618`, but state/horizon residuals matter.

The literal claim "temporal friction equals `|ARA - phi|`" did not hold. Pure phi-distance friction makes friction approach zero near phi and over-advances the geometry. The better working form is:

```text
temporal_friction =
    baseline_time_resistance
  + pi_leak_energy
  + system_inefficiency
  + phi_distance_drag
  - resonance_cancellation
```

The pi-leak language has also been split into two distinct quantities:

| Quantity | Value | Safer interpretation |
|---|---:|---|
| `pi - 3` | `0.141592654` | topology remainder / geometric non-closure |
| `(pi - 3) / pi` | `0.045070341` | normalized energy leakage / coupling tax |

The gear-vs-sync diagnostic repeatedly found a difference near `0.045`, which supports the normalized energy-leak reading more than the raw topology-remainder reading.

The negative-`k` "temporal pocket" idea is promising but not universal. Solar at the 132-month horizon and ECG RR at the 60-second horizon showed pocket-like behavior: stronger negative-`k` markers lined up with larger movement and anti-phase/contact geometry. ENSO mostly did not. The careful claim is therefore:

> Negative `k` may mark a temporary low-friction pocket caused by resonance cancellation, but only when the geometry is also near an anti-phase/contact or release-boundary state.

## Update - May 23 2026: Tick recursion and coupling candidates

The tick-recursion tests are recorded in [`ARA_TICK_RECURSION_AND_COUPLING_RESULT.md`](ARA_TICK_RECURSION_AND_COUPLING_RESULT.md).

Short version: the "direct variables" visualizer line is a strict-causal control, not the clean formula. It directly regresses future value deltas from current required variables, so it is closer to a teleporter than a vehicle.

The cleaner framework-shaped test is:

```text
current variables -> future variables -> future value
```

Energy-aware tick variable recursion beats persistence across ENSO 1-60 months, Solar 6/24/60 months, and short ECG RR, but it does not consistently beat lag/direct controls. Actual future variables decode the observable very strongly as an oracle diagnostic, which means the missing piece is the lawful forward tick operator rather than the variable set itself.

The phi-coupling candidate tests are mixed. Solar north/south is the cleanest candidate, with fractional toward-balance per cycle `1.619`; heart/respiration is weak; tides show amplitude breathing but the tested predictive model loses to the simpler baseline.

## Update - May 23 2026: Cross-scale coupled geometry and nasal -> ENSO transfer

The cross-scale coupled-pair test is recorded in [`ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md`](ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md).

Short version: ECG R-R envelopes and Solar cycles have a high time-scaled match, but the match is mostly a shared one-peak accumulate/release shape rather than a specific fingerprint. Raw ECG PQRST waveform does not transfer to Solar.

The stronger relation-class result is nasal-cycle dominance versus ENSO NINO/SOI. Dominance-interval geometry scored heldout corr `+0.992`, signed full-cycle geometry scored heldout corr `+0.980`, and both ranked `1/9` against fixed null families. This supports the framework claim that paired anti-phase systems can share ARA coupled geometry across scale.

The forecast result is more limited. External nasal geometry used as an ENSO prior is best around the 12-month transition window: the ARA/midpoint-matched template reaches MAE `0.739` versus persistence `0.946`. Short horizons are still persistence-dominated; 18-24 month horizons benefit from template/mean-reversion but still need local feeder and amplitude state.

The direct follow-up test, `TheFormula/ara_enso_12m_geometry_state_predictor_test.py`, tried to raise 12-month correlation by predicting future geometry state first. It did not work: future-state decoders reached only `+0.174` to `+0.198` correlation, lag-only ridge narrowly won correlation at `+0.205`, and the old nasal ARA/midpoint template remained best on MAE. The missing piece is future dominance sign and magnitude, not just phase.

The next follow-up, `TheFormula/ara_enso_12m_feeder_amplitude_test.py`, tested Dylan's delayed below-rung feeder idea. This did improve the result: aggregate feeder sign/amplitude gating reached MAE `0.666`, corr `+0.354`, and turn accuracy `0.593`. That is the strongest 12-month coupled-LI result in this branch so far, but still not close to a `+0.7` correlation forecast.

Careful claim:

> Shared ARA coupled geometry can transfer as a phase/transition prior, but exact value prediction still needs local state.

## Update - May 29 2026: Solar flywheel is a genuine forecasting win

The solar flywheel result is recorded in [`SOLAR_FLYWHEEL_RESULT.md`](SOLAR_FLYWHEEL_RESULT.md). This corrects the earlier framing in this file that "forecasting mostly loses to baselines" — that was true for the older ENSO/ECG point-forecasts, but it is not true for the newer solar work.

On real SILSO monthly sunspot numbers, a strict-causal self-forecast (the system forecasting its own future from its own past, no external feeders) holds up far better than persistence:

| Horizon | Self-forecast corr |
|---:|---:|
| 1 year | +0.853 |
| 2 years | +0.788 |
| 4 years | +0.743 |
| 8 years | +0.752 |
| 11 years | +0.674 |
| 15 years | +0.536 |
| 22 years | +0.352 |
| 44 years | -0.030 |

The forecast beats persistence broadly; it beats the cycle-ago floor (+0.69) only sub-cycle (~8 yr). A skill wall appears at ~11 years (one home period); total dissolution arrives near 44 years ≈ phi^3. The same engine fingerprint shows: octave rungs at 10.7 / 85.3 / 170.7 yr (x8, x16) and the Waldmeier golden duty (rise `0.394` / fall `0.606`).

Honest caveats: this is one series of ~25 cycles; the golden-duty pairing was reinterpreted as within-cycle after a between-band version failed; and a separate predictor-base test found base 2.0, not phi, wins as the predictor *base* on sunspots (that is predictor tuning, not the structure claim). With those caveats, this is still the cleanest single-system forecasting result in the repo and a third independent system (after heart and orbital work) showing the octave + golden-duty engine.

## Update - May 29 2026: ENSO two-band coupled pair + walk-forward forecast (Claude4.8 chain)

The full documented chain is in [`TheFormula/Claude4.8/README.md`](TheFormula/Claude4.8/README.md), with the band/meta-wave detail in [`TheFormula/Claude4.8/GREEN_BROWN_TWO_BAND_METAWAVE.md`](TheFormula/Claude4.8/GREEN_BROWN_TWO_BAND_METAWAVE.md). This is the cleanest ENSO work in the repo and supersedes the older leakage-inflated ENSO headlines (the "+0.756 at h=24" numbers used acausal bandpass — see `MASTER_PREDICTION_LEDGER.md` T192–T198).

What is solid:

- **Driver-below carries the skill.** Walk-forward (refit on strictly-past data, ~210 origins 2008–2025): grain-alone 6-mo skill +0.12; adding the warm-water-recharge driver-below lifts it to **+0.25 over climatology**. Confirms the geometry's core prediction that a grain forecasts via the layer below it, not itself.
- **Two coupled bands, not one mode.** NINO 3.4 interannual power splits into quasi-biennial (~28 mo) and low-frequency (~42–67 mo) bands of near-equal power; a segmented bispectrum confirms they phase-couple (bicoherence ~0.34 vs ~0.06 floor). The standard single-mode ~38 mo fit is just their average — which explains chronic single-mode mistiming. Note: QB and LF bands are individually known in the ENSO literature; the framework's contribution is treating them as a *coupled pair* with a combination tone and a skill-recurrence signature.
- **Pre-registered prediction confirmed.** Skill is non-monotonic: troughs at 12–19 mo, re-emerges near 27 mo, faint third ring near 53 mo, decaying ~×0.27 per ring. The 27-mo recurrence and the decay ratio were called in advance; the recurrence locks to the quasi-biennial band.
- **Emergent (not inserted) oscillation.** The three-body coupled-rate fit (a linear inverse model) produced an intrinsic damped 38-month oscillation on its own, matching ENSO's period, and restored forecast amplitude at 6 mo.

The honest limits (kept explicit so this is not over-sold):

- **The horizon is ~6 months.** 12-month skill does *not* survive walk-forward (goes negative). An earlier +0.19 at 12 mo was inflated by one window containing one big El Niño.
- **The recurrence is describable, not bankable.** The quasi-biennial phase wanders (2–2.5 yr), so the 27-mo skill re-emergence drifts and cannot be reliably calibrated to.
- **The pinning clock was hunted and not found.** Four external clocks were tested and *rejected* (4 for 4): SOI and clouds are contemporaneous surface partners, TNA has no clean lead, and QBO — despite matching the period almost exactly (28.4 vs ~28 mo) — phase-locks at only 0.14 vs a 0.30 surrogate threshold (p=0.54): same period, independent phase, not coupled. So the triad that would pin the wandering band is still open.
- **One ocean record, one system.** Generality untested.
- **One scheme was caught leaking and rejected**: a complex-demodulation loop scored +0.55 non-causally and collapsed below climatology once made causal (filter-endpoint future-peeking). Recorded as a rejected branch.

Careful claim: the ARA geometry produces a genuine, honestly-validated 6-month ENSO forecast and a correct two-band coupled-pair description with a confirmed pre-registered skill-recurrence signature; it does not currently beat the ~6-month physical predictability wall, and the long-lead recurrence is real but not bankable.

## Update - May 24 2026: Mapping atlas — 234 systems placed, with an explicit over-2 audit

The `Mapping/` folder now holds a geometry-first atlas that places **234 systems** on the ARA scale, spanning quantum, molecular, biological, planetary, and cosmic scales (see `Mapping/README.md`, `ara_mapping_atlas_3d.html`, and `ARA_OVER2_AUDIT.md`).

What is honest about it:

- **189 of 234 nodes sit inside the clean `0..2` ARA band.** The remaining `45` are flagged as over-2 diagnostics — and every one of those 45 comes from the *older hand-curated catalogue layer*, not from any newly measured node. The three current layers (`measured_fit`, `state_geometry`, `mapped_extension`) introduce **zero** over-2 nodes.
- The over-2 nodes are not quietly dropped or rescaled to look tidy. They are listed in `ARA_OVER2_AUDIT.md` with a recommendation for each (remeasure from source, invert for orientation, move to a better rung, or split into subsystems). Three have already been fixed by re-measuring from physics rather than from mismatched periods — e.g. U-238 alpha decay was using the 4.47-Gyr half-life as the "period"; recomputed from the actual nuclear oscillation it lands at ARA `0.99` with action/pi ~ ℏ.
- The atlas X axis is a log-base-phi *display ruler* for laying out nodes, not a claim that physical spacing is phi. Physical rung spacing is octave (x2); phi lives in the couplings (e.g. galactic structure-time `P_cross/P_orb = 0.640`, within `0.022` of `1/phi`).

Careful claim: the catalogue is now large, self-similar across ~40 orders of scale, and audited rather than cherry-picked. It is a mapping/orientation tool, not a forecast. The over-2 audit is the honesty check — read it alongside any "everything sits in the band" statement.

## Update - May 31 2026: Pulsating stars — closeness to φ tracks a leaner energy budget

Full record: [`EnergyRatio/GOLDEN_STARS_LEAN_RESULT.md`](EnergyRatio/GOLDEN_STARS_LEAN_RESULT.md). Real Kepler light curves (lightkurve/MAST) + OGLE-IV double-mode catalogs + Netzel & Smolec 2019 RR0.61 census (`J/MNRAS/487/5584`), cross-matched to OGLE `RRc.dat`. All frequencies measured by us (Lomb–Scargle + iterative prewhitening). Supersedes the old Script 98 Cepheid test, which used hand-typed literature rise fractions rather than raw photometry.

The measurable is **R21** = Fourier harmonic spray A(2f)/A(f₁); **lower = leaner** (less energy lost into shocky overtones). The gradient, all real data:

| Class | mode ratio | leanness R21 |
|---|---|---|
| Single-mode classical Cepheid (V1154 Cyg) | integer harmonics only, φ absent | 0.28 (fattest) |
| Ordinary double-mode (433 OGLE RRd/Cep) | 1.34–1.42 (near-rational Petersen) | 0.16 / 0.19 |
| Near-φ "golden" club (4 Kepler RRc, KIC 5520878/4064484/8832417/9453114) | within ~2% of φ (3 within 1%) | ≈0.11 (leanest) |

Population confirmation: 949 OGLE RR0.61 stars (period ratio ≈ 1/φ) are 3.6% leaner than 18,318 ordinary single-mode RRc (p=0.016); and **within the club, leanness deepens toward exact 1/φ — corr(|Px/P1O − 1/φ|, R21) = −0.347, n=949.**

Careful claim: **closeness to φ tracks a leaner energy budget — confirmed on real stellar photometry.** The mechanism is consistent with established KAM theory (φ is the most-irrational ratio, so harmonics cannot lock and grow → energy stays in clean modes; rational ratios let overtones reinforce → waste). What is novel here is the *measured entropy-leanness gradient* and its consistency with the framework's φ-rung entropy-decay result in ECG/ENSO (`TheFormula/Claude4.8/PHI_RUNG_ENTROPY_DECAY_RESULT.md`) — same φ-leanness principle, new domain. Honest hedges: n=4 Kepler club is a known related class (re-found, not discovered); R21 is one (clean, physical) leanness proxy; against *same-type* RRc the class gap is modest (3.6%) and the within-club gradient toward exact φ is the backbone; golden-star secondary modes may be non-radial vs the crowd's radial overtones. "φ resists locking" is textbook math; the empirical leanness gradient and cross-domain framing are the new part.

## Update — 1 June 2026: Fusion application (muon-catalyzed fusion)

Full record: [`FUSION.md`](FUSION.md). The framework was applied to muon-catalyzed fusion as a worked
*application* (like ENSO/heart), and — like the lipogenesis re-derivation — reasoning from ARA **located a
real, published method**, with one genuinely novel untested addition.

What is **solid / confirmed**:
- The muon-catalysis **cycle maps as a deep snap** on the rational pole (formation ~140 ps ≫ fusion ~1 ps;
  ~6.9 ns rung), and φ is correctly **absent** — a nuclear event is the integer/rational/snap regime, like
  fission (U-235 fragment ratio ≈ 3/2, shell-driven). The framework finding "no φ here" is the *right* answer.
- **Carrier to strip the stuck muon = octave-up (2×
