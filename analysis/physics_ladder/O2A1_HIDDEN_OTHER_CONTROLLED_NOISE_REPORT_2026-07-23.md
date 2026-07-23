# O2-A1 hidden `Other` under controlled observation noise

**Run:** 23 July 2026  
**Frozen rating:** **NOT SUPPORTED `[pre-registered; synthetic instrument test]`**  
**Protocol SHA-256:** `d16485a828d4396e3ced05ce04fd7ca784a7e662fb9f6f46e078b83cb12add49`  
**Independent validation:** `11/11` checks passed  
**Orientation:** positive residual is a source into the declared identity; negative residual is a sink from it

## Answer first

The noiseless hidden-`Other` result did **not** remain a reliable pointwise locator at the registered `12 dB`
condition. Across the 32 untouched capacitor and quantum runs, only `4/8` frozen gates passed:

| Frozen 12 dB endpoint | Result | Gate | Pass? |
|---|---:|---:|:---:|
| exact hidden-location accuracy | `0.5000` | at least `0.90` | no |
| median active-point sign accuracy | `0.76197` | at least `0.95` | no |
| median waveform correlation | `0.45991` | at least `0.80` | no |
| median peak-normalized RMSE | `0.31391` | at most `0.50` | yes |
| median integrated-amount relative error | `0.007872` | at most `0.35` | yes |
| median inactive-identity RMS fraction | `0.36747` | at most `0.50` | yes |
| median NRMSE versus raw finite difference | `0.3139` vs `47.7264` | lower | yes |
| median NRMSE versus zero-`Other` | `0.3139` vs `0.2212` | lower | no |

The operator therefore retained the **net accumulated loss** far better than it retained the instantaneous waveform
or its location. Calling the 12 dB result a recovery would be misleading: the median integral was within `0.79%`,
but the pointwise estimate was worse on NRMSE than predicting no `Other` at all.

## Claim verdict

**The registered 12 dB robustness claim is NOT SUPPORTED.**

This does not retract the noiseless result. The clean systems still localized the correct sink, and the original
fourth-order derivative recovers the clean native residual to numerical precision. It establishes a measurement
boundary: the residual is exact when \(q\) and \(g\) are adequately observed, but differentiation and transfer
measurement error can create larger false residuals than the concealed term.

## Geometry verdict

The geometry did not disappear uniformly. It separated into two resolutions:

1. **Parent/integrated account:** positive and negative zero-mean errors largely cancelled over the record, leaving
   median integrated error `0.007872`.
2. **Child/local account:** noise spread residual magnitude into inactive identities, reduced sign accuracy and
   obscured which child or relation owned the loss.

In ARA language, the whole-account `Other` remained visible after temporal accumulation, while its local identity
assignment smeared across neighbouring accounts. This is a measurement-resolution effect, not evidence for a new
physical coupling.

The two observed inputs were also not interchangeable. The development-selected smoother acted on \(q\) before
differentiation, but observed transfer \(g\) entered the residual directly. Consequently, transfer noise dominated
the 12 dB failure.

## Target-system breakdown

### Registered white-noise condition

| System | SNR | Location | Sign | Correlation | NRMSE | Integrated error | Inactive spill |
|---|---:|---:|---:|---:|---:|---:|---:|
| capacitor relation | 24 dB | `0.000` | `0.9615` | `0.8170` | `0.0659` | `0.0182` | `0.0928` |
| capacitor relation | 18 dB | `0.000` | `0.8968` | `0.5783` | `0.1313` | `0.0149` | `0.1845` |
| capacitor relation | 12 dB | `0.000` | `0.8016` | `0.3323` | `0.2622` | `0.0502` | `0.3681` |
| quantum state 2 | 24 dB | `1.000` | `0.9478` | `0.9380` | `0.0923` | `0.0030` | `0.0928` |
| quantum state 2 | 18 dB | `1.000` | `0.8648` | `0.8060` | `0.1831` | `0.0020` | `0.1839` |
| quantum state 2 | 12 dB | `1.000` | `0.7601` | `0.5692` | `0.3660` | `0.0039` | `0.3661` |

All 16 quantum 12 dB replicates localized state 2. All 16 capacitor replicates instead selected capacitor 1 rather
than the coupling relation. The validation receipt independently reproduced those counts.

The circuit failure is informative. The true relation has zero storage, and its native `Other` cancels the declared
positive relation transfer. Once each transfer channel is independently corrupted relative to its own RMS,
capacitor 1's larger transfer channel produces a larger false residual budget than the hidden relation loss. The
operator can still reconstruct the relation waveform approximately, but no longer ranks that location first.

### Stored-quantity versus transfer noise at 12 dB

| System | Noise input | Location | Sign | Correlation | NRMSE | Inactive spill |
|---|---|---:|---:|---:|---:|---:|
| capacitor | \(q\) only | `0.8125` | `1.0000` | `0.9201` | `0.0393` | `0.0505` |
| capacitor | \(g\) only | `0.0000` | `0.8077` | `0.3469` | `0.2595` | `0.3655` |
| capacitor | \(q+g\) | `0.0000` | `0.8016` | `0.3323` | `0.2622` | `0.3681` |
| quantum | \(q\) only | `1.0000` | `0.9856` | `0.9787` | `0.0529` | `0.0592` |
| quantum | \(g\) only | `1.0000` | `0.7591` | `0.5672` | `0.3617` | `0.3614` |
| quantum | \(q+g\) | `1.0000` | `0.7601` | `0.5692` | `0.3660` | `0.3661` |

The quantum \(q\)-only condition passes the frozen numeric gates. The capacitor \(q\)-only condition reconstructs
the waveform strongly but misses the 90% location gate (`81.25%`). Adding \(g\) noise causes most of the registered
failure. This identifies a concrete next method problem: storage and transfer uncertainty must be modeled jointly
rather than treating the observed transfer as exact after smoothing only storage.

## Required method controls

Across the same 32 registered target runs:

| Method | Location | Sign | Correlation | NRMSE | Integrated error | Inactive spill |
|---|---:|---:|---:|---:|---:|---:|
| centred local cubic (primary) | `0.500` | `0.7620` | `0.4599` | `0.3139` | `0.00787` | `0.3675` |
| moving average + finite difference | `0.500` | `0.7984` | `0.5415` | `0.3124` | `0.03888` | `0.3530` |
| causal local-linear state estimate | `0.000` | `0.7391` | `0.2317` | `0.3611` | `0.00996` | `0.3959` |
| raw fourth-order difference | `0.000` | `0.5156` | `0.0139` | `47.7264` | `0.02501` | `56.0678` |

The local cubic estimator was enormously better than the raw derivative, but it did not beat the ordinary moving
average on pointwise correlation or NRMSE. Its advantage here was the integrated amount. Smoothing performance is
therefore not ARA-specific evidence.

## Other noise families

At 12 dB with noise on both \(q\) and \(g\):

| System | Family | Location | Correlation | NRMSE | Integrated error |
|---|---|---:|---:|---:|---:|
| capacitor | white | `0.000` | `0.3323` | `0.2622` | `0.0502` |
| capacitor | AR(1) | `0.000` | `0.2554` | `0.3329` | `0.4478` |
| capacitor | impulsive | `0.000` | `0.3321` | `0.2602` | `0.0528` |
| capacitor | drift | `0.000` | `0.2043` | `0.2570` | `0.8148` |
| quantum | white | `1.000` | `0.5692` | `0.3660` | `0.0039` |
| quantum | AR(1) | `0.875` | `0.4627` | `0.4742` | `0.0207` |
| quantum | impulsive | `1.000` | `0.5596` | `0.3661` | `0.0053` |
| quantum | drift | `0.875` | `0.6338` | `0.3526` | `0.1695` |

Zero-mean white and impulsive errors mostly cancel in the integral. Coloured noise and especially drift do not,
which is why the circuit's integrated error rises to `44.8%` and `81.5%`.

The empirical 90% replicate intervals covered approximately `100%` of active points in the primary target
conditions. That is over-coverage, not excellent calibration: the intervals are too broad to be informative at
their nominal 90% level.

## Missingness and timestamp stress tests

The structural tests were secondary and did not decide the verdict.

- With one missing block covering 10% of the record, the quantum waveform retained correlation `0.6773` and NRMSE
  `0.3083`; at 5%, correlation was `0.9236`.
- With timestamp jitter of one full sample interval, the quantum result retained correlation `0.9988` and NRMSE
  `0.0123`.
- The smooth exponential capacitor simulation was almost exactly reconstructed after interpolation even at the
  largest structural severities. This is a property of this simple synthetic trajectory and interpolation, not a
  general missing-data guarantee.

## What changed scientifically

The noiseless result established that the typed residual can localize an omitted term when its inputs are accurate.
O2-A1 supplies the missing robustness boundary:

\[
\boxed{
\text{accurate cumulative closure}
\;\not\Rightarrow\;
\text{accurate local waveform or location}
}
\]

This is useful negative evidence. It prevents the current operator from being carried directly into ECG,
AmeriFlux or ENSO and interpreted physically without an observation-error model.

The best next technical step is a separately frozen **joint \(q,g\) uncertainty model** that outputs both a
residual and a location-confidence measure. It must be developed only on the oscillator and compared with the same
moving-average and state-estimation controls. O2-B can still test clean/noisy ECG identity retention, but it must
remain a signal-robustness test rather than be called physical hidden-`Other` recovery.

## Reproduction

Run from the repository root with a Python environment containing NumPy:

```powershell
python analysis/physics_ladder/o2a1_hidden_other_controlled_noise.py
python analysis/physics_ladder/validate_o2a1_hidden_other_controlled_noise.py
```

Artifacts:

- frozen protocol and receipt:
  `O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_PROTOCOL_v1_FROZEN.md`,
  `O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_PROTOCOL_v1_FROZEN.sha256`;
- runner: `o2a1_hidden_other_controlled_noise.py`;
- result: `O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_RESULTS.json`;
- development selection: `O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_DEVELOPMENT.csv`;
- all trial summaries: `O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_TRIALS.csv.gz`;
- bounded aggregates: `O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_AGGREGATES.csv`;
- representative waveforms: `O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_WAVEFORMS.csv`;
- independent validator and receipt:
  `validate_o2a1_hidden_other_controlled_noise.py`,
  `O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_VALIDATION.json`.

The validator passed `11/11` checks, including protocol and artifact hashes, development-window selection,
independent primary-metric/gate calculation, and clean local-polynomial reproduction through direct non-FFT
convolution.

