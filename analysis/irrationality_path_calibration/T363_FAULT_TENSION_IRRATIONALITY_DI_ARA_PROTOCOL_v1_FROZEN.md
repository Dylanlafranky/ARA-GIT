# T363 frozen protocol v1 — fault-tension Irrationality Di-ARA

**Frozen:** 12 August 2026, after source/schema QA and before tension-coordinate scoring  
**Claim packet:** `T363_FAULT_TENSION_IRRATIONALITY_DI_ARA_CLAIM_PACKET_v1.md`

## WHO

The dense identity is local fault tension at shear-stress sensor S20 (`x=73.15 mm`) in laboratory Event 101. Local displacement L3 (`x=70 mm`) independently marks main slip.

Replication identities are the 10 dry and 5 water-pressurized stress-drop events in the published Acosta shear-stress records.

## WHAT

The physical tension Di-ARA is `(x_S,x_F)`:

- `x_S=0→2`: low → high stored shear tension, using the causally smoothed stress and calibration-only robust stress quantiles.
- `x_F=0→2`: accumulation-dominant → release-dominant signed tension transfer.

For the dense 2 ms record, first take a causal 10-bin (`0.02 s`) mean of stress. Across a causal 50-bin (`0.10 s`) transfer window, let

`A(t)=sum(max(delta smoothed stress,0))`,

`R(t)=sum(max(-delta smoothed stress,0))`,

and

`x_F(t)=2 R(t)/(A(t)+R(t))`.

Thus `x_F=0` is a pure accumulation reference, `1` is equal local accumulation/release throughput, and `2` is a pure release reference. Total transfer activity `A+R` is retained separately; the ratio is not an energy total.

The four gradient mixtures retain the frozen orientation `Ab`, `aB`, `bA`, `Ba`. Their labels describe relation states, not earthquake types.

The higher Irrationality parent is calculated from the ordered circumference angle of `(x_S,x_F)`:

- `x_P`: finite/reused → open/resolving angular addresses;
- `x_R`: relation-determined → stochastic successor residual;
- `C(H)`: uncompressed multi-lag closure coherence.

## WHEN

The dense source remains in non-overlapping 2 ms bins. Calibration quantiles use only the first 80%. The independently marked main slip is the largest positive displacement increment.

Dense Irrationality-parent readings use causal 256-bin (`0.512 s`) windows ending every 16 bins (`0.032 s`). Parent address resolutions are `8,16,32,64,128`; the successor relation uses nine neighbours; closure lags are `1–64`.

For replication, each stress-drop event uses `2,048` source rows before and `512` after its independently detected stress drop. Dry and fluid media are normalized separately by their complete published stress records. Their causal smoothing and transfer widths are 31 and 101 source rows respectively. Replication parent windows contain 256 rows and end every 16.

## WHERE

Dense storage coordinate:

`x_S=clip(2*(stress-Q05_cal)/(Q95_cal-Q05_cal),0,2)`.

Replication uses the same formula on causally smoothed stress with Q05/Q95 fixed once per medium from the full published stress record. This prevents every event from being individually forced to span 0–2.

The tension-path circumference is

`z=atan2(x_F-1,x_S-1)/(2*pi) mod 1`.

Radius from `(1,1)` and total transfer activity remain visible.

## WHY

T363 asks whether the fault's tension channel—not its displacement movement—has the proposed Irrationality Di-ARA architecture: connection stored as tension, signed release at slip, and ordered handover into lower storage/reaccumulation.

## HOW

### Dense physical markers

- Main slip: largest positive displacement increment.
- Tension-release time: largest causal released-stress activity `R(t)`, chosen without the displacement label.
- Early reconnection: first return below the `x_F=1` ridge within `0.30 s` after main slip.
- Pre/post storage: median `x_S` in `[-0.10,-0.02] s` and `[+0.02,+0.10] s` relative to slip.

### Dense parent

Calculate `(x_P,x_R,C(H))` causally. The label-blind parent handover is the largest chronological Euclidean step in `(x_P,x_R)`. Retain its time, quadrant occupation and percentile among all parent steps.

### Controls

1. `100` same-value time shuffles jointly permute the stored and transfer coordinates, destroying order but preserving visited pairs.
2. Reverse chronology preserves the visited geometry but reverses traversal.
3. Storage-only sets `x_F=1`.
4. Signless-transfer sets `x_F=1` while retaining transfer activity separately; it removes accumulation/release orientation.
5. Wrong slip markers circularly shift the independent displacement marker by one quarter, one half and three quarters of the dense record. They do not change the tension path and test event-specific alignment only.

Real parent timing must improve on the median shuffles, reversal, both missing-coordinate controls and all wrong markers. Equality is not improvement.

### Replication events

Stress drops are source events separated by at least 1,000 rows with instantaneous stress fall of at least 5 MPa. This produces the published 10 dry and 5 fluid events.

A child tension handover is recovered when all conditions hold:

- at least three `(x_S,x_F)` quadrants each occupy at least 0.5% of the event window;
- median storage from rows `[-512,-32]` relative to the drop exceeds median storage from rows `[+32,+512]` by at least `0.25` ARA units;
- maximum `x_F` within ±100 rows of the drop is at least `1.5`;
- `x_F` returns below `1` within 512 rows after the drop.

An Irrationality-parent handover is recovered when at least two parent quadrants contain three windows each and its largest step ends within 128 source rows of the stress drop.

## FROZEN GATES

1. **Source and identity QA:** all published source hashes match; dense `x_S` and `x_F` are not forced complements (`abs(r)<0.98` outside ±0.1 s of slip); tension-release time lies within `0.10 s` of independently marked slip.
2. **Dense child tension handover:** at least three physical quadrants occupy at least 0.5% each; pre-slip storage exceeds post-slip storage by `≥0.25`; `x_F≥1.5` within ±0.1 s; and early reconnection occurs within 0.30 s.
3. **Dense Irrationality parent:** at least two parent quadrants contain at least three windows; the globally largest parent step lies within `0.512 s` of slip; and the parent step nearest the independently calculated tension-release time is in the top 1% of all parent steps.
4. **Chronology and marker specificity:** real parent timing error is strictly smaller than median shuffles, reversal, storage-only, signless-transfer and all three wrong slip markers.
5. **Repeated child tension handover:** at least 12/15 events pass, including at least 8/10 dry and 4/5 fluid.
6. **Repeated Irrationality-parent handover:** at least 12/15 events pass, including at least 8/10 dry and 4/5 fluid.

`SUPPORTED ON THIS PHYSICAL ARCHIVE` requires Gates 1–6. Child-level success cannot rescue a failed Irrationality-parent gate; a failed parent with passing child gates supports only the ordinary tension ARA realization.

## CHART CONTRACT

1. Dense stress/storage, transfer ratio/activity and displacement marker through slip.
2. Physical `(x_S,x_F)` 0–2 path with equal axes and quadrant labels.
3. Dense `(x_P,x_R)` parent path with fixed 0–2 axes and chronology.
4. Control timing errors with the real value highlighted.
5. All 15 child paths or event summaries separated by medium.
6. Child and parent replication gate matrix plus frozen gate table.
