# T342 — multi-medium Irrationality TE-ARA result

**Run:** 5 August 2026  
**Registered auxiliary verdict:** **NOT SUPPORTED**  
**Intended intact-pair Di-ARA coupling claim:** **NOT TESTED BY T342**  
**Eligible/pass:** `6` eligible, `1` pass

## Result first

The frozen auxiliary common-gait rule passed in 1/6 eligible holdout domains, so its registered verdict is **NOT SUPPORTED**. All 7/7 holdouts populated the four mixed regions. The intended intact-pair Di-ARA coupling claim was not tested by T342.

All seven holdouts populated all four mixed regions under the frozen coordinate. The registered 1/6 result concerns an auxiliary identical-gait rule, not the intended Di-ARA claim that two perpendicular ARA relations form an identity-specific coupled parent.

## Originator interpretive correction

After seeing the result visually, Dylan clarified that Di-ARA does not require one neighbour-by-neighbour quadrant order, cadence, speed or proportion across identities. It supplies the two coupled axes and the four mixed regions `Ab`, `aB`, `bA`, `Ba`; the exact movement through them depends on identity and coupling. T342's frozen auxiliary verdict remains unchanged, but the intended intact-pair coupling advantage is **not tested** by T342.

See `T342_INTERPRETIVE_CORRECTION_ORIGINATOR_CLARIFICATION_2026-08-05.md`. The frozen protocol and addendum were not altered.

## Holdout auxiliary common-gait audit

| domain | selected states | four-sector eligible | adjacency | shuffle p | ordered information | shuffle p | verdict |
|---|---:|---|---:|---:|---:|---:|---|
| acoustics | 99,999 | yes | 0.4515 | 1.0000 | 0.1278 | 0.0010 | FAIL |
| bubbles | 4,704 | yes | 0.5995 | 1.0000 | 0.0577 | 0.0010 | FAIL |
| cold_room | 93,323 | yes | 0.7445 | 1.0000 | 0.4229 | 0.0010 | FAIL |
| hydraulic | 99,650 | yes | 0.6166 | 0.0010 | 0.0068 | 1.0000 | FAIL |
| pendulum | 100,000 | yes | 0.8326 | 0.0010 | 0.0450 | 1.0000 | FAIL |
| qutrit | 100,000 | yes | 0.7042 | 0.0010 | 0.1017 | 0.0010 | PASS |
| river | 414 | no | 0.5017 | 1.0000 | 0.1507 | 0.0010 | INELIGIBLE |

Adjacency excludes same-sector persistence: it asks whether actual handovers go to a neighbouring quadrant rather than jumping diagonally. Ordered information asks how much the present quadrant tells us about the next. These were the frozen auxiliary endpoints. They are retained for reproducibility and must not be read as the framework's required universal gait.

## Secondary constants

| domain | line median R | nearest radial | strong e | circle median turns | nearest circular | strong Phi |
|---|---:|---|---|---:|---|---|
| acoustics | 0.428789 | three_halves | no | 0.131102 | quarter | no |
| bubbles | 0.020242 | plastic | no | 0.002694 | quarter | no |
| cold_room | 0.029629 | plastic | no | 0.001637 | quarter | no |
| hydraulic | 0.008079 | plastic | no | 0.003960 | quarter | no |
| pendulum | 0.000187 | plastic | no | 0.000219 | quarter | no |
| qutrit | 0.896260 | e | no | 0.352190 | one_over_e | no |
| river | 0.176488 | plastic | no | 0.074723 | quarter | no |

Exact `e` survived the strong line gate in 0 domain(s), and exact reciprocal-Phi survived the strong circle gate in 0 domain(s). These counts are reported as the frozen secondary audit and do not alter the registered auxiliary verdict.

## What this establishes—and what it does not

In the recorded qutrit, the chronological-versus-shuffled result is evidence that this two-axis cut retained both local handover preference and ordered state information. Several other domains passed only one endpoint. That does not imply that those identities failed Di-ARA: the frozen auxiliary demanded one particular combination of movement properties that the intended framework does not require universally.

All seven holdouts occupied all four mixed regions. This is compatible with the intended geometry but is not unique proof: the coordinate itself defines four possible regions, and smooth systems or ordinary state-space dynamics can populate them. The direct empirical question is now whether the intact pair carries more stable transferable information than either child or a broken pairing.

TE-ARA closure (`X + (2-X) = 2`, and the angular equivalent) is definitional bookkeeping. It is not counted as an empirical pass.

## Data and evidence boundary

Cold-room and acoustic numerical files were unopened fresh sources at protocol freeze. Pendulum, hydraulic, bubble, qutrit and river records had been used previously for other ARA questions, so their T342 results are cross-question transfers rather than independent discoveries.

The cadence-neutral addendum capped each domain/split at 100,000 native ordered states in deterministic non-overlapping blocks. This prevents 44.1 kHz audio from outweighing five-second environmental logging. Domain verdicts are never pooled by row.

## Reproduction

```powershell
$env:PYTHONPATH='analysis/irrationality_te_ara_multimedium/vendor'
& 'C:/Users/Dylan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' analysis/irrationality_te_ara_multimedium/t342_multimedium_irrationality_te_ara.py
& 'C:/Users/Dylan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' analysis/irrationality_te_ara_multimedium/validate_t342_multimedium_irrationality_te_ara.py
```

The ignored fresh public sources can be reacquired with `acquire_t342_public_sources.py`.
