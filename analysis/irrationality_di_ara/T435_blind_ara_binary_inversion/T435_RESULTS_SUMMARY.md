# T435 results — blind ARA binary-identity inversion

**Frozen verdict: PARTIAL.**

The combined SXS waveform retained enough relational structure to recover the two-hole **axis**, their shared **closing history**, and the two child **radial histories** up to unordered-label and coordinate symmetries. The frozen handover clock was late, and the odd/even mode contrast did not yet recover the individual child shares accurately enough to claim that both black-hole identities were fully separated.

## Answer first

- **Two-child orientation passed:** axis coherence `0.99421`; median modulo-pi error `0.792 degrees`.
- **The octave rule mattered:** using the full parent phase instead of half-phase gave coherence `0.00619`.
- **The shared relation passed:** Spearman `0.99956` against hidden A–B horizon separation; the circular-shift control was `-0.33359`.
- **The science crosswalk agreed:** the conventional `omega^(-2/3)` separation proxy scored Spearman `0.99929`.
- **Child radial histories passed the frozen correlation gate:** median Spearman `0.99938`.
- **But child identity amount remains unresolved:** predicted mean shares were approximately `0.364/0.636`, while the hidden mass-weighted horizon shares were `0.450/0.550`; mean absolute share error was `0.0858`.
- **Handover timing failed:** blind estimate `3723.038 M`; first common horizon `3685.496 M`; error `37.542 M`, versus an allowed parent-waveform cycle of `11.371 M`.

## What was actually separated

The waveform-only inversion recovered:

1. a pair of antipodal child directions from `phase(h22)/2`;
2. a remaining-relation/closing coordinate from the tightening parent cadence;
3. two unordered radial histories by splitting that relation with the waveform's odd/even modal imbalance.

The first two are strong. The third mainly inherits the common closing trend; its high correlation does **not** mean that the individual mass or size shares were recovered. The independent share error exposes that distinction.

Accordingly, T435 separates the **two-child geometry and their shared relation**, but does not yet uniquely recover the full identities of both black holes or the two physical near-side combining edges.

## Frozen gates

- PASS — orientation coherence `>= 0.80` and margin over unhalved control `>= 0.10`.
- PASS — relation Spearman `>= 0.70` and margin over shifted control `>= 0.20`.
- PASS — median child-radius Spearman `>= 0.50`.
- FAIL — handover error no greater than one parent waveform cycle.

## Handover anatomy

The three frozen waveform landmarks were:

- total modal-power maximum: `3692.748 M` (`+7.252 M` after common-horizon formation);
- modal-concentration change: `3723.038 M` (`+37.542 M`);
- cadence-derivative maximum: `3792.026 M` (`+106.529 M`).

Their predeclared median was therefore late. The power maximum alone lies within one parent cycle, but selecting it after seeing the answer would be post hoc and does not rescue the frozen gate. The ordering instead suggests that common-horizon formation begins before the waveform's later redistribution and cadence landmarks finish.

## Scientific anchor and evidence class

The source is the public numerical-relativity simulation [SXS:BBH:0305](https://zenodo.org/records/13182440). SXS defines horizon A as the first inspiralling black hole, B as the second, and C as the final/common apparent horizon, with masses, spins, and coordinate-center trajectories available for each in the horizon product ([SXS horizon documentation](https://sxs.readthedocs.io/en/main/tutorials/03-Horizons/)).

Because the source is generated within established general relativity, this is a blind **crosswalk and inversion calibration**, not independent evidence that ARA generates gravity. The coordinate-center relation is also gauge-sensitive; the excellent phase and rank recovery should not be read as an invariant physical-distance measurement.

## Best next test

Freeze the same inversion across a development/holdout panel of SXS simulations spanning mass ratio and spin. The decisive new target is not another within-event rank correlation. It is whether one fixed waveform-only odd/even mapping predicts the hidden child share or mass contrast across untouched systems while preserving the half-phase orientation and relation recovery. If it does, the inversion advances from recovering a binary relation to recovering two distinct identities.

## Files

- `T435_FROZEN_PROTOCOL.md`
- `T435_FREEZE_LOCK.json`
- `T435_predict_waveform_only.py`
- `T435_score_hidden_horizons.py`
- `results/T435_PREDICTION_SHA256.txt`
- `results/T435_WAVEFORM_ONLY_PREDICTION.json`
- `results/T435_SCORED_RESULT.json`
- `results/T435_SCORED_SERIES.npz`
- `results/T435_BLIND_BINARY_INVERSION_AUDIT.png`
- `T435_VALIDATION.md`

