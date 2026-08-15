# T387 — full-pulse return-wave result

## Outcome

**NON-MIRRORED TWO-AXIS RETURN**

Both state/path coordinates crossed and returned, closing the median detector loop, but the radial halves were unequal and the return timing was neither physically fixed nor a one-window translation.

This is a retrospective Class-D liquid-scintillator detector result. It does
not provide advance neutrino timing and does not directly observe the proposed
upstream muon handover.

## Exact window comparison

| Window | Events | x_R at pulse minimum | 95% CI | x_R one window later | 95% CI | mirror residual | x_H maximum | return fraction | trough time |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 64 ns | 284 | 1.89124 | [1.88110,1.89763] | 0.67987 | [0.67448,0.68650] | +0.57363 | 1.96226 | 100.0% | 128 ns |
| 128 ns | 284 | 1.84914 | [1.83599,1.85848] | 0.68334 | [0.67743,0.69144] | +0.53755 | 1.57335 | 98.8% | 256 ns |
| 256 ns | 284 | 1.79912 | [1.78397,1.80643] | 0.68758 | [0.68280,0.69621] | +0.48840 | 1.07247 | 99.6% | 464 ns |


## Frozen gates

- PASS — opposite radial half recovered.
- FAIL — approximate radial mirror (`|sum-2|<=0.10`).
- PASS — `x_H` crosses ridge and returns.
- PASS — at least 75% return by `+768 ns`.
- Timing classification: **MIXED / UNDETERMINED**; trough-time slope `1.732`.

## Interpretation

An `x_R` expansion followed by contraction is partly expected from comparing
adjacent RMS windows: activity first enters the current window and later sits
in the previous window. Its timing-scale test determines whether that symmetry
is predominantly instrument-generated or physically anchored.

The stronger claim requires the independent path coordinate to cross its own
ridge and return. If `x_H` remains on one side, the test has recovered a radial
pair inside only one half of the state/path Di-ARA, not a complete local
two-axis wave.

### Post-result extrema observation

The actual median `x_R` expansion peaks and contraction troughs were much more
nearly complementary than the frozen pulse-minimum/one-window-later pair:
their `peak + trough - 2` residuals were
`+0.01958`,
`+0.00133` and
`+0.00381` for
64, 128 and 256 ns. This is exploratory and does not replace the failed frozen
mirror gate. It is partly induced by the same pulse energy moving between the
two adjacent RMS windows, for which `x_R(1/s)=2-x_R(s)` exactly.

## Reproduction

```powershell
python analysis/muon/t387_full_pulse_return_wave.py
python analysis/muon/validate_t387_full_pulse_return_wave.py
```
