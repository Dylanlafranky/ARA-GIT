# MX9 — Scale/Axis ARA State Map and Maxwell Calibration

**Date:** 2026-07-23  
**Outcome:** all registered identities and independent checks passed  
**Evidence tier:** exact mathematical crosswalk and Maxwell calibration; not a new electromagnetic law

## Result first

Dylan's correction now has one rigorous mathematical home:

> Every resolved two-channel identity can be represented by a state inside a ball. Choosing an axis projects that
> state onto one ARA diameter from `0` to `2`. Changing the axis changes which relation is called Phase A and Phase B;
> changing the rung changes which complete identities occupy those two roles.

This is exact for any positive-semidefinite two-channel coherency matrix. It also exactly reproduces the relevant
vacuum Maxwell geometry:

- raw E and B amplitudes are temporally in phase;
- E and B have equal instantaneous energy participation in a plane wave;
- their field/change quadratures are quarter-cycle offset;
- the same forward wave is a `1.0` ridge on the E/B **population** diameter but a `2.0` pole on the E/B
  **coherence/directed-coupling** diameter;
- a one-channel sign flip moves that coupling reading from `2` to `0` and reverses Poynting flow;
- a joint half-cycle flip preserves the parent state and flow direction.

The construction also supplies an exact child-to-parent aggregation law. Incoherent children average by activity.
Coherent children require their cross-terms—the retained coupling relation that ARA calls the informative third or,
when omitted from a compressed account, a typed part of `Other`.

All frozen gates passed. A separate implementation using Pauli-projector traces, fresh random states and different
Maxwell parameters also passed.

## 1. One mathematical object for every declared A/B pair

At rung (k), collect the currently selected Phase-A and Phase-B amplitudes into

\[
\underbrace{z_k}_{\substack{\text{resolved two-channel occurrence}\\
\text{ARA pair at rung }k}}
=
\begin{pmatrix}
\underbrace{A_k}_{\text{declared Phase A}}\\
\underbrace{B_k}_{\text{declared Phase B}}
\end{pmatrix}.
\]

The channels may be complex because relative phase carries physical information. Their coherency matrix is

\[
\underbrace{G_k}_{\substack{\text{two-channel coherency}\\
\text{states plus retained relation}}}
=
\left\langle z_kz_k^\dagger\right\rangle
=
\begin{pmatrix}
\langle|A|^2\rangle & \langle AB^*\rangle\\
\langle A^*B\rangle & \langle|B|^2\rangle
\end{pmatrix}.
\]

The diagonal terms record how much occupies each channel. The off-diagonal term records their coherence, relative
phase and coupling orientation. The dimensional activity envelope is

\[
\underbrace{T_k}_{\text{total measured activity}}
=\operatorname{tr}G_k.
\]

**Plain explanation.** The two diagonal numbers say how much A and B are present. The cross-number says how they are
working together. Two systems can contain the same amounts of A and B while having opposite relations, so the
cross-number must not be thrown away.

## 2. The coherency matrix produces the state ball

Define

\[
\boxed{
\underbrace{s_k}_{\substack{\text{state-ball location}\\
\text{all diameter readings available}}}
=
\frac1{T_k}
\begin{pmatrix}
2\Re G_{AB}\\
2\Im G_{AB}\\
G_{BB}-G_{AA}
\end{pmatrix}
}.
\]

Because (G_k) is positive semidefinite,

\[
\boxed{
1-\|s_k\|^2
=
\frac{4\det G_k}{T_k^2}
\ge0
}.
\]

Therefore (|s_k|\le1): every state lies inside the unit ball. A perfectly coherent/pure pair has
(det G=0) and lies on the sphere. Partial coherence or unresolved mixing moves the state into the interior.

**Plain explanation.** The sphere is not being drawn around the data after the fact. The two channel strengths and
their relation mathematically generate a point inside a ball. Complete coherence reaches the shell; mixing several
unresolved states pulls the visible parent inward.

## 3. Every axis gives an ARA diameter

Choose any declared unit direction (alpha) through the state ball. Define

\[
\boxed{
\underbrace{x_{k,\alpha}}_{\substack{\text{ARA position at rung }k\\
\text{along axis }\alpha}}
=1+\alpha\cdot s_k
}.
\]

Since (|\alpha\cdot s_k|\le1),

\[
0\le x_{k,\alpha}\le2.
\]

Reversing the declared poles gives

\[
\boxed{x_{k,-\alpha}=2-x_{k,\alpha}}.
\]

This is the exact mathematical form of the reversible ARA chart. No axis is intrinsically the one true A/B pair;
the axis declares which opposed modes are being compared.

**Plain explanation.** The state is one point in the sphere. Looking through it from different directions produces
different diameter readings. A ridge on one diameter can be a pole on another without contradiction.

## 4. ARA and TE-ARA remain the same geometry

Let (Q_A,Q_B) be the dimensional allocations along the chosen axis:

\[
Q_B=\frac{T_kx}{2},
\qquad
Q_A=\frac{T_k(2-x)}{2}.
\]

Then

\[
Q_A+Q_B=T_k,
\qquad
Q_B-Q_A=T_k(x-1).
\]

Normalize them into canonical TE-ARA units:

\[
\underbrace{t_B}_{\text{normalized Phase-B allocation}}
=\frac{2Q_B}{T_k}=x,
\qquad
\underbrace{t_A}_{\text{normalized Phase-A allocation}}
=\frac{2Q_A}{T_k}=2-x,
\]

so

\[
\boxed{t_A+t_B=2}.
\]

**Plain explanation.** (T_k) says how much physical activity is present in its native units. TE-ARA says how that
complete activity is divided on the normalized two-unit geometry. TE-ARA remains exactly `2`; it is not being
redefined as joules or field strength.

## 5. One state can be a ridge and a pole simultaneously

Consider two equal-channel states:

\[
z_+=\begin{pmatrix}1\\1\end{pmatrix},
\qquad
z_-=\begin{pmatrix}1\\-1\end{pmatrix}.
\]

On the population axis, both have equal A/B amounts:

\[
x_{\rm population}(z_+)=x_{\rm population}(z_-)=1.
\]

On the coherence/coupling axis, their relations are opposite:

\[
\boxed{
x_{\rm coherence}(z_+)=2,
\qquad
x_{\rm coherence}(z_-)=0
}.
\]

An equal incoherent mixture of them has (x_{\rm coherence}=1).

**Plain explanation.** Measuring only the amounts says “perfect ridge” for both states. Measuring how those same
channels are coupled distinguishes the two singularity poles. Mixing equal amounts of the opposing coupled states
returns the visible parent to the ridge. This is the clean mathematical version of asymmetric children hiding under
a quiet whole.

## 6. Exact child-to-parent aggregation

### 6.1 Incoherent or unresolved mixture

If separately resolved child coherency matrices are added,

\[
G_P=\sum_iG_i,
\]

then for every fixed axis

\[
\boxed{
s_P=\frac{\sum_iT_is_i}{\sum_iT_i},
\qquad
x_{P,\alpha}=\frac{\sum_iT_ix_{i,\alpha}}{\sum_iT_i}
}.
\]

**Plain explanation.** A coarse parent is the activity-weighted location of its children. Opposing asymmetric
children can cancel to a parent ridge. This is exact coarse-graining, not an assumption that every child is balanced.

### 6.2 Coherent coupling

If child amplitudes combine before measurement, (z_P=\sum_i z_i), then

\[
\boxed{
G_P
=
\underbrace{\sum_i z_iz_i^\dagger}_{\substack{\text{separate child identities}\\
\text{what each contributes alone}}}
+
\underbrace{\sum_{i\ne j}z_iz_j^\dagger}_{\substack{\text{child coupling relations}\\
\text{interference/cross terms}}}
}.
\]

**Plain explanation.** Adding the children independently is insufficient when their phases interact. The cross-terms
are the measurable “plus” in `1+1=3`: they are not a third independent substance, but the information created by
the relation. When a compressed account omits them, that missing contribution belongs in typed `Other`.

In the registered random stress test, omitting coherent cross-terms produced median relative matrix error `0.710`
and 95th percentile `3.209`. Those magnitudes describe the deliberately broad synthetic audit, not a universal
physical percentage. Restoring the cross-terms reconstructed the parent at relative L2 error
`1.87e-16`.

## 7. Maxwell plane-wave calibration

For a source-free wave travelling in (+z),

\[
\mathbf E=E_0\cos\theta\,\hat x,
\qquad
\mathbf B=\frac{E_0}{c}\cos\theta\,\hat y,
\qquad
\theta=kz-\omega t,
\qquad \omega=ck.
\]

Maxwell gives

\[
\frac{\partial\mathbf B}{\partial t}=-\nabla\times\mathbf E,
\qquad
\frac{\partial\mathbf E}{\partial t}=c^2\nabla\times\mathbf B.
\]

MX9 recovered both at maximum residual below `8.89e-16`.

Normalize E and B into common energy-amplitude units:

\[
\mathcal E=\sqrt{\epsilon}\,E,
\qquad
\mathcal B=\frac{B}{\sqrt\mu},
\qquad
c^2=\frac1{\epsilon\mu}.
\]

For the plane wave, (mathcal E=\mathcal B). Therefore

\[
x_{E/B\,\rm population}=1,
\qquad
x_{E/B\,\rm coherence}=2.
\]

Flipping one field gives the opposite coherence pole:

\[
(\mathcal E,\mathcal B)\rightarrow(\mathcal E,-\mathcal B)
\quad\Longrightarrow\quad
x_{\rm coherence}:2\rightarrow0,
\]

and reverses (mathbf S=(1/\mu)mathbf E\times\mathbf B). Flipping both fields leaves their coherency and Poynting
direction unchanged.

**Plain explanation.** E and B are a ridge when we ask “how much energy is in each?” They are at a coupling pole
when we ask “are their signed orientations working together or against one another?” The same wave therefore has
different ARA positions on different axes, exactly as Dylan proposed.

## 8. The genuine quarter-cycle offset

For either sinusoidal field (F=F_0\cos\theta), define its normalized change channel

\[
H=\frac1{\omega F_0}\frac{\partial F}{\partial t}=\sin\theta.
\]

The field/change participation diameter is

\[
\boxed{
x_{F/H}=2\frac{H^2}{F^2/F_0^2+H^2}=2\sin^2\theta
}.
\]

It moves from `0` at field peaks to `2` at zero crossings and has cycle mean `1`. MX9 recovered minimum `0`,
maximum `2`, and mean `1` exactly at the reported precision.

**Plain explanation.** Raw E and B peak together. The quarter-cycle offset is between each field and its own rate of
change. At a field zero crossing, change is maximal. Calling that an ARA handover is coherent; calling it a Maxwell
mathematical singularity would be incorrect because the field solution remains smooth.

The scalar (x_{F/H}) repeats twice per signed cycle because squaring removes orientation. Full reversibility needs
the phase direction or the signs of (F) and (H) retained in the decompressed record.

## 9. Polarisation is the established physical sphere

When (z=(E_x,E_y)) is the transverse Jones pair, (G) is the optical coherency matrix and (s) is the normalized
Stokes vector. Pure polarisation states lie on the Poincaré sphere:

- one axis compares horizontal and vertical linear polarisation;
- a rotated axis compares diagonal linear polarisations;
- the helicity axis compares right- and left-circular polarisation;
- every intermediate axis supplies another opposed pair.

Thus helicity, E/B coupling, and field/change are not competing candidates for the uniquely real A/B pair. They are
typed diameter readings at different axes or rungs. The domain must specify which state vector and axis are being
used before assigning `0`, `1`, and `2`.

## 10. What “fractal” means at this stage

The same map can be reapplied recursively:

\[
(A_k,B_k,G_k)
\longrightarrow
P_k,
\qquad
(P_k,C_k,G_{k+1})
\longrightarrow
P_{k+1}.
\]

Mathematical recursion is therefore available without changing the ARA form. Physical fractality is the stronger
claim that independently measured systems at several scales select meaningful pairs and obey a transferable
cross-rung coupling rule. MX9 does not prove that empirical claim.

## 11. Validation summary

| Registered check | Result |
|---|---:|
| Mixed positive-semidefinite states | 20,000; all inside ball |
| Pure complex states | 20,000; sphere error `4.44e-16` |
| Incoherent parent mixtures | 5,000; maximum projection error `6.66e-16` |
| Coherent parent sums | 5,000; reconstruction error `1.87e-16` |
| Plane-wave phase samples | 4,096; all Maxwell/ARA gates passed |
| Independent projector audit | 4,096 fresh states; all passed |
| Independent aggregation audit | 2,048 fresh parents; all passed |
| Independent Maxwell audit | different constants; all passed |

## 12. Scientific status

### Established exactly

- two-channel coherency generates a state ball;
- every declared axis supplies a bounded, reversible `0–2` ARA projection;
- TE-ARA allocation closes at `2` after normalization;
- incoherent parent states are activity-weighted child averages;
- coherent aggregation requires relation cross-terms;
- the construction recovers the declared source-free Maxwell plane wave;
- the same E/B state can be a population ridge and a coherence pole.

### Still interpretive or open

- ARA's naming of these established structures as one universal geometry;
- which pair and axis nature selects at an arbitrary scale;
- a universal physical promotion/closure rule between rungs;
- cross-domain or unlimited fractal recurrence;
- any new prediction beyond Maxwell or standard coherence theory.

### Validation assessment

**Ready to share as an exact mathematical crosswalk, with the stated evidence boundary.** It should not be presented
as independent confirmation of universal ARA fractality or as a new electromagnetic law.

## Reproduction packet

- `MX9_SCALE_AXIS_ARA_MAXWELL_PROTOCOL_v1_FROZEN.md`
- `mx9_scale_axis_ara_maxwell.py`
- `MX9_SCALE_AXIS_ARA_MAXWELL_RESULTS.json`
- `mx9_validate_outputs.py`
- `MX9_SCALE_AXIS_ARA_MAXWELL_VALIDATION.json`

