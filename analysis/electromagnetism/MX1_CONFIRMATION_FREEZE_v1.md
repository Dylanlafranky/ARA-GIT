# MX1 confirmation freeze v1 — Gauss ↔ ARA/TE-ARA transfer

**Frozen:** 12 July 2026, before opening any Tang–Wu–Tao numerical array  
**Status:** `REGISTERED / CONFIRMATION SEALED`  
**Claim ID:** `MX1-v2`  
**Fidelity:** `EXACT ENOUGH TO TEST`

## Confirmation archive

Tang, Wu & Tao, *1D particle-in-cell simulation of the electron two-stream instability*,
DOI `10.5281/zenodo.3696310`.

The record metadata and filenames are known. The numerical contents of `data.mat`, `field_data.mat` and
`distribution.mat` remain unopened at freeze time. Once opened, this archive must be labelled confirmation and
must not be returned to development status.

## Frozen development artifacts

| Artifact | SHA-256 |
|---|---|
| `mx1_development_analysis.py` | `6DE8E6FAD466D96EB38B2509FF0E7FB33449C462176F13C8C10E292806DFB4C7` |
| `MX1_DEVELOPMENT_RESULTS.json` | `6BF5FD7E10A51C95E452BE6FB103400C21DDE6730E68025498D35630189711FD` |
| `MX1_GAUSS_ARA_TEARA_PROTOCOL_DRAFT.md` | `3B583758B9ACDEECEBA19A67D1F802DE7EF41E41FCDE0F1A06A0002C585C0618` |
| `MX1_TRANSLATION_FIDELITY_PACKET_v2_DRAFT.md` | `8A69973FD74277AAD9622B63E30A6E376704F455FAC196AEBA5EA154B3C8669F` |

Any change to these files after this freeze must create v2 and be disclosed. It may not silently replace this packet.

## Frozen geometry

For each confirmation time slice:

1. independently reconstruct particle-side charge/source density;
2. reconstruct Gauss source from the electric field using the grid-compatible derivative;
3. detect the reference spatial rung by the frozen unsupervised amplitude/coherence rule;
4. keep the reference mode and its available integer multiples through the twelfth harmonic as the identity family;
5. measure whole-domain and phase-aligned peer-cell \(Q_+\), \(Q_-\), \(T_Q=Q_++Q_-\), and
   \(x_Q=2Q_+/T_Q\);
6. calculate field, Gauss-source and particle-source signal-power TE-ARA analogues;
7. measure positive and negative component ARAs using the frozen 64-bin phase fold and one-pass circular 1:2:1 smoother;
8. retain component raw ratios above 2 diagnostically but mark them compound/undefined for the bounded scalar model;
9. retain `Other = 1-p_{id}`; do not renormalise it away.

The exact pair identity remains

\[
Q_{\mathrm{net}}=T_Q(x_Q-1).
\]

The dimensional source scale is

\[
B_Q=k_0E_{\mathrm{rms}},
\qquad
y_Q=\frac{\langle|\rho-\langle\rho\rangle|\rangle}{B_Q}.
\]

TE-ARA is participation, not absolute magnitude. Models predict \(y_Q\); direct source activity is
\(\widehat S_Q=B_Q\widehat y_Q\).

## Frozen transfer models

Apply the development means, standard deviations, intercepts and coefficients stored in
`MX1_DEVELOPMENT_RESULTS.json` without refitting:

1. scale-only;
2. TE-only;
3. ARA-only;
4. ARA + TE-ARA;
5. matched-feature generic.

All five primary models must be scored on the same slices for which both component ARAs are clean bounded readings.
The scale-only result on every eligible slice is retained only as a separate coverage diagnostic.

The full Fourier derivative remains the established referee, not an ARA competitor. Dominant-mode-only and the
fixed identity-family reconstruction must also be reported.

## Primary thresholds

These thresholds were selected after development inspection and before confirmation opening:

| Level | Transfer requirement |
|---|---|
| Instrument / Level 0 | field-vs-particle source correlation ≥ 0.98 and NRMSE ≤ 0.15 |
| Identity family / Level 1 | identity-Gauss vs identity-particle correlation ≥ 0.95 and NRMSE ≤ 0.15 |
| TE-ARA participation | Gauss-source vs particle-source TE-ARA correlation ≥ 0.60 and MAE ≤ 0.15 on 0–2 |
| Local pair ARA | field/Gauss vs particle \(x_Q\) correlation ≥ 0.60 and MAE ≤ 0.08 |
| Local total magnitude | field/Gauss vs particle \(T_Q\) correlation ≥ 0.98 and NRMSE ≤ 0.10 |
| Local signed result | field/Gauss vs particle \(Q_{\mathrm{net}}\) correlation ≥ 0.98 and NRMSE ≤ 0.15 |

The compressed ARA + TE-ARA bridge counts as adding transferable value only if, on confirmation:

- its direct source-activity \(R^2\) exceeds scale-only by at least 0.05;
- its MAE is at least 5% lower than scale-only;
- it also beats the matched-feature generic model on both \(R^2\) and MAE;
- no coefficient, orientation, harmonic family or eligibility threshold is refitted.

## Interpretation fixed before confirmation

- Level 0 is established-physics/instrument validation, not ARA evidence.
- Level 1 plus the TE-ARA thresholds supports a transferable identity-participation crosswalk.
- Level 1 passing while compressed ARA + TE-ARA fails means the scalar compression is narrowed: the full identity
  family survives, but the tested scalar coordinates do not add magnitude skill beyond the established scale.
- Failure of the identity-family or TE thresholds does not support the proposed TE-ARA bridge.
- Whole-domain \(x_Q\approx1\) is expected for a periodic neutral ring. Local phase-aligned cells are the primary
  moving pair-coordinate test.
- Every registered metric and failed threshold must be reported.

## Mechanical schema rule

After opening, variable names, array ordering and simulator normalisation may be mapped mechanically from metadata,
dimensions and established Gauss consistency. If two mappings remain physically plausible, stop and mark the
confirmation adapter ambiguous. Do not select an orientation or axis by ARA performance.
