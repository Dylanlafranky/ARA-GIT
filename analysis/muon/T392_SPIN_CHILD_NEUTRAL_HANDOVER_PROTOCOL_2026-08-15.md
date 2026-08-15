# T392 - spin-child to joint-neutral handover

**Status:** FROZEN BEFORE DIGITISING OR SCORING FIGURE 6  
**Recorded:** 15 August 2026  
**Parent programme:** T381 C09, downstream daughter-allocation cut  
**Claim ceiling:** published population spectrum / crosswalk calibration; not an individual decay-time predictor

## 1. Exact question

T391 recovered an opposed population spin pattern in the raw 96-detector field. T392 asks whether the next measured child beneath that anti-phase is the energy-resolved charged-versus-neutral allocation at muon decay.

The proposed handover is not "the muon makes neutrinos only at one energy." Every ordinary muon decay in this source produces a positron and two neutrinos. The test is narrower:

> Does the measured daughter direction relative to the parent spin reverse near a charged-daughter energy allocation of `0.5`, leaving the combined neutral sibling near the complementary `1.5` coordinate on a TE-ARA budget of `2`?

## 2. W5H freeze

- **Who:** polarized positive muons stopped by TWIST, observed through their charged positron daughters.
- **What:** the published forward/backward positron asymmetry `A(p)` versus positron momentum, and the combined neutral-daughter packet `q = p_mu - p_e`.
- **When:** at the decay handover, aggregated over many events. There is no pre-decay event clock in this source.
- **Where:** the stopped-muon rest frame, oriented along the parent muon spin axis.
- **Why:** identify whether the spin anti-phase has an energy-resolved child allocation with the proposed coarse pair near `(0.5, 1.5)`.
- **How:** digitise the official TWIST Figure 6 fit and data-minus-fit residuals, reconstruct approximate data asymmetry, and score the frozen landmarks and controls below.

## 3. ARA identity and orientation

This execution states every coordinate explicitly.

| Quantity | Identity / rung | Orientation | Measurement |
|---|---|---|---|
| parent spin anti-phase | population parent | parent spin axis | established by T391, not re-estimated here |
| charged daughter | downstream child / visible sibling | measured positron direction | TWIST `A(p)` |
| combined neutral daughters | downstream child / neutral sibling | opposite total momentum | `q = p_mu - p_e` |
| charged energy coordinate | child Phase-A allocation | `0 -> 1` within its allowed energy half | `x_e = 2 E_e / m_mu` |
| neutral energy coordinate | complementary child allocation | opposed contribution | `x_N = 2 - x_e` |

Thus

```text
x_e + x_N = 2
```

is conservation bookkeeping. It is not an empirical gate. The empirical object is the momentum at which the measured spin-direction asymmetry changes sign.

The momentum relation of the joint neutral packet,

```text
q_vector = -p_e_vector
```

is also exact for a stopped parent. It determines orientation but does not independently prove ARA.

## 4. Public source and capability

Primary source:

- B. Jamieson et al. (TWIST Collaboration), "Measurement of P_mu xi in Polarized Muon Decay," *Physical Review D* 74, 072007 (2006).
- Official PDF: `https://twist.triumf.ca/~e614/pubs/PmuXi_2006_PRD.pdf`
- Figure used: Figure 6, PDF page 10 (one-indexed).
- Published endpoint: `E_max = 52.83 MeV`.

Figure 6 supplies:

1. the fitted asymmetry `A_fit(p)`;
2. the measured `data - fit` residuals with error bars;
3. the `xi` and `xi-delta` contributions for interpretation.

The paper reports that the simulation mimics the data-acquisition files and the result is obtained from momentum-angle spectra. However, no public event table was located. T392 therefore remains a population-spectrum execution. Figure digitisation uncertainty and detector/radiative corrections are `Other`.

## 5. Reproduction and frozen digitisation

1. Render PDF page 10 at exactly 400 DPI with Poppler.
2. Use the following pixel calibration on the 3400 x 4400 render:
   - plot x borders: `502` and `1633` pixels;
   - momentum range: `17` to `50 MeV/c`;
   - fit zero row: `1094.5` pixels;
   - fit vertical scale: `427 pixels / asymmetry unit`;
   - residual zero row: `1726` pixels;
   - residual vertical scale: `6400 pixels / asymmetry unit`.
3. Residual points are sampled at the published half-MeV bin centres `17.25, 17.75, ..., 49.75 MeV/c` using the centre of each filled blue square.
4. The black fitted curve is traced near its printed pixels. To avoid mistaking the printed zero axis for the fitted curve at the crossing, a cubic is fitted to traced curve pixels outside `|A_fit| <= 0.008` and evaluated through the crossing.
5. Reconstruct `A_data = A_fit + (data - fit)`.
6. Convert momentum to energy with `E_e = sqrt(p^2 + m_e^2)` and then to `x_e = 2 E_e / m_mu`.

Constants are frozen as:

- `m_mu = 105.6583755 MeV`;
- `m_e = 0.51099895 MeV`.

## 6. Primary estimate

Fit a weighted quadratic to reconstructed `A_data` over `21 <= p <= 32 MeV/c`. Its physical root inside that interval is the handover estimate. Bootstrap 20,000 residual realisations using digitised error-bar scales plus two printed pixels of fit-curve uncertainty.

The registered target is a tolerance band, not an exact point null:

```text
0.45 <= x_e,handover <= 0.55
```

An exact `0.5` remains the pure coarse-pair reference. Real detector response, radiative corrections, target effects and figure digitisation may displace the measured centre.

## 7. Frozen gates

1. **Directional reversal:** low allocation (`x_e <= 0.40`) has negative median reconstructed asymmetry and high allocation (`x_e >= 0.70`) has positive median reconstructed asymmetry.
2. **Unique handover:** the weighted local fit has exactly one physical root in `0.35 <= x_e <= 0.65`.
3. **Coarse-pair band:** the estimated root lies in `0.45 <= x_e <= 0.55`.
4. **Bootstrap stability:** at least 95% of bootstrap roots lie inside the same coarse-pair band.
5. **Wrong-landmark control:** the estimated root is closer to `0.5` than to `0.25` or `0.75`.

All five gates are required for the registered population handover-child result.

## 8. Interpretation boundary

A pass supports this statement only:

> In the published polarized-muon population spectrum, the charged daughter's spin-direction relation reverses near a `(0.5, 1.5)` charged/joint-neutral TE-ARA energy allocation. This is consistent with a child handover beneath the parent spin anti-phase.

It does **not** show:

- that spin triggers the decay;
- that exactly 7.5 turns creates a neutrino;
- the advance time of one muon's decay;
- the separate trajectories of the two neutrino siblings;
- that the conservation complement is an independent observation.

Those require Class S/G event-linked data under the T381 protocol.
