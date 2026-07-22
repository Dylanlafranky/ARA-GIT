# PN24 nearest-handover cascade protocol — frozen development v1

**Frozen:** 22 July 2026, before PN24 computation  
**Status:** exploratory/development test; no confirmatory novelty claim  
**Protected 87-bit anchor:** remains sealed and is not an input

## User proposal being translated

Choose an integer `N`. At the current structural rung, retain only the nearest surviving child wave below `N`
and the nearest surviving child wave above `N`. The upper child supplies the first signed correction from `N`.
If that child is released by a higher gate, repeat the same local handover at the next rung. Test whether two or
three visible handovers are normally enough to reach the next prime.

This is the operational version of:

> two child waves + chosen number + their difference; chosen number + difference = the candidate prime.

Here “largest child” means **closest to handover at the declared rung**, not the numerically largest prime label.

## Exact definitions

Let `G_k` be the processed factor gates at rung `k`. An integer survives that rung when it is not divisible by any
gate in `G_k`.

For anchor `N`, define the local pair

\[
L_k(N)=\max\{m\le N:m\text{ survives }G_k\},
\qquad
U_k(N)=\min\{m>N:m\text{ survives }G_k\}.
\]

The forward child difference and candidate are

\[
\Delta_k=U_k(N)-N,
\qquad
C_k=N+\Delta_k=U_k(N).
\]

The base ARA rung is the mod-14 wheel:

\[
G_0=\{2,7\},
\]

whose reversible lanes are `(1,13)`, `(3,11)` and `(5,9)` modulo 14.

The remaining prime gates are introduced in ascending order:

\[
3,5,11,13,17,19,23,\ldots
\]

(`2` and `7` are omitted because they are already in the base rung).

If the current candidate is divisible by a newly introduced gate `p`, that candidate is released. The processed
set is enlarged through `p`, and the next upper survivor becomes the new candidate. This is one **visible handover
event**. Gates that do not remove the candidate are **silent gate checks**.

The cascade terminates when the current candidate has survived every prime gate through its square root. It is then
prime by the standard factor criterion and, because every update retained the nearest survivor above `N`, it is the
next prime after `N`.

## Frozen data

### Previously opened scale anchors

Use these seven already-opened anchors:

`10^8`, `10^9`, `10^10`, `10^11`, `4×10^11`, `7×10^11`, `9×10^11`.

### Deterministic development sample

Generate 2,000 distinct anchors from the already-open PN19 interval
`[4,000,000,000, 4,001,000,000)` using Python `random.Random(240722).sample(...)`, then sort them.

This is development data, not a fresh blind target. Repeated/overlapping next-prime labels are allowed but must be
reported because the rows are not statistically independent prime events.

## Frozen comparisons

For every anchor, calculate:

1. next odd candidate (`G={2}`);
2. base mod-14 candidate (`G={2,7}`);
3. fixed wheel candidates through `3`, `5`, `11`, `13`, and `17`;
4. the event-driven handover cascade through exact prime closure.

Report for each fixed rung:

- exact-next-prime rate;
- candidate-prime rate;
- mean and median absolute location error;
- mean number of surviving candidates from that rung through the true prime.

Report for the cascade:

- fraction requiring 0, 1, 2, 3, and more than 3 handover events;
- fraction reaching the true prime within at most 1, 2, and 3 candidate states;
- candidate states inspected (`handover_events + 1`);
- silent gates and total gates crossed before proof;
- initial correction `Delta_0`, final correction, and `Delta_0/final_delta`;
- the full event path for every scale anchor.

## Interpretation frozen before results

- **Strong compact support:** at least 90% of development anchors reach the exact next prime within three candidate
  states (base candidate plus at most two handovers).
- **Partial structural support:** the nearest pair gives a valid monotone cascade and usually captures a substantial
  part of the final correction, but fewer than 90% close within three candidate states.
- **Compact null:** fewer than 50% close within three candidate states, or the nearest pair is not materially better
  than the matched wheel controls.

Regardless of visible event count, this is **not** a constant-operation prime algorithm unless the gate work needed
to detect each collision and prove the terminal candidate is also bounded. A small number of candidate changes must
not be reported as a small number of arithmetic operations.

## Falsifiers and integrity guards

- Any final candidate differs from an independently calculated next prime.
- Any update skips an integer that survives all gates processed at that moment.
- Any handover is recorded when the old candidate is not divisible by its named gate.
- Any fixed-rung candidate is not the first integer above `N` coprime to that rung's modulus.
- The protected 87-bit anchor appears in source code, outputs, or notebook.

## Claim boundary

A positive result would show that the exact sieve path often has a short **visible correction lineage** when viewed
through nearest ARA handovers. It would not by itself be a new prime theorem, a faster primality proof, or a
three-arithmetic-operation next-prime method. The construction is an incremental wheel/trial-division crosswalk;
novelty would require a way to infer the handover gates without performing the equivalent factor checks.
