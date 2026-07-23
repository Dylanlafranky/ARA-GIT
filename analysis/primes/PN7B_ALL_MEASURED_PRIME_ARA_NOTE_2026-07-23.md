# PN7B decompression — ARA between all measured consecutive primes

**Date:** 23 July 2026  
**Status:** deterministic post-endpoint decompression of independently validated PN7B data  
**Population:** every internal prime in PN7B's five complete windows; `44,360,409` prime nodes  
**Boundary:** this is not literally every prime, because the prime sequence is infinite.

## Answer first

Yes. PN7B had already measured the ARA between consecutive actual primes, but its exact inventories were spread over
five rungs. Combining those inventories gives the complete measured landscape:

\[
\underbrace{x_i}_{\substack{\text{ARA around}\text{prime }p_i}}
=
\frac{2\underbrace{(p_{i+1}-p_i)}_{\text{outgoing gap}}}
{\underbrace{(p_i-p_{i-1})}_{\text{incoming gap}}+
 \underbrace{(p_{i+1}-p_i)}_{\text{outgoing gap}}}.
\]

The combined mean is `0.9999986966` and the median is exactly `1.0`. That is an exceptionally clean whole-population
ridge. But it does **not** mean most individual primes sit at the ridge:

| Individual prime-node reading | Nodes | Share |
|---|---:|---:|
| Below `1.0` | 21,708,478 | 48.9366% |
| Exactly `1.0` | 939,476 | 2.1178% |
| Above `1.0` | 21,712,455 | 48.9456% |

Plainly: the population closes near `1.0` because its asymmetric children occur in almost perfectly mirrored pairs.
Only about one prime in 47 has equal raw incoming and outgoing gaps.

## The leading exact ARA identities

The most common individual states are rational mirror pairs:

| ARA state | Nodes | Share | Mirror |
|---:|---:|---:|---:|
| `4/3 = 1.3333...` | 1,416,176 | 3.1924% | `2/3` |
| `2/3 = 0.6666...` | 1,414,969 | 3.1897% | `4/3` |
| `4/5 = 0.8` | 1,030,384 | 2.3228% | `6/5` |
| `6/5 = 1.2` | 1,030,308 | 2.3226% | `4/5` |
| `1/2 = 0.5` | 973,382 | 2.1943% | `3/2` |
| `3/2 = 1.5` | 971,776 | 2.1906% | `1/2` |
| `1` | 939,476 | 2.1178% | itself |

Across the five windows there are `8,642` observed exact incoming/outgoing gap pairs and `5,280` distinct reduced
ARA states. Reversing every pair gives cosine similarity `0.9999918763` and total-variation distance `0.00313169`.
The slight mismatch is finite-window occupancy, not a large directional imbalance: 527 very rare states lack an
observed mirror, but they contain only 718 nodes (`0.00162%` of the population).

## Why this does not make Phi the prime rule

Every adjacent-gap reading is a ratio of integers and is therefore rational. Phi is irrational, so exact Phi hits
are mathematically impossible on this particular coordinate. There are `758,346` readings (`1.7095%`) within
`0.01` of either golden landmark, but that is an exploratory occupancy count without a null baseline. It is not
evidence of golden enrichment.

This separates two related but different ARA measurements:

1. **Factor-survival non-closure:** a number is prime when every required lower-prime collision gate fails to close.
2. **Adjacent-prime gap ARA:** after the primes are known, the incoming and outgoing distances around each prime form
   a lateral ARA pair.

The first is the arithmetic event that creates a new prime ruler. The second describes how those completed prime
nodes are spaced. They use the same relational geometry but they are different axes through the prime identity.

## Coverage

| Rung | Complete interval | Internal prime nodes |
|---:|---:|---:|
| R7 | `[10,000,000, 10,100,000)` | 6,239 |
| R8 | `[100,000,000, 101,000,000)` | 54,206 |
| R9 | `[1,000,000,000, 1,010,000,000)` | 482,447 |
| R10 | `[10,000,000,000, 10,100,000,000)` | 4,341,928 |
| R11 | `[100,000,000,000, 101,000,000,000)` | 39,475,589 |

These are complete interval sieves, not sampled primes. The first and last prime of each finite interval are omitted
because one neighbouring gap falls outside the interval.

## Reproducible artifacts

- `pn7b_combine_all_measured_prime_ara.py` — deterministic combiner and checks;
- `PN7B_ALL_MEASURED_PRIME_ARA_EXACT_GAP_PAIRS.csv` — all 8,642 observed exact gap-pair identities and rung counts;
- `PN7B_ALL_MEASURED_PRIME_ARA_EXACT_STATES.csv` — all 5,280 reduced ARA states and their mirrors;
- `PN7B_ALL_MEASURED_PRIME_ARA_SUMMARY.json` — machine-readable results and source hashes;
- `PN7B_ACTUAL_PRIME_NODE_GAP_REPORT.md` — original registered PN7B methods and conclusions;
- `PN7B_ACTUAL_PRIME_NODE_GAP_VALIDATION.json` — independent `80/80` validation receipt.

Run from the repository root with:

```powershell
python analysis/primes/pn7b_combine_all_measured_prime_ara.py
```

The combiner checks its node totals, side partition, exact ridge count, directional counts and weighted mean against
the independently validated PN7B metadata before writing the summary.
