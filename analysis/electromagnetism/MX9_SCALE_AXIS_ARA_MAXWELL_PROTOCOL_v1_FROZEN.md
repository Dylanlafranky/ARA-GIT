# MX9 — Scale/Axis ARA State Map and Maxwell Calibration (v1, frozen)

**Frozen:** 2026-07-23, before the MX9 numerical audit was run  
**Status:** exact mathematical crosswalk and analytic Maxwell calibration  
**Data:** deterministic synthetic states and exact vacuum plane-wave solutions; no fitted physical data

## Question

Can one mathematical construction represent Dylan's clarification that every resolved identity may be read as a
Phase-A/Phase-B pair, while the selected pair changes with scale and measurement axis, without falsely imposing an
E/B time lag on a travelling vacuum wave?

MX9 must connect four already recorded pieces:

1. the ARA line is a `0–2` diameter;
2. rotating the diameter reconstructs a state sphere/ball;
3. a parent pole may contain its own lower-rung A/B pair;
4. E and B in a vacuum plane wave are perpendicular in space but in phase in time.

## Frozen mathematical object

At rung `k`, let a resolved two-channel complex occurrence be

\[
z_k=(A_k,B_k)^\mathsf T.
\]

Its time/ensemble coherency matrix is

\[
G_k=\langle z_kz_k^\dagger\rangle,
\qquad T_k=\operatorname{tr}G_k>0.
\]

Define the normalized state-ball coordinate

\[
s_k=
\frac1{T_k}
\left(
2\Re G_{AB},
2\Im G_{AB},
G_{BB}-G_{AA}
\right).
\]

For any predeclared unit measurement axis `alpha`, define

\[
x_{k,\alpha}=1+\alpha\cdot s_k.
\]

Frozen expectations:

- `||s_k|| <= 1` for every positive-semidefinite coherency matrix;
- `x` lies on `[0,2]`;
- axis reversal gives `x(k,-alpha)=2-x(k,alpha)`;
- projected TE-ARA allocations

\[
t_B=T_kx/2,\qquad t_A=T_k(2-x)/2
\]

obey `t_A+t_B=T_k` and `t_B-t_A=T_k(x-1)`;
- on the population axis `alpha=(0,0,1)`, `x=2G_BB/T` exactly.

This uses a dimensional activity total `T`. Canonical TE-ARA is the normalized allocation
`2(t_A+t_B)/T=2`, not the dimensional total itself.

## Frozen child-to-parent laws

### Incoherent/coarse mixture

For child matrices `G_i`,

\[
G_P=\sum_iG_i,
\qquad
s_P=\frac{\sum_iT_is_i}{\sum_iT_i},
\qquad
x_{P,\alpha}=\frac{\sum_iT_ix_{i,\alpha}}{\sum_iT_i}.
\]

This must hold at numerical precision. It permits a parent ridge even when the children are asymmetric.

### Coherent coupling

For simultaneously added child amplitudes `z_P=sum_i z_i`,

\[
G_P
=
\sum_i z_iz_i^\dagger
+
\sum_{i\ne j}z_iz_j^\dagger.
\]

The second sum is the retained child relation/coupling term. Omitting it is expected to lose the parent whenever
children are coherent.

## Frozen Maxwell calibration

Use a source-free plane wave travelling in `+z`:

\[
\mathbf E=E_0\cos(kz-\omega t)\,\hat x,
\qquad
\mathbf B=\frac{E_0}{c}\cos(kz-\omega t)\,\hat y,
\qquad \omega=ck.
\]

Check:

1. source-free Maxwell curl residuals are zero;
2. normalized E and B amplitudes are in temporal phase;
3. each field and its normalized time derivative are in phase quadrature;
4. electric and magnetic energy densities are equal;
5. `|S|=cu`;
6. on the E/B population diameter, `x=1` wherever the field is active;
7. on the E/B coherence diameter, forward flow is `x=2` and a one-channel sign flip is `x=0`;
8. the paired half-cycle flip leaves the coherency state, Poynting flow and stress identity unchanged.

No numerical tolerance larger than `1e-12` relative/absolute error may be used for deterministic identity gates.

## Frozen randomized audit

Use deterministic seed `20260723`.

- 20,000 random positive-semidefinite mixed two-channel states;
- 20,000 random pure complex states;
- 5,000 random incoherent child mixtures;
- 5,000 random coherent child sums;
- 4,096 plane-wave phase samples.

## Claim boundary

MX9 may establish:

- an exact scale-and-axis indexed ARA embedding for any resolved two-channel coherency state;
- exact axis reversal, TE allocation, incoherent parent averaging and coherent cross-term closure;
- exact compatibility with the declared vacuum Maxwell plane wave;
- a precise explanation of how one E/B state can be a ridge on one diameter and a pole on another.

MX9 may not establish:

- that every physical system naturally supplies a privileged two-channel decomposition;
- universal fractal recurrence across independently observed physical scales;
- that zero crossings are mathematical singularities in Maxwell theory;
- a new electromagnetic prediction or replacement for Maxwell;
- a temporal phase offset between raw E and B amplitudes in a travelling vacuum plane wave.

