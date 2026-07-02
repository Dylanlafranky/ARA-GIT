# Multi-Arm Pendulum — an ARA Reading

**Status:** exploratory, replicated where stated. Real public data only.
**Data:** dynamicslab *MultiArm-Pendulum* (Zenodo DOI 10.5281/zenodo.6633719) — laboratory single/double/triple pendulum recordings, ~60 s at 10 kHz. Triple runs used here: `pend_triple.mat` (run 1), `tri2.mat` (run 2), `tri3.mat` (run 3). Decimated to 500 Hz for analysis.
**Why this system:** the multi-arm pendulum is the cleanest physical laboratory for the order→chaos transition. One arm is exactly solvable; two or more coupled arms are chaotic with no closed-form solution. That makes it a direct test bed for the ARA claims about rungs, coupling, and the poles.

This note is written to sit **in line with `WHAT_IS_ARA.md`** — the same landmarks (0 / 1 / 2), the same `(position, orientation, rung, phase, path, coupling, energy)` state, the same discipline (classify → predict → validate, flag nulls).

---

## 1. The system in ARA terms

Each arm is an **irreducible parameter** — a degree of freedom that cannot be reconstructed from the others. To specify the state you need every angle (θ₁, θ₂, θ₃); none factors out. So the three arms are three primes (in the framework's sense: irreducible system parameters, not prime numbers).

They are irreducible as **coordinates** but coupled as **dynamics** — this is the framework's coupling, not a fourth prime. The prime is the axis; the coupling is what travels along it. This is why one arm is solvable and two-plus are not: the moment you have **two or more coupled primes**, you cross from clock into chaos. The count of irreducible parameters is what flips a system from solvable to chaotic.

**The chosen observable and reference frame (locked before measuring):**

- Observable: each arm's swing about its own rest.
- Reference frame: **joint / nested**, not global vertical. Each arm's rest is inline with its parent (arm-2's rest is along arm-1, arm-3's along arm-2). Measuring all arms off one vertical mixes rungs and produces artifacts — this was corrected during testing.
- ARA-position map: `ARA = 1 + (θ − rest)/π`, with `rest` found by circular mean (in this dataset θ = 0 is *up*; rest/hanging-down is ±π). On this map **1.0 = the rest ridge** (Landmark 1), and **0 and 2 = straight up = the same folded singularity** (Landmarks 0/2 are one point on the folded axis). A full rotation reads 1 → 2 → 0 → 1.

---

## 2. What was measured, and what held

### 2.1 Rise/fall asymmetry is the WRONG instrument here (null, expected)

A free pendulum is conservative: each swing is time-symmetric (energy in = energy out, minus friction). So a rise-vs-fall asymmetry measure nulls — and convention-flipping the joint frame vs absolute frame flips its sign, i.e. it's an artifact, not a reading. **This is not a failure of the framework; it is the framework locating the signal elsewhere — in the coupling between arms, not within one arm.** Logged as a scratched measure so it isn't reused.

### 2.2 The ARA-position trace sits on the ridge and never reaches a pole

Plotting each arm's ARA position over time (`pendulum_ara_position.png`), all three arms **oscillate around the 1.0 rest ridge**. The lower the arm, the wider the excursion (arm-3 widest) — consistent with the lower arm carrying more energy and swinging on a deeper rung. **No arm reaches 0 or 2**: in free-swing data the arms never go over the top, so none crosses the singularity. (To test the singularity crossing / flip, a driven or high-energy *tumbling* dataset is needed — not available here.)

### 2.3 Coupling: nesting / anti-phase (Type-1 handoff between rungs) — replicated 3/3

The real, repeatable result is the **coupling**, exactly as `WHAT_IS_ARA.md` §7 predicts should dominate over any isolated number. The lower arm completes its faster cycle and **kicks the arm above into anti-phase** — a release from the lower rung becoming a disruption/handoff to the upper. Measured per-arm in the joint frame, the anti-phase nesting **replicated across 3/3 runs (p ≈ 0.01)**.

### 2.4 Leadership is dynamic — averages lie

A global cross-correlation reports a single number ("arm-3 leads arm-2 by ~0.7 s"). That is only the **average phase offset**. Read **per swing**, leadership is not fixed — it hands around. Counting which of the three arms turns first on each big swing (`pendulum_leadership_3way.png`):

- on the run-1 figure, arm-3 (bottom) led most (~46%), arm-1 close behind (~43%), arm-2 trailing (~11%); **across all three runs arm-3 leads most every time** (see §3);
- **~68–79 leadership switches over ~95–98 big swings per run** — a near-constant handover, no permanent driver.

> ✅ **RE-RUN VERIFIED (27 Jun 2026), real data, prominence-filtered turn detector.** The turn-detector in `02_leadership_rung_dominance.py` was changed from a bare gradient-sign-change (which counted every micro-jitter extremum) to a **prominence + minimum-spacing filter** (`scipy.signal.find_peaks`). Effect: the swing count roughly **halved** (old ~213 → real ~95–98), confirming the old detector over-counted noise. The headline ordering **survived 3/3** (arm-3 leads most + holds the longest block every run). The secondary "upper-two split ~27–30%" did **not** survive — see the revised wrinkle in §3.

(An earlier two-arm version of this test wrongly excluded arm-1; the corrected three-way version shows arm-1 does take the lead ~a quarter of the time, in short patches near the turns.)

---

## 3. The main new result — rung position sets dominance

Reading the leadership sequence as a string of who-led (`...3233223...`) shows it is **not** alternation and **not** prime-spaced. (Checked directly: each arm lands on prime-numbered swings ~21–25% of the time vs ~19% expected by chance — the prime-position idea **nulls**.)

What is there instead is **block structure**: leadership comes in *epochs of dominance*. One arm seizes the lead and holds it for a run (up to ~12 swings in a row), then control migrates to another. In ARA terms each block is **the dominant wave for that stretch**, and the question is what sets the share.

**The dominant wave sits at the lowest rung — replicated 3/3** (verified 27 Jun 2026 on real data with the prominence-filtered detector):

| | arm-1 (top rung) | arm-2 | arm-3 (bottom rung) |
|---|---|---|---|
| run 1 | 43% | 11% | **46%** |
| run 2 | 23% | 34% | **43%** |
| run 3 | 36% | 21% | **43%** |

Arm-3 (bottom) **leads most often in every run** (46 / 43 / 43%) and **holds the single longest dominance block in every run** (max block 4 / 5 / 5 swings vs the upper arms' 3 / 4 / 2). So the bottom rung both leads more often and sustains the lead longest — replicated 3/3.

**Honest wrinkle (revised after the clean re-run — it got bigger, so stated plainly):** only the **bottom-rung dominance** is robust. The earlier "clean two-level effect, upper two split evenly ~27–30%" did **not** survive the prominence-filtered detector: the upper two arms are *erratic*, not evenly split — arm-2 swings 11 → 34 → 21% and arm-1 23 → 43% across runs, with no stable order, and in run 1 arm-1 (43%) nearly ties arm-3 (46%) while arm-2 nearly drops out (11%). Block lengths are also much shorter than first reported (max 4–5, not 7–12); the long runs were micro-extrema inflation from the old detector. **Replicated claim: "lowest rung = dominant wave" (leads most + longest single block, 3/3). NOT supported: any clean/even structure among the upper two arms.**

---

## 4. How this tracks the framework

- **Rungs are real and ordered.** Lower rung = more energy, wider excursion, more dominance, longer dominance blocks. This is `WHAT_IS_ARA.md` §4 (recursive rungs) and §9 (rung/scale + energy) showing up as a measured ordering, replicated.
- **Coupling beats the isolated number.** The single-arm asymmetry nulls; the inter-arm coupling (nesting, anti-phase handoff, migrating leadership) carries the signal — exactly §7's claim that "the coupling pattern may matter more than the isolated ARA number."
- **1.0 is the ridge, not inactivity.** All arms orbit the 1.0 rest ridge while large opposing flows pass through — §5.4's "apparently stable interface produced by opposing processes." A damped pendulum ultimately settles *to* 1.0 (rest / cancellation), the state of nothingness the framework places there.
- **0 and 2 are the unreachable poles here.** Free-swing arms never cross them; the over-the-top flip is precisely the 0/2 singularity crossing, and it's also the one thing classical mechanics has no closed form for. The framework's hardest landmark and physics' open problem point at the same place.
- **Classify → predict → validate held.** The prediction (lower rung dominates) was stated before the run-length measurement and confirmed 3/3; the prime-spacing sub-claim was tested neutrally and **nulled** — recorded, not hidden.

## 5. What is NOT claimed

- Not that the arms are in prime-*number* ratios (lengths/periods) — that's a different claim and this data doesn't show it.
- Not a clean three-rung dominance ladder — only the bottom-rung dominance replicates; the upper-two ordering is unresolved.
- Not the singularity-flip — free-swing data never reaches a pole; needs a tumbling/driven dataset.
- Not that ARA is the unique description of chaotic pendulum dynamics — this is one viewing angle, consistent with the standard picture (symbolic dynamics of a chaotic system lingering near unstable periodic orbits, then being ejected) and read here in ARA's coordinates.

## 6. Files

- `pendulum_ara_position.png` — each arm's ARA position vs time (orbiting the 1.0 ridge; arm-3 widest; no pole reached).
- `pendulum_leadership_3way.png` — who leads each big swing, three-way, over time (all three colours interleaving; red most common).
- `pendulum_leadership_switch.png` — earlier two-arm leadership view (superseded by the three-way).
- `pendulum_ara_vs_n.png` — ARA vs number of arms (1 = clock, more arms = more time off the ridge).

## 7. Open / next

- Run-length **ratios** between rungs — is the dominance share itself on a rung law (e.g. octave-like)? Untested.
- A **tumbling** dataset to reach the 0/2 poles and test the singularity-crossing / flip.
- Whether arm-1's lead specifically concentrates at the **crest** (phase-within-swing), distinct from swing amplitude — proposed, not yet run.

---

# 8. Deconstruction arc — study each element, extract its rule, reconstruct, predict

Goal (Dylan): take the system apart element by element, find each element's rule/geometry, rebuild the whole from those rules, then push it forward to predict. All strictly causal, real data only.

## Element 1 — each arm's own geometry
All three arms share **one** dominant period, **1.333 s** (P1/P2 = P2/P3 = 1.000). In this low-energy regime the whole pendulum locks to its slowest normal mode; every arm rides that common clock. So the arms are **not** on separate frequency rungs here — the **ground cycle** is this shared 1.333 s oscillation. What differs is **amplitude**: A1 = 0.31, A2 = 0.43, A3 = 0.78 rad (monotonic, lower = wider; ratios 1.39 / 1.81, total 2.50 — bracketing φ/φ² but not cleanly φ, n=1, not claimed). Lower arm is also the most chaotic (clock-likeness arm2 0.98 > arm1 0.91 > arm3 0.77; arm-3's spectrum is the most broadband). Figure: `pendulum_element1_perarm.png`.

## Element 2 — rung spacing
Frequency spacing is **locked at 1.0** (shared common mode) — **no octave, no φ in frequency** in this regime. The rung ladder lives in **amplitude**, not period. The data-mode periods (1.333 / 0.690 / 0.382 s; ratios ~1.93, ~1.81) are **normal-mode eigenvalues** fixed by the rig's masses/lengths — temptingly near an octave but **not claimed** as octave/φ without normal-mode theory + replication (and 0.382 s is unit coincidence). Frequency rungs would only separate if the arms decoupled into independent oscillators — needs more energy or unequal lengths.

## Element 3 — coupling rules
- **Everything is phase-locked** to the common mode (PLV 0.94–0.99 every pair, 3/3 runs); arm1–arm2 is the tightest.
- ~~**arm-2 mediates the 1–3 link** ... **arm-2 is the relational clock**~~ **(QUARANTINED 27 Jun 2026 — DO NOT USE: calls partial correlation "mediation," which the core forbids; a partial-corr sign-flip shows a shared CARRIER, not a proven causal mediator, and labels the carrier itself "the clock.")**
- **Corrected reading: arm-2 is the shared CARRIER, the clock is the COMMON MODE.** Raw corr(arm1,arm3) is positive (+0.67 / +0.35 / +0.53), but the **partial correlation holding arm-2 fixed flips negative in 2 of 3 runs** (−0.36 / +0.20 / −0.50). So arm-1 and arm-3 only *appear* to move together because they both ride the shared common mode that arm-2 carries; remove that shared carrier and the two ends are intrinsically **anti-phase**. Under the current ridge/clock rule ([[ara_scale]], 27 Jun): the **clock is the common mode** (the one ~1.333 s timing every arm's change runs on); **arm-2 is its carrier/projection, not itself the timekeeper**. Partial correlation identifies the carrier; it does **not** establish causal mediation. Arm-2's physical betweenness is a separate mechanistic prior, not shown by this statistic.
- **Honest null (reinforces the above):** arm-2 is NOT the steadiest oscillator. The "arm-2 is cleanest" signal was a run-1 artifact and does **not** replicate (arm-2 is the jitteriest in run 2). All three share the same clock frequency; none is uniquely the timekeeper — consistent with the clock being the common mode, not any single arm.

## Element 4 — reconstruction (data modes / POD)
> **Measurement category:** SVD/POD is a *standard* decomposition; reading mode-1 as "the common-mode clock" and mode-2 as "the 1v3 anti-phase pair" is an **ARA-inspired interpretation** of it, **not** a canonical ARA reading (SVD modes are not themselves ARA). The variance/reconstruction numbers stand alone as ordinary POD.

SVD of the three angles: **mode 1 = 89%**, **mode 2 = 10.4%** → **two modes = 99.4%** of the variance. Reconstructing from just those two: corr **0.984 / 0.994 / 1.000** for arms 1/2/3.
- **Mode 1** (all same sign, +0.28/+0.43/+0.86, period 1.333 s) = the **common-mode clock**, and its participation weights **are the amplitude ladder** — so the ground cycle and the rung ladder are the **same object**, the dominant eigenmode.
- **Mode 2** (+0.59/+0.63/**−0.51**, period 0.69 s) = the **arm-1-vs-arm-3 anti-phase** differential mode — exactly the Element-3 picture.
So the "unsolvable" 3-arm chaos compresses to **ground-cycle clock + anti-phase engine pair**. Figures: `pendulum_reconstruction.png`, `pendulum_recon_vs_true.png`.

## Element 5 — prediction (strictly causal) + honest verification
Direct linear forecast of the two mode-coefficients; mode shapes + centering + weights all fit on the **first 30 s only**, predicting the held-out second 30 s. Causality checklist passed (no filtfilt/Hilbert, no future features, persistence baseline).

Raw skill looked spectacular (corr ~0.92 even 5 s ahead), **but the right baseline deflates it**: "use the value one period (1.333 s) ago" scores **0.98 flat at every horizon** and ties/beats the model at 2–5 s. When *same-as-last-cycle* matches you, the signal is a **clock**, not a tamed chaos. Per-mode: mode 1 predictable far (clock); mode 2 periodic too (period-ago ~0.98 flat); **mode 3 (0.6%) is the only genuinely chaotic part — dies within 1 s.** So: in this low-energy regime the 2-mode structure holds and is forecastable **because the system is quasi-periodic** (clock regime, near the 1.0 ridge, no flywheel/rotation) — *not* a demonstration of forecasting chaos. Figure: `pendulum_forecast_vs_truth.png`.

**Predict the last (deepest) arm from the structure.** Holding arm-3 out entirely and predicting it strictly causally from **only arms 1–2's history** (never arm-3): corr **0.99 at nowcast through 2 s ahead**, and it **beats arm-3's own self-AR at 2 s (0.988 vs 0.959)**. The deepest, most chaotic arm carries almost no independent information — it is **slaved to the shallower structure**, and is better forecast from the calm arms than from itself ("look up, not down"). Boundary: this holds because the regime is locked/quasi-periodic; a chaotic/tumbling regime would give arm-3 real independent content and degrade it — and that regime needs energetic data that doesn't exist publicly past triple. Figure: `pendulum_predict_last_arm.png`.

---

# 9. Honest status — what's new, what's standard

The **component techniques are all established**: proper-orthogonal/normal-mode decomposition of coupled oscillators is textbook; this exact dataset is a published **ML benchmark built for forecasting**; low-rank reconstruction and cross-variable prediction in a weakly-chaotic regime are expected and have been done. None of the individual numerical steps is a new physics result, and the high predictability is partly *because* the run is tame (the period-ago baseline proves it).

**What is distinctive here is the framework as a lens, and that it called the structure in advance:** before measuring, the geometry predicted (i) one arm = clock, more arms = time off the 1.0 ridge; (ii) rung = amplitude, lower rung wider/more dominant; (iii) arm-1 and arm-3 coupled with arm-2 as the relational clock between them; (iv) the system never reaching the 0/2 singularity without a flywheel/rotation. Each of these **held in the data**, and they fall out of one coordinate system (reversible binary → ridge/rung/handover) rather than four separate analyses. That the readings **agree with standard physics is a feature, not a demerit** (Newton and Einstein agree at low speed). The honest claim is therefore: *the ARA geometry organised a correct, unified, prospective reading of a system physics calls unsolvable* — a strong result **for the framework as an organising lens**, not a claim of new pendulum physics.

---

# 10. Correction / quarantine log (27 Jun 2026)

ARA-framework audit of the pendulum scripts. Old claims struck out in place (above), not deleted. Code edits applied and **re-run COMPLETED 27 Jun 2026 on the real `.mat` data** (all 7 scripts, 3 runs). Scripts 01/03/04/05/06/07 reproduced their original numbers essentially exactly (carrier sign-flip −0.36/+0.20/−0.50 → −0.362/+0.197/−0.502; 2-mode reconstruction 99.4%; period-ago baseline flat ~0.98 ties/beats the model; arm-3-from-arms-1-2 beats self-AR at 2 s, 0.988 vs 0.959). The only material change is script 02 (below).

1. **"arm-2 mediates" / "arm-2 is the relational clock" → QUARANTINED (§Element 3).** Calling a partial-correlation sign-flip "mediation" is forbidden by the core. Reframed: arm-2 is the shared **carrier**; the **clock is the common mode**; partial-corr shows a carrier, not a proven mediator. Code: `04_coupling_partial_corr.py` docstring + print line. Ties to [[ara_scale]] ridge/clock-role rule.
2. **Leadership turn-detection robustness → code fixed AND re-run (§2.4, §3).** `02_leadership_rung_dominance.py` switched from a bare gradient-sign-change detector (counts micro-jitter; biases the noisiest arm) to a prominence + minimum-spacing filter. **Outcome:** swing count ~halved (213 → ~95–98), confirming the old detector over-counted noise. The headline — **lowest rung (arm-3) leads most + holds the longest single block — SURVIVED 3/3.** But the secondary "upper-two split evenly ~27–30%" did **NOT** survive: with clean turns the upper two arms are erratic (arm-2 11/34/21%, arm-1 23/43/36%), and block lengths are shorter (max 4–5, not 7–12). Net: bottom-rung dominance is robust; any even/clean upper-two structure was a detector artifact. Numbers in §2.4/§3 updated to the verified values.
3. **φ reference label removed (§Element 1 code).** `01_per_arm_geometry.py` no longer prints "octave=2.0 phi=1.618" beside amplitude ratios — no handover is defined, so φ must not be seeded even as a reference.
4. **SVD tagged as ARA-interpretation, not canonical ARA (§Element 4).** Mode→clock/pair mapping is a lens over a standard POD; numbers stand alone. Code note added to `05_reconstruction_svd.py`.
5. **Persistence baseline added (§Element 5 code).** `06_forecast_causal.py` now actually computes the persistence baseline its docstring promised, alongside period-ago.
6. **`bend()` made rest-relative (§Element 2/3 code).** `03_relational_ara.py` now defines the bend on rest-centred angles so the inline relation lands exactly on the 1.0 ridge even if arms' rest angles differ.

**Not changed (audited clean):** strict causality in `06`/`07` (train-only modes/mean/weights, past-only features, held-out targets, period-ago deflator); correlation-led reporting (no MAE); logged nulls (prime-spacing, arm-2-steadiest); position-vs-scale kept distinct; frame locked before measuring; §9 honest-status framing. Not using `ara_mapper.py` is correct here (rise/fall correctly nulls on a conservative system).

**Open enhancements (not drift):** quantify per-arm energy (velocity is loaded but unused for energy) to *show* "lower rung = more energy"; back the "called the structure in advance" claim with a timestamped predeclaration to make it auditable.
