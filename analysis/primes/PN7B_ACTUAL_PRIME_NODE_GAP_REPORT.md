# PN7B actual-prime node / traversal-gap report

**Test ID:** `PN7B/ACTUAL-PRIME-NODE-GAP/OPENED-R10-R11-v1`  
**Status:** `DIRECT PAIR CORE SUPPORTED / 6 OF 7 REGISTERED CONDITIONS PASS / OPENED-DATA STRUCTURAL TEST`  
**Independent validation:** `80/80` checks passed after a full re-sieve with different chunk boundaries  
**Protected material:** p31 primorial wheel and R12 remain unopened

## TL;DR

Yes: when the pair is measured directly, actual prime nodes and their incoming/outgoing gaps produce a highly
repeatable ARA shape.

For every internal actual prime, PN7B treated the gap entering the prime and the gap leaving it as the two sides of
one node-centred ARA. It then retained both:

- the **frequency wave** — how often every ARA mix occurs; and
- the **ordered handover** — how one node-gap mix proceeds to the next.

Between R10 and R11:

- frequency correlation is `0.9994386`, with Jensen-Shannon divergence `0.0001781` bits;
- ordered-plane cosine similarity is `0.9990303`, with divergence `0.0006077` bits;
- the immediate node pairing differs from a distant same-inventory gap control by 25.3 times split-half instability
  at R10 and 67.0 times at R11;
- immediate ordered handover differs from a distant same-frequency transition control by 26.9 and 74.3 times
  split-half instability;
- R10 predicts the R11 ARA-frequency distribution better than R9 or the R10 distant-pair control;
- both frequency and ordered-plane distances decrease monotonically across the final rungs.

P1-P6 pass. P7, the frozen even-bin mirror test, fails. That failure is a measurement-grain issue: the exact ridge
and other discrete rational states lie on bin boundaries. The registered failure is preserved. A post-endpoint exact
gap-pair reversal audit gives cosine similarities `0.999928` at R10 and `0.999991` at R11, while mean directed
asymmetry is almost zero. This diagnostic cannot change the declared 6/7 outcome, but it prevents the failed bin
mirror from being mistaken for a large physical direction bias.

The result supports the direct ARA crosswalk and its scale recurrence. It does not generate primes, add information
not present in raw prime gaps, or prove that the mathematical cause is a physical wave.

## What was measured

For three consecutive actual primes,

\[
\underbrace{p_{i-1}}_{\text{previous connection}}
\xrightarrow{\quad\underbrace{g_i^-}_{\text{incoming traversal}}\quad}
\underbrace{p_i}_{\text{measured prime node}}
\xrightarrow{\quad\underbrace{g_i^+}_{\text{outgoing traversal}}\quad}
\underbrace{p_{i+1}}_{\text{next connection}}.
\]

The gaps are

\[
\underbrace{g_i^-}_{\text{distance into the prime node}}=p_i-p_{i-1},
\qquad
\underbrace{g_i^+}_{\text{distance out of the prime node}}=p_{i+1}-p_i.
\]

Their direct ARA reading is

\[
\underbrace{x_i}_{\substack{\text{node-gap location}\\\text{on the 0-2 diameter}}}
=
\frac{2\underbrace{g_i^+}_{\text{outgoing side}}}
{\underbrace{g_i^-}_{\text{incoming side}}+\underbrace{g_i^+}_{\text{outgoing side}}},
\]

or, centred on the ridge,

\[
\underbrace{a_i}_{\substack{\text{directed asymmetry}\\-1<a_i<1}}
=x_i-1
=
\frac{g_i^+-g_i^-}{g_i^-+g_i^+}.
\]

Plainly:

- below `1.0`, the route into the prime is longer than the route out;
- at `1.0`, the two gaps are equal;
- above `1.0`, the route out is longer;
- `g^-+g^+` retains the local traversal size that the reduced ratio omits.

The actual prime is the connecting node. Its two neighbouring gaps supply the directional pair. This is the direct
object Dylan described; it is not the PN7A left/right position proxy.

## The “how often” and ordering waves

For each rung, the test constructed

\[
\underbrace{F_r(b)}_{\substack{\text{frequency appearance}\\\text{how often ARA bin }b\text{ occurs}}}
=
\frac{\#\{i:x_i\in b\}}{\#\{i\}},
\]

and

\[
\underbrace{T_r(b,c)}_{\substack{\text{ordered handover}\\\text{current mix }b\to\text{next mix }c}}
=
\frac{\#\{i:x_i\in b,\ x_{i+1}\in c\}}{\#\{i\}}.
\]

Plainly: `F` says how often each prime-gap relation appears. `T` prevents that frequency curve from flattening the
sequence by recording which relation follows which.

## Why this is not a repeat of the early prime tests

PN1-PN1I used gaps between surviving positions on finite primorial wheels. Those were deterministic candidate
connection geometries. PN2 then used p29-wheel candidate gaps to forecast which candidates survive as actual primes,
and explicitly prohibited actual-prime gaps as predictors.

PN7B instead begins only after the actual primes are known and measures the real consecutive-prime gap sequence.
The same ARA equation is deliberate: the question is whether the form found in the candidate geometry also appears
in the final prime identity.

## Exact data and integrity

| Rung | Interval | Actual primes | Internal measured nodes | Ordered handovers |
|---:|---:|---:|---:|---:|
| R7 | `[10,000,000, 10,100,000)` | 6,241 | 6,239 | 6,238 |
| R8 | `[100,000,000, 101,000,000)` | 54,208 | 54,206 | 54,205 |
| R9 | `[1,000,000,000, 1,010,000,000)` | 482,449 | 482,447 | 482,446 |
| R10 | `[10,000,000,000, 10,100,000,000)` | 4,341,930 | 4,341,928 | 4,341,927 |
| R11 | `[100,000,000,000, 101,000,000,000)` | 39,475,591 | 39,475,589 | 39,475,588 |

The first and last prime in each finite interval are discarded as incomplete nodes. Every other prime contributes
exactly one incoming/outgoing gap state. Prime totals reconcile exactly with PN3A, PN5 and PN6 terminal survivor
counts.

## Registered results

### Cross-rung recurrence

| Rung pair | Frequency correlation | Frequency JSD (bits) | Ordered cosine | Ordered JSD (bits) |
|---|---:|---:|---:|---:|
| R7-R8 | 0.991798 | 0.00111762 | 0.972174 | 0.0193805 |
| R8-R9 | 0.998421 | 0.000396684 | 0.995246 | 0.00323832 |
| R9-R10 | 0.999134 | 0.000243196 | 0.998354 | 0.00106219 |
| **R10-R11** | **0.999439** | **0.000178127** | **0.999030** | **0.000607714** |

The shape is already recognisable at R7 and becomes progressively more stable as the measured population grows and
the decimal rung increases. P1, P2 and P6 pass.

### Does local prime-node pairing add structure beyond the same gap inventory?

The fixed control pairs each gap with one 257 positions away. It preserves the rung's gap inventory but removes the
immediate prime node.

| Rung | Direct-control frequency TV | Split-half TV | Control/noise ratio |
|---|---:|---:|---:|
| R10 | 0.0475043 | 0.00187545 | **25.33** |
| R11 | 0.0425959 | 0.000635760 | **67.00** |

P3 passes. The direct adjacent gaps do not behave like arbitrary gaps drawn from the same rung. Which gap arrives
immediately before and after a prime matters to the distribution of the ARA mix.

### Does immediate handover add structure beyond the state-frequency curve?

The fixed control compares `x_i -> x_(i+257)` rather than `x_i -> x_(i+1)`. It preserves the ARA-state inventory
but removes immediate ordering.

| Rung | Direct-control transition TV | Split-half TV | Control/noise ratio |
|---|---:|---:|---:|
| R10 | 0.210996 | 0.00784546 | **26.89** |
| R11 | 0.207098 | 0.00278617 | **74.33** |

P4 passes. The immediate transition plane contains much more structure than the state-frequency curve alone.

One strict qualification is necessary: consecutive ARA states share a raw gap,

\[
x_i=f(g_i^-,g_i^+),
\qquad
x_{i+1}=f(g_i^+,g_{i+1}^+).
\]

Therefore some immediate dependence is built into the overlapping geometry even if gap values were otherwise
independent. P4 establishes handover beyond state frequency; it does not say how much remains after an independent
gap sequence is projected through the same overlap. That requires the next matched control.

### Rung transfer

Cross-entropy on the R11 node states is:

| Frequency model | Bits per node |
|---|---:|
| **R10 direct frequency** | **4.496505** |
| R9 direct frequency | 4.499156 |
| R10 distant-pair control | 4.506595 |

The advantage is small but correctly directed over tens of millions of exact nodes. P5 passes. This is distribution
transfer after actual primes are known, not prediction of their locations.

## The failed mirror criterion

P7 required reversing the 24 equal ARA bins and obtaining mirror correlation above `0.995`. Registered correlations
are only `0.2698` at R10 and `0.3038` at R11, so P7 fails.

The direct continuous readings tell a different story:

| Audit | R10 | R11 |
|---|---:|---:|
| Mean centred asymmetry | -0.00002577 | +0.00000220 |
| Exact equal-gap ridge share | 2.2879% | 2.0937% |
| Off-ridge directional asymmetry | +0.0001299 | +0.0001079 |
| Exact gap-pair transpose cosine | 0.999928 | 0.999991 |
| Exact gap-pair transpose TV | 0.009112 | 0.003370 |

The even-bin mirror is not the exact reversal operator for discrete ratios that land on bin boundaries, including
the `1.0` ridge. An exact reversal swaps the incoming and outgoing raw gaps. That post-endpoint audit is almost
perfectly symmetric and becomes more symmetric at R11.

Scientific bookkeeping remains strict: the exact audit was added only after P7 failed, so it cannot rescue P7 or
change the 6/7 result. It does identify a specific protocol-design distortion to avoid in future work: the ridge
should be isolated or the reversal should act on exact gap pairs before binning.

## Sensitivity to measurement grain

The principal recurrence and non-triviality results persist at 12, 24 and 48 ARA bins:

| Bins | R10-R11 frequency correlation | Frequency JSD | Ordered cosine | Ordered JSD |
|---:|---:|---:|---:|---:|
| 12 | 0.999707 | 0.00007824 | 0.999586 | 0.00023125 |
| 24 | 0.999439 | 0.00017813 | 0.999030 | 0.00060771 |
| 48 | 0.999265 | 0.00033375 | 0.997579 | 0.00146292 |

Finer grain exposes more child detail and therefore slightly lowers agreement, but all three views remain extremely
close. The direct-control effects remain many times larger than split-half instability at all resolutions.

## Registered decision

| Condition | Result |
|---|---:|
| P1 frequency-wave recurrence | **PASS** |
| P2 ordered-handover recurrence | **PASS** |
| P3 local node pairing is not gap inventory alone | **PASS** |
| P4 immediate handover is not state frequency alone | **PASS** |
| P5 R10 frequency transfers best to R11 | **PASS** |
| P6 scale distances converge | **PASS** |
| P7 frozen even-bin mirror criterion | **FAIL** |

**Direct pair core P1-P4: supported. Total: 6/7 pass.**

## What this means for ARA

The strongest supported ARA statement is:

> Actual primes can be represented as connection nodes between incoming and outgoing traversal gaps. Their direct
> 0-2 relation produces a highly repeatable frequency shape and ordered handover across five decimal rungs. Immediate
> node pairing carries structure beyond the same rung's unpaired gap inventory.

That is a much cleaner result than PN7A because the two sides are now relationally attached to the same actual node.
The “how often” curve and the ordered relation are both present, rather than trying to infer traversal from an
arbitrary left/right decimal-window split.

The scientific boundary is equally important:

- `x=2g+/(g-+g+)` is a one-to-one transform of the ordinary log gap ratio; it is a useful bounded geometry, not new
  raw information;
- actual primes are inputs, so this does not locate unknown primes;
- known modular constraints make consecutive prime gaps dependent;
- shared-gap overlap mechanically creates part of the ordered-plane structure;
- recurrence of one mathematical representation is not proof of a physical universal wave.

Within those boundaries, this is strong evidence that the ARA node/gap geometry is genuinely present and stable in
the actual prime sequence, not only in primorial-wheel candidate geometry.

## Recommended next test

Freeze a PN7C actual-gap memory test before running it:

1. predict the next actual-prime ARA state from the current state;
2. add the previous ARA state to retain arrival direction;
3. compare with a raw-gap first-order model;
4. compare with independently shuffled gap sequences projected through the **same overlapping** ARA construction;
5. train on R9/R10 and score on code-isolated R11.

That would measure how much sequential information remains after both raw one-step gap dependence and mechanical
shared-gap overlap are controlled. It is the appropriate next test of the proposed larger interaction wave; it is
recorded here but was not run after seeing PN7B.

## Reproducibility artifacts

- Protocol: `PN7B_ACTUAL_PRIME_NODE_GAP_PROTOCOL.md`
- Aggregate builder: `pn7b_build_actual_prime_gap_aggregates.py`
- Exact counts: `PN7B_ACTUAL_PRIME_NODE_GAP_AGGREGATES.npz`
- Aggregate metadata: `PN7B_ACTUAL_PRIME_NODE_GAP_AGGREGATES.json`
- Scorer: `pn7b_score_actual_prime_node_gap.py`
- Results: `PN7B_ACTUAL_PRIME_NODE_GAP_RESULTS.json`
- Curve table: `PN7B_ACTUAL_PRIME_NODE_GAP_CURVES.csv`
- Figure: `PN7B_ACTUAL_PRIME_NODE_GAP_FIGURE.png`
- Independent validator: `pn7b_validate_actual_prime_node_gap.py`
- Independent validation: `PN7B_ACTUAL_PRIME_NODE_GAP_VALIDATION.json`
- Executed notebook: `PN7B_ACTUAL_PRIME_NODE_GAP.ipynb`

