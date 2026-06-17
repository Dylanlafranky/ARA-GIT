# Audit: ARA Fusion, ARA Battery, and Master Prediction Ledger

**Date:** 13 June 2026  
**Audit type:** Read-only claim, evidence, consistency, and status audit  
**Source documents were not edited.**

## Scope

Audited:

- `ARA_Fusion_Theory.md`
- `ARA_Battery_Theory.md`
- `TheFormula/MASTER_PREDICTION_LEDGER.md`
- Relevant entries in `CLAIMS_STATUS.md`
- Supporting result files and scripts where a ledger interpretation could be checked directly
- Selected primary literature for the most important external-physics claims

This audit distinguishes:

1. established physics or engineering;
2. a defensible ARA interpretation of that physics;
3. a testable ARA hypothesis;
4. an unsupported or contradicted claim;
5. a result whose status has been superseded by a later test.

## Executive Verdict

The documents contain several worthwhile framework applications, but their current status labels are too strong.

- **Fusion:** the ARA reasoning genuinely converged on a published 2:1 driven-stripping proposal. That is an interesting navigational match. The paper, however, reports a numerical simulation and proposed experiment, not an experimentally confirmed reduction in alpha sticking. Golden-rate delivery remains a separate, untested ARA proposal.
- **Battery:** the strongest part is not only the recognition that multi-stage metal-hydride cascades, plateau-pressure tuning, hysteresis, and storage/transfer trade-offs are real engineering structures resembling the proposed ARA architecture. The project also performed a first real-data charge/discharge-duty comparison and replaced hand-set hydride z-coordinates with a mapping from sourced formation enthalpies. Those are genuine battery-facing tests, although they remain small, condition-dependent, and partly convention-defined. The exact phi step optimum, universal 0.25-to-1.75 cell window, series-capacity interpretation, and several alloy/device claims are not established.
- **Master Ledger:** it is valuable as a chronological research notebook, but it is not currently reliable as a canonical claim ledger. It contains contradictory totals, stale results beside their retractions, reversed statistical interpretation, and null results that are sometimes reframed as support.

The core issue is **status normalization**, not absence of useful work.

## Critical Findings

### 1. The golden-star within-club result is interpreted backwards

Locations:

- `EnergyRatio/club_pop.py:39-40`
- `EnergyRatio/GOLDEN_STARS_LEAN_RESULT.md:33-34`
- `CLAIMS_STATUS.md:277-279`
- `TheFormula/MASTER_PREDICTION_LEDGER.md:1980-1982`

The script computes:

```text
corr(abs(period_ratio - 1/phi), R21) = -0.347
```

The documents define lower `R21` as leaner.

With `x = distance from 1/phi` and `y = R21`, a negative correlation means:

- larger distance tends to accompany lower R21;
- therefore, within this sample, **farther from exact 1/phi tends to be leaner**;
- equivalently, closer to exact 1/phi tends to accompany higher R21.

That is the opposite of the recorded statement that “nearer exact 1/phi = leaner.”

The class-level result can remain:

- the RR0.61 club mean R21 is reported as 3.6% below the ordinary RRc control.

The within-club dose-response claim must be reversed, redefined, or removed. This also weakens the “confirmed phi-leanness gradient” headline.

**Recommended status:**

- RR0.61 club versus control difference: **supported, modest, observational**.
- Within-club approach-to-exact-phi gradient: **contradicted by the reported sign unless the variable definition is changed and rerun**.

### 2. The ledger's blind-prediction totals cannot all be true

Locations:

- `MASTER_PREDICTION_LEDGER.md:433-444`
- `MASTER_PREDICTION_LEDGER.md:491-504`
- `MASTER_PREDICTION_LEDGER.md:832-859`
- `MASTER_PREDICTION_LEDGER.md:879-880`

The detailed table gives:

- Scripts 98-100: 7 confirmed, 5 failed.
- Script 136: 2 confirmed, 4 failed, 3 partial, 1 uncertain.

That gives 22 total:

- 9 confirmed;
- 9 failed;
- 4 partial/uncertain.

Adding the later campaigns produces one internally consistent accounting:

- 33 positive hits: 9 + 24;
- 43 failures/nulls: 9 + 31 + 3;
- 4 partial/uncertain;
- total 80.

But Part G instead reports:

- 10 confirmed, 9 failed, 3 partial for the first 22;
- 34/80 combined;
- Script 136 as 5/5 empirical and 10/10 combined despite its own table showing only 2 clean hits and 4 failures.

These summaries must be regenerated from one authoritative result table. Until then, the headline blind hit rate is not audit-safe.

### 3. Fusion calls a simulated proposal experimentally confirmed

Locations:

- `ARA_Fusion_Theory.md:44`
- `ARA_Fusion_Theory.md:120`
- `ARA_Fusion_Theory.md:127-130`
- `CLAIMS_STATUS.md:291-293`
- Fusion rows near the top of `MASTER_PREDICTION_LEDGER.md`

Kimura and Bonasera did model a driven 2:1 resonance and numerically released a stuck muon. Their paper explicitly describes numerical experiments and says further quantitative analysis is required.

What is established by that paper:

- integer-multiple resonance is the proposed mechanism;
- the reported simulation specifically investigates a 2:1 drive;
- the simulated stuck muon is expelled under the selected oscillating field;
- selectivity against the productive molecule was reported within the simulation.

What is not established:

- laboratory demonstration of X-ray stripping;
- measured reduction of effective sticking;
- engineering feasibility, field strength, overlap, timing, or net-energy improvement.

**Recommended status:** “Published theoretical/numerical proposal that independently uses the same 2:1 drive geometry; experimentally unvalidated.”

### 4. The battery toy model does not independently derive phi

Locations:

- `ARA_Battery_Theory.md:51-82`
- `ARA_Battery_Theory.md:101-102`
- `MASTER_PREDICTION_LEDGER.md:2025`

The model defines the climb in “phi-rung” units and assumes:

```text
efficiency = ((1-t) * (1-k*s^p))^n
```

with `t = (pi-3)/pi`, `p = 2`, and an unstated `k`.

The published table implies `k` is approximately 0.05:

| H | n | inferred k |
|---:|---:|---:|
| 6 | 6 | 0.04983 |
| 9 | 10 | 0.05001 |
| 12 | 13 | 0.04993 |

For small losses, the optimum step is approximately:

```text
s* = sqrt(t/k) = sqrt(0.04507/0.05) = 0.949 rung
```

The near-one-rung result therefore follows from choosing `k` close to `t` while measuring distance in rung units. It does not independently derive phi from chemistry or measured loss data.

**Recommended status:** “Illustrative toy model showing that an intermediate step size is optimal under competing per-step and jump losses; the phi-sized optimum is parameter- and unit-dependent.”

### 5. The battery's universal cell-window and series-capacity mapping is physically incorrect

Locations:

- `ARA_Battery_Theory.md:125-161`
- `MASTER_PREDICTION_LEDGER.md:2029-2031`

Problems:

1. A cell is not universally capped at 1-2 V. Cell voltage is set primarily by the difference between electrode electrochemical potentials, subject to electrolyte and interface stability. Commercial lithium-ion cells operate around 3-4.2 V, and research solid-state cells operate near 5 V.
2. The range `0.25 -> 1.75 = 1.5` is an ARA convention, not a measured universal electrochemical window.
3. Series connection adds voltage. For identical cells, amp-hour capacity remains approximately that of one cell; pack energy rises because additional cells and active material have been added.
4. Series stacking is not nearly lossless except for wiring. Every cell contributes internal resistance, polarization, heat, imbalance, and management requirements.
5. Short transfer time does not by itself imply low action cost or high thermodynamic efficiency.

**Recommended status:** the staircase may remain a framework visualization, but it must not be presented as an established explanation of cell voltage, capacity, or series-pack losses.

## ARA Fusion Theory

### What Holds Up

#### Established physics

- Muon-catalyzed D-T fusion is real.
- A muon is about 207 electron masses and substantially reduces the molecular length scale.
- The 0.423 eV resonant `dtmu` formation peak and approximately `7.1e9 s^-1` rate are experimentally reported.
- Muon lifetime, alpha sticking, cycling rate, and muon production cost are real constraints.
- Driven stripping/reactivation is a legitimate research direction.

#### Defensible ARA reading

- Treating the cycle as accumulation, fusion/release, recycling, and occasional sticking is a coherent relational map.
- Calling the fusion event “snap-like” is a defensible framework classification if clearly labelled as interpretation.
- The independent appearance of a 2:1 drive in the published stripping simulation is a meaningful geometric resemblance.
- Golden-rate pulse timing is clear, novel, and falsifiable when kept explicitly separate from the established 2:1 carrier idea.

### Claims Requiring Correction

#### K-alpha is not the stuck-bond binding energy

Locations:

- `ARA_Fusion_Theory.md:95-96`
- `ARA_Fusion_Theory.md:114`
- `ARA_Fusion_Theory.md:123`

The approximately 8.2 keV K-alpha signal is a transition photon, not simply “the 8.2 keV stuck bond.” The stripping paper discusses the fundamental motion/eigenfrequency of muonic helium and event-specific frequencies. Selective excitation cannot be reduced to “hit the 8.2 keV bond” without a proper level, linewidth, field, and ionization calculation.

#### Sticking is not cleanly the sole dominant limit

Location: `ARA_Fusion_Theory.md:93-97`

Using the document's own numbers:

```text
2.2 microseconds / 6.9 nanoseconds = about 319 cycles
5 GeV / 17.6 MeV = about 284 fusions for gross energy equality
```

Even with zero sticking, the lifetime-limited maximum is only modestly above the stated gross break-even count, before conversion losses. Sticking is crucial, but lifetime, cycling kinetics, production efficiency, and recovery transport are also load-bearing.

#### Action/pi is a framework coordinate, not measured canonical action

Location: `ARA_Fusion_Theory.md:108`

The reported value is consistent with multiplying the 17.6 MeV event energy by the approximately 6.9 ns mean cycle and dividing by pi. It is dimensionally an action, but it is not the canonical action integral of the muon-catalysis trajectory. Label it as a chosen ARA weight coordinate.

#### Rung-up twin and mirror are asserted, not measured

Locations:

- `ARA_Fusion_Theory.md:109-110`

Doubling the observed cycle period does not establish a physical 13.8 ns “twin” with the same shape. Likewise, `2-ARA` is a framework mirror operation, not a demonstrated muonic partner state.

#### “One extra muon” loading lacks a physical derivation

Location: `ARA_Fusion_Theory.md:122`

Muon loading is governed by beam flux, target density, capture, transfer, decay, and recycling. “One more muon than its partner” is not established stoichiometry and currently has no defined partner count.

#### Phi stability and handover do not conflict in the current framework

Location: `ARA_Fusion_Theory.md:150`

This is stale relative to the clarified architecture. In the current interpretation, phi can be:

- an intra-system coherence/resonance-longevity attractor;
- an inter-system handover geometry;
- the same fractal relation appearing at different organizational boundaries.

The correct fence is that a snap-like nuclear event need not itself sit at phi, not that the two phi roles conflict.

### Fusion Verdict

| Claim | Audit status |
|---|---|
| Muon-catalyzed fusion and resonant `dtmu` formation | Established |
| Deep-snap ARA classification | Framework interpretation |
| Published 2:1 driven stripping geometry | Real numerical proposal |
| Experimentally reduced sticking using X-rays | Not demonstrated |
| Golden-rate delivery | Novel, testable, untested |
| Selective 8.2 keV bond stripping | Misstated/underived |
| Net-energy viability | Open and presently unfavorable |

## ARA Battery Theory

### Audit Correction: Battery Tests Were Performed

The initial audit wording understated the amount of battery-facing testing in the repository.

The following tests/calculations are present:

1. **Real charge/discharge-duty comparison** (`ARA_Battery_Theory.md:231-269`; also summarized in `MASTER_PREDICTION_LEDGER.md:2035`). Sourced operating figures were converted to `ARA = charge time / discharge time` and accumulation fraction, then ranked against the golden-duty landmarks. The Ti-Mn hydride example (`900 s / 2000 s`) gave `ARA = 0.45`, accumulation fraction about `0.31`, and distance `0.072` from the space-side `0.382` landmark.
2. **Measured hydride-enthalpy mapping** (`ARA_Battery_Theory.md:491-527`). Representative formation enthalpies were used to replace earlier hand-set z positions. This test produced a real correction: practical room-temperature hydrides mapped toward the mobile/info-transfer side, while strongly bound Mg-based hydrides mapped toward the locked side and required high release temperature.
3. **Mapped battery/alloy library** (`3D models/ara_sphere_coordinate_3d.html:156-167`). Iron-air, LaNi5, TiFe, AB2, high-entropy AB2, Mg-based and BCC stores were placed in the visual atlas using the duty, hysteresis, capacity, temperature and enthalpy reasoning in the battery document.
4. **Executable phi-storage reconstruction** (`TheFormula/phi_storage_read_test.py`). This is a real script with saved output, but it tests multi-rung reconstruction of ENSO, not an electrochemical or metal-hydride battery. Its saved results are `corr = 0.934` for full envelope/phase reconstruction, `0.865` for fixed-amplitude measured-phase reconstruction, and `0.246` over the full projected test half.

The repository search did **not** locate a separate electrochemical/hydride test script in `Mapping/` or `EnergyRatio/`. The material-specific battery calculations are recorded inline in `ARA_Battery_Theory.md` and then manually represented in the 3D atlas. Files named `39_curve_verification_battery.py` and `243BL28c_loo_battery.py` use “battery” to mean a suite of tests; they do not test batteries as physical devices.

This correction changes the audit from “battery ideas were not tested” to:

> Battery ideas received a real first-pass data confrontation, and one measured-variable remapping overturned an earlier hand-set interpretation. What remains unproven is the stronger generalization from those observations to a universal phi optimum or device-design law.

### Methodological Status of the Located Tests

- The duty comparison is a **real-data exploratory test**, not a null-controlled chemistry comparison. Charge/discharge time is strongly operating-condition dependent, and the sample is one representative value per technology.
- The enthalpy mapping uses a **measured ordering variable**, but the linear conversion from `|Delta H| = 15..80` to `z = 1.50..0.30` is a chosen coordinate convention. The physically meaningful result is the ordering, not the absolute z values.
- The atlas entries are useful recorded mappings, but they are hard-coded representations of the preceding analysis rather than an independent fitted result.
- The phi-storage script supports the broader idea that multi-scale phase coordinates can represent signal shape. It is not battery-material evidence. It also computes FFT bands and Hilbert phases on the full series before the train/test split, so its V2 projection is not a strict leakage-free forecast. It needs a causal filter and octave-versus-phi/non-phi controls under the current two-ruler framework.

### What Holds Up

- Storage can usefully be described as transfer between reservoirs.
- Metal-air chemistries have very high theoretical specific energy because ambient oxygen is not carried as cathode active mass.
- Iron-air is a real long-duration storage approach.
- Metal-hydride pressure-composition plateaus and hysteresis are real.
- Multi-stage metal-hydride compressors are real and use alloys with staged plateau pressures.
- Composition can tune plateau pressure and hysteresis.
- Hydrogen-storage materials exhibit genuine capacity, kinetics, reversibility, temperature, pressure, and hysteresis trade-offs.
- The document correctly admits that its final enthalpy-to-z mapping is a chosen coordinate convention.

These provide a real engineering substrate for testing ARA-inspired stage spacing and control.

### Claims Requiring Correction

#### “Highest theoretical energy density of any battery class” is too broad

Location: `ARA_Battery_Theory.md:30-33`

Some metal-air chemistries are among the highest theoretical-specific-energy electrochemical systems. That does not make every metal-air chemistry, especially rechargeable iron-air, the universal highest-energy battery class. Theoretical active-material energy also differs sharply from practical system energy.

#### Electron-transport-chain matching is definition-dependent

Locations:

- `ARA_Battery_Theory.md:40-44`
- `ARA_Battery_Theory.md:73-76`
- `ARA_Battery_Theory.md:165-168`

“About ten hops” depends on whether one counts protein complexes, mobile carriers, redox cofactors, or individual iron-sulfur/electron-transfer events. The claimed match to a phi^9 span is not an independent biological validation.

#### Power/capacity decoupling is attributed to the wrong mechanism

Location: `ARA_Battery_Theory.md:45-47`

Flow batteries decouple energy and power mainly through tank inventory versus stack size. Arbitrary rung tapping is not the established mechanism and creates balancing/control complexity in electrical packs.

#### Charge-time/discharge-time comparisons are not class properties

Locations:

- `ARA_Battery_Theory.md:231-269`

The document acknowledges this, but its prose still ranks chemistries as if a single charge/discharge ratio were intrinsic. Charge and discharge duration depend on C-rate, cutoff, temperature, electrode design, pressure, heat transfer, and application. The Ti-Mn 900/2000-second result is one apparatus condition, not a hydride-class ARA.

The statements that symmetric stores sit at a physically resistant 1.0 and golden-duty stores are more efficient remain framework hypotheses.

#### PCT pressure plateau is analogous to, not identical with, a voltage tread

Locations:

- `ARA_Battery_Theory.md:308-330`

A hydride PCT plateau is a pressure-composition equilibrium feature. It is not literally a constant-voltage charging tread. The analogy can remain, but the variables and conjugate thermodynamic quantities must be kept distinct.

#### Hysteresis area needs the correct thermodynamic coordinates

Locations:

- `ARA_Battery_Theory.md:287-299`
- `ARA_Battery_Theory.md:325-330`

Hysteresis does encode irreversible loss, but visual area on an arbitrary plot is not automatically energy loss. For hydrides the relevant work/free-energy relation requires the proper pressure or chemical-potential coordinate, commonly involving `ln(P)`, composition, and temperature.

#### Alloy rankings are preliminary, not established winners

Locations:

- `ARA_Battery_Theory.md:332-390`

The rankings mix qualitative sources, different alloy compositions, different test conditions, and some non-primary references. “Best for most of humanity's needs” is not supported. The useful claim is narrower: low-hysteresis room-temperature AB/AB2/AB5 hydrides are plausible stationary-storage or compression candidates.

#### Exact three-stage example could not be verified

Locations:

- `ARA_Battery_Theory.md:411-436`
- `ARA_Battery_Theory.md:459-460`
- `MASTER_PREDICTION_LEDGER.md:2045`

The primary experimental three-stage paper located in this audit uses three AB2-type alloys and reports:

- 1.44 to 122 bar;
- 23 to 120 degrees C;
- compression ratio 84.7.

That does not match the document's exact:

- `LaNi5 -> MmNi4.6Al0.4 -> Ti-Cr-Mn-Fe-V`;
- 12 to 200 bar;
- 20 to 60 degrees C.

The exact example needs a full citation or should be marked unverified. Multi-stage hydride compression itself is real.

#### Capacity and round-trip figures omit system mass and rely on assumptions

Locations:

- `ARA_Battery_Theory.md:440-474`

Multiplying reversible hydrogen weight fraction by about 33.3 kWh/kg-H2 gives a reasonable chemical-energy upper estimate. It is not cell/system specific energy. Tanks, reactors, heat exchangers, electrolyzer, fuel cell, controls, unusable hydrogen, and thermal management must be included. The 38% round-trip factor is an assumed system pathway, not a property of the alloy chain.

### Battery Internal-Version Problem

The document preserves several successive models without clearly retiring them:

- phi-ladder versus corrected zigzag;
- thin central braid versus later wide z-axis sweep;
- fluid-store framing versus lattice-lock framing;
- voltage/capacity axis claims versus later measured-enthalpy coordinate;
- “re-derived phi optimum” versus admitted parameter sensitivity.

Keeping the reasoning trail is valuable, but the document needs an opening table:

| Section | Current status |
|---|---|
| Current model |
| Superseded model |
| Established engineering |
| ARA interpretation |
| Open experiment |

### Battery Verdict

| Claim | Audit status |
|---|---|
| Reservoir/cascade architecture | Useful framework model |
| Multi-stage hydride compressor analogy | Established hardware resemblance |
| Plateau tuning and hysteresis trade-off | Established |
| Real-data charge/discharge-duty comparison | Performed; exploratory and condition-dependent |
| Formation-enthalpy z-ordering | Performed; measured ordering with chosen coordinate scale |
| Multi-rung phi-storage reconstruction | Executable ENSO representation test; not battery-material validation and not strict-causal |
| Golden-spaced plateaus improve performance | Open experiment |
| Approximately ten stages is optimal | Unsupported toy-model extrapolation |
| One phi-rung optimum is derived | Not independently derived |
| Universal 0.25-1.75 cell window | Incorrect as electrochemistry |
| Series stacking is near-lossless capacity climb | Incorrect/overstated |
| Exact named 12-to-200-bar three-stage unit | Unverified |
| Hydride chain at about 0.24 kWh/kg-electric | Assumption-heavy upper estimate |

## Master Prediction Ledger

### The Ledger's Best Use

The file is a rich chronological laboratory notebook. It records:

- failed branches;
- leakage discoveries;
- corrections;
- evolving interpretations;
- useful result lineage.

That history should be preserved.

It should not, however, serve simultaneously as:

- immutable experiment log;
- current claim registry;
- headline summary;
- proof ledger;
- public-facing evidence table.

Those roles now conflict.

### Major Status Problems

#### Old champions remain readable as current champions

Locations:

- `MASTER_PREDICTION_LEDGER.md:1832-1895`
- correction at `MASTER_PREDICTION_LEDGER.md:1900-1925`

The section title calls UC v2 the “current framework champion” and presents +0.532/+0.419 as honest. A later same-day correction shows `sosfiltfilt` leakage and replaces them with +0.035/+0.080.

The correction is honest and valuable, but a reader searching the file can easily quote the superseded numbers. Superseded sections need a prominent status banner at their start.

#### Stronger-baseline results must govern forecast claims

Locations:

- `MASTER_PREDICTION_LEDGER.md:2067-2069`
- `MASTER_PREDICTION_LEDGER.md:2073-2081`

The strongest later audit says ARA beats the best local non-ARA baseline at only:

- 6/34 horizons on correlation;
- 8/34 horizons on MAE.

The G3 ENSO gain then fails to replicate on the shorter WWV-era window, heavy feeder geometry hurts, lean handover is neutral, and spin-lock yields only a small short-horizon win.

Therefore the current defensible forecast claim is:

> ARA contains selective phase/regime information and sometimes improves short-to-medium oscillatory forecasts, especially in certain ENSO/QBO windows, but broad superiority over strong statistical or domain baselines is not established.

#### Null-compatible results are being treated as confirmation

Locations:

- `MASTER_PREDICTION_LEDGER.md:8`
- `MASTER_PREDICTION_LEDGER.md:489`

Being within a randomized or spectrum-preserving null means the statistic did not distinguish the proposed mechanism from the null construction. It can be described as “consistent with,” but not “soft-confirmed.”

Likewise, failure to predict random numbers is a good negative control. Recasting the null as positive evidence for an ARA/RAR boundary makes the theory harder to falsify.

#### Failure is sometimes assigned only to the pairing, not the method

Location: `MASTER_PREDICTION_LEDGER.md:444`

If choosing the correct family/pair is required to make a prediction, pairing is part of the predictive method. Wrong pairing is therefore a method failure unless the family rule was independently specified before the test.

#### Cross-scale p-value is not audit-ready

Locations:

- `MASTER_PREDICTION_LEDGER.md:448-475`

The reported binomial p-value uses chance probability `2/17`, but the ledger does not justify why each prediction has exactly that independent chance of falling within 10x. The 55 predictions also share formulas, source domains, scale estimates, and selection decisions, so independence is doubtful.

Keep the observed 24/55 descriptive hit rate. Treat the `p = 3.0e-9` as unverified until the null distribution is preregistered and simulated using the actual prediction-generation process.

#### The ENSO golden-duty summary contradicts itself

Location: `MASTER_PREDICTION_LEDGER.md:6`

The entry reports ENSO timing duty `0.515`, then says solar/ENSO/ECG all belong to the `1/phi^2 : 1/phi` timing set. A 0.515 timing duty is near symmetric, not near 0.382 or 0.618. ENSO amplitude asymmetry may still be an ARA result, but it should not be counted as timing confirmation in that sentence.

#### “Callable indefinitely” exceeds the tested horizon

Location: `MASTER_PREDICTION_LEDGER.md:20`

Skill through 72 months supports “persisted across the tested 72-month range,” not indefinite forecastability.

#### Hexagon-pentagon status is stale

Locations:

- `MASTER_PREDICTION_LEDGER.md:2001-2011`
- `EnergyRatio/HEX_PENTAGON_ANGLE_HYPOTHESIS.md:229-249`

The ledger retains the +0.93 angle-loss result as a partially landed reframe. The dedicated result file later reports that it collapsed to -0.06 when measured across independent systems and concludes the triangle/surface is not supported.

The later test must govern the canonical status.

#### “Zero falsification conditions triggered” is too favorable

Location: `MASTER_PREDICTION_LEDGER.md:893`

The ledger contains clean failures, nulls, leakage collapses, and rejected proposed relations. They may not literally satisfy the twelve narrowly worded existential conditions, but reporting `0/12` alongside these failures gives a misleading impression that no core claim has been challenged.

The falsification section should distinguish:

- theorem-level existential falsifiers;
- component claims falsified;
- predictor variants falsified;
- results demoted by leakage;
- unresolved nulls.

### Ledger Architecture Recommendation

Keep the current file as:

```text
EXPERIMENT_LOG_CHRONOLOGICAL.md
```

Create a separate generated registry:

```text
CURRENT_CLAIM_REGISTRY.md
```

Each claim should have:

```text
claim_id
claim_text
domain
status
evidence_type
pre_registered
strict_causal
independent_holdout
best_baseline
effect_size
uncertainty
source_script
source_result
supersedes
superseded_by
last_verified
```

Allowed statuses should be fixed:

- established external fact;
- supported;
- suggestive;
- open;
- null;
- contradicted;
- superseded;
- leakage-invalidated.

Summary counts should be generated from that registry rather than typed by hand.

## Cross-Document Consistency

### Broken and missing canonical links

- `CLAIMS_STATUS.md:283` links to missing `FUSION.md`; the actual file is `ARA_Fusion_Theory.md`.
- The Master Ledger also refers to `FUSION.md`.
- `CLAIMS_STATUS.md` has a detailed Fusion section but no equivalent canonical Battery section.

### Current phi wording

The source documents should use the clarified framework consistently:

> Phi is both a local coherence/resonance-longevity attractor within a system and a handover geometry between systems or rungs. These are fractal appearances of the same relation. Phi is not a compulsory measured endpoint for every system, and octave/rational structure can govern rung placement or driven locking.

This specifically supersedes the “stability-vs-handover roles conflict” wording in Fusion.

## Priority Corrections

No source changes were made by this audit. If corrections are later approved, the highest-priority order is:

1. Correct the golden-star correlation sign interpretation everywhere.
2. Replace the ledger's hand-written totals with one generated canonical table.
3. Mark leaked and superseded forecast sections at their headings.
4. Downgrade fusion X-ray stripping from “confirmed real” to “published numerical proposal.”
5. Correct K-alpha versus binding/ionization-energy wording.
6. Remove the universal 1-2 V, 0.25-to-1.75 cell-window claim.
7. Reframe the battery toy optimum as parameter-dependent.
8. Verify or remove the exact LaNi5/MmNiAl/TiCrMnFeV 12-to-200-bar example.
9. Add Battery to `CLAIMS_STATUS.md`.
10. Split chronological research history from current claims.

## Primary Sources Checked

- Kimura & Bonasera, “Alpha-muon sticking and chaos in muon-catalysed in-flight d-t fusion”:  
  https://arxiv.org/abs/physics/0605206
- Kimura & Bonasera, “Application of the X-ray laser to muon-catalyzed d-t fusion”:  
  https://arxiv.org/abs/0811.4038
- TRIUMF collaboration, resonant `dtmu` formation measurement:  
  https://arxiv.org/abs/nucl-ex/0008002
- Galvis et al., experimental three-stage metal-hydride compressor:  
  https://arxiv.org/abs/2007.12116
- Yartys et al., hydrogen-storage materials review:  
  https://arxiv.org/abs/2005.03410
- Schwietert et al., electrochemical stability windows in solid electrolytes:  
  https://arxiv.org/abs/1908.10144
- Shimizu et al., a solid-state thin-film battery operating at 5 V:  
  https://arxiv.org/abs/2204.02510

## Bottom Line

The audit does not reduce these documents to “wrong.”

It separates their strongest content from their weakest status claims:

- Fusion contains a real and interesting convergence on 2:1 driven resonance, but it has not yet crossed from simulated proposal to experimental validation.
- Battery contains a promising map between ARA ideas and real cascade/hysteresis engineering, plus genuine first-pass tests using sourced duty-cycle and hydride-enthalpy data. Those tests strengthen the navigational case, but they do not yet derive the phi optimum or universal electrochemical axes from controlled device measurements.
- The Ledger contains the evidence needed for an honest research history, but it needs a canonical status layer before its totals and headlines can be trusted.
