# Pendulum — Present/Future Dissociation (Test 6 of the 2 Jul queue)

**Date:** 2 July 2026. **Run by:** Claude (Fable 5) at Dylan's request, live in session.
**REPLICATED same day on the author's own hardware (Windows), independent environment
and data download: all tables digit-identical, including the 19–8 free-swing tally and
the driven-run 53/13/33 leadership + 9–0 ceiling result.**
**Data:** real only — dynamicslab MultiArm-Pendulum (Zenodo 10.5281/zenodo.6633719),
all three triple-pendulum free-swing runs, re-downloaded fresh from Zenodo this session.
**Script:** `test6_dissociation.py` (this folder). Strictly causal throughout: train/test
split in time, SVD modes and means from the training half only, features are past samples
only, ridge weights fit on train, scored out-of-sample.

## The rule under test (stated before running)

Dylan's neighbor-dominance rule: **"Larger waves dominate right now; lower/slower
structure dominates the future."**

- Present half (already established, prior repo result, 3/3): arm-3 — the most
  energetic, widest-swinging arm — leads the present (turns first most often, holds the
  longest dominance blocks).
- Future half (the prediction on record for this test): strictly-causal forecast skill
  should route through the **slow common mode**, not through energetic arm-3 — i.e. at
  mid/long horizons, common-mode-past features should forecast any arm's future better
  than arm-3-past features.

## Method

Per run: rest-centered angles at 50 Hz, ~60 s, split 30/30. Mode-1 coefficient from
train-only SVD = the shared slow clock ("common"). Three univariate causal feature sets
(common-past, arm3-past, own-past; 1.6 s lag window, ridge λ=1e-2) forecasting each
arm's future angle at horizons 0.5–8 s; persistence as baseline.

## Result — SUPPORTED (direction), with fences

**Primary count:** at horizons ≥ 2 s, common-mode-past beats arm3-past **19 to 8**
across 3 runs × 3 targets × 3 horizons (naive sign test p ≈ 0.03; trials are correlated,
so treat as direction, not proof).

**The cleaner finding (unlooked-for, 3/3 runs):** the arm that owns the present has the
least ownable future. Arm-3 — the established present-leader — is the **least
forecastable target** at long horizon in every run (8 s own-future corr 0.71 / 0.44 /
0.80, vs arm-2's 0.95 / 0.95 / 0.98). Leadership of the present and predictability of
the future are *anti-associated across arms*. Both halves of the rule land in one table:
the energetic arm rules the moment; the slow shared structure carries what future there
is; and the ruler of the moment is the future's most opaque citizen.

| finding | status |
|---|---|
| common-past > arm3-past at ≥2 s (19–8) | supported, small margins |
| present-leader arm-3 = least forecastable future, 3/3 | supported, clean |
| rule's two halves dissociate as predicted | supported |

## Honest fences

- **Margins are third-decimal** (e.g. 0.990 vs 0.988): this low-energy regime is
  quasi-periodic — the repo's own prior note stands (period-ago baseline ~0.98; the
  common clock makes everything predict everything). The 19–8 count is directional
  support, not a strong effect.
- Trials are correlated (same runs/targets/horizons); the binomial p is generous.
- One regime, one rig. The harsher test is the **driven/tumbling** dataset
  (TripleDataWithControl, same Zenodo record — already downloaded this session), where
  the common clock is broken and the feature sets should genuinely separate. Next run.
- Feature sets are univariate by design (isolating *whose past*); a multivariate
  comparison would tangle attribution.

## Addendum — Test 6b, the driven regime (same session)

Ran the identical battery on the driven triple run (`TripleDataWithControl_1`,
re-downloaded from the same Zenodo record). Two findings, one honest null:

1. **Forecast half: UNINFORMATIVE here — ceiling effect.** The drive entrains the
   whole chain into a near-perfect clock (train-only SVD mode-1 = **99.5%** of
   variance; every feature set forecasts every target at 0.999–1.000 out to 8 s).
   Common beat arm3 9–0 at ≥2 s but by rounding dust — do not count it. In the
   framework's own vocabulary this is the forced-clock / ARA→2 regime, where "whose
   past owns the future" has a trivial answer: the forcer's. The dissociation test
   needs a regime with a future left to own; the free-swing result stands as the
   informative one.
2. **Present half: INDEPENDENT REPLICATION of the repo's driven finding #5.**
   `PENDULUM_DRIVEN_ARA_RESULT.md` reports leadership migrating up toward the drive
   entry (free 45/11/45 → driven 50/15/35, arms 1/2/3). This session's independent,
   differently-implemented detector (prominence + spacing on |angle| peaks) reads
   **53/13/33** on the same run — same migration, different code. Replication, not
   discovery.
3. **The rule, sharpened by the pair of regimes:** present-dominance follows the
   energy — bottom arm when the energy lives at the bottom (free swing), top arm when
   the energy enters at the top (driven). "Larger waves dominate right now" is
   regime-dependent in exactly the way the rule implies: find the big wave first.

## Framework reading

Consistent with the cross-system pattern that motivated the rule: pendulum leadership
(present) = most energetic rung; ENSO forecast (future) = slow reservoir below (WWV);
heart horizon (future) = slowest driver. The rule now has a within-system confirmation:
the same three arms, present and future, dissociating in the predicted directions.
Upgrade the rule's status from "per-system taxonomy" to "supported within-system, one
system, weak-regime" — pending the driven-data rerun.
