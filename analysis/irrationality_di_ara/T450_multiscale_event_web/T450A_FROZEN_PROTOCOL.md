# T450A — pose-scale and observable-child discovery

Status: frozen before extraction of the T450A sixty-second pose histories. This is the first cut in the approved T450 lineage; it does not yet infer lifecycle periods or claim a time wave.

## Who

Eight individual adult male *Drosophila melanogaster* are measured. The first and last HDF5 filename from each experimental date are selected without using behaviour, collapse or death outcomes.

- Development: six flies from experiments 1–3 (two per date).
- Untouched regime transfer: two flies from experiment 4 (the later, hotter condition).

Experiment 4 may not influence feature definitions, scale selection, quality rules, ARA display mappings or report emphasis.

## What

The source is the authors' two-dimensional pose tracking, not the coarser behaviour labels used in T448/T449. Six independently observed candidate relations are derived:

1. whole-body traversal speed from thorax displacement;
2. body-axis rotation speed from the head–abdomen axis;
3. core bend from thorax displacement perpendicular to the head–abdomen line;
4. core span from head–abdomen distance;
5. internal articulation from legs and wings moving in the body frame;
6. left/right articulation balance, only where both sides have adequate visible nodes.

The published behaviour label and `on_edge` channel remain annotations and controls. They do not define the pose children. Proboscis visibility is retained as an event annotation but cannot be a continuous child because the source inventory found only about 2.1% visibility.

These channels are candidate observable ARA children. T450A must not pre-name any pair Phase A/Phase B, a Di-ARA or the hidden time coordinate.

## When

Each fly contributes four continuous 60-second parent envelopes centred at 12.5%, 37.5%, 62.5% and 87.5% of its recording. This placement uses recording fraction alone; author-recorded collapse and death are not used.

Within every envelope, temporal structure is examined at dyadic local scales of 1, 2, 4, 8, 16, 32, 64, 128, 256, 512 and 1,024 frames. At 99.96 frames/s these are approximately 0.010 to 10.244 seconds. A local scale requires at least five complete observations in the 60-second envelope.

The 60-second envelope is a parent container, not a discovered 60-second cycle. The unresolved 10–60 second gap is explicitly carried forward to T450B, where longer continuous histories can measure it.

## Where

The relational address is:

individual fly → recording-fraction parent → 60-second pose envelope → body-frame feature children → empirically supported local rungs → existing T449 ten-minute, T448 one-hour and T448B 24-hour parents.

All body-frame channels use the thorax as origin and the head–abdomen direction as the local axis. Distances are divided by that fly's robust median head–abdomen length across its four envelopes. This removes camera pixels and fly size without fitting to lifecycle outcome.

The same fly may provide repeated envelopes, but the fly—not the frame or envelope—is the independent unit for support and uncertainty.

## Why

T448/T449 found broad lifecycle and behavioural timing geometry but did not identify the finer observed children that form it. T450A asks which physical pose relations have reproducible temporal scales and whether those scales survive a new experimental regime.

This is a scale-and-node discovery test. It is not a death predictor, a universal ridge test or proof that any recovered rhythm is time itself. It supplies the measured child vocabulary needed before T450B can infer lifecycle periods and T450C can build a cross-scale web.

## How

### Pose construction

- Core nodes (`head`, `thorax`, `abdomen`) must be finite.
- The thorax is translated to the origin; all nodes are rotated so the head–abdomen axis is horizontal.
- The fly reference length is the median finite head–abdomen distance across all four envelopes.
- No gap longer than two frames is interpolated. Core failures remain missing.
- Internal articulation uses legs and wings and requires at least four of eight appendage nodes in a frame.
- Left/right balance requires at least two visible appendages on each side. It is conditioned on paired visibility because the inventory found asymmetric left/right missingness.
- Framewise feature values are winsorised only at development-derived 0.5th and 99.5th percentiles. Raw values remain cached and visible in the report.

### Scale descriptors

For every feature, envelope and dyadic scale, non-overlapping block summaries are formed. Speed/amount channels use block means; pose-state and signed-balance channels use block medians. Three independent descriptors are retained:

1. **Persistence:** Spearman correlation between consecutive block values.
2. **Retained dispersion:** block MAD divided by raw-scale MAD.
3. **Time-reversal asymmetry:** the third moment of consecutive block differences divided by their absolute third moment.

No single descriptor is called the scale. The geometry-change score at each interior scale boundary is the Euclidean change in persistence, retained dispersion and absolute reversal asymmetry after descriptor-wise robust standardisation on development data.

### Rung selection

For each feature and development fly, the two strongest interior boundaries are nominated, with at least two octaves between them. A feature rung is frozen only if at least four of six development flies nominate that boundary within plus or minus one octave.

**Pre-holdout finite-window correction.** The first development computation exposed a mechanical endpoint problem before experiment 4 was opened: geometry-change scores at the largest scales were inflated because only 5–11 blocks remained. Accordingly, every feature/envelope/boundary score is compared with 32 independently timestamp-permuted histories at that identical scale. A fly may nominate a boundary only when its median observed score across four envelopes exceeds the median of the envelope-specific 95th-percentile nulls; eligible boundaries are ranked by their null-standardised excess. This correction was frozen before extracting or reading either experiment-4 fly. The uncorrected development addresses are retained in `T450A_SELECTION_CORRECTION.md`; they are not treated as biological rungs.

If two supported rungs remain, both are retained as micro and bout candidates. If none remains, that feature's local rung is unresolved. A common parent candidate may be reported only when at least three independent feature identities support the same octave band. The method may not force all features onto one scale.

### Display mapping

Raw units and raw scale metrics are primary. For comparable ARA displays only, every frozen feature/rung uses

\[
x_{ARA}=1+\tanh\left(\frac{x-m_{dev}}{2\,MAD_{dev}}\right),
\]

where the centre and MAD are fit once on development flies. The ridge at 1 is therefore the development relational centre, not a universal physical constant. Experiment 4 receives the frozen mapping unchanged.

### Controls and evaluation

- Chronology control: independently permute timestamps within each feature history and repeat the scale descriptors. A circular shift is reserved for later cross-node lead/lag tests because it preserves most within-node persistence and is therefore not an adequate null for scale discovery.
- Phase control: reverse each envelope. Persistence and retained dispersion may remain; signed reversal asymmetry must reverse.
- Visibility control: repeat articulation summaries in high-visibility frames and report left/right missingness separately.
- Behaviour reduction control: stratify discovered scale occupancy by the published behaviour labels; a pose rung is not independent if it merely reproduces a label boundary.
- Edge control: report `on_edge` occupancy for every envelope.

Transfer is descriptive at this eight-fly calibration size. A rung transfers when both experiment-4 flies place their strongest geometry change within plus or minus one octave of the frozen development rung and the relevant raw descriptor direction agrees. Failure is retained as a visible regime distortion rather than erased by a binary gate.

## Mandatory pivot notices

Stop and report before changing the question if any of these occurs:

1. range extraction cannot recover continuous 60-second pose blocks;
2. body-length normalisation is unstable or core-node continuity is inadequate;
3. apparent scales collapse under the chronology or visibility controls;
4. the available record supports only a projection perpendicular to the proposed time-facing relation;
5. a longer scale, different medium or outcome-aligned window becomes necessary.

Such a pivot may be sensible, but it belongs to a separately named test with a new Who/What/When/Where/Why/How.
