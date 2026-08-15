# T378 — independent 2017 CsI muon-handover holdout

## Result in one sentence

The independent 2017 COHERENT CsI[Na] release resolves an earlier prompt
neutrino branch and a later muon-decay neutrino branch in the expected order,
but it remains a **strong near-replication rather than a frozen pass** because
two of eight predeclared gates missed their thresholds.

## W5H boundary

- **Who:** the prompt `nu_mu` branch from stopped-pion decay and the delayed
  `nu_e + anti-nu_mu` branch from subsequent muon decay.
- **What:** an ensemble two-branch handover in a solid CsI[Na] detector. This
  is not a linked prediction of the decay time of one identified muon.
- **When:** `0 <= t < 6 us`, in twelve 0.5-us bins.
- **Where:** the released `6 <= PE < 30` coincidence and anticoincidence count
  grids, with a recorded exposure of `7.47594 GW hr`.
- **Why:** this is the closest public independent holdout to the earlier clean
  stopped-pion/muon ARA test: it uses the same physical source architecture and
  solid scintillator family, but is an earlier separately released exposure.
- **How:** a frozen joint non-negative Poisson fit of steady background,
  prompt SNS neutrons, prompt neutrinos and delayed neutrinos, followed by
  bootstrap, time-permutation, leave-one-out, beam-off and response-variant
  controls. The fitted branches are then compressed onto the ARA 0–2 line.

The frozen protocol is
[T378_COHERENT_2017_HOLDOUT_PROTOCOL_2026-08-14.md](T378_COHERENT_2017_HOLDOUT_PROTOCOL_2026-08-14.md).

## Data boundary and quality

The source is the official COHERENT data release associated with the original
CsI[Na] observation, Zenodo DOI `10.5281/zenodo.1228631`. The exact released
grids reproduce these frozen-boundary counts:

| Grid | Counts |
|---|---:|
| Beam-on coincidence | 547 |
| Beam-on anticoincidence | 405 |
| Beam-off coincidence | 209 |
| Beam-off anticoincidence | 207 |

The local audit records SHA-256 hashes for all eleven source files. An
independent validation pass reproduced the grid shapes, counts, normalized
templates, saved fit, handover, exported row counts, beam-off control and the
unchanged frozen gate verdict. Its disposition is **SHARE WITH CAVEATS** with
zero failed validation checks.

## Conventional fit result

The fitted expected counts in the frozen beam-on coincidence window were:

| Component | Fitted events | 95% bootstrap interval |
|---|---:|---:|
| Steady background | 416.247 | — |
| Prompt neutron | 5.622 | — |
| Prompt `nu_mu` | 33.698 | 16.419–55.126 |
| Delayed `nu_e + anti-nu_mu` | 79.568 | 30.192–128.548 |

Both signal branches therefore have bootstrap lower bounds above zero. Their
timing is ordered as expected:

- prompt crest: `0.75 us`;
- delayed crest: `1.25 us`;
- equal fitted branch contribution: `t_H = 1.039 us`;
- bootstrap interval for `t_H`: `0.787–1.184 us`.

The full pair model's AIC advantage was `9.946` against the prompt-only model
and `12.841` against the delayed-only model.

## ARA and TE-ARA reading

Compressing the independently fitted signal yields onto the ARA diameter gives

\[
x_{\rm prompt}
=2\frac{N_{\rm prompt}}{N_{\rm prompt}+N_{\rm delayed}}
=0.595,
\]

\[
x_{\rm delayed}=2-x_{\rm prompt}=1.405.
\]

At the time where the two fitted timing branches contribute equally,

\[
t_H=1.039\ {\rm us},\qquad x_H=0.749,
\]

with bootstrap interval

\[
x_H\in[0.294,1.285].
\]

That interval overlaps the earlier T372 interval and contains the proposed
coarse child value `0.5`. The point estimate is not fixed at `0.5`, and the
interval is wide, so this is compatibility rather than a precise recovery.

The identity

\[
x_{\rm prompt}+x_{\rm delayed}=2
\]

is **forced by the chosen normalization**. It is TE-ARA bookkeeping, not an
empirical result. The observed coupling evidence is instead the combination of
independently positive branches, pair-versus-single comparisons, correct
chronology, beam-on/off contrast, leave-one-out survival and response-variant
survival. The normalized balance product is `0.836`.

## Frozen gates

| Gate | Result | Observation |
|---|:---:|---|
| Provenance and boundary counts reproduce | PASS | Official grids and hashes retained |
| Both branch bootstrap lower bounds exceed zero | PASS | 16.419 and 30.192 |
| Delta-AIC at least 10 against each single branch | **FAIL** | 9.946 and 12.841 |
| No more than 10/1000 common time permutations as good | **FAIL** | 17/1000 |
| Delayed crest follows prompt crest | PASS | 1.25 us after 0.75 us |
| Both branches survive every leave-one-bin-out fit | PASS | 24/24 removals |
| Beam-off does not support the same pair | PASS | Beam-off prompt fit collapsed to zero |
| Both branches survive response variants | PASS | QF-low, QF-high and time-only |

The AIC gate missed by `0.0535`; the permutation result corresponds to an
empirical tail fraction of `0.017`. These are close and encouraging, but the
thresholds were frozen, so they remain failures.

## Robustness and affecting variables

The following were explicitly included or varied:

- steady-background magnitude and time profile;
- prompt-neutron normalization;
- finite event counts;
- detector acceptance;
- CsI[Na] quenching factor;
- light yield;
- reconstructed CEvNS photoelectron response;
- PE-bin and time-bin leverage;
- beam-off behavior;
- common chronology permutations.

Both branches remained positive under low and high quenching-factor variants
and in a time-only fit. The handover coordinate moved from `0.646` to `0.821`
under the quenching-factor variants and to `0.935` in the time-only model. This
means the two-population and ordering result is more stable than the exact ARA
coordinate.

## Verdict

The new source supports the same broad architecture as the initial clean
result:

1. an early prompt branch is present;
2. a later muon-decay branch is present;
3. their fitted contributions cross in the expected time region;
4. the ARA compression is compatible with the earlier child-scale region;
5. the beam-off and deletion controls do not reproduce or destroy the result.

However, it does **not** satisfy every frozen high-stringency handover gate.
The scientifically faithful label is therefore:

> **Independent two-population near-replication; handover architecture
> supported, frozen full-pass claim not reached.**

## Reproduction

From the repository root:

```powershell
python analysis/muon/t378_coherent_2017_holdout.py
python analysis/muon/validate_t378_coherent_2017_holdout.py
```

Primary machine-readable artifacts:

- `analysis/muon/T378_coherent_2017_holdout/T378_results.json`
- `analysis/muon/T378_coherent_2017_holdout/T378_validation.json`
- `analysis/muon/T378_coherent_2017_holdout/T378_timing_components.csv`
- `analysis/muon/T378_coherent_2017_holdout/T378_bootstrap.csv`
- `analysis/muon/T378_coherent_2017_holdout/T378_permutation_nll.csv`

## Source

- COHERENT Collaboration, official 2017 CsI[Na] data release:
  <https://zenodo.org/records/1228631>

