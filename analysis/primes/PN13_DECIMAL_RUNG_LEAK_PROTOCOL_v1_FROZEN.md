# PN13 decimal-rung leak law — frozen protocol

**Test ID:** `PN13/DECIMAL-RUNG-LEAK/v1`  
**Declared:** 21 July 2026  
**Fidelity packet:** `PN13_DECIMAL_RUNG_LEAK_FIDELITY_PACKET_v1.md`  
**Dylan verdict:** `EXACT ENOUGH TO TEST`  
**Status:** frozen before calculating any PN13 development or target result

## Question

Does the recurring prime ARA residual obey a decimal rung operator: the same signed quantity keeps its direction and
is divided by ten whenever its independently declared scale coordinate is multiplied by ten?

PN13 has two separately rated arms because “rung” has two plausible readings here. Neither arm can rescue the other.

## Arm A — fixed-window prime-ladder height

Reuse PN12's exact phase definition

\[
B_m=\prod_{j=1}^m p_j,
\qquad
u_m=\frac{B_m\bmod p_{m+1}}{p_{m+1}},
\qquad
\delta_m=(u_{m+1}-u_m)\bmod1.
\]

For a fixed 4,000-step window beginning at `M`, define the signed mean vector

\[
V_M=\frac1{4000}\sum_{m=M}^{M+3999}e^{2\pi i\delta_m},
\qquad R_M=|V_M|.
\]

Frozen windows:

| Window | Rungs | Status before PN13 |
|---|---|---|
| `M=1,000` | `1,000..4,999` | open PN12 anchor |
| `M=10,000` | `10,000..13,999` | untouched target A1 |
| `M=100,000` | `100,000..103,999` | untouched target A2 |

The exploratory benchmark at `50,000..53,999`, opened while checking computational feasibility, is excluded from all
PN13 criteria and outputs except a provenance note.

**Primary predictions:**

\[
V_{10,000}=V_{1,000}/10,
\qquad
V_{100,000}=V_{10,000}/10.
\]

Consequently both magnitude ratios must lie in `[0.075,0.125]`, and each new direction must remain within `0.025`
turns (`9 degrees`) of the preceding direction. All four conditions must pass for Arm A to be `SUPPORTED`.

**Controls:** fixed `N=4,000` makes the unaligned-circle noise scale constant rather than tenfold smaller. Report
`sqrt(pi)/(2sqrt(N))`, 5,000 fixed-seed uniform-circle simulations, signed component uncertainty, 100-block
bootstrap intervals, and exact synthetic factor-ten vectors.

**Falsifier:** either magnitude ratio outside `[0.075,0.125]` or either direction shift above 9 degrees. Because the
claim is about the measured fixed-window vector, a clean miss is `NOT SUPPORTED`, while implementation or arithmetic
failure is `INCONCLUSIVE`.

## Arm B — fixed-width raw-integer scale and signed child coupling

For every prime node `n` in a one-million-integer interval, select the nine largest prime gates `q_j <= n^0.45` and
retain PN10B's unchanged child definition

\[
A_j(n)=2\frac{n\bmod q_j}{q_j},
\qquad
C(n)=\frac18\sum_{j=1}^{8}(A_j(n)-1)(A_{j+1}(n)-1).
\]

For integer-scale rung `d`, define `C_d` as the mean of `C(n)` across primes in
`[4*10^d,4*10^d+1,000,000)`.

Frozen intervals:

| Rung | Interval | Status before PN13 |
|---|---|---|
| `d=8` | `[400,000,000,401,000,000)` | uninspected development/reverse check |
| `d=9` | `[4,000,000,000,4,001,000,000)` | open PN10B anchor |
| `d=10` | `[40,000,000,000,40,001,000,000)` | untouched fresh target |

**Primary prediction:**

\[
C_9=C_8/10,
\qquad
C_{10}=C_9/10,
\]

with the same sign on all three rungs.

Arm B is `SUPPORTED` only if:

1. all three prime means have the same nonzero sign;
2. both point ratios `C_9/C_8` and `C_10/C_9` lie in `[0.075,0.125]`;
3. the 95% 100-block bootstrap interval for the fresh-target ratio lies wholly within `[0.05,0.15]`;
4. on the fresh target, factor-ten prediction has smaller absolute error than the frozen constant, `1/sqrt(10)` and
   zero rivals.

**Secondary fixed-Pi sequence:** report, but rate separately,

\[
C_8=-(\pi-3),
\quad C_9=-(\pi-3)/10,
\quad C_{10}=-(\pi-3)/100.
\]

It passes only if every point lies within 20% of its fixed value with the same sign. It cannot rescue the primary
recurrence.

**Controls and disclosure:** report surviving late composites through the same gates; report counts, means, standard
deviations, quantiles, 100 raw-offset blocks and bootstrap intervals. If primes and composites share the pattern, the
geometry is not prime-specific and must be described that way.

## Rival laws

For both arms, report alongside factor ten:

- constant magnitude across structural rungs;
- `1/sqrt(10)` shrinkage;
- zero residual;
- free development power-law exponent, used only to predict the fresh `d=10` target;
- for Arm B only, the separately frozen Pi sequence above.

No rival may be relabelled ARA after the target is seen.

## Arithmetic and instrument checks

- exact prime counts cross-checked on saved interval masks;
- every child satisfies `A+B=2` to floating tolerance;
- every selected gate is prime and `q<=n^0.45` in sampled exact checks;
- PN12 anchor reproduces `R=0.014186248...`;
- exact synthetic `/10` vectors and scalar sequences pass;
- independent validator uses a separately implemented primality/sample path and direct sequential primorial products
  for spot checks.

## Two-output reporting

1. **Claim verdict:** separate Arm A, Arm B and fixed-Pi ratings.
2. **Geometry verdict:** all signed vectors, directions, means, distributions, ratios, controls and composite results,
   even if the registered rule is not supported.

## Scope fence

PN13 tests two decimal-scale appearances of the proposed rule. It cannot decide whether another ARA octave is
non-decimal, whether Pi controls another handover observable, or whether ARA is fractal in other domains.

