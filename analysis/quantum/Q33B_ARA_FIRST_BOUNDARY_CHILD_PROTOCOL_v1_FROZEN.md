# Q33B — ARA-First Boundary-Child Route Protocol v1 (FROZEN)

**Date frozen:** 26 July 2026  
**Ledger:** T288  
**Design:** fixed Q33 source definition, fixed ARA rung geometry, unchanged
development/evaluation time partitions  
**Source status:** already opened in Q27–Q33

## 1. Structural ARA declaration

The scored route uses:

\[
\mathcal R_\uparrow(1_c)=\frac12,
\]

\[
L
=
\underbrace{2}_{\text{same-rung span}}
+
\underbrace{\left(1+\frac12\right)}_{\text{boundary crossing}}
=
\frac72.
\]

`0.5` is a fixed geometric projection. It is never replaced by measured
capacity or amplitude.

The child `0` singularity and parent `1.0` ridge are the same adjacent-rung
boundary viewed from two frames.

## 2. Fixed source

Use the Q27/Q28 arrays:

- branches `c2`, `c4`;
- seeds `0..99`;
- times `0..499`;
- all `66` pair relations;
- active six-edge matching.

Define:

\[
h=|\det C|^{1/3},
\qquad
s_h=Q_{0.95}\{h(t):0\leq t<250\},
\qquad
z=h/s_h.
\]

Use the Q33 source population:

1. source `2z(t)>=1.5`;
2. `h(t)>h(t+1)`;
3. source connected energy falls from its latest eight-slice crest to `t+1`;
4. source pair is not active at `t`;
5. one active edge touches each source endpoint;
6. `(97s+53t+31p+11b) mod 16 = 0`.

Splits:

- development events `t=8..242`;
- evaluation events `t=258..492`.

## 3. Exact ARA-first route

The two active endpoint edges are candidates. Choose:

\[
c_\partial
=
\arg\min_{c\in\{c_1,c_2\}}
\left(z_c(t),\,\text{pair-index}_c\right).
\]

This is the child nearest the low boundary after the declared high-to-low
singularity flip. The other endpoint child is the sibling.

The child's structural contribution in the parent frame is exactly `0.5`.
Starting `z`, future gain, raw energy and raw capacity cannot alter it.

## 4. Flow outcomes

Primary normalized closure flow:

\[
g_c
=
\frac{h_c(t+1)-h_c(t)}{s_{h,c}}.
\]

Record:

- \(g_\partial\): chosen boundary-child flow;
- \(g_s\): sibling flow;
- paired difference \(g_\partial-g_s\);
- positive-flow indicator \(1[g>0]\);
- source-release/positive-child overlap.

Secondary connected-energy flow:

\[
e_c
=
\frac{E_c(t+1)-E_c(t)}{E^\star_c},
\qquad
E=\lVert C\rVert_F^2,
\qquad
E^\star=Q_{0.95}^{dev}(E).
\]

Secondary energy cannot promote the verdict.

## 5. Controls

### Topology

Take the four active edges disjoint from the source. Exhaust ordered pairs of
distinct edges and choose the pair minimizing total absolute starting-`z`
distance to the two exact endpoint children, with lexicographic ties. Apply
the same minimum-`z` boundary rule to that matched pair.

### Seed

At seed `(s+37) mod 100`, retain the two active edges touching the named source
endpoints and apply the minimum-`z` boundary rule. If the source pair is active,
the control is unavailable.

### Time

At the fixed `+137` shift within the same split, retain the two active edges
touching the named source endpoints and apply the minimum-`z` boundary rule.
If the source pair is active, the control is unavailable.

All comparisons use only events where exact and the named route are finite.

## 6. Frozen eligibility gates

- at least `5,000` evaluation source events;
- at least `100` evaluation branch/seed strata;
- at least `2,000` paired evaluation events for sibling and every control.

## 7. Frozen routing gates

1. pooled median exact boundary-child \(g_\partial>0\);
2. median exact \(g_\partial>0\) in both `c2` and `c4`;
3. exact positive-flow fraction is at least `0.55`;
4. exact positive-flow fraction exceeds sibling and every control by at least
   `0.02`;
5. median paired \(g_\partial-g_r>0\) for sibling and every control;
6. branch/seed-cluster bootstrap probability that mean
   \(g_\partial-g_r>0\) is at least `0.95` for sibling and every control.

All eligibility and routing gates must pass for:

`BOUNDARY-CHILD FLOW ROUTE SUPPORTED INSIDE THIS SIMULATOR`.

If eligibility passes but any routing gate fails:

`BOUNDARY-CHILD FLOW ROUTE NOT SUPPORTED BY THIS IMPLEMENTATION`.

Otherwise:

`INCONCLUSIVE`.

## 8. Interpretation fence

A supported result means that the ARA-first fixed `3.5` route selects a
recipient whose subsequent flow behaves as predicted more often and more
strongly than matched alternatives inside this simulator.

It does not empirically derive `3.5`, because `3.5` is the declared geometric
coordinate used to generate the directional prediction. It does not prove
universal ARA, physical conservation, Phase B, quantum hardware behaviour or
the dark-sector ratio.

## 9. Validation

An independent validator must:

- verify source, fidelity and protocol hashes;
- reconstruct development scales from the raw caches;
- reproduce a bounded deterministic event sample;
- recompute all headline flow and control metrics from saved rows;
- reproduce every frozen gate and verdict;
- verify event uniqueness and artifact row counts.
