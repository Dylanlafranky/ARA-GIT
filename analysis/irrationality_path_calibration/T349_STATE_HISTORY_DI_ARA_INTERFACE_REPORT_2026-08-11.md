# T349 — State/history Di-ARA interface calibration

**Run date:** 11 August 2026  
**Evidence boundary:** synthetic known-referee instrument/interface calibration only  
**Primary verdict:** **SUPPORTED — 7/7 frozen interface gates passed**  
**Constant verdict:** **NOT SUPPORTED — no frozen universal fixed amplitude passed**  
**Independent validation:** **PASS — 36/36 checks**

## Outcome first

T349 gave the older state Di-ARA and the newer path/history Di-ARA independent
information and then changed one relation at a time. The two instruments did
not collapse into one classifier.

Across `1,656` untouched holdout trajectories:

- the older radial coordinate recovered contraction, neutral and expansion
  with **100% fixed-ridge accuracy**;
- the newer path/history coordinate retained **95.6522%** broad-sector
  recovery across every radial state;
- radial inversion reflected `x_L` exactly while leaving `x_C`, `x_P`, `x_R`
  and closure history unchanged;
- phase reflection reflected `x_C` exactly while leaving `x_L`, `x_P`, `x_R`
  and unsigned closure history unchanged;
- chronology destruction moved the stochastic-residual coordinate by almost
  the full ARA span while leaving radial state and address openness unchanged;
- even when the first state, last state, radial path and complete visited-value
  multiset were preserved, destroying only the interior order produced the
  same decisive history change.

This supports a synthetic interface between a radial/orientation state cut and
an address/residual/closure history cut. It does **not** yet establish that one
is physically the parent of the other. The factors were independently
controlled by construction; the load-bearing empirical-style result is that
the frozen instruments and interventions recover the intended information
without leaking it onto the wrong axes.

## The two objects tested

Each trajectory was retained as

\[
z_t=r_t e^{2\pi i u_t}.
\]

The older typed Di-ARA measured

\[
D_{\rm state}=(x_L,x_C),
\]

where `x_L` is contraction ↔ expansion and `x_C` is reverse ↔ forward
orientation.

The newer typed Di-ARA retained

\[
D_{\rm history}=\bigl(x_P,x_R,C(H)\bigr),
\]

where `x_P` measures reused ↔ open addresses, `x_R` measures determinate ↔
stochastic residual, and `C(H)` keeps the uncompressed multi-lag closure
relation.

The `5 × 3` factorial crossed five T348 phase-history families with three
radial families:

| Phase/history referee | Contraction | Neutral | Expansion |
|---|---:|---:|---:|
| periodic rational | 100% | 100% | 100% |
| irrational rotation | 100% | 100% | 100% |
| deterministic chaos | 50% | 50% | 50% |
| finite stochastic | 100% | 100% | 100% |
| continuous stochastic | 100% | 100% | 100% |

The repeated 50% chaos result is the retained T348 limitation: one held-out
chaotic parameter group has support-growth dimension below the fixed `x_P=1`
ridge. Radial contraction or expansion neither repaired nor worsened it.

## Intervention result

| Intervention | median `|Δx_L|` | median `|Δx_C|` | median `|Δx_P|` | median `|Δx_R|` | median closure change |
|---|---:|---:|---:|---:|---:|
| radial inversion | 1.2502 | 0 | 0 | 0 | 0 |
| phase reflection | 0 | 2.0000 | 0 | 0 | approximately 0 |
| chronology shuffle | 0 | 0.9653 | 0 | 1.9453 | 0.9859 |
| endpoint-preserving interior shuffle | 0 | 0.9684 | 0 | 1.9439 | 0.9858 |

The first two rows are exact symmetry checks and are partly algebraic. The last
two are the stronger instrument result. The phase values themselves were not
changed or replaced; only their relation through order was destroyed.

For endpoint-preserving interior shuffling, the maximum endpoint error was
exactly zero. Nevertheless:

- periodic `x_R` increased by `1.9781`;
- irrational `x_R` increased by `1.9710`;
- deterministic-chaos `x_R` increased by `1.9999`;
- periodic closure coherence fell by `0.9865`;
- irrational closure coherence fell by `0.9865`.

Plainly: the same start, finish and available locations do not specify the
identity. The ordered relation remains independently measurable.

## Closure history remains load-bearing

The uncompressed `C(H)` relation reproduced the T348 distinction under every
radial state:

| Family | median closure coherence |
|---|---:|
| periodic rational | 1.0000 |
| irrational rotation | 1.0000 |
| deterministic chaos | 0.0444 |
| finite stochastic | 0.0135 |
| continuous stochastic | 0.1090 |

Periodic and irrational motion therefore still require `C(H)` to distinguish
exact closure from coherent non-closure. Irrational best-miss distance improved
from the 64-lag to the 512-lag search in **100%** of holdouts.

## Frozen gate table

| Gate | Result | Headline value |
|---|---|---|
| G1 radial recovery | **PASS** | 100% holdout radial accuracy |
| G2 history recovery across radius | **PASS** | 95.6522% history-sector accuracy |
| G3 radial inversion | **PASS** | exact `x_L -> 2-x_L` |
| G4 phase reflection | **PASS** | exact `x_C -> 2-x_C` |
| G5 chronology specificity | **PASS** | deterministic `Δx_R` from 1.9721 to 1.9999 |
| G6 endpoint/history distinction | **PASS** | zero endpoint error; decisive history loss |
| G7 factorial independence | **PASS** | maximum cross-factor median range 0 |
| G8 fixed constant specificity | **FAIL, separate** | best fixed mean log error 0.2833 |

## What happened to `e`, `1/e` and Phi

No constant was used in generation or primary coordinate normalization. The
arbitrary holdout log-spans were compared afterward with fixed reciprocal
amplitudes.

| Candidate amplitude | Mean absolute log error | Share within 0.10 | Universal gate |
|---|---:|---:|---|
| `e` | 0.2833 | 33.3% | fail |
| calibration-fitted control | 0.3333 | 0% | not eligible as universal |
| octave `2` | 0.3523 | 0% | fail |
| Phi | 0.4688 | 33.3% | fail |
| square root of two | 0.6034 | 0% | fail |
| plastic constant | 0.6688 | 0% | fail |

`e` was the closest fixed candidate only because these arbitrary holdout spans
happened to be centred nearer a one-unit logarithmic change. Its error was
almost three times the frozen universal threshold, and it described only one
third of paths within tolerance. This is not evidence for `e`; it is the
expected specificity result from deliberately varied amplitudes.

The scientific conclusion agrees with T340/T341: contraction/expansion ×
orientation is a usable Di-ARA geometry, while one universal `e/Phi` numerical
placement remains unsupported.

## What this implies for the proposed hierarchy

T349 supports three statements at the synthetic instrument level:

1. local radial state and ordered path identity are not interchangeable;
2. a path/history parent can preserve information absent from its endpoint or
   visited-value inventory;
3. orientation, stochastic residual and closure history are related but not
   identical—reflection changes orientation without changing residual, while
   chronology destruction changes both orientation and residual.

It does not yet prove

\[
D_{\rm state}(t)\longrightarrow\Gamma_{0:t}\longrightarrow D_{\rm history}
\]

as a physical child-to-parent mechanism. The next synthetic rung would need to
calculate the older state Di-ARA in causal sliding windows, compress that
sequence, and predict the held-out history parent. The next empirical rung
would then transfer the frozen interface to a physical oscillator with
independently known contraction/expansion and periodic/quasiperiodic/chaotic
regimes.

## Reproduction and validation

Run:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'analysis\irrationality_path_calibration\t349_state_history_di_ara_interface.py'
```

Independent validation:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'analysis\irrationality_path_calibration\validate_t349_state_history_di_ara_interface.py'
```

The validator does not import the run script. It independently recomputed the
headline accuracies, all intervention summaries, every fixed-constant score,
and all five coordinates from 15 complete raw example trajectories. All
`36/36` checks passed.

## Artifact index

- frozen claim packet: `T349_STATE_HISTORY_DI_ARA_INTERFACE_CLAIM_PACKET_v1.md`
- frozen protocol: `T349_STATE_HISTORY_DI_ARA_INTERFACE_PROTOCOL_v1_FROZEN.md`
- complete metrics: `T349_STATE_HISTORY_DI_ARA_METRICS.csv`
- factorial summary: `T349_STATE_HISTORY_DI_ARA_FACTORIAL_SUMMARY.csv`
- intervention summary: `T349_STATE_HISTORY_DI_ARA_INTERVENTIONS.csv`
- closure curves: `T349_STATE_HISTORY_DI_ARA_CLOSURE_CURVES.csv`
- constant specificity: `T349_STATE_HISTORY_DI_ARA_CONSTANT_SPECIFICITY.csv`
- frozen gates: `T349_STATE_HISTORY_DI_ARA_FROZEN_GATES.csv`
- machine-readable result: `T349_STATE_HISTORY_DI_ARA_RESULTS.json`
- independent validation: `T349_STATE_HISTORY_DI_ARA_VALIDATION.md` and `.json`
- main visual: `T349_STATE_HISTORY_DI_ARA_FIGURE.png`
- raw validation examples: `T349_STATE_HISTORY_DI_ARA_EXAMPLES.csv`

