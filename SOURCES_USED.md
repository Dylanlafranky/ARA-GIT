# SOURCES USED

Repository bibliography / provenance register for `ARA-GIT`.

Date compiled: 2026-07-01
Scope: active repo content first (`README`, `CLAIMS_STATUS`, `MASTER_PREDICTION_LEDGER`, `analysis/`, `Mapping/`, `EnergyRatio/`, `TheFormula/`, `LLM/`, and supporting docs). Archived materials are noted where relevant, but not yet fully normalized.

This is intentionally written as a **provenance register** rather than a fake-perfect journal bibliography. Some parts of the repo already contain full citations or DOIs; other parts only name a source family, dataset, or paper shorthand. Where the repo only gives partial metadata, this document keeps that limitation visible and points to the exact local files that use the source.

## Citation standard used here

Each entry tries to answer four questions:

1. What is the source?
2. What kind of source is it? (dataset, benchmark feed, paper, textbook, review, official reference)
3. Where in the repo is it used?
4. Is the citation status complete or does it still need normalization?

Status labels:

- `complete`: DOI / URL / source family is explicit enough to recover reliably
- `partial`: named source is clear, but full bibliographic details should still be normalized
- `needs normalization`: source is referred to indirectly or informally and should be upgraded before publication

---

## 1. Repository-level citation

| Source | Kind | Used in | Status | Notes |
|---|---|---|---|---|
| Zenodo DOI `10.5281/zenodo.19653363` | repo release DOI | `README.md` | complete | Canonical cite for the repository itself. |

---

## 2. Core public data platforms and benchmark feeds

These are the main external data families the repo repeatedly uses across mapping, prediction, and cross-system tests.

| Source | Kind | Used in | Status | Notes |
|---|---|---|---|---|
| NOAA PSL Nino 3.4 monthly anomalies / long anomaly series | climate time series | `ara_framework.py`, `README.md`, `CLAIMS_STATUS.md`, `MASTER_PREDICTION_LEDGER.md`, `TheFormula/01`, `TheFormula/02`, `TheFormula/13`, `TheFormula/16`, `Retrodiction/` | complete | Core ENSO target series. Used for canonical predictor, direction tests, shape transfer, and forecast-of-record work. |
| NOAA PMEL / TAO / GTMBA Warm Water Volume (WWV) | ocean heat-content / feeder series | `TheFormula/Claude4.8/SOURCES.md`, `MASTER_PREDICTION_LEDGER.md`, `TheFormula/14`, `TheFormula/16`, `TheFormula/19` | complete | Primary ENSO "driver-below" / recharge reservoir feed. |
| NOAA climate indices: SOI, PDO, AMO, TNA, IOD / DMI, QBO-related feeds | climate index feeds | `MASTER_PREDICTION_LEDGER.md`, `CLAIMS_STATUS.md`, `TheFormula/01`, `TheFormula/02`, `TheFormula/13`, `TheFormula/14`, `Retrodiction/` | partial | Widely used in ENSO feeder tests and five-axis neighborhood work. Exact per-file URLs should be normalized in a later pass. |
| NOAA / CPC / PSL QBO monthly series (30 mb and related levels) | stratospheric oscillation time series | `CLAIMS_STATUS.md`, `MASTER_PREDICTION_LEDGER.md`, `TheFormula/MULTI_SYSTEM_PREDICTION_STACK_RESULT.md`, `TheFormula/ARA_FORECAST_STANDARD_BASELINE_COMPARISON_RESULT.md`, `TheFormula/ARA_G3_SPHERE_NATIVE_QBO_RESULT.md` | partial | QBO is a headline self-forecast and concentration-rule comparison system. Exact feed URL / level selection should be normalized. |
| NASA JPL Horizons | ephemeris / orbital feed | `MASTER_PREDICTION_LEDGER.md`, `THE_FRAMEWORK_FORMULATION.md`, `TheFormula/01`, `TheFormula/13` | partial | Used for Moon / orbital element feeder tests. Source family explicit; exact query snapshots should be recorded if these become headline claims. |
| SILSO sunspot number archive | solar time series | `analysis/solar/analyze_sunspots.py`, `CLAIMS_STATUS.md`, `MASTER_PREDICTION_LEDGER.md`, `SOLAR_FLYWHEEL_RESULT.md`, `TheFormula/12`, `TheFormula/13`, `TheFormula/14` | complete | `analysis/solar/analyze_sunspots.py` fetches `https://sidc.be/SILSO/DATA/SN_m_tot_V2.0.txt`. |
| PhysioNet - Normal Sinus Rhythm RR Interval Database (NSRDB; e.g. `nsr001`, `nsr050`) | ECG / RR dataset | `README.md`, `CLAIMS_STATUS.md`, `MASTER_PREDICTION_LEDGER.md`, `TheFormula/01`, `TheFormula/02`, `TWOBAND_ECG_HORIZON_LADDER_RESULT.md` | complete | Core external heart / RR source for many formula and mapping tests. |
| PhysioNet - Fantasia | ECG + respiration | `analysis/breath/BREATHING_PHI_TEST.md`, `TWOBAND_ECG_HORIZON_LADDER_RESULT.md`, `TheFormula/12` | complete | Used for breathing / cardiorespiratory coupling and two-band horizon work. |
| PhysioNet - Apnea-ECG | ECG + respiration + oxygen context | `TWOBAND_ECG_HORIZON_LADDER_RESULT.md`, `TheFormula/12` | complete | Used in heart horizon and apnea-related coupling work. |
| PhysioNet / MIT-BIH Polysomnographic Database (`slpdb`) | sleep physiology / EEG / ECG / BP / respiration | `TWOBAND_ECG_HORIZON_LADDER_RESULT.md`, `Mapping/eeg_ara_test.py`, `Mapping/ARA_OVER2_AUDIT.md`, `TheFormula/12` | complete | Used for EEG band ARA, heart driver ladder, and sleep-state tests. |
| PhysioNet - gaitndd | gait force / gait cycle dataset | `analysis/gait/analyze_gait_phi.py`, `analysis/gait/analyze_running_phi.py`, `Mapping/README.md`, `Mapping/build_mapping_extensions.py` | complete | Used for measured walking baseline and gait atlas nodes. |
| PhysioNet - Big Ideas Lab Glycemic Variability dataset | CGM dataset | `analysis/cgm/analyze_cgm_phi.py`, `analysis/cgm/CGM_ARA_RESULT.md` | complete | Healthy non-diabetic CGM arm. |
| D1NAMO (Zenodo `5651217`) | CGM / T1D dataset | `analysis/cgm/analyze_cgm_phi.py`, `analysis/cgm/CGM_ARA_RESULT.md` | complete | T1D CGM comparison arm. |
| NSIDC monthly Arctic sea ice extent / concentration products | cryosphere time series | `CLAIMS_STATUS.md`, `MASTER_PREDICTION_LEDGER.md`, `TheFormula/MULTI_SYSTEM_PREDICTION_STACK_RESULT.md`, `TheFormula/ARA_FORECAST_STANDARD_BASELINE_COMPARISON_RESULT.md` | partial | Used in the sea-ice self-forecast and stronger-baseline comparison claims. Exact NSIDC product / processing path should be normalized. |
| CDC ILINet via Delphi Epidata | influenza surveillance time series | `CLAIMS_STATUS.md`, `MASTER_PREDICTION_LEDGER.md`, `TheFormula/MULTI_SYSTEM_PREDICTION_STACK_RESULT.md`, `TheFormula/ARA_FORECAST_STANDARD_BASELINE_COMPARISON_RESULT.md` | complete | Used for seasonal influenza self-forecast and local-baseline comparison. |
| FRED retail series `RSXFSN` (advance retail sales, NSA) | economic time series | `MASTER_PREDICTION_LEDGER.md`, `TheFormula/MULTI_SYSTEM_PREDICTION_STACK_RESULT.md`, `TheFormula/ARA_FORECAST_STANDARD_BASELINE_COMPARISON_RESULT.md` | complete | Used for retail / holiday-cycle self-forecast after causal detrending. |
| NOAA GML / Scripps Mauna Loa CO2 monthly record | atmospheric CO2 time series | `MASTER_PREDICTION_LEDGER.md`, `TheFormula/MULTI_SYSTEM_PREDICTION_STACK_RESULT.md` | partial | Included as a trend-dominated self-forecast control; explicitly flagged in-repo as not strong evidence for ARA forecasting. |
| PAHO Brazil dengue surveillance series | epidemiology time series | `MASTER_PREDICTION_LEDGER.md`, `TheFormula/MULTI_SYSTEM_PREDICTION_STACK_RESULT.md` | partial | Used in a weaker exploratory dengue self-forecast branch; excluded from the core public forecasting claim. |
| PhysioNet / MIMIC | ICU physiology dataset | `CLAIMS_STATUS.md`, `MIMIC_COMBINED_LOCK_RESULT.md`, `TheFormula/12` | partial | Source family explicit; exact MIMIC waveform subset and cohort should be normalized in a future pass. |
| MNE Sample dataset | EEG dataset | `analysis/eeg/analyze_all_bands.py`, `analysis/eeg/analyze_eeg.py` | complete | Accessed through MNE / NeuroKit2 tooling. |
| NeuroKit2 demo physiological datasets | toolkit-wrapped dataset source | `analysis/breath/analyze_breath.py`, `analysis/cardiac/cardiac_ara_analysis.py`, `analysis/eeg/analyze_eeg.py` | partial | Wrapper/tool source is explicit; underlying dataset identity should be recorded where results are kept. |
| dynamicslab MultiArm-Pendulum | experimental pendulum benchmark dataset | `analysis/PENDULUM_ARA_RESULT.md`, `analysis/PENDULUM_DRIVEN_ARA_RESULT.md`, `analysis/pendulum_scripts/README.md` | complete | GitHub dataset plus Zenodo DOI `10.5281/zenodo.6633719`; associated paper arXiv:2205.06231 is cited in the pendulum README. |
| USGS NWIS / Water Services | river discharge time series | `analysis/watershed/analyze_hydrographs.py` | complete | Used for hydrograph rise/fall / watershed tests. |
| Figshare nasal cycle dataset (`10.6084/m9.figshare.3807564`) | nasal airflow dataset | `ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md` | complete | Used in nasal laterality / ENSO coupled-geometry tests. |
| PLOS ONE nasal cycle paper (`10.1371/journal.pone.0162918`) | paper backing nasal dataset | `ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md` | complete | Context / interpretation for nasal-cycle dataset. |
| Kepler light curves via MAST / `lightkurve` | stellar photometry dataset | `CLAIMS_STATUS.md`, `MASTER_PREDICTION_LEDGER.md`, `EnergyRatio/GOLDEN_STARS_LEAN_RESULT.md`, `EnergyRatio/club_lean.py` | complete | Used for the golden-stars leanness result on real Kepler RRc light curves. |
| OGLE-IV RRd / Cepheid catalogs and `RRc.dat` | stellar variability catalog | `CLAIMS_STATUS.md`, `MASTER_PREDICTION_LEDGER.md`, `EnergyRatio/GOLDEN_STARS_LEAN_RESULT.md` | partial | Used to define the ordinary double-mode comparison population and RRc control set in the stellar leanness test. |
| Netzel & Smolec (2019), RR0.61 census, `J/MNRAS/487/5584` | stellar variability paper/catalog | `CLAIMS_STATUS.md`, `MASTER_PREDICTION_LEDGER.md`, `EnergyRatio/GOLDEN_STARS_LEAN_RESULT.md` | complete | Population-scale RR0.61 / near-1/phi comparison arm for the stellar leanness claim. |

---

## 3. Analysis folder: source-to-test map

### 3.1 Earth / climate / geophysics analysis

Primary file: `analysis/earth/earth_ara_analysis.py`

| Source | Used for | Status |
|---|---|---|
| OpenSnow; Wikipedia "diurnal temperature variation"; Met Office | diurnal thermal cycle | partial |
| Coastal Wiki; LibreTexts coastal dynamics 5.7.4; NOAA tidal currents | tidal asymmetry cycle | partial |
| NOAA water cycle education; USGS water science; Wikipedia water cycle | atmospheric water cycle | partial |
| NOAA Climate.gov; Li 2024 GRL on ENSO asymmetry | ENSO accumulation/release asymmetry | partial |
| Wikipedia seasonal lag; NOAA; Wang 2021 GRL changing season lengths | seasonal thermal cycle | partial |
| Archer 2009 Annual Review; Harde 2017; NASA Earth Observatory | carbon cycle timing | partial |
| National Academies / volcanic references; Geology 2022 Popocatepetl recharge; Kolumbo chamber study | volcanic recharge/eruption timing | partial |
| Wikipedia / Britannica / Kuhlbrodt 2007 Reviews of Geophysics | AMOC / thermohaline circulation | partial |
| NASA Milankovitch overview; Wikipedia; RealClimate | glaciation/deglaciation timing | partial |
| Wikipedia geomagnetic reversal; Nature 2005 structural requirements | geomagnetic dynamo / reversal timing | partial |

### 3.2 Hydrogen / atomic physics analysis

Primary file: `analysis/hydrogen/hydrogen_ara_analysis.py`

| Source | Used for | Status |
|---|---|---|
| NIST Atomic Spectra Database v5.11 | lifetimes, transition rates, energy timings | complete |
| CODATA / Bohr-model constants | ground-state orbital timing estimate | partial |
| Bethe & Salpeter (1957), *Quantum Mechanics of One- and Two-Electron Atoms* | hydrogen transitions / cascade framing | partial |
| Peebles (1968) | cosmological recombination bottleneck reference | partial |
| Ewen & Purcell (1951) | 21-cm detection context | partial |

### 3.3 Neuron / electrophysiology analysis

Primary file: `analysis/neuron/neuron_ara_analysis.py`

| Source | Used for | Status |
|---|---|---|
| Hodgkin & Huxley (1952), *J Physiol* | AP rise/fall timing | partial |
| Kandel et al., *Principles of Neural Science* (6th ed.) | AP duration, refractory framing | partial |
| Bean (2007), *Nature Reviews Neuroscience* | AP kinetics | partial |
| Sudhof (2013), *Neuron* | vesicle cycle timing | partial |
| Koch (1999), *Biophysics of Computation* | membrane time constant | partial |
| Attwell & Laughlin (2001), *J Cereb Blood Flow Metab* | Na/K recovery energetic timing | partial |
| Hille, *Ion Channels of Excitable Membranes* | refractory / channel gating support | partial |

### 3.4 Gait / locomotion analysis

Primary files: `analysis/gait/analyze_gait_phi.py`, `analysis/gait/analyze_running_phi.py`, `GAIT_LOCOMOTION_ARC.md`

| Source | Used for | Status |
|---|---|---|
| PhysioNet gaitndd | measured healthy walking baseline | complete |
| Novacheck (1998), *Gait & Posture* | walking-to-running temporal fractions | partial |
| Weyand et al. (2000), *J Appl Physiol* | contact/flight timing vs speed | partial |
| Riley et al. (2008), *Med Sci Sports Exerc* | walk/run transition and running temporal data | partial |
| Mann & Hagy (1980), *Am J Sports Med* | sprinting temporal parameters | partial |
| Schache et al. (2012), *Med Sci Sports Exerc* | systematic running-speed data | partial |
| Kram & Taylor (1990), *Nature* | contact time vs metabolic cost | partial |
| Keller et al. (1996), *Clin Biomech* | ground-reaction-force / speed relation | partial |
| Orendurff et al. (2008), *Prosthet Orthot Int* | very slow walking timing | partial |

### 3.5 CGM / glucose analysis

Primary files: `analysis/cgm/CGM_ARA_RESULT.md`, `analysis/cgm/cgm_ara_run.py`

| Source | Used for | Status |
|---|---|---|
| PhysioNet Big Ideas Lab Glycemic Variability Dataset | healthy CGM arm | complete |
| D1NAMO (Zenodo 5651217) | T1D CGM arm | complete |

Note: `analysis/cgm/analyze_cgm_phi.py` is explicitly quarantined in-file as framework-unfaithful and should not be used as a phi claim source.

### 3.6 Pendulum analysis

Primary files: `analysis/PENDULUM_ARA_RESULT.md`, `analysis/PENDULUM_DRIVEN_ARA_RESULT.md`, `analysis/pendulum_scripts/README.md`

| Source | Used for | Status |
|---|---|---|
| dynamicslab MultiArm-Pendulum GitHub dataset | free-swing and driven pendulum runs | complete |
| Zenodo DOI `10.5281/zenodo.6633719` | citable pendulum archive | complete |
| Kaheman et al. (2022), arXiv:2205.06231 | benchmark paper context | partial |

### 3.7 Solar analysis

Primary file: `analysis/solar/analyze_sunspots.py`

| Source | Used for | Status |
|---|---|---|
| SILSO monthly sunspot number archive | solar cycle ARA and solar self-forecast work | complete |

### 3.8 Watershed / river analysis

Primary file: `analysis/watershed/analyze_hydrographs.py`

| Source | Used for | Status |
|---|---|---|
| USGS NWIS instantaneous discharge service (`parameterCd=00060`) | natural vs managed hydrographs | complete |

### 3.9 Vertical rocks / sediment transport

Primary files: `analysis/vertical_rocks/ROUSE_ARA_RESULT.md`, `analysis/vertical_rocks/rouse_ara_test.py`

| Source | Used for | Status |
|---|---|---|
| Classical Rouse sediment transport framing | sediment transport ARA bridge / master-collapse work | needs normalization |
| Additional morphology / rock-shape references named in local vertical_rocks files | staircase / shape / rotation analyses | needs normalization |

Note: this folder should get its own future source cleanup pass. Its methodology is interesting, but the citations are not yet normalized to the same standard as the cleaner physiology/climate folders.

---

## 4. Mapping folder: source-to-test map

| Source | Used in | Status | Notes |
|---|---|---|---|
| PhysioNet slpdb `slp01a`, EEG C4-A1 | `Mapping/eeg_ara_test.py`, `Mapping/ARA_OVER2_AUDIT.md` | complete | Real EEG rise/decay remeasurement. |
| Hodgkin-Huxley 1952 | `Mapping/neural_ara_test.py`, `Mapping/ARA_OVER2_AUDIT.md` | partial | Used to fix over-2 neural spike placements. |
| NIST Atomic Spectra Database | `Mapping/quantum_fluorescence_ara_test.py`, `Mapping/precision_action_ladder_test.py` | complete | Quantum fluorescence and action-ladder work. |
| PhysioNet gaitndd | `Mapping/build_mapping_extensions.py`, `Mapping/README.md` | complete | Gait extension nodes. |
| NOAA station / tidal / QBO / MJO feeds | `Mapping/build_mapping_extensions.py`, `Mapping/ara_mapping_extensions.json` | partial | Mapping notes refer to NOAA-derived windows and saved analyses. |
| AAVSO / popastro Cepheid skewness references | `Mapping/ARA_OVER2_AUDIT.md` | partial | Used for Cepheid reclassification note. |
| MAGIC 2016 Crab pulse-width reference | `Mapping/ARA_OVER2_AUDIT.md` | partial | Used for Crab emission duty-cycle correction. |

---

## 5. TheFormula folder: source families used by prediction threads

TheFormula contains many scripts, but the source families are surprisingly concentrated. The same few external data platforms are reused across most forecasting tests.

| Source family | Main threads / files | Status | Notes |
|---|---|---|---|
| NOAA PSL Nino 3.4 and related climate indices | `TheFormula/01`, `02`, `05`, `06`, `07`, `09`, `10`, `13`, `14`, `16`, `18`, `19`, `Claude4.8/` | complete/partial | Core ENSO target and feeder ecosystem. Exact per-index URLs still need normalization in some scripts. |
| NOAA PMEL TAO / WWV | `TheFormula/14`, `16`, `19`, `Claude4.8/SOURCES.md` | complete | Main external reservoir / recharge series. |
| JPL Horizons | `TheFormula/01`, `13`, some headline claims in `MASTER_PREDICTION_LEDGER.md` | partial | Moon / orbital element feeders. |
| PhysioNet NSRDB / RR data | `TheFormula/01`, `02`, `06`, `11`, `16` | complete | ECG template, topology, and formula-across-systems work. |
| PhysioNet Fantasia / Apnea-ECG / slpdb / MIMIC | `TheFormula/08`, `11`, `12` | complete/partial | Heart horizon, oxygen/BP/respiration driver ladder, and ceiling work. |
| SILSO monthly sunspot numbers | `TheFormula/12`, `13`, `14`, solar flywheel claims in root docs | complete | Solar self-forecast and cross-system comparison. |
| Figshare/PLOS nasal cycle data | `TheFormula/08`, `ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md` | complete | Coupled-geometry transfer branch. |
| NSIDC sea ice, CDC/Delphi ILINet, FRED retail, NOAA/Scripps CO2, PAHO dengue, Big Ideas / D1NAMO CGM | `TheFormula/13`, `TheFormula/MULTI_SYSTEM_PREDICTION_STACK_RESULT.md`, `TheFormula/ARA_FORECAST_STANDARD_BASELINE_COMPARISON_RESULT.md` | partial/complete | These are the multi-system self-forecast and stronger-baseline comparison series introduced by the claim files and June 2026 stack tests. |
| Kepler/MAST, OGLE-IV, Netzel & Smolec RR0.61 census | `EnergyRatio/GOLDEN_STARS_LEAN_RESULT.md` | complete/partial | Added here because the stellar leanness claim is now a headline data-backed result cited in both `CLAIMS_STATUS.md` and `MASTER_PREDICTION_LEDGER.md`. |

Special note: `TheFormula/Claude4.8/SOURCES.md` is already a useful thread-local source sheet for the WWV / Nino packet and should be preserved.

### 5.1 Claim/result documents explicitly referenced by `CLAIMS_STATUS.md` and `MASTER_PREDICTION_LEDGER.md`

This subsection was added to make the evidence chain for data-backed claims easier to follow. These files are not new raw sources by themselves; they are the local result documents that operationalize the sources listed above.

| Result document / thread | Main source families behind the claim | Status | Notes |
|---|---|---|---|
| `SOLAR_FLYWHEEL_RESULT.md` | SILSO monthly sunspots | complete | Core solar self-forecast claim. |
| `TheFormula/MULTI_SYSTEM_PREDICTION_STACK_RESULT.md` | NSIDC sea ice, QBO feed, CDC/Delphi ILINet, FRED retail, Big Ideas / D1NAMO CGM, NOAA/Scripps CO2, PAHO dengue | partial/complete | Main multi-system self-forecast stack cited by both claim files. |
| `TheFormula/ARA_FORECAST_STANDARD_BASELINE_COMPARISON_RESULT.md` | SILSO, QBO, NOAA NINO3.4 / SOI / WWV, FRED retail, NSIDC sea ice, CDC/Delphi ILINet | partial/complete | Stronger-baseline rerun that softened the broad public forecast claim. |
| `SPRING_PUMP_RESULT.md`, `GATE_MIX_PREDICT_RESULT.md`, `SPRING_REGIME_SWITCH_RESULT.md`, `PHI_RUNG_PUMP_FORECAST_UPGRADE.md`, `RECOIL_ENERGY_PHITURN_STACK_RESULT.md`, `ENSO_TURNING_POINT_NULLS.md`, `TheFormula/FROZEN_SPHERE_MOLD_THEN_ROLL_RESULT.md` | NOAA NINO3.4, PMEL WWV, SOI / PDO / IOD climate feeds | partial/complete | Main ENSO mechanics / feeder / amplitude / spring-barrier result chain. |
| `ARA_GEOMETRY_TRANSPORT_RESULT.md`, `ARA_TICK_RECURSION_AND_COUPLING_RESULT.md`, `ARA_TEMPORAL_FRICTION_RESULT.md`, `SINGULARITY_FLIP_CONJECTURE.md` | NOAA NINO3.4 / SOI / PDO / IOD / WWV, SILSO sunspots, PhysioNet ECG RR data | partial/complete | Core geometry-state / forward-operator / friction / coherence claim chain. |
| `HEART_TIME_SINGULARITY_CEILING_RESULT.md`, `HEART_SUBSYSTEM_DIP_RESULT.md`, `MIMIC_COMBINED_LOCK_RESULT.md` | PhysioNet NSRDB / RR, slpdb, Fantasia, Apnea-ECG, MIMIC | complete/partial | Heart-horizon, driver ladder, and within-beat subsystem claims. |
| `ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md` | Figshare nasal cycle data, PLOS nasal-cycle paper, NOAA ENSO / SOI series | complete/partial | Cross-scale coupled-pair geometry transfer claim. |
| `EnergyRatio/GOLDEN_STARS_LEAN_RESULT.md` | Kepler/MAST light curves, OGLE-IV catalogs, Netzel & Smolec RR0.61 census | complete/partial | Stellar photometry claim now promoted into the public claim files. |

---

## 6. Domain-reference documents (not raw datasets, but cited science used in reasoning)

These files are not all empirical tests; some are framework applications or theory-grounding documents that still rely on named literature.

### 6.1 Battery application

Primary file: `ARA_Battery_Theory.md`

Named source families already in the file:

- Battery University
- ACS *Journal of Physical Chemistry C*
- ScienceDirect metal-hydride / hysteresis / reactor studies
- Frontiers room-temperature hydride review
- Wiley / Lototskyy on thermally driven metal-hydride compression
- OSTI / Riso hydride enthalpy references
- Springer, DTIC, MDPI / PMC, ResearchGate, RSC / IntechOpen, Ergenics / Ames alloy data

Status: `partial`

Reason: the source families are explicit, and the engineering reasoning is traceable, but the exact paper titles / years / DOIs should be normalized into formal references before public release.

### 6.2 Fusion application

Primary file: `ARA_Fusion_Theory.md`

Named / implied source families already in the file:

- muon-catalyzed fusion literature
- published X-ray-laser-assisted / parametric-resonance muon stripping work
- standard solar fusion / tunneling / weak-interaction background
- alpha-sticking and muon lifetime literature

Status: `needs normalization`

Reason: the document is clear about what is established vs novel, but several cited physics strands are described conceptually rather than with formal bibliographic entries. This is one of the highest-value cleanup targets before publication.

### 6.3 Mechanics / KAM / action-axis grounding

Primary files: `ACTION_AXIS_AND_KAM_GROUNDING.md`, `ARA_FOUNDATIONS_FROM_ESTABLISHED_MECHANICS.md`, `Supporting/PROOF_ROADMAP_kam_connection.md`

Named sources include:

- Kolmogorov (1954)
- Arnold (1963)
- Moser (1962)
- Kirkwood (1866)
- Scheffer et al. (critical slowing down)
- standard Hamiltonian action-angle mechanics references

Status: `partial`

Reason: named, checkable, and enough for an auditor to trace, but they should be converted into a formal reference list with publication venues.

---

## 7. Operational and benchmark comparisons mentioned in the repo

These are not always used as direct data feeds, but they are part of the claim-comparison apparatus and should be in the bibliography register.

| Source / benchmark family | Used in | Status |
|---|---|---|
| ECMWF / NOAA Climate Forecast System references for ENSO horizon context | `what_is_this_original.html`, `MASTER_PREDICTION_LEDGER.md` | partial |
| SWPC solar-cycle forecast panels | `MASTER_PREDICTION_LEDGER.md`, `TheFormula/13` benchmark framing | needs normalization |
| IRI / NMME / CFSv2 ENSO benchmark context | `MASTER_PREDICTION_LEDGER.md`, `TheFormula/13` | needs normalization |
| Sea Ice Outlook / NSIDC-style baselines | `MASTER_PREDICTION_LEDGER.md`, `TheFormula/13` | needs normalization |
| CDC / Delphi ILINet / FluSight style benchmarks | `MASTER_PREDICTION_LEDGER.md`, `TheFormula/13` | partial |
| FRED / retail seasonal baselines | `TheFormula/13` | partial |

---

## 8. Files already acting as local source ledgers

These files should be treated as companion provenance documents:

- `TheFormula/Claude4.8/SOURCES.md`
- `analysis/pendulum_scripts/README.md`
- `ARA_COUPLED_GEOMETRY_TRANSFER_RESULT.md`
- `TWOBAND_ECG_HORIZON_LADDER_RESULT.md`
- `README.md`
- `MASTER_PREDICTION_LEDGER.md`
- `CLAIMS_STATUS.md`

They already carry source metadata; this document is the repo-wide index that ties them together.

---

## 9. Known gaps to fix next

Before any formal paper, public release package, or external audit round, these are the source-cleanup priorities:

1. **Normalize TheFormula climate feeds**
   - exact URLs / series names for AMO, TNA, PDO, DMI / IOD, QBO, and Moon ephemeris queries
   - especially in `TheFormula/01`, `TheFormula/02`, `TheFormula/13`, and `TheFormula/Claude4.8/`

2. **Normalize Fusion references**
   - exact muon-catalysis / alpha-sticking / X-ray stripping papers
   - exact weak-interaction / solar-fusion references used in `ARA_Fusion_Theory.md`

3. **Normalize Battery references**
   - convert source-family shorthand in `ARA_Battery_Theory.md` into proper bibliography entries with titles, years, and DOIs where available

4. **Normalize vertical_rocks**
   - sediment / Rouse / morphology references need the same cleanup level as the cleaner physiology folders

5. **Normalize benchmark-comparison claims**
   - where the repo says "industry standard", record the exact benchmark source, forecast target, horizon, and metric

---

## 10. Minimum citation rule for future additions

For every new test, save the source metadata in the result file or README with at least:

- dataset / source name
- URL or DOI
- exact local filename or series name used
- access date if fetched live
- script(s) that consumed it
- whether the source is raw data, benchmark baseline, or interpretive paper

If that rule is followed consistently, this file can stay short and authoritative instead of becoming archaeology.
