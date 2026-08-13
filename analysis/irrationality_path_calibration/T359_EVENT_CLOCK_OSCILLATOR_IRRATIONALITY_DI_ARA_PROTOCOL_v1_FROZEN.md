# T359 frozen protocol — event-clock oscillator Irrationality Di-ARA

**Frozen:** 12 August 2026, before event extraction and outcome scoring.  
**Seed:** `3590812`  
**Source archive:** local byte-identical copy of Zenodo record 15122129 (`T358_SOURCE_DATA.zip`, expected MD5 `abe81a3631481b58977925daf453ede5`).

## 1. Physical records

Coupled sweep:

| ΔR (ohm) | raw file |
|---:|---|
| 0 | `oc091818_28.lvm` |
| 50 | `oc091818_39.lvm` |
| 100 | `oc091818_41.lvm` |
| 150 | `oc091818_42.lvm` |
| 170 | `oc091818_43.lvm` |
| 190 | `oc091818_45.lvm` |
| 240 | `oc091818_46.lvm` |
| 290 | `oc091818_50.lvm` |
| 340 | `oc091818_51.lvm` |

Uncoupled detuned control: population-A channels from `oc032118_4.lvm` (1000 ohm) and population-B channels from `oc032118_8.lvm` (1150 ohm), aligned by fractional record time.

Sampling is 200 Hz. The first 10 seconds are excluded before thresholds or events are defined. Oscillator pair `p=0…39` means parent column `p` and child column `40+p`.

## 2. Frozen raw event clock

For each channel independently, using only its retained raw-current samples:

1. Let `L=Q35(current)` and `U=Q65(current)`.
2. The detector is armed after a sample is at or below `L`.
3. Once armed, the first upward crossing from below `U` to at or above `U` is one event; disarm until `L` is reached again.
4. Between consecutive events `e_i,e_{i+1}`, assign unwrapped phase
   `u(t)=i+(t-e_i)/(e_{i+1}-e_i)`.
5. Extrapolate only the leading and trailing partial interval using the first and last observed event duration. The ARA diameter position is `2*(u mod 1)`.

This makes phase direction monotone by construction but does not force cycle duration, cross-channel closure, address reuse, history predictability or one-cycle return.

## 3. Clock QA prerequisite (G0)

The T359 physical interpretation is valid only if every one of the 11 source records satisfies all of the following at the **record median across 80 channels**:

- at least 30 registered events;
- median event-to-event duration in `[1.5,4.0]` seconds;
- at least 85% of event intervals in `[1.5,4.0]` seconds;
- zero adjacent-step backtracking in the constructed unwrapped phase.

If G0 fails, G1-G6 remain arithmetically reported but the physical question is labelled inconclusive.

## 4. Parent/child sampling

At each parent oscillator's monotone clock, sample times are placed at phase fractions `0,1/8,…,7/8` for every complete parent cycle. The matched child event phase is interpolated at those physical times. The retained child sequence is `z=(u_child mod 1)`.

Use non-overlapping windows of 32 readings: four parent cycles × eight landmarks. The first usable window begins after the 10-second exclusion and the first complete parent cycle.

## 5. Frozen ARA coordinates

The mathematical instrument is unchanged from T358/T357:

- `x_P`: twice the occupied-bin log slope at 4, 8, 16 and 32 bins.
- `x_R`: twice the ratio of past-only `k=3` circular nearest-neighbour successor loss to circular-mean null loss, clipped to `[0,2]`.
- `C(H)`: circular return coherence and signed miss for lags 1 through 16.
- One parent cycle is lag 8.
- Closure: `rho_8 ≥ 0.80` and `|miss_8| ≤ 0.03` turns.
- Coherent non-closure: `rho_8 ≥ 0.80`, `|miss_8| > 0.03`, and at least one lag with `rho ≥ 0.80`.

Forty matched pairs are summarized inside each physical record. They are not counted as 40 independent experiments.

## 6. Controls

- **Shuffle:** seeded permutation within each 32-reading window.
- **Reverse:** exact reversal of each chronological window.
- **Wrong record:** same parent times, but the matched child column is read from the next detuning record in the fixed cyclic order `0→50→100→150→170→190→240→290→340→0`, aligned by fractional record time.
- **Uncoupled detuned:** 1000-ohm parent and 1150-ohm child records aligned by fractional time.

## 7. Frozen outcome gates

- **G1 — closure reference:** at 170 ohm, record medians have `x_P<1`, `x_R<1`, `rho_8≥0.80`, `|miss_8|≤0.03`, and at least 60% of matched pairs close in at least half their windows.
- **G2 — coherent non-closure:** at least 3/7 candidates `{50,100,150,190,240,290,340}` have `x_R<1.25`, `rho_8≥0.80`, `|miss_8|>0.03`, and at least 40% of pairs coherently non-close in at least half their windows.
- **G3 — chronology:** in at least 4/7 candidates, shuffle raises `x_R` by at least 0.25 and lowers best return coherence by at least 0.15; `|Δx_P|≤0.02` for every coupled record.
- **G4 — coupling specificity:** at least 4/7 candidates exceed the uncoupled detuned control by at least 0.15 in either lower `x_R` or higher best coherence, and the candidate median does so as a group.
- **G5 — lineage:** in at least 4/7 candidates, wrong-record substitution worsens either `x_R` or best coherence by at least 0.15.
- **G6 — reversal:** across all nine coupled records, maximum `|Δx_P|≤0.02`, maximum unsigned best-coherence change `≤0.05`, and at least seven records reverse orientation to within 0.02 turns.

Complete support requires G0 and all G1-G6. Partial passes are reported but do not rescue failed gates.

## 8. Required artifacts

- claim and protocol plus SHA-256 sidecars;
- raw-clock QA table;
- window, pair and record summaries;
- compact closure-history summary;
- frozen-gate table and JSON result;
- visual diagnostic showing the 0–2 paths and QA;
- independent validator that does not import the analysis program;
- concise report and reproduction commands.
