# PN10B event-centred ARA geometry disclosure

**Status:** post-hoc descriptive analysis only  
**Registered PN10B predictive verdict:** **NULL — unchanged**  
**Fresh interval:** `[4,000,000,000, 4,001,000,000)`  
**Population:** 1,000,000 raw integers; 54,275 `c=0.90` survivors; 45,166 primes; 9,109 late composites  
**Independent validation:** **12/12 checks passed**

## Technical summary

The original brief PN10B verdict hid an important two-layer result.

1. **At the parent factor-survival level, every prime is an exact 1.0 event crest.** A prime has survived all possible factor collisions through `sqrt(n)`, so its parent factor-progress coordinate is exactly `1.0`. Every odd raw offset around these odd primes is an even composite and falls to the parity trough near `0.062701`. The lead/lag trace is therefore a sharp central ridge embedded in a sieve-generated sawtooth.
2. **Inside each prime, the nine paid-gate child waves are strongly asymmetric rather than quiet.** Across all prime-child readings, Phase A spans `0.0000955` to `1.9999044`. The first prime alone has child A values from `0.071972` to `1.435762` and four orientation flips.
3. **Aggregation conceals that local asymmetry.** The pooled child A coordinate across 45,166 primes is `0.999860546`, almost exactly the 1.0 ridge, while individual prime centroids range from `0.499788889` to `1.426638535`.
4. **The registered child proxy is not prime-specific.** The 9,109 surviving composites show nearly the same child-centroid, dispersion, coupling, landmark and flip distributions. Every standardized prime–composite mean difference is below `0.015`. This explains the registered null ranking result without erasing the observed geometry.

Plainly: the **parent prime event is a crest**, but the **paid-gate child centroid is not a crest detector**. The child waves are real, broad and structured; this representation does not distinguish a prime from a composite that also survived the same paid gates.

## What PN10B measured

For candidate integer `n`, PN10B used the nine largest already-paid prime gates `q_j <= n^0.45`:

\[
A_j(n)=2\frac{n\bmod q_j}{q_j},
\qquad
B_j(n)=2-A_j(n).
\]

Each child is one reversible ARA axis: `A_j+B_j=2` exactly. The following summaries were then exposed:

- **child centroid:** `mean_j A_j`; where the nine-child identity sits on the 0–2 line;
- **child dispersion:** `mean_j |A_j-1|`; how far the children spread from the ridge;
- **child adjacent coupling:** `mean_j (A_j-1)(A_(j+1)-1)`; whether neighboring gate children usually occupy the same or opposite side;
- **child flip count:** number of adjacent gate ranks whose signed orientation changes side;
- **parent factor progress:** `1` for a prime and `2 log(LPF(n))/log(n)` for a composite.

The parent coordinate and child coordinate answer different questions. The parent says **how far the factor-collision search travelled before the node closed or failed**. The children say **where the already-paid modular interactions sit inside that candidate**.

## A prime is an exact parent ridge with parity troughs on both sides

The table aligns 45,162 interior primes at raw-integer offset zero. Four boundary primes were excluded only because the full `±32` window would leave the interval.

| Offset | Prime rate | Mean parent progress | Mean child centroid | Mean child spread | Mean adjacent coupling | Mean flips |
|---:|---:|---:|---:|---:|---:|---:|
| -10 | 0.077632 | 0.286800 | 0.999813 | 0.499508 | -0.014115 | 4.1290 |
| -9 | 0 | 0.062701 | 0.999791 | 0.499508 | -0.014100 | 4.1289 |
| -8 | 0.059497 | 0.246121 | 0.999773 | 0.499508 | -0.014098 | 4.1289 |
| -7 | 0 | 0.062701 | 0.999756 | 0.499508 | -0.014079 | 4.1289 |
| -6 | 0.121075 | 0.393391 | 0.999758 | 0.499508 | -0.014067 | 4.1286 |
| -5 | 0 | 0.062701 | 0.999740 | 0.499508 | -0.014065 | 4.1286 |
| -4 | 0.059519 | 0.247668 | 0.999748 | 0.499508 | -0.014087 | 4.1288 |
| -3 | 0 | 0.062701 | 0.999774 | 0.499508 | -0.014078 | 4.1287 |
| -2 | 0.059475 | 0.246652 | 0.999796 | 0.499508 | -0.014086 | 4.1286 |
| -1 | 0 | 0.062701 | 0.999789 | 0.499508 | -0.014073 | 4.1286 |
| **0** | **1.000000** | **1.000000** | **0.999884** | **0.499508** | **-0.014073** | **4.1287** |
| +1 | 0 | 0.062701 | 0.999872 | 0.499508 | -0.014075 | 4.1287 |
| +2 | 0.059475 | 0.245640 | 0.999859 | 0.499508 | -0.014077 | 4.1285 |
| +3 | 0 | 0.062701 | 0.999891 | 0.499508 | -0.014082 | 4.1284 |
| +4 | 0.059519 | 0.245671 | 0.999888 | 0.499508 | -0.014093 | 4.1286 |
| +5 | 0 | 0.062701 | 0.999909 | 0.499508 | -0.014111 | 4.1289 |
| +6 | 0.121075 | 0.394463 | 0.999872 | 0.499508 | -0.014091 | 4.1288 |
| +7 | 0 | 0.062701 | 0.999865 | 0.499508 | -0.014093 | 4.1289 |
| +8 | 0.059497 | 0.247569 | 0.999857 | 0.499508 | -0.014091 | 4.1290 |
| +9 | 0 | 0.062701 | 0.999849 | 0.499508 | -0.014071 | 4.1287 |
| +10 | 0.077632 | 0.286791 | 0.999857 | 0.499508 | -0.014062 | 4.1288 |

This is the event-centred crest/trough pattern:

- **offset 0:** exact parent crest/ridge `1.0`;
- **every odd offset:** even-number trough `~0.062701`, because the least factor is 2;
- **even offsets:** intermediate daughter crests and troughs set by their least factor and by whether another prime occurs at that separation;
- **offset ±6:** the largest nearby mean shoulders in this window (`~0.393–0.394`) because prime pairs separated by six are more common than pairs at many neighboring even offsets;
- **child centroid:** almost flat through the event, changing by only roughly `0.00017` across the displayed population mean.

The parent crest is exact but not an advance prediction. Assigning `1.0` requires knowing that the candidate survived every divisor gate through its square root. The neighboring sawtooth is established parity and sieve structure expressed in the ARA coordinate.

## The child waves at the prime are broad, alternating and locally asymmetric

Across all 406,494 prime-child readings:

| Statistic | Pooled child Phase A |
|---|---:|
| Mean | 0.999860546 |
| Median | 0.999856370 |
| Standard deviation | 0.576870871 |
| 1st percentile | 0.019809560 |
| 10th percentile | 0.200602957 |
| 25th percentile | 0.499353758 |
| 75th percentile | 1.499544867 |
| 90th percentile | 1.798151961 |
| 99th percentile | 1.979782901 |
| Minimum | 0.000095516 |
| Maximum | 1.999904439 |

So `~1.0` is a population cancellation result. It does **not** mean that each prime contains nine children sitting near 1.0.

At the level of one prime node, the nine-child centroid has this distribution:

| Statistic | Prime child centroid |
|---|---:|
| Mean | 0.999860546 |
| Median | 1.032589083 |
| Standard deviation | 0.200419075 |
| 1st percentile | 0.545169630 |
| 10th percentile | 0.708424398 |
| 25th percentile | 0.858132973 |
| 75th percentile | 1.158133553 |
| 90th percentile | 1.241486627 |
| 99th percentile | 1.345398604 |
| Minimum | 0.499788889 |
| Maximum | 1.426638535 |

The median being `1.032589` while the mean is `0.999861` also shows that the node-centroid distribution is not perfectly symmetric in its finite sample: a longer lower tail pulls the mean back toward the ridge.

## The nine gate ranks cancel in the population but not inside an individual prime

| Child rank | Mean A across primes | Median A | 10th percentile | 90th percentile | Share below ridge |
|---:|---:|---:|---:|---:|---:|
| 1 | 1.001839 | 1.002197 | 0.202590 | 1.795548 | 49.858% |
| 2 | 1.002429 | 1.006069 | 0.198757 | 1.800239 | 49.677% |
| 3 | 0.997506 | 0.996463 | 0.200928 | 1.799885 | 50.182% |
| 4 | 1.006585 | 1.010000 | 0.202019 | 1.799655 | 49.522% |
| 5 | 0.991096 | 0.985310 | 0.197100 | 1.795866 | 50.715% |
| 6 | 1.005738 | 1.008089 | 0.202039 | 1.797913 | 49.597% |
| 7 | 0.992116 | 0.984916 | 0.197577 | 1.795480 | 50.753% |
| 8 | 1.000843 | 1.001964 | 0.204033 | 1.798189 | 49.916% |
| 9 | 1.000593 | 1.002877 | 0.199453 | 1.799779 | 49.858% |

Every rank separately covers almost the full ARA line. The rank means do not form a large common crest or trough; their deviations from 1.0 are at most about `0.009`.

### Worked prime: 4,000,000,007

The first prime in the interval has nine-child centroid `0.591385104`, dispersion `0.585064584`, adjacent coupling `-0.012118145`, and four ridge-side flips.

| Rank | Paid gate `q` | Remainder | Phase A | Phase B | `A-1` | Coupling to next child |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20,929 | 7,669 | 0.732859 | 1.267141 | -0.267141 | +0.026777 |
| 2 | 20,921 | 9,412 | 0.899766 | 1.100234 | -0.100234 | +0.081753 |
| 3 | 20,903 | 1,927 | 0.184375 | 1.815625 | -0.815625 | -0.355419 |
| 4 | 20,899 | 15,003 | 1.435762 | 0.564238 | +0.435762 | -0.404400 |
| 5 | 20,897 | 752 | 0.071972 | 1.928028 | -0.928028 | -0.332476 |
| 6 | 20,887 | 14,185 | 1.358261 | 0.641739 | +0.358261 | -0.317526 |
| 7 | 20,879 | 1,187 | 0.113703 | 1.886297 | -0.886297 | +0.661082 |
| 8 | 20,873 | 2,652 | 0.254108 | 1.745892 | -0.745892 | +0.543263 |
| 9 | 20,857 | 2,833 | 0.271659 | 1.728341 | -0.728341 | — |

This prime is not locally balanced. Six of its nine children are well below the ridge, two are above it, and one is nearer the ridge. The sequence crosses sides four times. Its parent still closes at 1.0 because these children are not the same coordinate as the completed factor-survival walk.

### The immediate neighborhood of the worked prime

| Offset | Integer | Prime? | Least factor | Parent progress | Child centroid |
|---:|---:|---:|---:|---:|---:|
| -7 | 4,000,000,000 | no | 2 | 0.062701 | 0.590715 |
| -6 | 4,000,000,001 | no | 47 | 0.348279 | 0.590811 |
| -5 | 4,000,000,002 | no | 2 | 0.062701 | 0.590906 |
| -4 | 4,000,000,003 | no | 23,687 | 0.911161 | 0.591002 |
| -3 | 4,000,000,004 | no | 2 | 0.062701 | 0.591098 |
| -2 | 4,000,000,005 | no | 3 | 0.099379 | 0.591194 |
| -1 | 4,000,000,006 | no | 2 | 0.062701 | 0.591289 |
| **0** | **4,000,000,007** | **yes** | — | **1.000000** | **0.591385** |
| +1 | 4,000,000,008 | no | 2 | 0.062701 | 0.591481 |
| +2 | 4,000,000,009 | yes | — | 1.000000 | 0.591577 |
| +3 | 4,000,000,010 | no | 2 | 0.062701 | 0.591672 |
| +4 | 4,000,000,011 | no | 3 | 0.099379 | 0.591768 |
| +5 | 4,000,000,012 | no | 2 | 0.062701 | 0.591864 |
| +6 | 4,000,000,013 | no | 569 | 0.573859 | 0.591959 |
| +7 | 4,000,000,014 | no | 2 | 0.062701 | 0.592055 |
| +8 | 4,000,000,015 | no | 5 | 0.145588 | 0.592151 |
| +9 | 4,000,000,016 | no | 2 | 0.062701 | 0.592247 |
| +10 | 4,000,000,017 | no | 3 | 0.099379 | 0.592342 |

This single example makes the two geometries visible. The parent coordinate spikes at the prime and at its twin prime two steps later. The paid-gate child centroid instead moves as a slow local ramp. It does not know that offset zero is special.

## ARA landmark occupancy is almost mirror-balanced

| ARA region | Prime-child share | Survivor-composite-child share |
|---|---:|---:|
| `0–0.25`, left singularity well | 12.4651% | 12.4358% |
| `0.25–0.381966`, left inner-to-handover | 6.6328% | 6.6271% |
| `0.381966–1`, left handover-to-ridge | 30.9107% | 30.9377% |
| `1–1.618034`, ridge-to-right handover | 30.9119% | 31.0279% |
| `1.618034–1.75`, right handover-to-inner | 6.6618% | 6.6576% |
| `1.75–2`, right singularity well | 12.4176% | 12.3138% |

The prime children are distributed almost as a uniform traversal of the 0–2 axis: roughly half below the ridge and half above it, with the outer wells occupied as often as their widths imply. This is why the pooled mean lands at 1.0. It is also why these particular children do not rank primes—the surviving composites traverse the same regions at nearly identical rates.

## Flip structure is rich but also shared by late composites

There are eight possible adjacent boundaries among nine children. In this interval, both populations exhibited one through six side flips; no node exhibited zero, seven or eight flips.

| Flip count | Prime count | Prime share | Composite count | Composite share |
|---:|---:|---:|---:|---:|
| 1 | 1,152 | 2.5506% | 234 | 2.5689% |
| 2 | 7,714 | 17.0792% | 1,481 | 16.2586% |
| 3 | 6,667 | 14.7611% | 1,320 | 14.4912% |
| 4 | 10,149 | 22.4704% | 2,085 | 22.8894% |
| 5 | 7,607 | 16.8423% | 1,625 | 17.8395% |
| 6 | 11,877 | 26.2963% | 2,364 | 25.9524% |

The prime mean is `4.128637` flips and the survivor-composite mean is `4.150291`. The slightly higher composite value is only `0.0145` pooled standard deviations away—far too small to act as a useful separator here.

## Extreme prime nodes show the available geometric range

| Selected prime | `n` | Child centroid | Spread | Adjacent coupling | Flips | Minimum A | Maximum A |
|---|---:|---:|---:|---:|---:|---:|---:|
| First prime | 4,000,000,007 | 0.591385 | 0.585065 | -0.012118 | 4 | 0.071972 | 1.435762 |
| Lowest centroid | 4,000,605,341 | 0.499789 | 0.652710 | +0.012294 | 4 | 0.000096 | 1.365233 |
| Centroid nearest ridge | 4,000,903,211 | 1.000034 | 0.444872 | -0.190305 | 6 | 0.451311 | 1.870903 |
| Highest centroid | 4,000,018,019 | 1.426639 | 0.632021 | +0.258945 | 1 | 0.454107 | 1.998849 |
| Maximum spread | 4,000,625,201 | 0.844441 | 0.665170 | +0.104208 | 3 | 0.001054 | 1.907738 |

Three details matter:

- a centroid close to 1.0 can coexist with **six flips** and large individual asymmetries;
- a strongly phase-A-heavy node (`1.426639`) can remain mostly on one side with only one flip;
- large spread and centroid direction are separate geometric coordinates.

That is precisely the sort of information lost by reporting only the final log-loss verdict.

## Prime versus late-composite differences are negligible in this child representation

| Child summary | Prime mean | Survivor-composite mean | Raw difference | Standardized difference |
|---|---:|---:|---:|---:|
| Centroid | 0.999861 | 0.998614 | +0.001246 | +0.00622 |
| Dispersion | 0.499517 | 0.499724 | -0.000208 | -0.00221 |
| Adjacent coupling | -0.014076 | -0.015149 | +0.001073 | +0.00904 |
| Flip count | 4.128637 | 4.150291 | -0.021654 | -0.01446 |

This is the bridge to the registered result. The geometry exists, but the tested geometry belongs almost equally to primes and late composites. Therefore ARA full achieved AUC `0.500307` and did not beat the parent forecast on fresh log loss.

## What the result establishes—and what it does not

### Established or exactly recovered

- The factor-survival coordinate has an exact prime ridge at `1.0`.
- Its neighboring raw-integer trace contains a parity trough and sieve-period shoulders.
- Individual prime nodes contain wide 0–2 paid-gate child traversals, multiple side changes and nontrivial adjacent coupling.
- Population aggregation can conceal those local child asymmetries by cancelling at the ridge.
- The descriptive geometry is reproducible on every integer in the declared fresh interval.

### Not established

- The parent crest is not a new prime prediction; it is the completed factor test expressed in ARA coordinates.
- The nine paid-gate children do not provide a useful pre-prime crest/trough warning in PN10B.
- The near-1.0 pooled child result is not prime-specific; late composites show the same cancellation.
- This post-hoc analysis cannot overturn the registered PN10B null.
- It remains unresolved whether these paid-gate residues are the correct **internal prime child waves** in the intended ARA ontology or only a gate-relative proxy.

## Recommended next confirmatory test

Before opening another interval, freeze three objects separately:

1. **parent event coordinate:** the factor-survival walk, already defined;
2. **internal prime children:** a native ARA definition chosen without looking at the new target;
3. **event warning rule:** the precise crest, trough, flip or crossing expected at fixed lead offsets.

Then report two verdicts side by side:

- **predictive verdict:** did the frozen warning rank unseen prime events above controls?;
- **geometry verdict:** what child, parent and lead/lag structure appeared, including negative and shared structure.

The second verdict must never again be omitted merely because the first is null.

## Artifacts

- `pn10b_event_geometry_diagnostic.py` — reproducible analysis
- `PN10B_EVENT_GEOMETRY_RESULTS.json` — complete summary statistics and definitions
- `PN10B_EVENT_CENTERED_TRACES.csv` — all 130 event-profile rows (`2 populations × 65 offsets`)
- `PN10B_CHILD_LANDMARK_COUNTS.csv` — ARA landmark occupancy
- `PN10B_PRIME_CHILD_EXAMPLES.csv` — exact nine-child vectors for five prime examples
- `PN10B_EXAMPLE_NEIGHBORHOODS.csv` — lead/at/lag values around the examples
- `PN10B_EVENT_GEOMETRY_FIGURE.png` — four-panel visual summary
- `PN10B_EVENT_GEOMETRY_DIAGNOSTIC.ipynb` — executed reader-facing notebook
- `PN10B_EVENT_GEOMETRY_VALIDATION.json` — independent 12-check validation

