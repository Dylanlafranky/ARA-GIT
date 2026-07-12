# MX1 draft protocol — Gauss ↔ ARA/TE-ARA bridge in two-stream plasma

**Prepared:** 12 July 2026  
**Status:** `DEVELOPMENT COMPLETE / TRANSFER RULES FROZEN / DO NOT OPEN CONFIRMATION ARRAYS`  
**Fidelity packet:** `MX1_TRANSLATION_FIDELITY_PACKET_v2_DRAFT.md` (v1 preserved as superseded)  
**Binding condition:** Dylan verdict is `EXACT ENOUGH TO TEST`. Freeze the development bridge and add a ledger entry before opening the confirmation `.mat` files.

## Outcome first

Use a public one-dimensional plasma wave as the simplest real numerical slice where the same physical event is exposed
both as an electric field and as independently simulated charged particles. Develop the ARA/Gauss crosswalk on one
archive. Freeze it. Test it on a second untouched archive from different authors.

This is a **compression/crosswalk test**, not a competition with Maxwell's equations. Gauss/Fourier is the referee.
The question is whether current ARA + TE-ARA coordinates preserve the relationship compactly and transferably.

## Dataset decision

### Development/calibration — selected and inspected

**Dataset:** E. Paulo Alves, *Two-stream instability dataset from Particle-In-Cell code OSIRIS*  
**DOI:** `10.5281/zenodo.7968601`  
**URL:** https://zenodo.org/records/7968601  
**License:** CC BY 4.0  
**Associated primary paper:** Alves & Fiuza, *Data-driven discovery of reduced plasma physics models from fully-kinetic simulations*, Physical Review Research 4, 033192 (2022), DOI `10.1103/PhysRevResearch.4.033192`.

Published setup:

- 1D1V electrostatic two-stream instability;
- two equal electron populations at \(\pm0.2c\);
- fixed neutralising ion background;
- periodic length \(10c/\omega_{pe}\);
- 10,000 particles per cell;
- Yee field solver, Boris particle pusher and charge-conserving Esirkepov deposition;
- no current smoothing.

Files verified locally outside the Git repository:

| File | Size | Published MD5 | SHA-256 checked locally |
|---|---:|---|---|
| `fld_data.pkl` | 473,173 B | `b4f645e3876e3ae6b432b0de211ded8c` | `0b368655fe61b33a3193d7d01180623d4f1df4be068b68fb4d453cd8e6d62907` |
| `phase_space_data.pkl` | 120,329,405 B | `e73debf0cf66d6c5af5d7cd1f62490c1` | `1cef8ab44720f60ab6559d04333fa60e8a9415963ff26356a177128181b8770f` |

Array structure safely inspected without unrestricted pickle loading:

- \(x\): 256 positions, \(\Delta x=0.0390625\), periodic length 10;
- \(t\): 459 slices from about 3.8 to 38.608, \(\Delta t=0.076\);
- \(E(t,x)\): shape 459 × 256;
- \(F(t,v,x)\): shape 459 × 256 × 256;
- \(\Delta v=0.00390625\).

**Contamination declaration:** broad field growth and selected-time Gauss agreement have already been inspected.
This archive may develop/calibrate the method but cannot provide confirmatory ARA evidence.

Exploratory feasibility only:

- electric-field RMS grows from about \(2.1\times10^{-4}\) at the first saved slice to about \(5.1\times10^{-2}\)
  at the last;
- the late spatial field contains about five coherent cycles around the periodic domain;
- integrating \(F\) over velocity gives an electron-density pattern independently of \(E\);
- at selected developed slices, a simple central-difference \(\partial_xE\) correlates about 0.996–0.998 with the
  independent charge pattern. This is not a registered result and will not be promoted.

### Confirmation/transfer — selected but numerical arrays remain unopened

**Dataset:** Tang, Wu & Tao, *1D particle-in-cell simulation of the electron two-stream instability*  
**DOI:** `10.5281/zenodo.3696310`  
**URL:** https://zenodo.org/records/3696310  
**License:** CC BY 4.0  
**Associated primary paper:** Tang et al., *Electron Mixing and Isotropization in the Exhaust of Asymmetric Magnetic Reconnection With a Guide Field*, Geophysical Research Letters (2020), DOI `10.1029/2020GL087159`.

Published files total 14.4 MB:

- `data.mat`, 7.2 MB, MD5 `058e88be103efeded577542aa1da6646`;
- `field_data.mat`, 7.2 MB, MD5 `783bcca549cde7dd6c798b0f2dfbd6f5`;
- `distribution.mat`, 17.9 kB, MD5 `10d915d0904be9ae7baf0ac3042c4921`.

The record states that it contains electric/magnetic perturbations and a 1D electron distribution. Metadata inspection
is allowed; numerical arrays must remain unopened until fidelity sign-off, development bridge freeze and ledger
registration.

### Later experimental replication — not the first test

NASA's four-spacecraft MMS mission provides public vector electric-field measurements and tetrahedral geometry. A
published Gauss analysis and code are available:

- paper: https://www.nature.com/articles/s42005-024-01553-5
- data: https://lasp.colorado.edu/mms/sdc/public/
- code: https://github.com/LaiGao93/Charge-Density-Calculations

MMS is physically stronger but methodologically harder: charge is inferred from the same four-point electric field,
spacecraft geometry and measurement uncertainty matter, and independent plasma density is incomplete in relevant
intervals. Use it only after the simulation bridge is frozen.

## Why this system is unusually suitable

1. The two counter-streaming electron populations provide a literal Phase/anti-phase starting structure.
2. The instability turns small fluctuations into a coherent electrostatic wave and later nonlinear structure.
3. The periodic domain contains repeated peer wave cells at one declared rung.
4. Electric field and particles provide two views of the same event.
5. In 1D, Gauss becomes an especially transparent boundary difference.
6. The second archive offers an affordable untouched transfer test.

## Plain-language geometry

Imagine a flexible electric wave repeated around a ring. Each complete repetition contains a positive-source half and
a negative-source half. Adding the whole repetition gives nearly zero net charge, but that does not mean nothing is
happening; it is the everything-ridge cancellation. We keep the complete repetition as the identity and inspect both
halves.

Gauss approaches from the boundary: how much does the electric field change from the left edge of a half-wave to the
right edge? The particle distribution approaches from inside: how many positive-background charges remain after the
electrons in that half-wave are counted? Established physics says these match.

ARA asks how the wave's accumulation and release are shaped. TE-ARA asks how much field energy belongs to the declared
main wave and its fixed harmonics rather than Other modes. The bridge should rotate the wave by a quarter cycle and
give short-scale harmonics more weight. We learn no arbitrary curve: we test whether this fixed structure plus a small
ARA compression transfers to the second simulation.

## Established anchor

In the dataset's normalised units, independently reconstruct source density from the particles:

\[
\underbrace{\rho_F(x,t)}_{\text{independent particle-side source}}
=1-\Delta v\sum_vF(t,v,x).
\]

Compute the field-side Gauss source with the grid-consistent derivative \(D_x\):

\[
\underbrace{\rho_G(x,t)}_{\text{Gauss source from field}}
=\underbrace{D_xE(x,t)}_{\text{normalised }\partial_xE}.
\]

Use both a centred finite difference and a periodic spectral derivative during development. Freeze the derivative
matching the simulator's staggering before the confirmation data are opened. Report both; never choose by confirmation
performance.

Fourier mode bridge:

\[
\widehat\rho_G(k,t)=ik\widehat E(k,t).
\]

This is the fixed “hypotenuse”: quarter-cycle phase rotation from \(i\), magnitude weighting from \(|k|\), and the
sign/orientation retained in complex phase.

## Identity segmentation

At each eligible time slice:

1. determine the dominant spatial wavenumber \(k_0\) under the frozen development rule;
2. phase-fold the periodic field into its repeated \(\lambda_0=2\pi/k_0\) cells;
3. treat one complete positive/negative pair as one identity;
4. measure positive-source and negative-source half-waves separately for Gauss magnitude/sign;
5. aggregate peer cells only after recording their variance.

For each coherent complete cell, retain three different ARA measurements:

- \(a_+\): raw/phase-folded waveform ARA of the positive-source half;
- \(a_-\): raw/phase-folded waveform ARA of the negative-source half;
- \(x_Q=2Q_+/(Q_++Q_-)\): pair-level source-composition ARA.

The exact Gauss reconstruction is

\[
\Phi_E
=\frac{Q_+-Q_-}{\varepsilon_0}
=\frac{Q_++Q_-}{\varepsilon_0}(x_Q-1).
\]

This pair-level identity is an established algebraic embedding. The ARA-added test is whether component waveform ARAs,
TE-ARA, rung, phase and frozen Other rules recover the unsigned magnitude \(Q_++Q_-\) transferably.

Time slices before coherent-cycle detectability are labelled `ARA undefined`, not forced to 1.0.

## ARA measurement

Use raw spatial \(E(x,t)\), not a narrowband-filtered sine. The wave is expected to be single-feature per spatial
cycle after coherent growth, so use phase-folded or raw-peak ARA under a synthetic calibration at the dataset's grid
length and noise. The development phase must select one method and freeze it.

Report:

- ARA scalar;
- pole orientation;
- \(k_0\), spatial phase and cell origin;
- number of coherent cells;
- cycle-to-cycle variance;
- harmonic amplitudes/phases retained by the identity decomposition.

## TE-ARA measurement

Define a fixed identity harmonic family

\[
H=\{k_0,2k_0,\ldots,N_Hk_0\},
\]

where \(N_H\le12\), Nyquist and synthetic SNR allow. Development chooses \(N_H\) by a rule independent of confirmation
performance; confirmation uses the same rule.

Electric-field TE-ARA:

\[
\mathrm{TE\!-\!ARA}_E(t)
=2\frac{\sum_{k\in H}|\widehat E(k,t)|^2}{\sum_{k\ne0}|\widehat E(k,t)|^2}.
\]

Gauss/source participation predicted from the same identity family:

\[
\widehat{\mathrm{TE\!-\!ARA}}_{\rho,G}(t)
=2\frac{\sum_{k\in H}k^2|\widehat E(k,t)|^2}{\sum_{k\ne0}k^2|\widehat E(k,t)|^2}.
\]

Independent observed source participation uses \(\widehat\rho_F\) in numerator and denominator. This tests whether
the field-defined identity family survives the Gauss projection.

These are normalised simulation-energy/power fractions, not raw joules.

TE-ARA is not \(Q_++Q_-\). The protocol must test their scale-aware relation rather than substituting one for the
other. Report both source magnitude and energy participation.

## Three test levels

### Level 0 — instrument sanity, established physics

Compare \(\rho_G\) with independent \(\rho_F\). This validates parsing, axes, sign, staggering and derivative. It is
not ARA evidence.

### Level 1 — full identity-harmonic bridge

Retain the frozen complex coefficients in \(H\), apply \(ik\), reconstruct the identity part of charge, and compare
with \(\rho_F\). This tests whether the declared main wave family and Other split survive Gauss.

If this fails, TE-ARA's numerator or the node segmentation is physically wrong.

### Level 2 — compressed ARA + TE-ARA bridge

Ask whether a small frozen model using ARA and TE-ARA predicts the Gauss-side summary without retaining every harmonic
coefficient. A dimensional magnitude coordinate is mandatory: TE-ARA is a fraction and cannot produce an absolute
charge/source magnitude by itself. For the development plasma define

\[
\underbrace{B_Q(t)}_{\text{established dimensional source scale}}
=
\underbrace{k_0}_{\text{inverse-length scale}}
\underbrace{E_{\mathrm{rms}}(t)}_{\text{field magnitude}},
\qquad
\underbrace{y_Q(t)}_{\text{dimensionless source-shape factor}}
=
\frac{\langle|\rho_F-\langle\rho_F\rangle|\rangle}{B_Q(t)}.
\]

Then compare a scale-only constant-shape bridge against TE-only, ARA-only, ARA+TE and a matched-feature generic
model for \(y_Q\). The direct prediction is \(\widehat S_Q=B_Q\widehat y_Q\). Spatial phase is retained for local
waveform reconstruction but is not used to predict a translation-invariant total-source summary.

One candidate compressed form is

\[
\widehat y_Q
=\beta_0+\beta_1p_{id}
+\beta_2\bar a_c+\beta_3\Delta a_c+\beta_4p_{id}\bar a_c,
\]

where \(p_{id}=\mathrm{TE\!-\!ARA}/2\), \(\bar a_c\) is the centred mean of the two clean bounded component ARAs, and
\(\Delta a_c\) is their signed contrast. Component readings outside \(0<x\le2\) are retained diagnostically but marked
compound/undefined and excluded from the compressed scalar fit. Freeze terms and coefficients before confirmation.

If Level 1 transfers but Level 2 does not, the current scalar compression is missing phase/path/harmonic information
or contributes no information beyond the dimensional scale.
That is a useful narrowing result, not a failure of Maxwell or of the full field relation.

## Development outputs to freeze before confirmation download

1. exact spatial identity and half-wave segmentation;
2. coherent-time eligibility rule;
3. ARA extractor and synthetic calibration;
4. \(k_0\) and identity-harmonic-family rule;
5. TE-ARA numerator/Other rule;
6. grid derivative/staggering operator;
7. Level-2 bridge terms and coefficients;
8. target summaries and units;
9. numeric transfer thresholds;
10. exclusion and missing-data rules.

Hash this frozen packet, add `MASTER_PREDICTION_LEDGER.md` entry, then download/open the Tang arrays exactly once.

## Baselines

Mandatory:

1. **Established full Fourier derivative:** upper-bound referee, not an ARA competitor.
2. **Dominant Fourier mode only:** same main scale without waveform asymmetry.
3. **TE-only:** identity energy participation without ARA shape.
4. **ARA-only:** waveform asymmetry without energy participation.
5. **Matched-feature generic:** RMS, skewness, dominant wavenumber, phase and spectral entropy with the same or fewer
   fitted degrees of freedom as Level 2.
6. **Constant/mean target:** minimal null.
7. **Shuffled cells/times:** destroys the field/source relation while retaining marginal distributions.

## Primary metrics

- correlation, normalised RMSE and signed error for \(\rho\) reconstruction;
- positive/negative half-wave sign accuracy and charge-magnitude error;
- TE-ARA source-participation absolute error;
- ARA summary error if a charge-side ARA summary survives the fidelity gate;
- calibration slope/intercept;
- residuals versus time, amplitude, \(k_0\), cell index and harmonic energy;
- transfer degradation from development to confirmation.

## Interpretation rules

### Supports a useful crosswalk

- Level 0 passes on confirmation under the frozen derivative;
- Level 1's fixed identity family captures the source structure predicted by its participation measure;
- Level 2 transfers without coefficient/orientation refit and beats all matched-feature low-dimensional baselines;
- residuals do not demand a different bridge at each time or cell.

### Narrows the current ARA compression

- Level 1 works but Level 2 does not;
- TE helps but ARA adds no held-out information;
- phase/harmonic coordinates are necessary, showing the scalar pair is insufficient;
- different node segmentation is required.

### Does not support the proposed bridge

- a bridge must be refit or reoriented for the confirmation dataset;
- ARA + TE-ARA fails to beat the matched-feature generic baseline;
- Other is so large or unstable that the declared identity family has no transferable meaning;
- results arise only when the positive/negative pair is flattened or the confirmation definition is changed.

## Dependency and replication design

The eventual script must:

- auto-fetch public files from both DOI records;
- verify published MD5 and recorded SHA-256 values;
- never unrestrictedly unpickle public files; use a restricted loader allowing only NumPy array constructors;
- include or auto-install no hidden local dependencies;
- print the fidelity packet hash, bridge freeze hash, data hashes and exact result tier;
- leave downloaded data outside Git or in an ignored cache;
- ship a tiny safe sample so a fresh clone can run the parser/instrument check if the full download is unavailable.

## Current state

- Dataset audit: complete.
- Development analysis: complete on 299 eligible slices; exploratory/calibration only.
- Confirmation metadata: selected; numerical arrays unopened.
- Formal claim: registered as a sealed transfer test in `MASTER_PREDICTION_LEDGER.md`.
- Fidelity gate: passed as `EXACT ENOUGH TO TEST`.
- Freeze packet: `MX1_CONFIRMATION_FREEZE_v1.md`.
- Next gate: mechanically adapt the frozen rules to the confirmation file schema, then open the arrays once and report
  every registered metric without refitting.
