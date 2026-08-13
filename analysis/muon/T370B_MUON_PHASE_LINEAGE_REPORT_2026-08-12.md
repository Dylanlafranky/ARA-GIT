# T370B — Muon parent-phase lineage across an in-band field ladder

## Result

**NOT SUPPORTED** — 11 of 14 runs passed the frozen resolved-parent gate (required: 10).

The ARA circle was learned only from early raw detector counts. Its recovered
cadence then tracked the independently controlled field with Spearman
`0.5985` and a zero-intercept slope only
`32.54%` from the independently known muon
rate. The duplicate 200 G acquisitions differed by
`0.010 MHz`.

This registered verdict stays failed because the 520 G acquisition collapsed
at the frozen 64 ns analysis resolution and therefore broke the all-run rank
and slope gates. The other 13 runs had a near-perfect rank relation of
`0.9986`
and their slope was
`0.159%`
from the independent value. A labelled post-hoc check at 32 ns recovered the
520 G cadence at `7.060 MHz` versus `7.048 MHz` expected and passed all four
holdout baselines plus the detector-rotation control. This diagnoses the frozen
failure as a resolution boundary, but it does not retroactively change the
registered verdict.

## Plain-language ARA reading

Before decay, the parent muon carries an opposing Phase A/Phase B directional
relation. We learned that circle from the first part of each acquisition and
then asked it to predict the later visible daughter pattern. When the cadence
of that fitted circle was placed beside the applied field only after fitting,
the two formed the registered parent lineage rather than an arbitrary slow
envelope.

The charged daughter therefore preserves readable information about the parent
relation through the handover. The unseen two-neutrino packet is the natural
opposite daughter branch in the stopped-parent frame, but this archive does not
measure it directly.

## Side-by-side translation

| ARA | Established muon description |
|---|---|
| Parent Phase A ↔ Phase B circle | Precessing polarized muon spin |
| Ridge crossing of the circle | Equal projection on the chosen detector cut |
| Visible child branch | Direction-dependent positron counts |
| Hidden complementary child | Combined two-neutrino energy/momentum packet |
| Parent cadence retained after handover | Positron angular distribution encodes the muon spin at decay |

## Frozen results

| Run | field G | ARA f MHz | expected f MHz | f error | holdout gain | corr. | resolved gate |
|---|---:|---:|---:|---:|---:|---:|---:|
| EMU00066651 | 20 | 0.280 | 0.271 | 3.29% | +77.39% | 0.974 | PASS |
| EMU00066652 | 25 | 0.330 | 0.339 | 2.61% | +12.16% | 0.480 | FAIL |
| EMU00066627 | 40 | 0.550 | 0.542 | 1.45% | +22.93% | 0.640 | PASS |
| EMU00066654 | 60 | 0.820 | 0.813 | 0.83% | +14.27% | 0.517 | PASS |
| EMU00066655 | 80 | 1.090 | 1.084 | 0.52% | +13.05% | 0.496 | PASS |
| EMU00066656 | 100 | 1.360 | 1.355 | 0.34% | +13.20% | 0.498 | PASS |
| EMU00066657 | 150 | 2.040 | 2.033 | 0.34% | +10.85% | 0.454 | PASS |
| EMU00066658 | 200 | 2.720 | 2.711 | 0.34% | +9.41% | 0.424 | PASS |
| EMU00066661 | 200 | 2.710 | 2.711 | 0.03% | +9.83% | 0.433 | PASS |
| EMU00066669 | 230 | 3.130 | 3.117 | 0.40% | +6.69% | 0.362 | FAIL |
| EMU00066659 | 280 | 3.800 | 3.795 | 0.13% | +5.81% | 0.337 | PASS |
| EMU00066662 | 360 | 4.890 | 4.879 | 0.22% | +3.46% | 0.263 | PASS |
| EMU00066660 | 400 | 5.420 | 5.422 | 0.03% | +2.59% | 0.229 | PASS |
| EMU00066663 | 520 | 0.100 | 7.048 | 98.58% | -24.18% | 0.028 | FAIL |

## Gates

{
  "resolved_runs_at_least_10_of_14": true,
  "field_frequency_spearman_at_least_0_90": false,
  "slope_within_5_percent": false,
  "duplicate_200G_within_0_10_mhz": true
}

## Boundary

This is a strong recovery/crosswalk of a known physical relation using the ARA
geometry on raw public data. It does not directly observe the neutrino branch,
demonstrate a new hidden field, or show that ARA predicts beyond the standard
precessing-spin description. A more decisive next rung would require a public
event-level polarized decay archive measuring the charged daughter energy and
direction together, or an ARA-only prediction frozen before a new field run.
