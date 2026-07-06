# ARA Test Kit — 2 July 2026 session

Portable instruments for the queued tests. Built by Claude (Fable 5); to be wired to
local data and file structure by Dylan + local AI. **Every script carries its
pre-registered prediction in the header — the pre-registration travels with the code.**
Dependencies: numpy, scipy only. All output is text. No gated vocabulary anywhere:
for gated-data systems, compute the summary numbers with your local pipeline and feed
the CSVs (test 1 takes `duties.csv` directly).

## Files

| file | test | decides |
|---|---|---|
| `kit_utils.py` | shared | series IO, duty, floors, damping angle, bath share, the constants |
| `test1_duty_table.py` | **1 — the duty table** | φ's decisive experiment: duty peak vs {1/e, 3/8, 1/φ², 2/5} in pre-classified columns |
| `test2_lagshape.py` | 2 — lag shape | structure vs leak: log-linear floors (e-null) vs bent tail (return path) |
| `test3_modal_angle.py` | 3 — angle race | 0–1° vs 17° (golden pitch) vs 36°; **sign the horse before running** |
| `test7_lottery_star_line.py` | 7 — FDT line | shed vs bath-share monotonicity across the atlas; the diamond's first map |
| `test_bridge_phasestep.py` | bridge | duty = arc fraction? phase-step 137.5° vs 144° vs 180°; run WITH test 1 on the same systems |
| `test8_cascade_optimum.py` | 8 — cascade | golden vs equal-log plateau spacing with sourced hysteresis; pure engineering |

## Adaptation notes (for the local AI)

1. Fill each script's CONFIG block with local paths + sample rates. `read_series`
   eats one-column or last-column CSVs; adjust `col=` if needed.
2. The band split (`two_bands`) and duty extractor are transparent generics —
   for authoritative runs substitute the canonical `ara_mapper.py` decomposition
   and keep BOTH results (if generic and canonical disagree, the decomposition
   is the live issue, not the constant).
3. Zero-phase filtering is used for DESCRIPTIVE measurement only (duty, phase,
   floors). It must never touch a prediction target (repo rule). `bath_share`
   is strictly causal by construction.
4. Discipline reminders baked into outputs: report ALL competing constants;
   crowded-neighborhood rule (if several constants sit inside the CI, say
   "cannot discriminate," do not pick φ); test 3 requires the horse signed in
   the file BEFORE real data runs.
5. Run order suggestion: 1 + bridge together (same systems — the conjunction is
   the claim), then 2, then 7 (reuses floors), then 3, then 8 whenever the
   sourced hysteresis numbers are in hand.

## The predictions, one line each (as pre-registered in SESSION_NOTES §11/§13)

1. Engines' duty peaks at 0.382; dead/forced column shows no golden peak.
2. Recyclers' floor curves bend away from log-linear; leaky systems don't.
3. (Signed horse) — the angle distribution peaks where the framework signs.
7. Spearman(shed, bath) > 0 — the shed and the jitter are one door.
Bridge. Golden-duty systems advance ~137.5°/cycle; 144° means Fibonacci lock.
8. Golden plateau spacing beats equal-log outside parameter uncertainty — or doesn't.

Falsification is a first-class outcome for every one of these. That's the point.

## Calibration & estimator notes (added after smoke tests, 2 Jul)

- **Duty bias:** the extractor reads slightly toward 0.5 (harmonic truncation).
  With the default 12 harmonics, a true 0.382 reads ~0.392 at SNR ~50. Since the
  constant gaps in the crowded neighborhood are ~0.007-0.018, ALWAYS calibrate:
  generate synthetic sawtooths at your series' noise level and period, measure
  the bias, and correct — or fit the bias curve and report corrected duties.
- **Angle estimator measures decoherence, not deterministic decay** (Pearson
  autocorrelation is amplitude-blind). Correct for sustained noisy oscillators
  (real systems); validated on a stochastic zeta=0.05 target: measured 3.3 deg
  vs 2.9 true. For transient/ringdown data fit the envelope instead.
- **bath_share validation:** pure noise -> 1.02; clean sine -> 0.000. Sound.

## CORRECTION (2 Jul, post-first-run — Dylan's catch)

The repo's registered golden duty is **band-dominance duty** (fraction of time
the fast band's envelope dominates the slow band's — relational, in-motion), NOT
waveform rise/fall (a shape measure). `kit_utils.dominance_duty()` added. Test 1
must be run BOTH ways and the framework's claim adjudicated on the DOMINANCE
version; the rise/fall version is a separate (space-side) measurement.

**The boundary, pinned so it cannot move again (2 Jul):** the framework now
formally expects φ ONLY in caught-in-motion relational measures — dominance
duty, phase-step per cycle, handover timing — and expects its ABSENCE in
slice/shape measures (waveform rise/fall, spacing ratios, static shape indices;
consistent with all of today's slice-side nulls). If canonical dominance-duty
and phase-step ALSO read rational/anti-phase, there is no remaining
measurement-class for φ to retreat to. This boundary is part of the
pre-registration from this point forward.

- **dominance_duty calibration (post-fix):** SOS filters (stability at narrow
  low bands) + mean-normalized envelopes (median creates quiet-period ties).
  Synthetic gated targets 0.2/0.382/0.6 read 0.283/0.416/0.563 — compressed
  toward 0.5 by filter edge-smearing, bias ~+0.03 at golden. SAME RULE AS
  RISE/FALL DUTY: calibrate on synthetic gated signals at your record length
  and SNR, correct, or defer to the canonical mapper. The bias exceeds the
  constant gaps; uncalibrated dominance numbers must not adjudicate phi.

## L1 DIGITAL RIG CORRECTION (2 Jul, late — circle-map ground truth run)

The folded phase-step angle CANNOT discriminate locks from the golden channel in
practice: the 5/8 lock folds to 135.0 deg, golden to 137.5 deg — 2.5 deg apart,
inside any realistic measurement error. Demonstrated numerically on the circle map
(digital_rig_L1.py). ALSO: tongues are not centered on the bare rational drive
value (drive at exactly 3/5 sat OUTSIDE the 3/5 tongue at K=0.9) — locks must be
identified in the RESPONSE, not the forcing.
KIT UPGRADE REQUIRED for test_bridge_phasestep: replace angle-nearest-neighbor
adjudication with LOCK DETECTION — (a) is the step constant across time windows
(plateau) and (b) does the winding sit at an exact rational under perturbation/
detuning. Angle values report; lock/no-lock decides.
Ground-truth results for the record: tongue widths 2/3: 0.0228 > 3/5: 0.0060 >
5/8: 0.0016 (correct Farey ordering); 1/phi in the open channel, no lock; one
explicit pull-in demonstrated (drive 0.596 -> W snapped to exactly 0.60000).

## OUT-OF-THE-BOX RULE (3 Jul — applies to all kit scripts once committed)

When wiring these to real data, follow the repo's replication rule (see
TEST_PROTOCOL.md): script checks for the data file at its relative path and
auto-downloads from the canonical public source if missing (URL + DOI +
checksum in the header). Synthetic scripts: fixed seeds, no inputs. Gated
data: include a runnable sample. `python script.py` on a fresh clone must
reproduce the registered result — no author required.
