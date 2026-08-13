# T346 temporal Di-ARA storage-handover-release protocol v1 (frozen)

**Frozen:** 9 August 2026, before calculating any T346 metric or result  
**Originator:** Dylan La Franchi  
**Operational translation:** Codex  
**Status:** frozen post-T345 mechanism test on an already-opened public source

## 1. Question

T345 recovered distinct straight, coherent-circle and crooked path geometry,
but falsified its registered claim that connection concentration should rise
*after* a circle-like interval. The post-result correction is that Phase-B
connection children may already maintain the recurrent interval and then be
released into the next Phase-A opening:

\[
A_n \longrightarrow B_{\rm stored}
\longrightarrow B_{\rm released}\longrightarrow A_{n+1}.
\]

T346 asks whether that corrected temporal coupling is present. It does not
test a universal source wave, light, gravity, Phi, `e`, or any other exact
irrational landmark.

## 2. Source and evidential status

Use the same six public BAW controlled-weir trajectory files and the same
laboratory/numerical representations used by T344-T345. Source hashes and
condition labels are inherited unchanged.

The source and representations have already been opened. T346 is therefore a
**frozen post-result mechanism test**, not an untouched independent-domain
confirmation. The laboratory and numerical records are two representations
of the same physical system and must not be counted as two independent
domains.

## 3. Declared identity, rung and directions

- Identity: one contiguous particle trajectory inside one hydraulic condition.
- Rung: one fixed `W`-step path block in the recorded `x-z` plane.
- Phase-A observable: directional movement/opening measured by path directness.
- Phase-B-child proxy: concentration of ordered Di-ARA sector transitions.
- Time direction: recorded frame order only.

The primary block size is `W=15` steps. `W=8` and `W=30` are frozen
sensitivity scales. Results are never pooled across these three rungs.

## 4. Non-overlapping block construction

For every contiguous run, begin at its first valid sample and divide its steps
into consecutive non-overlapping `W`-step blocks. Adjacent blocks may share
their boundary point but share no movement step.

Group blocks into non-overlapping triples:

\[
(0,1,2),\ (3,4,5),\ (6,7,8),\ldots
\]

Within each triple, call the blocks `pre`, `centre` and `post`. This prevents
one physical step from being counted in two primary handover events.

For each block calculate the same T345 quantities:

\[
D=\frac{\|p_W-p_0\|}{\sum_j\|v_j\|},
\qquad
G=\frac{|\sum_j\gamma_j|}{\sum_j|\gamma_j|},
\qquad
C=(1-D)G.
\]

`D` is line/direct traversal, `G` is signed-turn consistency, and `C` is
historical circularity.

The Phase-B-child proxy is the T345 Miller-Madow-corrected concentration of
the 16 ordered Di-ARA sector-transition channels:

\[
I_{\rm conn}=\log 16-\widehat H_{MM}.
\]

This is a proxy for organisation/concentration of observed connection
children. It is not total information, total energy, or the complete Phase B.

## 5. Movement-only handover anchors

The primary handover anchor is defined without using `I_conn`:

\[
D_{pre}\ge 0.75,
\quad
D_{centre}\le 0.75,
\quad
G_{centre}\ge0.75,
\quad
D_{post}\ge0.75.
\]

It is therefore a movement-defined
`open traversal -> coherent recurrence -> open traversal` event. Equality is
included. No connection value may change anchor membership.

The frozen crooked control uses the same directness requirements but
`G_centre<=0.25`.

## 6. Frozen temporal quantities

For each eligible anchor define:

\[
S_{build}=I_c-I_{pre},
\qquad
S_{release}=I_c-I_{post},
\]

\[
S_{peak}=I_c-\frac{I_{pre}+I_{post}}2,
\]

\[
O_{in}=D_{pre}-D_c,
\qquad
O_{out}=D_{post}-D_c.
\]

Positive `S_build` means connection concentration increased as Phase A closed
into the recurrent state. Positive `S_release` means connection concentration
decreased as the next Phase A opened. `O_in` and `O_out` measure the geometric
size of those movement-side changes; their positivity follows from anchor
selection and is descriptive, not a test result.

## 7. Primary components and gates

All scalar estimates first average eligible events within each complete
trajectory, then average trajectories equally. Confidence intervals use
`2,000` whole-trajectory cluster bootstraps with seed `34620260809`.

Eligibility requires at least `200` anchors from at least `30` trajectories
overall and at least `30` anchors from `10` trajectories in each of at least
two hydraulic conditions. An ineligible component fails rather than being
silently relaxed.

### Gate A - connection storage at the recurrent interval

All three primary quantities must have a strictly positive 95% cluster CI:

1. mean `S_build`;
2. mean `S_release`;
3. mean `S_peak`.

Each must also be positive separately in at least two of the three hydraulic
conditions.

### Gate B - magnitude-coupled handover

Within each hydraulic condition, convert the relevant magnitudes to average
ranks. Pool the condition-centred ranks and calculate:

\[
\rho_{in}=\operatorname{corr}_{rank}(S_{build},O_{in}),
\qquad
\rho_{out}=\operatorname{corr}_{rank}(S_{release},O_{out}).
\]

Each intact correlation must:

1. have a strictly positive 95% whole-trajectory bootstrap CI;
2. be positive in at least two of three conditions; and
3. exceed a broken-lineage null at one-sided `p<=0.01`.

The broken null uses `1,000` frozen-seed permutations of `O_in` or `O_out`
between different trajectories inside the same
`condition x progress-decile x centre-speed-quintile` stratum. It preserves
local scale and operating regime while destroying the event's own
connection-to-movement pairing. Rows in a stratum without another trajectory
are excluded from both intact and broken scores.

Gate B passes only if both the approach/build and release/opening components
pass.

### Gate C - coherent recurrence versus crooked curvature

The circle-anchor `S_peak` minus crooked-anchor `S_peak` contrast must have a
strictly positive 95% whole-trajectory bootstrap CI and be positive in at
least two of three conditions.

This tests coherent recurrent storage rather than curvature alone.

### Gate D - representation transfer

Laboratory and numerical representations must return the same signs for all
six primary quantities (`S_build`, `S_release`, `S_peak`, `rho_in`,
`rho_out`, circle-minus-crooked `S_peak`) and the same Gate A-C verdicts.

Gate D is a representation-transfer check, not independent-domain evidence.

## 8. Sensitivity and descriptive outputs

Repeat the complete construction at `W=8` and `W=30`. These scales cannot
change the frozen `W=15` verdict. Report sign agreement for all six quantities.

Also report, without promoting them to primary gates:

- median and mean path length and speed at `pre/centre/post`;
- the fraction of all non-overlapping triples selected as circle or crooked;
- condition-specific estimates;
- a three-point `D/I_conn` phase portrait;
- exemplar seven-block neighborhoods chosen only by maximum centre
  circularity among already eligible anchors.

## 9. Required figures

For both representations save one static figure containing:

1. mean `pre -> centre -> post` `D` and `I_conn` profiles with trajectory-level
   bootstrap intervals;
2. a `D` versus `I_conn` phase portrait with time arrows;
3. a release-versus-opening density plot;
4. primary estimates and broken-null comparisons;
5. at least one raw normalized movement example with its temporal ledger.

The figure must label circle-anchor selection as movement-defined and must
state that `I_conn` is a proxy, not the complete Phase B.

## 10. Interpretation boundary

Passing T346 would support a same-system temporal coupling in which ordered
connection children are concentrated during a coherent recurrent interval and
their build/release amount is related to the adjacent Phase-A geometry. It
would not establish conservation, a universal numerical constant, an
ever-present cosmic source wave, light, gravity, or the full ARA ontology.

Failure of Gate A would reject the proposed connection peak in this
coordinate. Failure of Gate B would reject magnitude-coupled handover even if
the mean profile is shaped correctly. Failure of Gate C would show that any
peak is not specific to coherent recurrence. Failed components remain failed
and may not be re-labelled after inspection.
