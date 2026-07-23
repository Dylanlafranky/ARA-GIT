# O2-A2 declared-child downstream time-stream lineage

**Run:** 23 July 2026  
**Frozen rating:** **NOT SUPPORTED `[pre-registered; synthetic conditional tracking]`**  
**Frozen gates:** `6/8` passed  
**Independent validation:** `12/12` checks passed  
**Protocol SHA-256:** `bea32f164f3d2dd3f4df211c5f7bca5b630c390bff9a211b3916659e54f5f712`  
**Fidelity SHA-256:** `3437518df06a178a549b4cedddea119545e79f77f2763d908bd65c7e1967d777`

## Technical summary

The exact preregistered claim is **not supported**, but the proposed direction produced a real, bounded improvement.
At the registered 12 dB condition, staying with the predeclared moving child reduced median NRMSE by `10.84%`
relative to repeatedly selecting the currently strongest child. It had lower NRMSE in both target systems, beat
zero-`Other` when pooled, and achieved median correlation `0.7638`, NRMSE `0.1681` and active-point sign accuracy
`0.9335`.

Two gates failed:

- correlation improved by `+0.0600`, short of the frozen `+0.10` requirement;
- median integrated error was `0.3538`, just above the frozen `0.35` limit.

The second miss is not safely described as a rounding accident. It hides a strong system difference: quantum
integrated error was `5.26%`, while the capacitor relation's was `177.10%`. The causal time-stream tracker retained
the circuit loss's local shape but badly biased its accumulated amount. The result therefore supports a modest
**conditional branch-following advantage**, not the stronger claim that the frozen operator robustly preserves
every time-stream account.

## Registered 12 dB gates

| Gate | Result | Frozen requirement | Pass? |
|---|---:|---:|:---:|
| fixed-lineage correlation | `0.7638` | at least `0.40` | yes |
| fixed-lineage peak-NRMSE | `0.1681` | at most `0.35` | yes |
| fixed-lineage sign accuracy | `0.9335` | at least `0.75` | yes |
| fixed-lineage integrated error | `0.3538` | at most `0.35` | **no** |
| correlation advantage over re-selection | `+0.0600` | at least `+0.10` | **no** |
| relative NRMSE improvement over re-selection | `10.84%` | at least `10%` | yes |
| pooled NRMSE below zero-`Other` | `0.1681` vs `0.2169` | lower | yes |
| NRMSE below re-selection in both targets | `2/2` systems | both | yes |

The status vocabulary is fixed by the test protocol: failure of either frozen gate prevents `SUPPORTED`, even
though both misses are close in the pooled summary.

## The two target systems did not behave alike

| Target at 12 dB | Method | Correlation | NRMSE | Sign | Integrated error | Declared-child occupancy |
|---|---|---:|---:|---:|---:|---:|
| capacitor relation | fixed time stream | `0.8187` | `0.1293` | `1.0000` | `1.7710` | `1.000` by declaration |
| capacitor relation | repeated re-selection | `0.7894` | `0.1350` | `1.0000` | `1.2675` | `0.175` |
| quantum state 2 | fixed time stream | `0.7583` | `0.1742` | `0.9019` | `0.0526` | `1.000` by declaration |
| quantum state 2 | repeated re-selection | `0.6438` | `0.2345` | `0.7310` | `0.2683` | `0.506` |

The quantum target is the clean positive case. Fixed lineage improved correlation by `0.1145` using the
median-of-method summaries and reduced NRMSE by about `25.7%`. It also preserved the integrated amount.

The capacitor target is mixed. Fixed lineage improved shape only slightly and did not beat the zero-`Other` NRMSE
control (`0.1293` versus `0.0932`). Its integrated amount was badly wrong. The compressed-parent control instead
had circuit NRMSE `0.0649` and integrated error `0.3643`. That distinction is consistent with Dylan's correction:
the time-side stream follows local movement, while a space/storage-side account may be better represented by
maintaining the broader stored whole. It does not prove that ontology; it identifies the exact numerical split
that a later space-side test can examine.

## Fixed identity helped most when re-selection became unstable

At 12 dB, the repeated selector stayed on the declared capacitor relation for only `17.5%` of samples and made a
median `29` switches. It stayed on quantum state 2 for `50.6%` and made `51` switches. Fixed lineage does not earn
location credit here: occupancy is `100%` because the child was given in advance.

The post-hoc paired description nevertheless shows that the improvement was not carried by only one or two seeds:

| Population | Correlation wins | Median paired correlation gain | NRMSE wins | Median paired NRMSE reduction |
|---|---:|---:|---:|---:|
| both targets (`n=32`) | `87.5%` | `+0.0412` | `93.75%` | `0.0180` |
| capacitor (`n=16`) | `75%` | `+0.0237` | `87.5%` | `0.0071` |
| quantum (`n=16`) | `100%` | `+0.0816` | `100%` | `0.0456` |

The pooled 90% paired-bootstrap intervals were `[+0.0238,+0.0506]` for median correlation gain and
`[0.0121,0.0405]` for median NRMSE reduction. These intervals were calculated after the frozen verdict and are
descriptive; they cannot replace the missed preregistered `+0.10` gate.

## The causal trajectory memory did most of the denoising

The selected development settings were a trailing cubic derivative spanning `4%` of the record and a causal
exponential half-life spanning `2%`. They were chosen using only the first 60% of the oscillator under fresh
12 dB noise.

Without trajectory memory, the 12 dB target residuals were poor:

| System | Fixed child without memory: correlation | Without-memory NRMSE | Fixed-lineage correlation | Fixed-lineage NRMSE |
|---|---:|---:|---:|---:|
| capacitor | `0.1671` | `0.5228` | `0.8187` | `0.1293` |
| quantum | `0.3748` | `0.6964` | `0.7583` | `0.1742` |

This is an important methodological fence. Exponential smoothing and causal polynomial estimation are standard
signal-processing tools. Their success is not uniquely ARA evidence. The ARA-specific proposition tested here is
the **fixed branch declaration** relative to an identical filter that repeatedly reselects from the parent.

## Noise-ladder geometry

The clearest downstream benefit appeared in the quantum target as noise increased:

| SNR | Fixed correlation | Re-selection correlation | Fixed NRMSE | Re-selection NRMSE | Re-selection occupancy |
|---:|---:|---:|---:|---:|---:|
| 24 dB | `0.7719` | `0.7766` | `0.1617` | `0.1613` | `0.785` |
| 18 dB | `0.7738` | `0.7591` | `0.1620` | `0.1769` | `0.637` |
| 12 dB | `0.7583` | `0.6438` | `0.1742` | `0.2345` | `0.506` |
| 6 dB | `0.6100` | `0.2166` | `0.2628` | `0.4100` | `0.345` |
| 0 dB | `0.4066` | `0.2091` | `0.4452` | `0.6546` | `0.327` |
| -6 dB | `0.2492` | `-0.0069` | `0.8668` | `1.2149` | `0.254` |

At high SNR, the correct stream was loud enough that re-selection nearly matched fixed lineage. As noise increased,
re-selection occupancy fell and the fixed path separated. This is the closest measured analogue of the coloured
river description: the benefit appears when neighbouring streams make repeated local choice unreliable.

The capacitor followed the same NRMSE direction but not the same integral behaviour. Its declared relation was
rarely selected even at 24 dB, yet repeated selection retained similar waveform correlation because the coupled
capacitor channels share much of the same parent trajectory. This is evidence that “same coloured water” must be
defined by typed identity, not merely by similar shape.

## Scope, definitions and validation

This test used the same deterministic oscillator, capacitor and open two-level probability systems as O2-A1.
Noise was added after clean generation to stored quantities and transfers independently. Six white-noise SNRs and
sixteen fresh deterministic target seeds were scored. The target waveform was the native omitted sink on the child
named before the run.

The independent validator passed `12/12` checks:

- protocol and fidelity hashes;
- artifact row counts;
- development minimum;
- all primary metric and gate calculations;
- both system comparisons;
- direct deterministic reproduction of a capacitor target run;
- direct re-selection occupancy and switch count;
- an aggregate-table spot check.

## Limitations and what this establishes

**Established by this run**

- Given the correct child, fixed downstream tracking usually improves local waveform recovery over repeatedly
  choosing the strongest child under moderate noise.
- The improvement is strong in the quantum target, modest in the capacitor, and present in paired NRMSE for
  `30/32` registered runs.
- Movement waveform recovery and cumulative closure can fail independently.

**Not established**

- the frozen universal conditional-tracking claim, because two gates failed;
- discovery of an unknown child;
- a general time-wave law;
- space-side information retention;
- upstream recursive recovery;
- forward prediction, natural-data attribution or a new denoising theorem.

## Recommended next steps

1. Preserve O2-A2 as the honest negative-with-structure result. Do not loosen its gates after seeing the data.
2. Develop a joint causal state model for noisy \(q\) and \(g\) that controls circuit integral bias, using a new
   development system and untouched target systems.
3. Register the complementary **space-side maintenance test** separately: follow stored identity rather than
   movement and compare fixed storage with child-local traversal.
4. Continue to O2-B only as calibrated ECG identity retention, not as a physical hidden-`Other` claim.

## Reproduction

From `analysis/physics_ladder` with NumPy available:

```powershell
python o2a2_time_stream_lineage.py
python validate_o2a2_time_stream_lineage.py
```

Artifacts:

- fidelity packet and hash receipt;
- frozen protocol and hash receipt;
- `o2a2_time_stream_lineage.py`;
- development, trial, aggregate and bounded waveform CSVs;
- `O2A2_TIME_STREAM_LINEAGE_RESULTS.json`;
- `validate_o2a2_time_stream_lineage.py`;
- `O2A2_TIME_STREAM_LINEAGE_VALIDATION.json`.

