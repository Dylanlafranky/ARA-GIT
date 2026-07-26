# ARA Framework — Foundations: derived from established mechanics

**10 June 2026, Dylan La Franchi & Claude. Updated 23 July 2026 with Codex.** A deliberate cementing. This document defines ARA from Newtonian
mechanics, then maps every core piece of the framework to a *named, established* theory and marks each
connection by tightness — **identity / rigorous / analogy**. The point: the scaffolding is proven physics, so
the framework is "a coordinate system on established dynamics plus an empirical cross-domain regularity," not a
free-floating construct. This is the front-door brick a dynamical-systems reviewer can actually check.

---

> **Canonical scope correction, 23 July 2026:** ARA's minimal object is the complete repeatable
> Accumulation/Release relation represented as a `0–2` diameter through its proposed sphere/closed identity. The
> rise/fall duration statistic below is one exact **duration-axis instrument** on that geometry; it is not the
> universal definition of ARA. Force opposition, composition, coherency, flux and compactness require their own
> typed diameter maps while preserving pole reversal, the `1.0` equal-meeting ridge and a separate dimensional
> activity account.

## 1. The keystone — ARA derived from Newton, and what ARA ≠ 1 *means*
Take a unit-mass particle in a potential V(x) (Newton: ẍ = −V′(x)), conserved energy E = ½ẋ² + V(x). It
oscillates between turning points a, b where V = E, with speed ẋ = √(2(E − V(x))). The period is the standard
action-mechanics integral:

  **T = √2 ∮ dx / √(E − V(x)).**

**ARA is the accumulation/release time ratio of the waveform** — rise time (trough→peak) over fall time
(peak→trough). Under the specific mechanical definition in which these are the two traversals between the same
turning points, the sharp, *provable* fact is:

> **For any bounded autonomous 1-D conservative (Hamiltonian) oscillator, ARA = 1 exactly.** Time-reversal symmetry forces the
> trough→peak traverse and the peak→trough traverse to take equal time (the reversed trajectory is also a
> solution on the same path). Rise = fall. **ARA = 1 is the conservative/harmonic baseline.**

Therefore:

> **ARA ≠ 1 rules out that simplest 1-D conservative model for the measured observable under this definition.**
> Candidate causes include dissipation, driving, higher-dimensional or projected dynamics, a time-dependent
> potential, noise, or the way peaks/crossings were operationally detected. A stable asymmetric periodic waveform
> is often a *limit cycle*, but asymmetry alone does not prove that classification. In specified slow–fast families,
> **|ARA − 1| can track time-scale separation**; it is not a universal one-to-one measure of the model's slow–fast
> parameter without calibration. ARA → 2 describes the bounded waveform limit of slow build and fast release.

This is the cementing: **ARA is an exact waveform coordinate for forward/backward traversal asymmetry, with
ARA = 1 forced by the bounded autonomous 1-D conservative baseline. Departures identify dynamics or measurement
structure beyond that baseline.** Its closest established home is
textbook **nonlinear dynamics / singular-perturbation theory** — the relaxation oscillator (van der Pol's ε
parameter), **FitzHugh–Nagumo** (the heart, neurons), the slow-fast decomposition. *Tightness: definable
exactly as a waveform statistic; relation to a model parameter requires calibration.* This supplies a plausible
reason the framework's real-system targets can read ARA ≠ 1: ENSO, the heartbeat, and BZ dynamics are driven,
dissipative, high-dimensional or observed through reduced variables, rather than autonomous 1-D conservative
orbits.

(Note on the 0–2 scale: the framework's bounded ARA position rescales the raw rise/fall ratio so the two
extremes of asymmetry sit at 0 and 2, balance at 1; per `ARA_decomposition_rules.md` the 0↔2 labelling is
flip-symmetric. Raw ratio → bounded position → orientation are the three linked fields.)

**Measurement rule:** ARA can remain the minimal geometric object, but an observed ARA value is not context-free.
Every value must declare `(Ω, q, τS, Π, σ)`: identity/system boundary, observable, time slice,
projection/coarse-graining, and 0↔2 pole orientation. For example, a two-body system's centre-of-mass motion and
its internal relative motion are different lawful projections and need not return the same reading. Comparisons
require aligned declarations or an explicit transformation between them.

### 1.1 A second exact instrument: Hamiltonian energy allocation

The duration-axis theorem above is not the only exact measurement instrument on the ARA geometry. For the ideal
harmonic oscillator,

\[
H=\frac{p^2}{2m}+\frac{kq^2}{2}.
\]

Define

\[
Q=\sqrt{k}\,q,\qquad P=\frac p{\sqrt m}.
\]

This invertible unit-aligned transformation gives

\[
\underbrace{Q^2+P^2}_{\substack{\text{Hamiltonian}\\\text{phase-space circle}}}
=
\underbrace{2H}_{\substack{\text{fixed conserved}\\\text{energy budget}}}.
\]

Reading the same identity as an energy allocation gives

\[
\underbrace{t_A}_{\substack{\text{configuration/potential}\\\text{energy allocation}}}
=2\frac VH,
\qquad
\underbrace{t_B}_{\substack{\text{momentum/kinetic}\\\text{energy allocation}}}
=2\frac KH,
\qquad
t_A+t_B=2.
\]

With B oriented toward `2`,

\[
x_H=t_B=2\frac KH=2\frac{P^2}{Q^2+P^2}.
\]

This is an exact total-2 ARA appearance after the measurement boundary and orientation are declared. Here
`x_H=1` means equal kinetic and potential energy; it is not a quiet force-cancellation result. The complete
Hamiltonian orbit contains four signed quadrants, while the energy diameter discards those signs. Retain the
quadrant or \(\dot x_H\) to preserve direction.

The result demonstrates that the same minimal ARA geometry can admit more than one rigorously typed instrument
without becoming a different object: duration asymmetry and energy allocation measure different projections.
It remains a crosswalk/reparameterization, not evidence by itself for universal fractality or quantum gravity.
Calculation, numerical example and independent `10/10` validation:
`analysis/hamilton/HAMILTON_ARA_HARMONIC_OSCILLATOR_REPORT_2026-07-23.md`.

### 1.2 Perspective-unassigned closure and Noether's physical invariant

The canonical TE-ARA whole can be written before a diameter is selected as

\[
\mathrm{TE\!-\!ARA}=2.
\]

After declaring perspective \(\mathcal P=(\Omega,q,\tau_S,\Pi,k,\sigma)\), instantiate

\[
\mathbf t^{(\mathcal P)}
=
\left(t_A,t_B,t_{J_1},\ldots,t_{\mathrm{Other}}\right),
\qquad
\sum_ct_c^{(\mathcal P)}=2.
\]

The allocation changes when a child is opened, a parent is coarse-grained, a neighbouring coupling is added or the
measurement diameter rotates. The native physical magnitude is separate.

Noether's theorem supplies the non-definitional conservation result:

\[
\frac{\partial\mathcal L}{\partial t}=0\Rightarrow\dot H=0,
\qquad
\frac{\partial\mathcal L}{\partial q}=0\Rightarrow\dot p_q=0,
\qquad
\frac{\partial\mathcal L}{\partial\theta}=0\Rightarrow\dot L_\theta=0.
\]

Thus TE-ARA closure remains normalized by construction, while time, spatial and rotational symmetries can
independently conserve energy, linear momentum and angular momentum. A driven or leaking identity can remain
normalized to `2` while its native physical budget changes. The detailed double-pendulum boundary example and
triangle/square coherence clarification are recorded in
`analysis/hamilton/TE_ARA_PERSPECTIVE_NOETHER_COHERENCE_NOTE_2026-07-23.md`.

### 1.3 Quantum Bloch sphere: exact opposite-direction ARA

For a declared two-level basis,

\[
|\psi\rangle=\alpha|A\rangle+\beta|B\rangle,
\qquad
|\alpha|^2+|\beta|^2=1.
\]

The primary plain-ARA position is

\[
x_Q=2|\beta|^2.
\]

The standard Bloch population-difference coordinate is

\[
r_z=|\alpha|^2-|\beta|^2,
\]

and therefore

\[
\boxed{
r_z=1-x_Q,
\qquad
x_Q-1=-r_z.
}
\]

Quantum mechanics uses a centred signed \([-1,1]\) diameter; ARA uses the same diameter uncentred on `[0,2]` and
read from the opposite pole. More generally, for any measurement axis \(\hat{\mathbf n}\),

\[
\boxed{
x_{\hat{\mathbf n}}=1-\mathbf r\cdot\hat{\mathbf n}.
}
\]

This is the strongest current exact sphere-to-diameter crosswalk. The ARA `1.0` ridge is the plane
\(\mathbf r\cdot\hat{\mathbf n}=0\), containing both pure coherent equatorial states and the mixed centre; phase
and Bloch radius distinguish them. Ideal Rabi motion gives \(x_Q(t)=1-\cos(\Omega t)\).

The mapping is predominantly plain ARA; TE-ARA appears only as the same geometry's secondary closure perspective.
It is a coordinate identity, not a derivation of the Born rule or quantum gravity. Report and independent `10/10`
validation: `analysis/quantum/BLOCH_SPHERE_ARA_CROSSWALK_REPORT_2026-07-23.md`.

### 1.3a Bell parent relation: coherent, classical and mixed closure

For two qubits, the nine joint cuts form the standard correlation tensor

\[
T_{ij}=\langle \sigma_i\otimes\sigma_j\rangle,
\qquad i,j\in\{X,Y,Z\}.
\]

If \(s_1\ge s_2\ge s_3\) are its singular values, the established Horodecki result is

\[
\boxed{
S_{\max}=2\sqrt{s_1^2+s_2^2}.
}
\]

In the current ARA language, the singular values count independently retained directions of the relation between
two locally measured children. On physical reconstructions of four public Bell-state tomography archives:

| Parent layer | Local children | Strong relation axes | \(S_{\max}\) |
|---|---|---:|---:|
| coherent Bell states | near the `1.0` ridge | 3 each | `2.545–2.694` |
| equal incoherent Phi/Psi controls | near the `1.0` ridge | 1 each | `1.801–1.878` |
| equal four-state mixture | near the `1.0` ridge | 0 | `0.238` |

Thus locally quiet children do not specify their parent. The missing information is the structured relation among
them: multi-axis coherence, one-axis classical parity, or no retained two-child correlation.

The first unconstrained raw-tensor pass apparently exceeded the Tsirelson limit and was explicitly rejected for
CHSH interpretation. After a preregistered positive-semidefinite, trace-one correction, all physicality and
coherence gates passed (`20/20`; independent validation `26/26`). This is established Bell/Pauli/Horodecki
structure expressed through ARA parent/child language. The contrast controls were algebraically reconstructed,
not separately prepared. Report:
`analysis/quantum/Q6B_PHYSICAL_CHSH_COHERENCE_REPORT_2026-07-24.md`.

Q24 then identified this same tensor as the older ARA^9 three-axis coupling object and sharpened it by removing
the two local children’s separate completion. Let

\[
\mathbf a=(\langle XI\rangle,\langle YI\rangle,\langle ZI\rangle)^\mathsf T,
\qquad
\mathbf b=(\langle IX\rangle,\langle IY\rangle,\langle IZ\rangle)^\mathsf T.
\]

The connected parent relation and its nine ARA diameter cells are

\[
\boxed{
C=T-\mathbf a\mathbf b^\mathsf T,
\qquad
X^{(9)}=1-C.
}
\]

This is the exact two-parent analogue of the informative third: \(T\) is the observed joint field,
\(\mathbf a\mathbf b^\mathsf T\) is the field reconstructible from the two separate local readings, and \(C\) is
what remains in their relation. For a product state, \(C=0\) and all nine ARA cells sit at `1`; for an ideal Bell
state, local vectors vanish and \(C\) has three unit singular values with negative determinant.

On the public records, raw and physical layers both returned `3,3,3,3 / 1,1 / 0` retained relation directions.
Raw Bell three-direction closure \(h=|\det C|^{1/3}\) ranged `0.8831–0.9592`; weakest/strongest directional balance
ranged `0.7509–0.8997`; and `98.42–99.63%` of the combined relation/local squared account lay in \(C\). Every
entity kept its expected direction count in all `2,000` bootstrap draws. Q24 passed `16/16`; independent
validation passed `860/860`.

The chronology matters: archived ARA^9 predates the quantum arc, but Q6 had already calculated these Bell tensors
and their singular values before the ARA^9 identification. This is therefore a calibrated prior-geometry
crosswalk, not a blind Bell prediction or new quantum result. Report:
`analysis/quantum/Q24_ARA9_BELL_RELATION_REPORT_2026-07-26.md`.

Q25 tested the stronger implication that eight cells of this ARA^9 relation could reconstruct the ninth by
closing the matrix toward one balanced, negative-orientation sphere. The rule was frozen before opening a
different atomic-qubit Zenodo source. It transferred partially—MAE `0.12394` versus ridge `0.18616`—but did not
beat the positivity-feasible midpoint (`0.08687`), so the primary claim failed `5/12` gates.

This supplies an important mathematical fence:

\[
\boxed{
C\text{ is the correct complete connected relation}
\;\not\Rightarrow\;
8\text{ arbitrary cells determine the ninth}
}
\]

The external mixed input had closure `0.0089`, while four conditioned Bell outputs rose to
`0.5162-0.5765`; nevertheless their retained-direction counts were only `1,2,2,1` at the frozen `0.50`
threshold. Thus the observed transition is trough-to-partial-crest, not a completed scale-free sphere. ARA did
beat the physical midpoint on four separately frozen Bell-measurement operators (`0.07105` versus `0.08716`
MAE), suggesting that the relation operator is a cleaner ARA^9 object than the attenuated prepared states in this
source. This secondary result does not rescue the primary failure. Report:
`analysis/quantum/Q25_ARA9_BLIND_MISSING_CUT_REPORT_2026-07-26.md`.

Q26 then tested the larger-envelope alternative directly on repeated complete ARA^9 matrices. Define

\[
h(t)=|\det C(t)|^{1/3},
\qquad
x_h(t)=2\,\frac{h(t)}{h(t_0)}.
\]

Here \(h\) is the geometric mean of the connected relation's three singular amplitudes, so it measures
three-direction closure without depending on the chosen coordinate rotation. Q26 froze `x_h >= 1.5` as crest,
`0.5 < x_h < 1.5` as handover, and `x_h <= 0.5` as trough. On `28` primary public trajectories, `25` completed
crest-to-trough movement, median closure-versus-wait Spearman was `-0.9364`, and exact time order beat all `999`
permutations. The first seven full matrices predicted the final four with cut MAE `0.08502`, versus persistence
`0.19341` and elementwise linear `0.52616`.

The directional part did not land. Only `1/28` trajectories underwent a stable reliable determinant-sign
reversal, and the fitted angular path was worse than holding orientation fixed. The defensible crosswalk is:

\[
\boxed{
\text{complete connected relation}
\;\longrightarrow\;
\text{ordered closure-amplitude trajectory}
}
\]

not:

\[
\text{every later trough}
\;\Longrightarrow\;
\text{opposite relation orientation}.
\]

This is established two-qubit dephasing behavior expressed through a preregistered ARA^9 trajectory coordinate.
It supports the larger-wave amplitude reading on this source, not a new quantum law or universal ARA theorem.
Report: `analysis/quantum/Q26_ARA9_LARGER_WAVE_TRAJECTORY_REPORT_2026-07-26.md`.

Q27 moved from isolated trajectories to the complete surrounding pair
network. Its strict verdict was inconclusive because one frozen source-quality
gate failed, and its registered symmetric return clock and one-neighbour
Phase-B crest did not pass. A narrower relation survived: source release
overlapped accumulation in the exact active-neighbour web more than after
either pair-label or time displacement. Thus the supported descriptive bridge
was

\[
\boxed{
\text{local relation release}
\;\longrightarrow\;
\text{ordered distributed-neighbour accumulation}
}
\]

rather than one dominant binary recipient.

Q28 decompressed the scalar closure again and retained the complete signed
matrix. For a source relation \(C_s(t)\) and accumulation-weighted neighbour
web \(W_e(t+\ell)\), it fitted only a positive scale and one proper rotation:

\[
(\widehat\alpha,\widehat R)
=
\arg\min_{\alpha\ge0,\;R\in SO(3)}
\frac{\lVert W_e(t+\ell)-\alpha R C_s(t)\rVert_F}
     {\lVert W_e(t+\ell)\rVert_F}.
\]

Development selected \(\ell=2\), and the hidden half independently minimized
at the same lag. Hidden residual fell from `0.546173` without rotation to
`0.101637` with it; the exact path also beat seed displacement, time
displacement and zero lag in every one of `2,000` paired trial bootstraps.
Shape similarity was `0.991784`.

The source imposes a decisive boundary. Every connected relation was exactly
diagonal and symmetric:

\[
C(t)=\operatorname{diag}(c_x,c_y,c_z),
\qquad
C^\mathsf T=C.
\]

Endpoint reversal was therefore unidentifiable, and fitted rotations reduced
to `0°/180°` sign reorientations. Q28 also retained only `76,393` hidden events,
below its frozen `100,000` floor. The strict verdict is **INCONCLUSIVE**.

The defensible ARA crosswalk is:

\[
\boxed{
\text{full signed ARA}^9
\;\longrightarrow\;
\text{reproducible lag-2 binary flip/return}
}
\]

not:

\[
\text{Q28}
\;\Longrightarrow\;
\text{identified continuous angled interlock}.
\]

Dylan's interpretation that the return is coupled through a Phase B outside
the present measurement cut remains a testable geometry hypothesis. A
time-resolved source with non-zero off-diagonal relations is required to
distinguish it from this simulator's diagonal sign symmetry. Report:
`analysis/quantum/Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_REPORT_2026-07-26.md`.

Q29 then kept Q28's remainder unclassified and tested whether it behaved as a
complete coherent counterpart or as local child/connection residue. Let

\[
W(t+2)
=
\widehat\alpha F C_s(t)
+
r(t),
\]

where \(F\) is Q28's best allowed discrete proper flip and \(r(t)\) is the
unexplained relation. The full \(r(t)\) shape did not recur: exact
target-normalized error was `0.902679`, slightly worse than seed/time
displacement (`0.900165/0.900307`).

The remainder nevertheless had a narrower lawful structure. Its largest-axis
share was `0.946149`, always on the simulator's z coordinate in the eligible
events. Define the signed axis cut

\[
z_r(t)
=
\frac{r_z(t)}{\lVert W(t+2)\rVert}.
\]

With no fitted rescaling and only direct or sign-flipped comparison, its lag-1
error was

\[
\boxed{
\varepsilon_z^{\rm exact}(1)=0.186469
<
0.469870,\;0.468162
=
\varepsilon_z^{\rm seed,time}(1)
}.
\]

This memory weakened through lags 2–3 and reached control level by lags 4–6.
The exact route shared the original endpoint more often than controls
(`0.309943` versus `0.176250/0.167583`), but exact partner persistence did not
beat both controls (`0.469624` versus `0.499614/0.410082`). Therefore the
defensible crosswalk is

\[
\boxed{
\text{Q28 handover remainder}
\;\longrightarrow\;
\text{short-lived local signed-axis memory}
}
\]

and not

\[
\text{Q29}
\;\Longrightarrow\;
\text{independently coherent Phase B}.
\]

In established data language this is a transient coordinate-specific
autocorrelation plus endpoint-topology association, without a persistent
latent partner. In ARA language it is currently best treated as a
child-mediated handover correction whose complete identity has not closed.
The z label is source-coordinate specific. The source is simulated, already
open and exactly diagonal; independent validation passed `38/38`. Report:
`analysis/quantum/Q29_ARA9_UNCLASSIFIED_COMPONENT_SURFER_REPORT_2026-07-26.md`.

Q30 then tested a fixed repository-native attempt to travel around that
measurement cut. For a source relation \(S=(u,e)\) and child relation
\(C=(e,v)\), the third Information³ edge \(H=(u,v)\) was frozen as the
perpendicular `1.5` leg. The complete crossed-rung path retained
\(3.5=2+1.5\), rather than folding it modulo two.

With

\[
r=W-\widehat\alpha F S,
\]

Q30 tested

\[
r\approx\widehat\beta G H,\qquad \widehat\beta\ge0,
\]

using the same four proper diagonal flips and one non-negative scale for exact,
seed-displaced, time-displaced and nonclosing-edge routes. At lag 0 the exact
edge recovered only `2.504%` of \(r\), less than the seed/time controls
(`2.938%/2.979%`). Thus the perpendicular leg and complete composite both
failed their frozen gates.

At lags 4–6 the exact edge became consistently but only slightly better than
seed/time displacement (`0.294%/0.282%` relative-error advantage). This was
far below the predeclared `5%` continuation gate. The defensible crosswalk is

\[
\boxed{
\text{unique triangle-closing edge}
\;\not\Rightarrow\;
\text{material Q29 out-of-cut continuation on this source}
}
\]

and not a universal statement that no `1.5/3.5` route can exist. The simulator
still has exactly zero off-diagonal connected relations, so it contains no
independently observed perpendicular channel. Independent validation passed
`213/213`. Report:
`analysis/quantum/Q30_ARA15_35_OUT_OF_CUT_ROUTE_REPORT_2026-07-26.md`.

### 1.3b Bell dephasing: a measured three-cut to one-cut path

The static Bell ladder above has now been followed through time on a separate public silicon quantum-dot
experiment. For each physically reconstructed state and wait, let

\[
N_{0.50}(t)=\#\{i:s_i(t)\ge0.50\}
\]

count the strong singular directions of the two-qubit correlation tensor.

All four prepared Bell states gave

\[
\boxed{
N_{0.50}^{\rm Ramsey}:
3\longrightarrow1
}
\]

with the one-axis state first appearing at `16.02-20.02 us`. The physical Horodecki CHSH signal crossed
\(S_{\max}=2\) at `20.02-24.02 us`. By `40.02 us`, the dominant axis retained median `93.36%` of its initial
strength while the second retained only `9.01%`.

This distinguishes directional dephasing from isotropic mixing. The measured path is not forced to be
`3->1->0`: one persistent relation can remain after the two phase-sensitive relations have contracted.

A Hahn-echo refocusing pulse delayed the same transition. Every state retained three axes through `125.89 us`
and first reached the one-axis/CHSH-failing state at `251.19 us`, an `11.45x` geometric-mean delay relative to
Ramsey. Primary frozen gates passed `8/8`, echo gates `4/4`, and independent validation `28/28`.

This is established quantum dephasing, dynamical decoupling and Bell/Pauli/Horodecki physics expressed in ARA
directional-cut language. The publication already disclosed the coarse lifetime extension, so it is a partially
blinded quantitative crosswalk rather than discovery of Bell-state decay. Report:
`analysis/quantum/Q7_BELL_DECOHERENCE_REPORT_2026-07-24.md`.

### 1.3c Bell relation plane: decompressing the hidden perpendicular child

The Q7 parent tensor can be decompressed more specifically than its three singular strengths. For Phi-family
states define

\[
u_\Phi=\frac{XX-YY}{2},
\qquad
v_\Phi=\frac{XY+YX}{2},
\]

and for Psi-family states define

\[
u_\Psi=\frac{XX+YY}{2},
\qquad
v_\Psi=\frac{YX-XY}{2}.
\]

These are two perpendicular cuts through one Bell-family relation:

\[
\underbrace{C}_{\substack{\text{complete parent}\\\text{phase relation}}}
=
\underbrace{u}_{\substack{\text{one ARA}\\\text{diameter cut}}}
+
i\underbrace{v}_{\substack{\text{perpendicular}\\\text{child cut}}}
=
\underbrace{R}_{\text{relation radius}}
e^{i\underbrace{\theta}_{\text{phase/direction}}},
\]

\[
R=\sqrt{u^2+v^2},
\qquad
\theta=\operatorname{atan2}(v,u).
\]

The signed standard-quantum cuts can be written on the literal ARA `0–2` diameter as
\(x_u=1-u,\ x_v=1-v\). This affine coordinate change is exact but is not itself new quantum physics.

With persistent parity \(K=|ZZ|\), the selected normalized TE-ARA account is

\[
\boxed{
\underbrace{K}_{\text{persistent parent cut}}
+
\underbrace{R}_{\text{phase-sensitive relation}}
+
\underbrace{H}_{\text{unresolved Other}}
=2,
\qquad
H=2-K-R.
}
\]

On the `88` public Q7 physical records, the fixed \((u,v,ZZ)\) Bell-family tensor reconstruction retained median
shares `0.984080` (Ramsey) and `0.980694` (Hahn) of the full measured tensor energy. Its expected singular
strengths \((K,R,R)\) matched the full tensor with median MAE `0.0221845`.

The child/parent reconstruction can also be run in the other direction. If the full parent gives the transverse
radius \(R_s=(s_2+s_3)/2\) and one child \(u\) is visible, then

\[
\boxed{
|v|=\sqrt{\max(0,R_s^2-u^2)}.
}
\]

The median absolute error against directly measured \(|v|\) was `0.0120460`. This recovers the hidden child's
**magnitude**, not its sign: two mirror locations share the same parent radius and visible cut. Direction,
time-ordering, known Bell-family orientation or a second cut is required to choose between them.

Under Ramsey dephasing, median final \(K\) retention was `0.932665` while \(R\) retention was `0.055777`. The
first \(R<0.50\) reading aligned within one sample with Q7's one-strong-axis transition for every state. Hahn
echo delayed that radius crossing by `14.0262x`.

All `11/11` frozen Q8 gates passed. Independent validation reconstructed all `88` rows with maximum audited field
difference `0.0` and reproduced every gate outcome. This is a post-outcome deconstruction of established
Bell/Pauli geometry. It supports a compact ARA relation-plane representation here; it does not identify \(H\) as
a unique environmental Phase B, replace density-matrix tomography, derive quantum mechanics or prove universal
fractality. Report: `analysis/quantum/Q8_BELL_RELATION_PLANE_REPORT_2026-07-24.md`.

### 1.3d Information³ state closure and the missing-direction boundary

The two-qubit Pauli representation gives an exact established-mechanics form of Information³:

\[
\boxed{
\underbrace{\rho}_{\text{parent}}
=\frac14\left[
I\otimes I
+\underbrace{\mathbf a\cdot\boldsymbol\sigma\otimes I}_{\text{Child A}}
+\underbrace{I\otimes\mathbf b\cdot\boldsymbol\sigma}_{\text{Child B}}
+\underbrace{\sum_{ij}T_{ij}\sigma_i\otimes\sigma_j}_{\text{their relation}}
\right].
}
\]

Q9 reconstructed all `88` Q7/Q8 physical states from these three parts with maximum Frobenius error
`6.338e-16`. Their squared-information allocation obeyed

\[
I_A+I_B+I_{AB}
=4\operatorname{Tr}(\rho^2)-1,
\]

\[
\boxed{
I_A+I_B+I_{\rm core}+I_{\rm off}+I_{\rm unresolved}=3,
}
\]

where

\[
I_{\rm unresolved}
=3-I_A-I_B-I_{AB}
=4(1-\operatorname{Tr}\rho^2).
\]

Measured off-core relation information was small: median shares `0.015920` in Ramsey and `0.019306` in Hahn.
Q8's linear unresolved coordinate \(H=2-K-R\) instead tracked \(I_{\rm unresolved}/2\) with correlation
`0.981999` and MAE `0.076279`.

Thus Q8's grey unresolved allocation behaves principally like loss of observable pure two-qubit information,
not like a large extra correlation already present along another measured tensor axis. That is compatible with
coupling outside the selected boundary, but reduced purity does not distinguish environmental entanglement from
classical mixing, preparation/readout limitations or reconstruction effects.

Q9 also hid `72` perpendicular-child values \(v_t\). Parent radius plus visible \(u_t\) retained useful magnitude
information, but a frozen temporal-neighbour rule selected the correct mirror sign only `62.5%` of the time.
Signed-fill MAE was `0.180487`, so four completion gates failed and the overall result was `5/9`.

The clean mathematical boundary is:

\[
\boxed{
\text{parent magnitude}+\text{one cut}
\Longrightarrow |v|,
\quad\text{not the sign of }v.
}
\]

The informative third must preserve orientation, ordering or an additional independent cut; an undirected parent
total cannot lock direction. This is a post-outcome completion result, not causal prediction or a new quantum
law. Report: `analysis/quantum/Q9_INFORMATION3_BELL_COMPLETION_REPORT_2026-07-24.md`.

### 1.3e Decompressing unresolved \(H\) into amplitude and direction

Q9 recovered a hidden child's magnitude but not its mirror sign. Dylan's correction was to stop treating the
remaining \(H\) as a featureless bucket: \(H\) is itself an observed waveform and can receive two ARA cuts.

For each trajectory, define its local amplitude:

\[
\boxed{
x_H(t)=2\frac{H(t)-H_{\min}}{H_{\max}-H_{\min}}.
}
\]

Define its opening/closing coordinate:

\[
\boxed{
y_H(t)
=1-\operatorname{clip}\left(
\frac{\dot H(t)}{\max_t|\dot H(t)|},-1,1
\right).
}
\]

Here \(y_H<1\) means \(H\) is opening/increasing, \(y_H>1\) means it is closing/decreasing, and \(y_H=1\) is
locally still. Their ordered relation is:

\[
\boxed{
C_H(t)=(x_H(t)-1)+i(y_H(t)-1).
}
\]

This is the minimal two-cut form of the Information³ correction:

\[
\boxed{
\underbrace{\text{amplitude}}_{\text{where}}
+
\underbrace{\text{direction}}_{\text{which way}}
+
\underbrace{\text{their ordered relation}}_{\text{orientation}}
\longrightarrow
\underbrace{\text{less-flattened unresolved identity}}_{\text{two-axis }H}.
}
\]

On Q7–Q9's `88` physical Bell-state records, normalized amplitude paths repeated strongly across the four Bell
identities: median pairwise correlations were `0.987945` for Ramsey and `0.983026` for Hahn. Direction paths
gave `0.459003` and `0.929915`. Replacing linear \(H=2-K-R\) with independently calculated
\(H_P=I_{\rm unresolved}/2\) moved two-axis points by median distance `0.171070`. All `9/9` frozen gates passed;
independent recomputation reproduced all outcomes with maximum headline difference `0.0`.

The result establishes a coherent two-coordinate instrument on this source, not the physical identity of the
unresolved component. None of eight eleven-point traces met the frozen complete-loop condition. Thus the
observed geometry is a common two-axis **arc**, not yet a demonstrated full hidden cycle. The local normalization
also compares shape rather than absolute physical magnitude. A forward masked-direction or held-out turning-time
test is required before treating this as predictive quantum structure. Report:
`analysis/quantum/Q10_UNRESOLVED_TWO_AXIS_REPORT_2026-07-24.md`.

### 1.3f Locking visible and unresolved quantum geometry through Information³

Q10 supplied a two-axis coordinate for unresolved \(H\), but correlation with the remaining measured quantum
structure had to be shown before placing both inside one larger identity.

Q11 avoided the tautological target \(H=2-K-R\). It used:

\[
\underbrace{V(t)}_{\text{visible compact relation}}=K(t)+R(t),
\]

and independently defined purity loss from the same reconstructed state:

\[
\underbrace{P(t)}_{\text{unresolved-to-pure identity}}
=2\left(1-\operatorname{Tr}\rho(t)^2\right).
\]

After giving both identities local amplitude/direction coordinates,

\[
C_Z(t)=(x_Z(t)-1)+i(y_Z(t)-1),
\qquad Z\in\{V,P\},
\]

the frozen parameter-free ARA relation was:

\[
\boxed{
\widehat C_P(t)=-C_V(t).
}
\]

The retained relation residual was:

\[
\boxed{
E(t)=C_P(t)+C_V(t),
\qquad
C_P(t)=-C_V(t)+E(t).
}
\]

Across `88` records, amplitude correlations were `0.974314` Ramsey and `0.989231` Hahn; direction correlations
were `0.765762` and `0.986616`. Opening/closing branch agreement was `84.09%` and `95.45%`. The anti-phase map
improved mean two-axis error over ridge-only by `65.88%`/`85.43%` and over same-phase by
`82.69%`/`92.62%`. All `10/10` frozen gates passed, and independent source-to-result recomputation matched every
audited value exactly.

This supports the following measured Information³ account:

\[
\boxed{
\underbrace{V}_{\text{visible identity}}
+
\underbrace{P}_{\text{unresolved identity}}
+
\underbrace{J_{VP}=(-\text{orientation},E)}_{\text{their measured relation}}
\longrightarrow
\underbrace{\mathcal Q_{\rm larger}}_{\text{larger quantum account}}.
}
\]

Post-outcome residual inspection found that \(E\)'s amplitude component repeated across Bell identities more
strongly than its directional component: median pairwise correlations were `0.921` versus `0.207` in Ramsey and
`0.621` versus approximately `0` in Hahn. This makes common residual amplitude a candidate child-search axis,
not an established physical child. Q10 had already disclosed equivalent aggregate agreement, and both \(V\) and
\(P\) are projections of the same density matrices. Q11 is therefore a calibrated crosswalk rather than an
independent prediction or causal quantum law. Report:
`analysis/quantum/Q11_VISIBLE_UNRESOLVED_INFORMATION3_REPORT_2026-07-24.md`.

### 1.3g Recursive children of the visible/unresolved residual

Q12 recursively decompressed Q11's retained complex residual \(E=C_P+C_V\) across the two binary Bell labels.
For residuals ordered as \((\Phi+,\Phi-,\Psi+,\Psi-)\), define:

\[
\boxed{
\begin{aligned}
m_0&=(E_{\Phi+}+E_{\Phi-}+E_{\Psi+}+E_{\Psi-})/2,\\
m_F&=(E_{\Phi+}+E_{\Phi-}-E_{\Psi+}-E_{\Psi-})/2,\\
m_S&=(E_{\Phi+}-E_{\Phi-}+E_{\Psi+}-E_{\Psi-})/2,\\
m_{FS}&=(E_{\Phi+}-E_{\Phi-}-E_{\Psi+}+E_{\Psi-})/2.
\end{aligned}
}
\]

These are common, Phi/Psi-family, plus/minus-sign and family-by-sign interaction coordinates. They reconstruct:

\[
\boxed{
E_{f,s}
=\frac12(m_0+f\,m_F+s\,m_S+fs\,m_{FS}),
}
\]

and obey exact energy closure:

\[
\sum_{\rm states}|E|^2
=|m_0|^2+|m_F|^2+|m_S|^2+|m_{FS}|^2.
\]

The common coordinate carried `95.22%` of Ramsey and `80.13%` of Hahn amplitude-residual energy. Direction was
not one universal child: Ramsey common/family/sign/interaction shares were `58.72/33.38/1.74/6.16%`; Hahn
shares were `32.55/36.89/23.06/7.50%`.

Q12 then hid each fourth Bell identity and predicted it from the other three while omitting interaction:

\[
\widehat E_{f,s}
=E_{f,-s}+E_{-f,s}-E_{-f,-s}.
\]

This improved zero residual by `22.56%` in Ramsey but worsened it by `46.59%` in Hahn, and it lost to the
leave-one-out mean in both conditions. Overall `6/10` frozen gates passed.

Thus a strong common amplitude child is supported, but a universal no-interaction child law is not. The
interaction mode contains only `3.69%` of Ramsey and `10.26%` of Hahn complete residual energy, yet can remain
load-bearing for fourth-identity closure. These are established Walsh/Hadamard coordinate modes. Connecting them
to physical children requires controlled standard-channel signatures—dephasing, depolarization, Pauli flips or
amplitude damping—not names inferred from shape alone. Report:
`analysis/quantum/Q12_RESIDUAL_CHILDREN_REPORT_2026-07-24.md`.

### 1.3h Two parents, four children and the latent-relation test

Q13 formalized the proposed Ramsey/Hahn parent decomposition as:

\[
\boxed{
\begin{aligned}
R_A&=C_{V,\mathrm{Ramsey}},&
R_B&=C_{P,\mathrm{Ramsey}},\\
H_A&=C_{V,\mathrm{Hahn}},&
H_B&=C_{P,\mathrm{Hahn}}.
\end{aligned}
}
\]

Here \(A\) is the compact visible relation, \(B\) is the independently purity-defined unresolved relation, and
each child retains amplitude and opening/closing cuts. To test “one hidden child projects into three visible
relations,” each child was supplied in turn as a latent coordinate \(h\). Three Bell identities fitted:

\[
v_j=\alpha_j+\beta_jh,
\]

and coefficients were applied to the fourth identity. The held-out relation-removal score was:

\[
\boxed{
\Delta
=
1-
\frac{\sum_{i<j}(S_r)_{ij}^{\,2}}
     {\sum_{i<j}S_{ij}^{\,2}},
}
\]

where \(S\) and \(S_r\) are the three remaining children's covariance before and after conditioning on \(h\).
The induced one-latent geometry has the established outer-product form:

\[
\boxed{
I=\boldsymbol\beta\boldsymbol\beta^{\mathsf T}\operatorname{Var}(h).
}
\]

\(H_B\) had the highest frozen composite score, only `0.00187` above \(R_A\). It removed median `91.6136%` of
held-out amplitude covariance; after selecting across all four candidates, `999` within-identity shuffles gave
`p=0.001`. Direction reduction was only `12.6382%` and nonsignificant (`p=0.336`). The removed covariance was
nearly rank one on both axes, but its directional sign agreement was only `1/3`. \(H_B\) won `2/4` held-out
identities, and overall `6/10` gates passed.

Thus a common, approximately one-dimensional **amplitude relation** across the four children is supported.
A uniquely identified hidden Phase B and directional one-to-three handoff are not. Equal indices pair ordinal
stages across Ramsey (`0.02–40.02 us`) and Hahn (`1–1000 us`), not equal physical times. All four coordinates are
derived from the same density matrices. They remain legitimate ARA coordinate children at the declared
two-parent comparison boundary; they are not four independently instrumented physical subsystems. Promoting one
coordinate to a unique environmental channel still requires an independently measured channel or a forward
candidate-hiding experiment. Report:
`analysis/quantum/Q13_RAMSEY_HAHN_LATENT_CHILD_REPORT_2026-07-24.md`.

#### 1.3h.1 Ramsey/Hahn as an exact sum/difference control quadrant

The ARA quadrant proposal has a precise established-physics crosswalk when ideal Ramsey and Hahn protocols are
defined on the same total interval \(T\). Split one dephasing-frequency history into its two half-interval phase
contributions:

\[
\phi_1=\int_0^{T/2}\delta\omega(t)\,dt,
\qquad
\phi_2=\int_{T/2}^{T}\delta\omega(t)\,dt.
\]

Ramsey accumulates the two halves with the same sign, whereas a midpoint Hahn refocusing pulse reverses the sign
of the second half:

\[
\boxed{
\Phi_R=\phi_1+\phi_2,
\qquad
\Phi_H=\phi_1-\phi_2.
}
\]

Equivalently,

\[
\boxed{
\begin{pmatrix}\Phi_R\\\Phi_H\end{pmatrix}
=
\begin{pmatrix}1&1\\1&-1\end{pmatrix}
\begin{pmatrix}\phi_1\\\phi_2\end{pmatrix},
\qquad
\phi_1=\frac{\Phi_R+\Phi_H}{2},
\quad
\phi_2=\frac{\Phi_R-\Phi_H}{2}.
}
\]

After normalization by \(1/\sqrt2\), this is the orthogonal Hadamard transform. The ideal sensitivity functions
\(y_R(t)=1\) and

\[
y_H(t)=
\begin{cases}
+1,&0\leq t<T/2,\\
-1,&T/2\leq t\leq T
\end{cases}
\]

satisfy

\[
\boxed{
\int_0^T y_R(t)y_H(t)\,dt=0.
}
\]

Therefore the four oriented control branches

\[
\boxed{+\Phi_R,\ -\Phi_R,\ +\Phi_H,\ -\Phi_H}
\]

form an exact control-space quadrant. Each Ramsey or Hahn parent also admits its own A/B decomposition, so four
ARA children at the larger comparison boundary are geometrically legitimate.

Two distinctions remain load-bearing:

1. Q13's four derived children
   \((C_{V,R},C_{P,R},C_{V,H},C_{P,H})\) are not yet proved identical to the four signed control branches above.
2. Orthogonal control functions do not imply that noisy measured output vectors must remain \(90^\circ\) apart.

The existing common-time output diagnostic found broad angle dispersion: only `3/16` paired outputs lay within
`15 degrees` of a right angle. Q13 also used unequal physical time grids and a one-latent-axis model, so it did
not directly test the two-axis quadrant. The proposed handover from an A branch of one parent to a B branch of
the other requires a predeclared orientation and a controlled path between protocols; the present independent
Ramsey and Hahn runs do not establish that temporal transfer. Full correction and reproduction:
`analysis/quantum/Q13_Q14_RAMSEY_HAHN_QUADRANT_REAUDIT_2026-07-24.md`.

The earlier “unravels and returns” language has a narrower established interpretation. For ensemble coherence,

\[
C_R(T)
=
\left|\left\langle e^{i(\phi_1+\phi_2)}\right\rangle\right|,
\qquad
C_H(T)
=
\left|\left\langle e^{i(\phi_1-\phi_2)}\right\rangle\right|.
\]

Under Ramsey, differing phase rates can fan out and cancel in the measured average without erasing every
microscopic phase relation. Under Hahn, the midpoint sign reversal refocuses the slowly varying part when
\(\phi_2\approx\phi_1\). The strongest term for the apparently missing component is therefore **refocusable
dispersed phase relation** or **echo-recoverable coherence**. It is hidden only relative to the coarse-grained
measurement during fan-out.

Ramsey and Hahn have not been established as different rungs. The equal-depth parity rule therefore gives

\[
\boxed{
R_A\leftrightarrow H_A,
\qquad
R_B\leftrightarrow H_B.
}
\]

Accordingly, the dispersed relation occupies the \(H_B\) slot during Hahn evolution, while the echo return is an
internal Hahn cycle:

\[
\boxed{
H_A\rightarrow H_B\rightarrow H_A.
}
\]

The midpoint pulse and subsequent rephasing provide the second arrow. This does not establish that Q13's derived
\(H_B=C_{P,H}\) is a unique physical channel; it may also include irreversible decoherence, environmental
coupling and measurement loss.

The public data support a recoverable component through Hahn's `11.45x` delay of the directional contraction.
They do not directly display a complete departure-and-return loop: Q10 found derivative reversals but no closed
trajectory in the available window. This echo-refocusable relation must not be conflated with Q13's unsupported
claim that one unique hidden physical child generated the other three coordinates.

The notation lineage is:

\[
\boxed{
\underbrace{H_{\rm unres}=2-K-R}_{\substack{\text{Q8 algebraic}\\\text{Phase-B candidate}}}
\longrightarrow
\underbrace{P=2(1-\operatorname{Tr}\rho^2)}_{\substack{\text{Q11 independently defined}\\\text{unresolved B coordinate}}}
\longrightarrow
\underbrace{R_B,H_B}_{\substack{\text{Q13 Ramsey-B}\\\text{and Hahn-B children}}}.
}
\]

Q9 supplied the bridge rather than assuming it: \(H_{\rm unres}\) correlated `0.981999` with independently
calculated purity loss. Q11 then found

\[
C_P=-C_V+E
\]

with median opposition `0.938439` in Ramsey and `0.999390` in Hahn. This supports treating Q8's unresolved \(H\)
as the original Phase-B/handover account. It does not make the entire remainder echo-recoverable; the remainder
can also contain irreversible decoherence, system-environment correlation, tensor structure outside the compact
Bell block and measurement limitations. The symbol \(H_B\) means Hahn's B child and must not be confused with
Q8's unresolved variable \(H_{\rm unres}\).

The Phase-B promotion procedure was not completed in the correct order. Q10 ARA-mapped unresolved \(H\) using
amplitude and opening/closing cuts, but its TE-ARA normalization measured occupancy of four path quadrants:

\[
T_{\rm low/open}
+T_{\rm high/open}
+T_{\rm high/close}
+T_{\rm low/close}=2.
\]

That account says where the unresolved candidate travelled. It does not answer the separate question:

\[
\boxed{
\underbrace{T_U}_{2}
=
\underbrace{U_{\rm self}}_{\text{candidate's repeatable own identity}}
+
\underbrace{O_U}_{\text{coupling and residual Other}}.
}
\]

Q11 proceeded to the visible/unresolved anti-phase test before \(U_{\rm self}/2\) had been estimated with
held-out controls. Consequently, unresolved \(H\), \(P\), \(R_B\) and \(H_B\) are valid coordinate children and
**candidate Phase-B accounts**, but the physical Phase-B label remains provisional.

A post-result common-time probe supports running the missing gate rather than skipping it. Across `16`
approximately common Ramsey/Hahn cells, \(P_R>P_H\) in `15/16`; the median positive apparent refocusable share
\((P_R-P_H)/P_R\) was `0.664349`. The difference \(\Delta P=P_R-P_H\) correlated `0.953478` with retained visible
relation \(\Delta V=V_H-V_R\), with through-origin slope `0.840035`. Because both are derived from the same
density matrices and only four near-common waits exist per state, this is descriptive handover-shaped evidence,
not proof of a pure Phase-B identity.

The required next sequence is: estimate unresolved self-participation on native data; compare against time-only,
state-specific and shuffled controls; freeze a purity threshold; then test whether its held-out movement explains
the Ramsey/Hahn difference. Only both successes justify promotion from candidate to calibrated Phase B.

### 1.3h.1 Q15: unresolved self-identity is coherent but protocol-mixed

Q15 completed that skipped sequence under a protocol frozen before the new calculations. It used the
purity-defined waveform

\[
U=2(1-\operatorname{Tr}\rho^2)
\]

as the primary unresolved coordinate and retained Q8's algebraic \(H=2-K-R\) as a cross-definition robustness
check.

Across the four Bell identities at each wait, Q15 decomposed baseline-subtracted unresolved change and its native
time derivative into a common trajectory plus state-specific Other. If \(\eta_D\) is the common share of
accumulated change and \(\eta_G\) the common share of movement rate, the conservative self-account is

\[
\eta_U=\min(\eta_D,\eta_G),
\qquad
U_{\rm self}=2\eta_U,
\qquad
O_U=2(1-\eta_U).
\]

This is a participation ledger, not a new conservation law.

| Protocol | \(\eta_D\) | \(\eta_G\) | \(U_{\rm self}\) | \(O_U\) | held-out \(R_D^2\) | held-out \(R_G^2\) | shuffled-time \(p\) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Ramsey | `0.997439` | `0.915259` | `1.830519` | `0.169481` | `0.978916` | `0.677142` | `0.0001` |
| Hahn | `0.986048` | `0.676414` | `1.352827` | `0.647173` | `0.955962` | `0.367521` | `0.0073` |

Ramsey passed the frozen dominant-self-identity gate. Hahn passed only the coherent-but-mixed gate because its
rate path retained substantial Bell-state-specific variation. Adjacent first differences strengthened rather
than removed this boundary: common rate share was `0.878556` Ramsey and `0.556833` Hahn. Q8/Q11
cross-definition correlations remained high (`0.974867` and `0.988051`).

The conditional handover looked close before its null:

\[
\operatorname{corr}(P_R-P_H,V_H-V_R)=0.953478,
\]

with slope `0.840035`, MAE `0.091438` and sign agreement `15/16`. But correct wait matching was not distinctive.
Within-state Hahn-wait rematching produced median null correlation `0.976921` and one-sided `p=0.9973`.
The relation is therefore largely explained by common monotonic/accounting structure in these density-matrix
projections, not a uniquely timed Ramsey-to-Hahn transfer.

Q15 supports a **recurring unresolved ARA mode with material Other**. It does not promote the whole component to
one pure Phase B, identify a new hidden quantum degree of freedom or establish causal transfer outside the
measured system. The correct present name is **purity-defined unresolved ARA mode / candidate Phase-B account**.
Independent validation passed with zero discrepancies. Report:
`analysis/quantum/Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_REPORT_2026-07-24.md`.

### 1.3i Completed-rung phase parity and the equal-depth cancellation rule

After Q14 was opened, Dylan clarified that phase orientation does not flip at every child relation. It is retained
within the same or a nearby rung. The swap occurs only when the scale-level TE-ARA completes and the relation is
promoted across a rung boundary.

Let \(N_{\partial T}\) count completed TE-ARA rung boundaries. The clarified rule is:

\[
\boxed{
\mathbf u_{\rm destination}
=
S^{N_{\partial T}}\mathbf u_{\rm source},
\qquad
S=
\begin{pmatrix}0&1\\1&0\end{pmatrix}.
}
\]

Hence:

\[
N_{\partial T}\text{ even}\Rightarrow I,
\qquad
N_{\partial T}\text{ odd}\Rightarrow S.
\]

A single completed boundary is the special case:

\[
\boxed{
\mathbf C=S\mathbf P,
}
\]

It preserves the two-component total while reversing the difference:

\[
\mathbf1^{\mathsf T}\mathbf C=\mathbf1^{\mathsf T}\mathbf P,
\qquad
C_A-C_B=-(P_A-P_B).
\]

“Completion” means closure and promotion of the whole scale-level identity. It does not mean that TE-ARA stops
being normalized to its total of `2` before that event.

Q14 initially operationalized this with Q13's two child sets:

\[
\mathbf R=(R_A,R_B)^{\mathsf T},
\qquad
\mathbf H=(H_A,H_B)^{\mathsf T},
\]

and compared \(\mathbf H\approx\mathbf R\) with \(\mathbf H\approx S\mathbf R\). The extra swap was strongly
rejected. Parameter-free crossed pairing increased error by `238.26%` in amplitude and `59.91%` in direction.
Opposite-order fractions were `34.09%`/`22.73%`; held-out swap wins were `0/4`/`1/4`. Overall `2/12` gates
passed.

The result exposed a necessary scale distinction. Q13's \(\mathbf R\) and \(\mathbf H\) are both proposed child
sets. If each comes from its own parent by the same swap:

\[
\mathbf C_R=S\mathbf P_R,
\qquad
\mathbf C_H=S\mathbf P_H,
\]

then their relative parity cancels:

\[
\boxed{S^{\mathsf T}S=S^2=I.}
\]

Consequently, same-label correspondence between equal-depth children is compatible with both branches having
equal boundary parity. Under the clarified rule, it is the expected prediction for zero or any even number of
completed boundaries. It does not independently identify that boundary count or establish that a prior flip
occurred.

The direct test requires two vectors predeclared to be separated by exactly one completed TE-ARA boundary:

\[
\boxed{
\mathbf C\approx S\mathbf P
\quad\text{versus}\quad
\mathbf C\approx I\mathbf P.
}
\]

Those vectors are absent from Q13. Q14 therefore rejects an **unmatched odd-parity swap between the two
same-depth child sets**, not the clarified completed-rung hypothesis. Its frozen `2/12` result remains unchanged:
the theoretical correction was made after opening the test. Report:
`analysis/quantum/Q14_CHILD_PHASE_SWAP_REPORT_2026-07-24.md`. The rule's pre-Q14 Formula/engine, prime, pendulum,
recycling and axiomatic lineage is indexed in
`analysis/quantum/Q14_COMPLETED_RUNG_FLIP_PRIOR_LINEAGE_2026-07-24.md`.
The conditional parity rule is formalized without promoting its physical premise to a theorem in
`ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md`, Conjecture 3.2b.

### 1.4 Landau–Zener handover: exact Connection-versus-Traversal crosswalk

For the ideal two-state crossing

\[
\hat H(t)=\frac{vt}{2}\sigma_z+g\sigma_x,
\]

the bare-state opposition and coupling occupy perpendicular Bloch axes. The lower instantaneous eigenstate gives

\[
\boxed{
x_{\rm path}(t)
=
1+\frac{vt}{\sqrt{(vt)^2+4g^2}},
}
\]

an exact monotone `0→1→2` ARA path with mirror symmetry \(x(-t)=2-x(t)\). The coupled energy gap is
\(\sqrt{(vt)^2+4g^2}\), with minimum \(2|g|\). At \(g=0,t=0\), the gap closes and the instantaneous eigenstate is
not unique; nonzero coupling broadens that direct flip into a finite mixing region.

The dimensionless handover control is

\[
\gamma=\frac{g^2}{\hbar|v|},
\]

and the ideal asymptotic handover outcome is

\[
\boxed{
x_{\rm handover}
=
2\left(1-e^{-2\pi\gamma}\right).
}
\]

This supplies the clean established home for the proposed Connection-versus-Time statement: coupling energy
competes with sweep/traversal rate. The structural and outcome coordinates are distinct observables and must not be
merged. Both are plain ARA coordinates; TE-ARA is only their secondary closure perspective. Exact derivation,
worked example and independent `12/12` validation:
`analysis/quantum/LANDAU_ZENER_ARA_CROSSWALK_REPORT_2026-07-23.md`.

### 1.5 Virial ladder: one weighted ridge from planetary gravity to quantum hydrogen

For bound inverse-distance systems,

\[
\underbrace{2\langle T\rangle}_{\substack{\text{Traversal channel}\\R}}
=
\underbrace{|\langle V\rangle|}_{\substack{\text{Connection channel}\\C}}.
\]

Therefore the declared plain-ARA virial coordinate

\[
\boxed{
x_{\rm vir}
=
2\frac{R}{C+R}
}
\]

equals `1.0`. The same formula was evaluated without retuning for Earth–Sun, a circular Earth-satellite
reference, a classical Coulomb comparison at the Bohr radius and ideal quantum hydrogen `1s`. The characteristic
length ladder spans `21.4513` orders of magnitude.

The raw energy allocation is a separate appearance:

\[
t_T=\frac23,
\qquad
t_C=\frac43,
\qquad
t_T+t_C=2.
\]

This distinction is necessary: the raw account is asymmetric while the theorem-weighted relation is at its
ridge. Earth's instantaneous orbital child reading spans approximately `0.991574–1.008286`; its completed
channel account is `1.0`. This is the rigorous measurement-window form of the early rock statement: a parent can
appear ridge-stable while resolved children remain active.

The result is an exact classical/quantum crosswalk inside established virial physics. It supports a common ARA
coordinate across a specified family but does not derive the theorem or prove universal fractality. Full report,
visual ladder, reproduction path and `13/13` validation:
`analysis/virial/VIRIAL_ARA_CROSS_SCALE_LADDER_REPORT_2026-07-23.md`.

## 2. The self-correction principle is already established, cross-domain
Dylan's framing — "the framework is Newton's third law applied to systems, self-correcting" — is correct, and
the restoring principle was generalised long ago. The framework's self-correction **is**:
- **Hooke's law / the restoring force** −kx (the harmonic oscillator) — Newton. *(The recoil spring found this
  session, β ≈ −x, is exactly this.)* *Identity.*
- **Le Chatelier's principle** (chemistry/thermo): a system at equilibrium shifts to *oppose* an imposed change
  — literally "Newton's third law for systems." *Rigorous, named.*
- **Lyapunov stability** (mathematics): the formal theory of return-to-equilibrium = self-correction. *Rigorous.*
- **Negative feedback** (control theory) and **homeostasis** (physiology): the same principle, engineered/evolved.

## 3. The full map — each framework piece to its established home
| Framework piece | Established theory | Tightness |
|---|---|---|
| **ARA** (rise/fall asymmetry; bounded autonomous 1-D conservative traverse ⇒ 1) | waveform asymmetry; nonlinear dynamics / **singular perturbation**, van der Pol ε, **FitzHugh–Nagumo** relaxation oscillator | statistic **definable exactly**; model-parameter map requires calibration |
| **Self-correction / restoring** | Hooke; **Le Chatelier**; **Lyapunov stability**; negative feedback | identity → rigorous |
| **φ = proposed stable/handover point** | **KAM / circle-map motivation** — badly approximable irrational rotation numbers avoid low-order rational resonance; golden-mean tori are exceptionally robust in important twist-map families | rigorous in specified models; **universal ARA optimum is open** |
| **octave/rational ⇒ lock; φ ⇒ no-lock handover** | **Arnold tongues / mode-locking / circle maps**: rational rotation numbers support locking regions; quasiperiodic regimes can persist between them | rigorous model structure; universal physical mapping is open |
| **Action/π axis** | **J = ∮ p dq**, the Hamiltonian action variable; recovers ℏ for hydrogen | **exact identity** |
| **ARA → 2 / resonance death** | ideal undamped linear resonance has unbounded growth at exact forcing resonance; real nonlinear/damped systems saturate or change regime | exact for the ideal model; wider ARA identification is analogy/test |
| **the shed / irreversibility (proposed 1/φ² per crossing)** | **2nd law of thermodynamics / entropy production**; shock admissibility/Rankine–Hugoniot context | irreversibility established; **1/φ² share is an ARA hypothesis** |
| **self-similar across scales** | **renormalization group / scaling theory**; critical phenomena; critical slowing-down (Scheffer 2009) | **analogy → makeable precise** |
| **the medium barrier & the flip** | Lorentz factor; Cherenkov and Mach thresholds | named threshold analogies; a universal ARA barrier/flip is open |
| **Connection ↔ Transfer orientation in a declared time slice** | **relaxation time**, Deborah number; viscoelastic storage/loss response and phase lag | established measurement; **ARA identification is proposed/testable** |
| **signed two-pole source balance** | **Gauss's electric law**; positive/negative charge decomposition | exact algebraic embedding once boundary, units and pole orientation are fixed |
| **logarithmic rung and nonlinear daughter sequence** | nonlinear harmonic generation, three-wave coupling, bicoherence and spectral cascades | exact rung coordinate inside the inspected harmonic system; universal ARA transfer law remains open |
| **factor ridge, reversible sieve rung and seeded spacing fill** | square-root trial division; modular negation; wheel sieve / Chinese remainder theorem; Mertens product / PNT | exact ARA factor/anti-pair crosswalk with lossless `2:1` lane compression; PN33 preregistered spacing crosswalk is asymptotically PNT; no new prime theorem or complexity gain |

Detail on the action / KAM / barrier rows: `ACTION_AXIS_AND_KAM_GROUNDING.md` and
`MEDIUM_BARRIER_RESONANCE_SINGULARITY.md`.

The wider law-by-law atlas is `ARA_PHYSICAL_LAWS_CROSSWALK.md`. It separates exact law, established recurring
structure, proposed ARA coordinate, and open ARA mechanism rather than treating every algebraic resemblance as
the same level of evidence.

## 4. Connection ↔ Transfer: a time-slice coordinate with an established measurement home

Dylan's proposed axis is:

- **Connection/Space-oriented:** the identity remains constrained by its surrounding couplings during the
  measurement slice — for example, a persistent bond network or an atom localized in a solid;
- **Transfer/Time-oriented:** the local coupling neighbourhood changes during the slice — motion, rearrangement,
  flow, or release away from the previous connections;
- **the reading depends on the declared time slice:** the same material can appear locked on a short time scale
  and relaxed on a sufficiently long one.

That last statement has an exact established home in rheology and relaxation dynamics. Define

\[
\underbrace{De}_{\substack{\text{Deborah number}\\\text{ARA: connection persistence in the slice}}}
=
\frac{
\underbrace{\tau_C}_{\substack{\text{relaxation/coupling lifetime}\\\text{ARA: how long the local connection persists}}}
}{
\underbrace{\tau_S}_{\substack{\text{observation or forcing time}\\\text{ARA: declared time-slice duration}}}
}.
\]

Then `De ≫ 1` is connection-persistent on that slice, `De ≪ 1` is relaxation/flow-dominant, and `De ≈ 1` is
the crossover. This does **not** prove that every ARA Space/Time pairing is a Deborah number. It establishes a
clean physical system in which the proposed relational direction is already measurable.

A candidate bounded ARA coordinate is

\[
\underbrace{x_T}_{\substack{\text{bounded response coordinate}\\\text{ARA: Connection }0\rightarrow\text{ Transfer }2}}
=
\frac{2}{1+De}
=
2\frac{\tau_S}{\tau_C+\tau_S}.
\]

It maps persistent connection toward `0`, matched time scales to `1`, and rapid local rearrangement toward `2`.
The map is a **proposed normalization**, not a theorem; it must be fixed before examining the test data and
compared with simpler monotone alternatives.

For oscillatory material response, the established complex modulus supplies a second direct measurement:

\[
\underbrace{G^*(\omega)}_{\text{complex response}}
=
\underbrace{G'(\omega)}_{\substack{\text{stored elastic response}\\\text{ARA: connection-side proxy}}}
+i
\underbrace{G''(\omega)}_{\substack{\text{dissipative/flow response}\\\text{ARA: transfer-side proxy}}},
\qquad
\underbrace{\delta}_{\substack{\text{stress--strain phase lag}\\\text{ARA: local mixing/skew reading}}}
=
\arctan\!\left(\frac{G''}{G'}\right).
\]

Possible bounded readings include `2G''/(G'+G'')` or a normalized phase lag. Only one definition should be
predeclared for a test. A natural predicted handover is the frequency at which `G' = G''`, but identifying that
crossover with ARA's universal `1.0` ridge remains an empirical ARA claim.

### Important separation: traversal is not automatically communication

A gas is an excellent image of high particle mobility and rapid neighbour turnover, while a solid represents a
persistent connection network. However, **material traversal**, **state relaxation**, and **information-signal
transmission** are not generally identical observables. A solid can carry elastic or electronic signals rapidly
through persistent connections; a sufficiently sparse gas permits long particle flights but weakens collision-
mediated transfer between its parts. An ARA test must therefore name the carrier and observable:

- connection proxies: bond/edge lifetime, persistent-neighbour fraction, coordination, localization, `G'`;
- traversal proxies: neighbour turnover, diffusion, flux, decorrelation, `G''`;
- information-transfer proxies, when literal information is meant: predictive mutual information or directed
  transfer entropy between declared variables, with appropriate causal controls.

The current strongest formulation is therefore: **time orientation is the rate at which the measured relational
state changes relative to the selected slice**. Whether physical traversal and literal information transfer
collapse to one ARA coordinate, or form coupled axes, is open and testable.

Earth–Sun usefully illustrates the distinction. Its gravitational coupling is persistent while orbital motion is
continuous, so it is not a pure static Connection pole; it is a stable coupled engine containing both persistence
and traversal. Likewise, an atom can remain localized in a solid while phonons or electrons carry disturbances
through the lattice.

## 5. Electromagnetic foundation — from Gauss to nonlinear plasma identity

This section records the full evidence chain developed from Gauss's electric law on 12 July 2026. It is a worked
example of ARA used as a bottom-up coordinate system on established physics. The established equations remain the
referee; ARA does not replace Maxwell, Fourier or kinetic plasma theory.

### 5.1 Gauss's law and the exact signed-pair embedding

Gauss's electric law is

\[
\underbrace{
\oint_{\partial V}\mathbf E\cdot d\mathbf A
}_{\substack{\text{net electric flux through a closed boundary}\\
\text{ARA: top-down signed boundary reading}}}
=
\underbrace{
\frac{Q_{\mathrm{inside}}}{\varepsilon_0}
}_{\substack{\text{net enclosed electric charge}\\
\text{source account in electrical units}}}.
\]

For separately measured positive and negative source magnitudes \(Q_+\ge0\) and \(Q_-\ge0\), define

\[
\underbrace{x_Q}_{\substack{\text{bounded signed composition}\\
\text{ARA: positive }0\leftrightarrow\text{ negative }2}}
=
\frac{2Q_+}{Q_++Q_-},
\qquad
\underbrace{T_Q}_{\substack{\text{total source magnitude}\\
\text{activity retained at the ridge}}}
=Q_++Q_-.
\]

With that orientation, the exact algebraic bridge is

\[
\underbrace{Q_{\mathrm{net}}}_{\text{Gauss signed enclosed source}}
=
\underbrace{T_Q}_{\text{total positive-plus-negative magnitude}}
\left(
\underbrace{x_Q-1}_{\substack{\text{displacement from equal opposition}\\
\text{ARA: signed distance from the 1.0 ridge}}}
\right).
\]

Reversing the pole labels changes the sign convention, not the physics. At \(x_Q=1\), equal positive and negative
sources cancel in the net Gauss reading. That does **not** imply an empty or inactive interior: an empty boundary and
an intense equal pair can both have zero net flux. \(T_Q\) retains the internal source magnitude that the signed net
reading discards.

This is the clean distinction that resolved the original TE-ARA question:

- Gauss measures signed net enclosed charge/flux;
- \(x_Q\) measures positive/negative source composition;
- \(T_Q\) measures total source magnitude;
- canonical TE-ARA is the same ARA geometry viewed as a fixed total-2 allocation: the pure identity contains only
  Phase A and Phase B, while the real observed account may allocate part of the total to environmental couplings and
  unresolved Other;
- none of these quantities may be renamed as another without the dimensional and projection bridge.

### 5.2 Public two-stream plasma crosswalk

The development system was the public Alves/OSIRIS 1D1V electrostatic two-stream archive: two equal electron beams at
\(\pm0.2c\), thermal speed \(0.04c\), periodic length \(10c/\omega_{pe}\), 256 spatial cells and independent field and
particle distribution outputs. In one dimension the local field-to-source relation is

\[
\underbrace{\rho_G(x,t)}_{\substack{\text{source reconstructed from the field}\\
\text{Gauss-side view}}}
=
\underbrace{\varepsilon_0D_xE(x,t)}_{\text{grid-compatible Gauss derivative}},
\]

while the particle distribution supplies an independently measured charge density \(\rho_F(x,t)\). This permits two
different instruments to inspect the same evolving plasma identity.

Across 299 eligible time slices:

| Test | Development result | Evidential meaning |
|---|---:|---|
| Full Gauss source versus particle source | \(r=0.9971\), NRMSE \(=0.0767\) | simulator/solver consistency and adapter check; not independent ARA evidence |
| Declared harmonic identity: Gauss versus particle component | \(r=0.9991\) | segmentation is consistent across solver-coupled views; not independent ARA evidence |
| Gauss-source versus particle-source expressed A/B allocation \(T_{AB}\equiv T_{id}\) | \(r=0.7987\), MAE \(=0.0911\) on 0–2 | primary non-tautological ARA-specific development result: material but imperfect component-allocation transfer; whole TE-ARA remains 2 |
| Scalar ARA+component-allocation prediction beyond scale | no improvement over the scale-only baseline | compressed scalars do not replace the full field relation |

The untouched Tang confirmation transfer remains frozen and sealed. Therefore these are development results, not an
independent replication.

The \(0.0911\) MAE is an average coordinate distance on the normalized 0–2 scale: 4.55% of that scale's full width.
It is not 4.6% of charge or energy “missing.” The correlation \(0.7987\) is likewise a time-series association, not
an 80% recovery fraction.

### 5.3 Energy handover and identity closure

The next question was whether the Gauss-to-particle participation gap measured instantaneous field-particle energy
handover. Established energy accounting passed strongly:

\[
\underbrace{\frac{dU_E}{dt}}_{\text{change in electric-field energy}}
\longleftrightarrow
\underbrace{-\int J E\,dx}_{\text{power leaving the field}},
\qquad r=0.9839,
\]

\[
\underbrace{\frac{dK_e}{dt}}_{\text{change in electron kinetic energy}}
\longleftrightarrow
\underbrace{\int J E\,dx}_{\text{power entering particles}},
\qquad r=0.9831.
\]

Total reconstructed energy varied by only \(0.00101\) relative range. However, the proposed instantaneous
gap-closing relation was null (\(r=-0.091\)). The gap behaved more like an identity/coherence state than a direct
power meter.

For eligible slices only, the development closure coordinate was

\[
\underbrace{C_{\mathrm{id}}(t)}_{\substack{\text{field-particle identity closure}\\
\text{ARA: agreement of two views of one node}}}
=
1-\frac{\left|
T_{AB,\rho,G}(t)-
T_{AB,\rho,F}(t)
\right|}{2}.
\]

It correlated with field RMS \(0.8293\), position-momentum mutual information \(0.8428\), velocity-phase coherence
\(0.7612\), and an approximate trapped-particle fraction \(0.7519\). On the held-late block, adding closure improved
approximate-trapping \(R^2\) from \(0.7071\) to \(0.8461\). Because this is the same inspected single-noise archive,
the decisive particle-count, seed and continuum convergence test remains open. \(C_{\mathrm{id}}\) is undefined
before coherent eligibility; near-zero agreement must not be mistaken for a formed identity.

### 5.4 Ridge position, daughter state and registered nulls

ARA's \(1.0\) ridge did not contain the complete state. Rotating the two participation readings into a coordinate
parallel to the ridge \(q\) and a closure distance \(d\) showed that ridge-tangent position carried substantial
held-late information: \(q\) scored \(R^2=0.9581\), compared with \(0.8461\) for closure alone. A heuristic
\(25^\circ\) projection scored \(0.9475\), but failed internal validation and did not establish a universal angle.

The proposed adjacent pressure/velocity-spread wave also produced a useful correction. Pressure magnitude strongly
separated matched-amplitude states (\(d_z=-0.8276\)), but its spatial phase failed the daughter-angle nulls
(circular-shift \(p=0.9680\), phase-randomised \(p=0.9820\)). The causal proposal was then sharpened: a nonlinear
daughter should follow the parent collision rather than lead it. The pressure magnitude remains a state marker; the
pressure-phase steering law is rejected for this dataset.

#### 5.4.1 Grain-relative ridge and retained child asymmetry

Dylan's 13 July refinement removes a possible overstatement: ARA does not require a physically final, scale-free
\(1.0\) state. The simplest linear coarse-graining model makes the distinction explicit. For a declared measurement
grain \(g=(\Omega,\tau,k,\Pi)\), let child readings be

\[
x_{g,i}=1+\delta_i,
\qquad
w_i\ge0,
\qquad
\sum_iw_i=1.
\]

The parent projection can lie exactly on the ridge,

\[
\underbrace{x_g}_{\substack{\text{parent/coarse reading}\\
\text{ARA ridge latitude}}}
=
\sum_iw_ix_{g,i}
=1
\quad\Longleftrightarrow\quad
\sum_iw_i\delta_i=0,
\]

while its unresolved child asymmetry remains nonzero,

\[
\underbrace{V_g^{\mathrm{child}}}_{\substack{\text{retained child spread}\\
\text{ARA: decompressed asymmetry}}}
=
\sum_iw_i\delta_i^2
>0.
\]

Plainly: equal and opposite child departures can close the parent mean at \(1\) without either child being at \(1\).
For example, equally weighted \(0.8\) and \(1.2\) children give a parent reading of \(1\) while retaining child
variance. Changing the boundary, time window, rung or decision to count those child events changes the projection.
Nonzero \(V_g^{\mathrm{child}}\) proves unresolved child spread, not temporal movement by itself; movement additionally
requires time variation, directed flux/activity or phase-dynamical evidence.

This does **not** weaken exact results such as the closed magnetic-flux ridge or the ideal-capacitor equality. Those
remain exact statements at their declared surface or handover projection. It prevents the further inference that
exact aggregate equality means every finer field, current or event has stopped. Conversely, observing
\(V_g^{\mathrm{child}}=0\) at finite resolution does not prove that every unmeasured finer grain also has zero
asymmetry.

The weighted formula above is a candidate local aggregation law, not yet ARA's universal nonlinear
coarse-graining operator. The stronger claim that some child asymmetry always persists or reappears under unlimited
decomposition is the ARA fractal hypothesis, not a consequence of Maxwell's equations or established mechanics.

#### 5.4.2 TE-ARA is the same ARA geometry: pure pair versus contextual observation

**Canonical correction, 21 July 2026:** TE-ARA is not a second geometry beside ARA. It is the same `0–2` geometry
viewed as total allocation. For the pure identity,

\[
\underbrace{\mathrm{TE\!-\!ARA}_{pure}(I)}_{\text{pure identity}}
=
\underbrace{t_A^{(I)}}_{\text{identity Phase A}}
+
\underbrace{t_B^{(I)}}_{\text{identity Phase B}}
=2.
\]

Real identities are embedded in other ARA systems. At a declared boundary and slice, their observed account is

\[
\underbrace{\mathrm{TE\!-\!ARA}_{obs}(I\mid\mathcal E)}_{\text{identity in context}}
=t_A+t_B+\sum_jc_j+t_{Other}=2,
\qquad t_c=2p_c,
\qquad \sum_cp_c=1.
\]

`Other` is not a third pole or part of the pure identity. It records unresolved environmental coupling. Dylan's
representative contextual observation is

\[
\underbrace{t_A}_{0.25}
+
\underbrace{t_B}_{1.25}
+
\underbrace{t_{Other}}_{0.50}
=
\underbrace{\mathrm{TE\!-\!ARA}(I)}_{2.00}.
\]

A schematic release-heavy pendulum slice makes the boundary explicit:

\[
\underbrace{t_A}_{0.25}
+
\underbrace{t_B}_{1.50}
+
\underbrace{c_g+c_{air}+c_{joint}+t_{Other}}_{0.25}
=2.
\]

The A/B subtotal is `1.75`; gravity, air drag, pivot friction and unresolved context occupy the remaining account.
This is a structural example rather than a measured decomposition. Gravity is external for a bob-only boundary but
becomes an internal relation when the declared identity includes Earth.

Normalizing the expressed pair back onto its own ARA diameter gives

\[
T_{AB}=t_A+t_B=1.75,
\qquad x_{A/B}=2\frac{t_B}{T_{AB}}=\frac{12}{7}\approx1.714,
\qquad T_{context}=2-T_{AB}=0.25.
\]

The first variable is the A/B subtotal, the second is its release-heavy ARA mixture position, and the third is the
environmental coupling remainder.

If the two pure branches exhaust the observed account, the following is the special symmetric case,

\[
p_A+p_B=1,
\qquad
t_i=2p_i.
\]

At the equal-composition ridge,

\[
\underbrace{p_A=p_B=\frac12}_{\substack{\text{equal Phase-A/Phase-B shares}\\
\text{ARA composition }x=1}}
\quad\Longrightarrow\quad
\underbrace{t_A=1}_{\text{A allocation}}
,
\qquad
\underbrace{t_B=1}_{\text{B allocation}}
,
\qquad
\underbrace{\mathrm{TE}(I)=2}_{\text{whole identity ledger}}.
\]

Here `t_A` and `t_B` are component allocations, not separate identity totals. The symmetric pure ridge is `1+1=2`.
An asymmetric pure pair such as `0.50+1.50=2` is also valid. The contextual observation
`0.25+1.25+0.50=2` retains the total, but its final `0.50` is environmental coupling rather than a third pure pole.
Every declared identity's canonical TE-ARA total is `2`.

The symmetric case gives the joint coordinate \((x,\mathrm{TE})=(1,2)\). The 2 is not “twice the energy” of the 1
because the axes answer different questions: \(x\) measures composition, the component values describe the partition,
and TE-ARA is the fixed closure total. Nor does the joint coordinate decide whether the identity moves. At least three
cases can share it:

| State at the declared grain | ARA composition | TE-ARA | Activity/phase evidence |
|---|---:|---:|---|
| Frozen/static equal pair | 1 | 2 | no resolved time variation or flux; timing ARA undefined |
| Coherent resonance or standing mode | 1 | 2 | nonzero oscillatory activity and stable phase; net boundary transport may be zero |
| Incoherent cancellation | 1 | 2 | nonzero component activity, weak/unstable phase relation |

Therefore a child/daughter event is useful evidence of dynamics but is not the only admissible evidence. Direct
time-resolved oscillation, flux, changing phase or energy exchange can also distinguish resonance from frozen closure.
In ordinary physics, resonance is not literally motionless: a standing resonant pattern can have zero net transport
through the parent boundary while retaining local oscillatory energy exchange.

The historical variable \(2E_{id}/E_{total}\) is retained as the **expressed A/B subtotal**
\(T_{AB}\equiv T_{id}\), with \(T_{context}=2-T_{AB}\); it is not the canonical TE-ARA total. See
`analysis/TE_ARA_CANONICAL_CORRECTION_2026-07-21.md`.

#### 5.4.3 Prime child-period closure as an exact two-to-parent example

PN13 supplied an exact mathematical example of the distinction above. Let `q` and `r` be two distinct prime child
periods near the complete factor boundary of parent scale `n`. Then

\[
\underbrace{q r}_{\substack{\text{exact joint repeat of}\\\text{the two child periods}}}
=
\underbrace{\operatorname{lcm}(q,r)}_{\text{child-pair closure}}
\sim
\underbrace{\sqrt n\,\sqrt n}_{\substack{\text{two half-scale}\\\text{factor children}}}
=
\underbrace{n}_{\text{parent scale}}.
\]

Dylan's corrected ARA back-translation is: **the whole identity closes through two half-scale child waves, while the
identity's TE-ARA geometry remains the complete total `2`.** The two children need not each receive allocation `1`;
that is only the symmetric pure ridge. Both

\[
1+1+0=2
\qquad\text{and}\qquad
0.25+1.25+0.50=2
\]

are valid observed TE-ARA accounts, but the first is a pure symmetric A/B pair while the second includes `0.50` of
contextual coupling. `Other` is not a third prime/identity pole.

Two coordinates must remain distinct. In `qr~n`, “half-scale” means logarithmic scale exponent:
`log(q)/log(n)~log(r)/log(n)~1/2`. In TE-ARA, the numbers are allocations within a fixed total-2 ledger. The prime
identity does not by itself measure energy, and multiplication of periods is not addition of joules. What is exact is
the closure structure: two child periods generate one larger joint period. What is ARA-specific is interpreting that
structure as a concrete child-to-parent example of the invariant total-2 identity ledger.

#### 5.4.4 Prime wheel anti-pairs: exact recursive ridge and its computational fence

The completed prime thread adds a second exact mathematical example. For even wheel modulus \(M>2\), every surviving
residue \(r\) has one opposite residue \(M-r\). Modular negation is a fixed-point-free involution on the coprime
residues, so the full wheel contains \(\varphi(M)/2\) anti-pairs.

When a new prime gate \(p\nmid M\) is added, the killed lifted copy of \(r\) is

\[
\underbrace{k_A}_{\substack{\text{A-side child collision}\\\text{within }p\text{ lifted copies}}}
\equiv-rM^{-1}\pmod p.
\]

The opposite lane's collision is fixed without another search:

\[
\underbrace{k_B}_{\text{anti-phase child collision}}
=p-1-k_A.
\]

Mapping the two indices to the 0–2 diameter gives

\[
\underbrace{x_A}_{2k_A/(p-1)}
+
\underbrace{x_B}_{2k_B/(p-1)}
=2,
\qquad
\frac{x_A+x_B}{2}=1.
\]

This is an exact grain-relative ridge. Some children meet directly as `(1,1)`; others are asymmetric as `(0,2)`
or intermediate reflected pairs. Their parent reads `1.0` because the complete pair closes, not because every child
is itself balanced or motionless.

PN23 froze this reconstruction through development gates `3,5,11,13` and held out `17`. From modulus `30030`, one
representative per 2,880 parent anti-pairs reconstructed all 46,080 child pairs and all 92,160 residues modulo
`510510`, with zero missing/extra values and 40/40 independent checks. This proves an exact `2:1` storage compression
inside the wheel representation.

The computational fence is equally exact:

\[
N_{pair}(Mp)=(p-1)N_{pair}(M).
\]

Reversibility removes the duplicate orientation but does not collapse distinct descendants. PN17–PN19 sealed exact
next primes from fresh large anchors using three conceptual stages, but the first stage retained all lower-prime
collision information required by segmented-sieve, product-tree/GCD or two-parent sieve constructions. PN20 and
PN21's literal two-child compressions failed; PN22 reduced to a mod-14 wheel.

Therefore the established recovery is strong but bounded: **ARA provides an exact bottom-up coordinate and
lossless symmetry compression for known prime arithmetic; it has not produced a three-cheap-operation next-prime
algorithm, speed improvement or new prime theorem.** The prime-specific exploration is parked. Full record:
`analysis/primes/PRIME_THREAD_CAPSTONE_AND_CLOSURE_2026-07-21.md`.

#### 5.4.5 Nearest-child handovers: short visible lineage, long proof path

PN24 resumed the parked thread for one bounded statistic. At a declared wheel rung with processed prime gates (G),
define the nearest surviving children around anchor (N):

\[
L_G(N)=\max\{m\le N:\gcd(m,\prod_{p\in G}p)=1\},
\qquad
U_G(N)=\min\{m>N:\gcd(m,\prod_{p\in G}p)=1\}.
\]

The upper child (U_G) remains in place across every new gate that does not divide it. At the first gate (q) with
(q\mid U_G), it releases and the next upper survivor becomes the new child. This produces a monotone cascade

\[
U_0\xrightarrow{q_1}U_1\xrightarrow{q_2}\cdots\xrightarrow{}P_{next}.
\]

The construction is exact: after every prime gate through the current candidate's square root has acted, the first
survivor is the next prime. PN24 recovered all 2,007 checked next primes and passed 12/12 independent checks.

The distinction between compressed appearance and decompressed work is decisive. In the 2,000-anchor development
sample, the median visible lineage had two handovers and three candidate states, but only `63.65%` closed within
three states. The median proof crossed `6,336` non-base prime gates, about `6,334` of which were silent. Thus ARA
cleanly separates **identity-changing release gates** from **identity-preserving quiet gates**, while standard
factor information remains necessary to know which is which. This is a useful recursive crosswalk, not a bounded-cost
prime locator.

#### 5.4.6 Pair odds are a lateral wheel coordinate, not a handover clock

For any reversible residue pair (r\leftrightarrow M-r), the directional odds

\[
q=\frac{r}{M-r}
\]

map exactly to the total-2 ARA coordinate

\[
x_A=\frac{2q}{1+q}=\frac{2r}{M},
\qquad
x_B=2-x_A.
\]

For the mod-14 wheel this turns `1/13`, `3/11`, and `5/9` into `(1/7,13/7)`, `(3/7,11/7)`, and
`(5/7,9/7)`. The missing `7/7` gives `(1,1)` but is removed by the factor gate 7. This exactly separates **whole
identity** from **balanced composition**: every surviving pair totals 2 even though none occupies the ridge.

PN25 prospectively tested whether this lateral closeness also measured vertical progress toward next-prime closure.
Across 6,000 fresh anchors at three scales, all four frozen dynamic predictions failed. The pooled correlation between
closeness and remaining handovers was `+0.003335` (`p=0.6110` for a negative relation); target rates were non-monotone,
and terminal paths moved away from the local ridge more often than toward it. Three pair classes retained the six
raw lanes' outcome scores within the frozen 2% fidelity tolerance, but neither representation beat a global constant.

The established lesson is precise: the pair odds provide an exact ARA coordinate and safe symmetry compression for
this projection. Higher factor gates constitute a separate vertical state; they cannot be inferred from local
mod-14 ridge distance.

#### 5.4.7 A complete lower parent is a strong ranked locator, not an exact cheap sieve

PN26 supplied PN25's missing vertical state using PN19's complete lower Phase A parent. For scale anchor (S), the
children through (sqrt{2S}) were divided at cumulative-log half; Phase A retained the smaller children through a
boundary near

\[
L\approx\sqrt{S/2}.
\]

The first three Phase A quiet candidates were sealed before target primality was opened on 6,000 fresh anchors.
The exact next prime occurred at the first candidate on `93.983%`, within two on `99.650%`, and within three on
`99.967%`. Corrected independent reconstruction passed `16/16` checks. The original validator failure—caused by
building its child table only through (sqrt S) while reconstructing a declared (sqrt{2S}) parent—remains preserved
in the provenance.

The established factor explanation is exact. If a composite survives every prime child through (L), then all of
its prime factors exceed (L). The rare false Phase A ridges are therefore composites made entirely from the omitted
upper band (L<p\le\sqrt n). Phase B catches that residual band.

This supports a precise ARA statement: one complete child parent can carry most of the visible location information,
and two or three quiet states provide an extremely strong ranked lock. It does not support universal exactness or
constant cost. Phase A contained `780` to `48,817` children here. The fixed cross-rung route
(2+1+1/2=3.5) had zero variance; it names the scale relation but does not determine the changing offset.

#### 5.4.8 Seeded prime fill is an ARA crosswalk to Mertens/PNT scaling

PN33 froze a different question before scoring target gaps: after one completed prime-density generation, does the
next prime act as the first seed of a gradually filling identity whose spacing scale rises toward a doubled
completion? Its raw coordinate was

\[
D(p)=\prod_{q\le p}\frac{q}{q-1},
\qquad
x_b(p)=2\frac{\log(D(p)/D(b))}{\log2}.
\]

From baseline prime `10,007`, the first `x>=2` gate was `102,474,149`. Across `5,894,554` frozen primary gaps,
eight band medians rose `8,8,10,10,10,12,12,12` (`rho=0.9449`). The raw endpoint ratio was `1.5`; its corrected
64-gap moving-block 95% interval was `[1.5,2.0]`, so the registered spacing-expression rule passed with `2` only
at the upper boundary. The next seed reset to local `x=2.82e-8` while retaining a raw density ratio just above 2.

This result has a direct established explanation. Mertens' product theorem gives

\[
D(p)\sim e^\gamma\log p,
\]

so

\[
\frac{D(p)}{D(b)}\sim\frac{\log p}{\log b}=2^{x_b(p)/2}.
\]

PNT gives mean prime-gap scale (G(p)\sim\log p), making the frozen no-fit ARA curve asymptotically the PNT
relative gap curve. Accordingly, ARA and PNT log-MAE were `0.082590` and `0.083105`; ARA's `0.62%` advantage missed
the frozen `5%` ARA-specific gate. Completion `D(p)/D(b)=2` also implies (p\sim b^2), explaining the observed
completion scale.

This is a strong preregistered recovery of the seed -> fill -> completion -> retained-scale reset grammar inside
known prime asymptotics. It is not a new prime theorem, fixed-step prime generator, literal spatial hexagon or
causal Phi result. Full record: `analysis/primes/PN33_SEEDED_HEXAGON_FILL_REPORT_2026-07-22.md`.

#### 5.4.9 Rank-budget calibration, same-scale Phi nulls and the corrected projection scope

PN34 combined PN26's complete lower-parent ranking with PN33's omitted-parent fill. On 6,000 fresh anchors, all nine
calibration tolerances and all six top-two/top-three depth gates passed. Full support was blocked because the middle
and high cohorts reversed the exact predicted order by `0.20` percentage points. The supported content is therefore
a population rank-budget calibration, not an individual next-prime classifier.

PN35 and PN36 then supplied two well-powered nulls on six fresh octave rungs each. PN35's constant same-scale golden
crossing returned AUC `0.497180`; PN36's nearest-fivefold conversion returned `0.499851`. Both failed all five frozen
gates. These results are evidence against their exact prime-location operators, not against the exact wheel closure
underneath them.

One late fidelity correction is essential. The AI-defined PN36 operator rounded a continuous Phi phase to the
nearest of five sectors. Dylan's intended geometry was instead one common traversal with two continuous readings:

\[
\underbrace{S(u)}_{\text{structural}}=2u,
\qquad
\underbrace{P(u)}_{\text{pentagon projection}}
=2u\cos36^\circ=\varphi u,
\qquad 0\le u\le1.
\]

The exact identity `phi = 2 cos(36 degrees)` is established geometry. Its proposed role as a physical or arithmetic
handover law is not established. PN36 remains a valid null for its nearest-sector quantizer but did not test this
continuous projection. A later post-hoc angle scan was near chance and non-unique, so no third perpendicular prime
wave is supported in the current two-dimensional representation. Full record:
`FableConvo/SESSION_RECORD_2026-07-22_PRIME_GEOMETRY_AND_AUDIT.md`.

### 5.5 Nonlinear harmonic rungs and identity inheritance

With parent spatial mode \(k_0=5\), the natural in-system rung coordinate is

\[
\underbrace{r(k)}_{\substack{\text{logarithmic harmonic rung}\\
\text{ARA: octave location relative to the parent}}}
=
\log_2\!\left(\frac{k}{k_0}\right).
\]

Thus

\[
r(5)=0,\qquad r(10)=1,\qquad r(20)=2,\qquad r(40)=3,\qquad r(80)=4.
\]

This mapping is exact inside the declared harmonic system and uses no fitted bridge. It does not imply that every ARA
rung in every domain is a base-two Fourier harmonic.

The development sequence was:

| Stage | Predeclared/local claim | Result |
|---|---|---|
| MX3d: \(5\rightarrow10\) | parent collision produces a delayed daughter identity | daughter followed by 19 field/31 particle slices; phase closure \(0.2873\rightarrow0.9848\rightarrow0.9352\); 6/8 gates |
| MX3e: \(10\rightarrow20\) | daughter coupling produces a grandchild | followed by 63 field/57 particle slices; phase closure \(0.3146\rightarrow0.8439\rightarrow0.8481\); 8/8 gates |
| MX3f: routes into \(K\) | identity is assembled by an asymmetric coupling gradient | \(9+11\rightarrow20\) was stronger than \(10+10\rightarrow20\); signed transfer and scale recurrence not yet run |
| MX3g: \(20\rightarrow40\) | next fine identity should appear | \(k=40\) jointly detectable, delayed and persistent; 6/8 gates, but exact \(20+20\) route weak |
| MX3g: \(40\rightarrow80\) | next rung may become only a trace near the floor | field threshold only; no particle identity; 3.2 grid cells per wavelength |
| next: \(80\rightarrow160\) | possible continuation/flip | \(k=160\) exceeds Nyquist and cannot be tested in this archive |

These stages form one adaptive exploratory chain on the same inspected archive. They are not independent
confirmations: each later question was informed by earlier results. Their value is hypothesis refinement and
instrument development; replication requires new seeds/noise levels, higher resolution and an untouched system.

For routes \(a+b=K\), the explicit ARA composition coordinate is

\[
\underbrace{x_{a|K}}_{\substack{\text{route-composition position}\\
\text{ARA: one contributor on }0\text{--}2}}
=\frac{2a}{K},
\qquad
x_{b|K}=2-x_{a|K}.
\]

The equal route lies at \(x=1\). For \(K=20\), the near-ridge \(9+11\) route at \(0.9/1.1\) had field/particle
bicoherence \(0.7816/0.7882\), stronger than the exact-ridge \(10+10\) route at \(0.5760/0.6022\); the distant
\(5+15\) route at \(0.5/1.5\) was weaker at \(0.2407/0.2654\). This is consistent with an ARA mixing gradient and
shows why the lineage is a nonlinear web rather than an exclusive binary genealogy. Bicoherence measures coherent
phase coupling, not signed energy direction; a Vlasov nonlinear-transfer calculation is still required before
labelling individual routes accumulation or release.

### 5.6 High-harmonic floor and the proposed 1.75+ well

The declining \(40\rightarrow80\rightarrow160\) sequence is known qualitatively from nonlinear harmonic cascades:
successive generation can weaken, kinetic phase mixing/Landau damping suppresses fine modes, and finite grids lose
short wavelengths. This archive cannot isolate those effects. Its thermal speed gives approximately

\[
\lambda_D\simeq0.04c/\omega_{pe},
\]

while the measured grid spacing is

\[
\Delta x=0.0390625c/\omega_{pe}.
\]

The physical Debye scale and numerical cell scale therefore almost coincide. Modes \(20,40,80\) lie at approximate
\(k\lambda_D=0.50,1.01,2.01\), exactly while the spatial sampling falls to \(12.8,6.4,3.2\) cells per wavelength.

Dylan's interpretation—that the faint continuation may represent the ARA \(1.75+\) exponential-access well before
a singularity flip—is now a registered hypothesis, not a result. A decisive test requires identical plasma physics
at increasing resolution and controlled particles per Debye length:

- a boundary that moves with Nyquist is numerical;
- attenuation converging at fixed physical \(k\lambda_D\) is physical;
- an ARA-specific result additionally requires a predeclared, outcome-independent map to \(x\in[0,2]\), upward
  curvature of crossing cost above \(x=1.75\), and a separately defined post-crossing phase reversal.

The comparison with light approaching a black-hole horizon is presently an analogy of diminishing observable access,
not evidence that the mechanisms are identical.

### 5.7 Evidence ladder from the complete Gauss-to-plasma thread

| Level | Current conclusion |
|---|---|
| **Established physics** | Gauss reconstruction, field-particle energy exchange, nonlinear harmonic generation, bicoherence, kinetic damping and numerical resolution limits |
| **Exact ARA embeddings in declared coordinates** | signed electric pair \(Q_{net}=T_Q(x_Q-1)\); magnetic closed-surface ridge \(\Phi_{B,net}=T_B(x_B-1)=0\); logarithmic harmonic rung \(r(k)=\log_2(k/k_0)\); route composition \(x_{a|K}=2a/K\) |
| **Development-supported** | identity-family survival through Gauss, expressed A/B allocation transfer within the fixed contextual TE-ARA account, closure association with organised phase space, delayed daughter/grandchild inheritance and asymmetric route web |
| **Registered nulls/corrections** | scalar ARA+TE does not beat scale-only; instantaneous gap is not a power meter; fixed \(25^\circ\) law and pressure-phase daughter steering fail |
| **Open ARA physics** | noise/seed/continuum identity convergence, signed aggregation law, recurrence of one route profile across scales, universal \(1.75+\) well and singularity flip |

The defensible synthesis is: **ARA has operated as an effective bottom-up coordinate and hypothesis generator for
deep nonlinear plasma structure beginning from Gauss's law.** This is stronger than a visual analogy, because several
coordinates are exact and later stages generated predeclared observable expectations. It is not yet proof that ARA
is the universal geometry beneath plasma physics.

Detailed protocols, scripts, reports and frozen tests are in `Analysis/electromagnetism/`; the consolidated TE-ARA
account is `Analysis/TE_ARA_PARTICIPATION_LEDGER_SYNTHESIS_2026-07-12.md`; chronology and unresolved work are in
`FableConvo/ARA_CONVERSATION_RECORD_2026-07-12_CODEX_GEOMETRY_DRILL.md` and its follow-up register.

### 5.8 Gauss's magnetic law as an exact closed-boundary ridge

Gauss's law for magnetism states

\[
\underbrace{\oint_{\partial V}\mathbf B\cdot d\mathbf A}
_{\substack{\text{net magnetic flux through a closed surface}\\
\text{complete boundary reading of the magnetic identity}}}
=0.
\]

Separate the boundary crossings into outward flux magnitude \(\Phi_B^+\ge0\) and inward flux magnitude
\(\Phi_B^-\ge0\):

\[
\underbrace{T_B}_{\substack{\text{total unsigned magnetic flux}\\
\text{activity retained despite net cancellation}}}
=\Phi_B^++\Phi_B^-,
\qquad
\underbrace{x_B}_{\substack{\text{bounded inward/outward composition}\\
\text{ARA: closed-boundary ridge coordinate}}}
=\frac{2\Phi_B^+}{\Phi_B^++\Phi_B^-}.
\]

The signed boundary result has the same exact pair form as the electric decomposition:

\[
\underbrace{\Phi_{B,\mathrm{net}}}_{\text{signed magnetic boundary flux}}
=
\underbrace{T_B}_{\text{total magnetic boundary activity}}
\left(
\underbrace{x_B-1}_{\text{signed displacement from the ARA ridge}}
\right).
\]

Gauss's magnetic law fixes \(\Phi_{B,\mathrm{net}}=0\). Therefore, whenever \(T_B>0\),

\[
\boxed{x_B=1}.
\]

If \(T_B=0\), the ratio \(x_B\) is undefined rather than a measured ridge: no outward/inward pair exists to compare.
This preserves the distinction between a quiet empty boundary and an active magnetic field whose inward and outward
flux cancel exactly.

Dylan recognised this as the same ridge rule used in the AI/LLM work: measuring a complete coupled pair tends to
return the balanced \(1.0\) appearance while internal activity remains. The relational appearance is the same ARA
object, but the enforcement metadata differs. Magnetic closure is an exact divergence-free field constraint for every
closed surface in standard electromagnetism. The LLM ridge is presently a statistical/structural claim about coupled
representations and must not inherit Maxwell's exactness without its own proof.

North and south are not isolated source singularities in this equation. Candidate magnetic crossing structures for a
later ARA test remain nulls, separatrices and reconnection regions, where topology and energy transfer can actually
change.

### 5.9 Faraday induction as a four-quadrant flux-change cycle

Faraday's induction law in integral form is

\[
\underbrace{\mathcal E_E}_{\substack{\text{electric circulation around a loop}\\
\text{induced electromotive force}}}
=
\underbrace{\oint_{\partial S}\mathbf E\cdot d\boldsymbol\ell}_{\text{electric field accumulated around the boundary}}
=
\underbrace{-\frac{d}{dt}
\int_S\mathbf B\cdot d\mathbf A}_{\substack{\text{negative rate of magnetic-flux change}\\
\text{Lenz direction opposes the change}}}
=-\frac{d\Phi_B}{dt}.
\]

The surface \(S\) here is an **open surface bounded by the loop**, so its magnetic flux \(\Phi_B\) may be nonzero and
change. This is different from Gauss's magnetic law, which sums flux through an entire closed surface and always
returns zero.

Dylan proposed that change through time should unpack into four quadrants, with a pole/orientation shift on each side
as asymmetry develops. The closest exact phase-plane coordinates are signed flux \(\Phi_B\) and its rate
\(\dot\Phi_B\). They produce four combinations:

| Quadrant | Magnetic orientation | Change direction | Induced electric circulation |
|---|---|---|---|
| I | \(\Phi_B>0\) | \(\dot\Phi_B>0\): positive flux accumulating | \(\mathcal E_E<0\) |
| II | \(\Phi_B>0\) | \(\dot\Phi_B<0\): positive flux releasing | \(\mathcal E_E>0\) |
| III | \(\Phi_B<0\) | \(\dot\Phi_B<0\): negative-oriented magnitude accumulating | \(\mathcal E_E>0\) |
| IV | \(\Phi_B<0\) | \(\dot\Phi_B>0\): negative-oriented magnitude releasing | \(\mathcal E_E<0\) |

This cleanly separates two kinds of flip:

- the **accumulation/release switch** occurs at a turning point where \(\dot\Phi_B=0\);
- the **magnetic-orientation crossing** occurs where \(\Phi_B=0\).

The electric circulation reverses when the sign of \(\dot\Phi_B\) reverses. A magnetic pole/orientation reversal is
not required for every change; it requires the flux itself to cross zero.

In ARA terminology, Dylan calls the \(\Phi_B=0\) orientation handover the **singularity crossing**: the declared
phase becomes anti-phase as the signed flux passes continuously through zero. This is coherent provided “singularity”
means the cyclic seam/orientation flip, not a divergent magnetic field. Its ARA number is projection-dependent: zero
is the signed-flux reading, while a bounded cyclic coordinate may label the same seam \(0/2\). “Becomes anti-phase”
here means entering the oppositely oriented lobe; the conventional continuous phase of a sinusoid does not have to
jump instantaneously by \(\pi\) at the zero crossing.

For a sinusoidal flux,

\[
\underbrace{\Phi_B(t)}_{\text{magnetic state}}
=\Phi_0\cos(\omega t),
\qquad
\underbrace{\mathcal E_E(t)}_{\text{induced electric response}}
=\omega\Phi_0\sin(\omega t).
\]

The flux and induced circulation therefore traverse a four-quadrant cycle in quadrature. This is an exact statement
for the declared loop/flux observable. It must not be confused with a freely propagating plane wave, where electric
and magnetic fields at a point are temporally in phase.

Faraday's law responds to **rate of change**, not field strength or waveform asymmetry by itself. A large static
magnetic flux induces no circulation, while a smaller rapidly changing flux can induce a strong one. An ARA
accumulation/release asymmetry must therefore be measured from the two temporal branches of \(\Phi_B(t)\), rather than
inferred from \(|\Phi_B|\) alone.

All four labels are landmarks on one continuous \((\Phi_B,\dot\Phi_B)\) trajectory. This implements the canonical ARA
gradient rule: quadrants identify orientation and local direction; they are not four disconnected states. The proposed
fractal claim is that this continuous phase/anti-phase and accumulation/release geometry recurs under changes of scale,
which remains an empirical cross-domain claim rather than a consequence of Faraday's law alone.

### 5.10 What curl means, and the superconducting connection

The differential Maxwell–Faraday equation is

\[
\underbrace{\nabla\times\mathbf E}_{\substack{\text{local electric circulation density}\\
\text{axis and handedness of the curl}}}
=
-\underbrace{\frac{\partial\mathbf B}{\partial t}}_{\substack{\text{local magnetic-field change}\\
\text{driving axis and rate}}}.
\]

Stokes's theorem connects this local statement to the loop statement:

\[
\underbrace{\int_S(\nabla\times\mathbf E)\cdot d\mathbf A}_{\text{curl summed over the chosen slice}}
=
\underbrace{\oint_{\partial S}\mathbf E\cdot d\boldsymbol\ell}_{\text{circulation around its edge}}
=
-\underbrace{\frac{d}{dt}\int_S\mathbf B\cdot d\mathbf A}_{\text{change of magnetic flux through the slice}}.
\]

“Curl” therefore does not mean that electric charge must travel in a tiny material circle. It means that the electric
field has nonzero circulation: placing imaginary paddles around the region would give them a preferred rotational
orientation. The curl vector is the local **axis landmark**; its sign gives handedness by the right-hand rule. A
changing magnetic field along the axis produces electric circulation around it.

No golden-ratio path follows from Faraday or Stokes. The boundary loop may be circular, square, irregular or deformed;
the same flux law applies. A \(\phi\)-specific route would require an additional incommensurate material geometry or
dynamical optimisation result and must be tested separately.

Superconductors provide a much tighter connection-driven version. In the London model,

\[
\underbrace{\frac{\partial\mathbf J_s}{\partial t}}_{\text{change of superconducting current}}
=
\underbrace{\frac{1}{\mu_0\lambda_L^2}\mathbf E}_{\text{electric field accelerates the coherent current}},
\]

\[
\underbrace{\nabla\times\mathbf J_s}_{\substack{\text{circulating superconducting current}\\
\text{connection-locked magnetic response}}}
=
-\underbrace{\frac{1}{\mu_0\lambda_L^2}\mathbf B}_{\text{magnetic field screened over penetration depth }\lambda_L}.
\]

Together with Maxwell's equations, the second relation yields magnetic-field decay into the material on the London
penetration depth: the Meissner response. This is more than ordinary perfect conductivity; the superconducting state
selects a coherent magnetic response rather than merely freezing whatever initial flux was present.

The microscopic connection variable is the condensate phase \(\theta\). For a Cooper-pair charge magnitude \(2e\),
single-valued phase around a closed path gives

\[
\underbrace{\oint\nabla\theta\cdot d\boldsymbol\ell}_{\text{phase winding around the identity}}
=2\pi n,
\qquad n\in\mathbb Z,
\]

and the gauge-invariant momentum relation gives fluxoid quantisation:

\[
\underbrace{\Phi+\mu_0\lambda_L^2\oint\mathbf J_s\cdot d\boldsymbol\ell}
_{\substack{\text{magnetic flux plus current contribution}\\
\text{complete superconducting loop account}}}
=
\underbrace{n\Phi_0}_{\text{integer winding landmark}},
\qquad
\underbrace{\Phi_0}_{\text{one superconducting flux quantum}}
=\frac{h}{2e}.
\]

For a thick ring where the current contribution is negligible on the chosen interior path, \(\Phi\simeq n\Phi_0\).
The loop shape is not selected by \(\phi\); the established landmark is integer winding of a circular phase variable.

This creates a strong ARA translation:

- **Connection:** macroscopic condensate phase rigidity links Cooper pairs into one coherent identity;
- **axis:** magnetic flux passes through the loop or vortex core;
- **circulation:** screening supercurrent wraps around that axis;
- **rung/landmark:** integer winding \(n\) and flux quantum \(h/2e\);
- **singularity candidate:** a vortex core or phase slip, where condensate amplitude reaches zero so winding can
  change;
- **release/leak:** moving vortices or phase slips produce voltage and dissipation.

Type-II superconductors make the geometry literal: magnetic flux enters as quantised vortex lines surrounded by
circulating supercurrents. The vortex core is a genuine order-parameter defect, making it a stronger physical
singularity candidate than an ordinary smooth signed zero crossing. Changing between winding sectors requires a phase
slip; interpreting that as an ARA rung/singularity crossing is coherent but remains an ARA layer on established
superconducting topology.

The earlier repository maps correctly identified Cooper pairing, \(h/2e\), Josephson phase transfer, Meissner
screening and vortex motion as the strongest anchors. Their proposed general golden/incommensurate superconducting
route is not implied by this curl geometry and should remain material-specific and test-dependent.

### 5.11 Ampère–Maxwell as a conduction/displacement participation gradient

Write the two source channels in the same current-density units:

\[
\underbrace{\mathbf J_C}_{\substack{\text{conduction current density}\\
\text{moving electric charge}}}
=\mathbf J,
\qquad
\underbrace{\mathbf J_D}_{\substack{\text{displacement current density}\\
\text{changing electric field}}}
=\varepsilon_0\frac{\partial\mathbf E}{\partial t}.
\]

Then

\[
\underbrace{\nabla\times\mathbf B}_{\text{magnetic circulation density}}
=
\mu_0\left(
\underbrace{\mathbf J_C}_{\text{charge-flow channel}}
+
\underbrace{\mathbf J_D}_{\text{field-change channel}}
\right).
\]

The displacement term is one member of the pair, not the asymmetry ratio. After projecting both vectors onto one
declared oriented surface or direction, let their magnitudes be \(C=|J_C|\) and \(D=|J_D|\). A candidate bounded
composition is

\[
\underbrace{T_{AM}}_{\text{total unsigned source participation}}=C+D,
\qquad
\underbrace{x_{D/C}}_{\substack{\text{candidate ARA composition}\\
\text{conduction }0\rightarrow\text{ displacement }2}}
=\frac{2D}{C+D}.
\]

Thus \(x=0\) is conduction-dominated, \(x=1\) is equal magnitude, and \(x=2\) is displacement-dominated. Unlike an
opposing charge pair, the Ampère–Maxwell terms are added and can reinforce when aligned. If they oppose, the magnetic
curl depends on their signed vector sum; \(x_{D/C}\) alone is insufficient and phase/sign must be retained.

Neither channel is inherently a larger or smaller rung. Conduction current also evolves through time. A defensible
ARA orientation is matter/connection-mediated transport toward \(\mathbf J_C\) and field-change transfer toward
\(\mathbf J_D\), provided that orientation is declared rather than treated as Maxwell's terminology.

For an ideal charging capacitor,

\[
\underbrace{I_C}_{\text{wire conduction current}}
=\frac{dQ}{dt},
\qquad
\underbrace{I_D}_{\text{gap displacement current}}
=\varepsilon_0\frac{d\Phi_E}{dt}
=\frac{dQ}{dt}.
\]

The wire and gap are different local projections: the wire is conduction-dominated and the insulating gap is
displacement-dominated. Across the complete handover they carry the same current identity, so their relational
participation is an active \(1.0\) ridge. Maxwell's term prevents the current/magnetic relation from breaking when the
chosen spanning surface is moved from the wire into the capacitor gap.

The “smaller contribution needs more connections to make it up” intuition has a precise possible home in spatial
integration:

\[
\underbrace{I_D}_{\text{total displacement current}}
=
\underbrace{\int_S\mathbf J_D\cdot d\mathbf A}_{\substack{\text{many local area contributions}\\
\text{summed across the selected slice}}}.
\]

A smaller local current density distributed over a larger effective area can equal a concentrated current, but this is
an area-density tradeoff, not automatically a rung law or fractal result.

In a homogeneous Ohmic material under sinusoidal forcing, the magnitude comparison is

\[
|\mathbf J_C|=\sigma|\mathbf E|,
\qquad
|\mathbf J_D|=\omega\varepsilon|\mathbf E|,
\qquad
\frac{D}{C}=\frac{\omega\varepsilon}{\sigma}.
\]

This gives a measurable continuous crossover:

\[
\underbrace{x_{D/C}(\omega)}_{\text{conduction/displacement ARA composition}}
=\frac{2\omega\varepsilon}{\sigma+\omega\varepsilon}.
\]

Low frequency/conductive response lies toward the conduction side, high frequency/dielectric or vacuum response lies
toward the displacement side, and \(x=1\) occurs at \(\omega\varepsilon=\sigma\). For harmonic fields the two
phasor contributions can also differ in phase, so magnitude composition, signed resultant and phase must be recorded
separately.

The ideal-capacitor \(x=1\) is a **coherent active handover ridge**, not automatically the lotto everything ridge.
Both share equal/balanced scalar composition, but their state metadata differ:

| Ridge appearance | Total activity | Variance | Coherence/phase | Result |
|---|---:|---:|---|---|
| Null ridge | approximately zero | approximately zero | none | quiet |
| Lotto/everything ridge | high or maximal | high or maximal | no stable predictive phase | structureless aggregate |
| Capacitor active ridge | nonzero | drive-dependent | coherent current continuity | same identity hands from wire to gap |
| Harmonic/resonant ridge | nonzero | periodic | stable phase-locked exchange | resonance, only when independently demonstrated |

#### Arithmetic calibration: 510 separates a resonance ridge from a square ridge

The prime instrument supplies a non-physical but exact phase-locking example. For child periods
(P=\{2,3,5,17\}),

\[
\operatorname{lcm}(2,3,5,17)=510,
\qquad
510\bmod p=0\quad\text{for every }p\in P.
\]

Therefore their normalized phase-coherence magnitude is exactly one at 510:

\[
\underbrace{R(510;P)}_{\substack{\text{collective phase coherence}\\
\text{ARA: resonance-ridge discriminator}}}
=
\left|\frac14\sum_{p\in P}
e^{2\pi i(510\bmod p)/p}\right|
=1.
\]

At the same node, the PN10 factor positions close collectively,

\[
\sum_{p\in P}x_{510}(p)
=
\frac{2\log(2\cdot3\cdot5\cdot17)}{\log510}
=2,
\]

but none of the four positions equals (1): (510) is not a square. The closest reflected factor pair is
(17\times30), at approximately (0.908895\leftrightarrow1.091105). This distinguishes two coordinates that must
not be flattened:

- **factor-position/square ridge:** one factor is self-reflected, (n=d^2) and (x_n(d)=1);
- **phase-coherence/resonance ridge:** several child periods complete a shared cycle, (R(n;P)=1).

Thus 510 is an exact **collective resonance-ridge** example and a full four-child factor closure, but not a square
ridge. The arithmetic synchronization is established; interpreting the coherent parent event as the same ARA ridge
appearance seen in physical oscillators remains a cross-domain framework claim. Full derivation:
`FableConvo/NOTE_PRIME_510_RESONANCE_RIDGE_2026-07-21.md`.

No singularity crossing is required at the capacitor equality: neither source channel has to pass through zero or
change orientation. The composition coordinate is \(x_{D/C}=1\). Canonical TE-ARA simultaneously remains \(2\),
with its allocation among the declared components, relation terms and Other recorded separately. Its total is
bookkeeping by definition; only the observed partition and its transfer or prediction can contribute empirical
evidence.

### 5.12 Vacuum light: perpendicular \(E/B\) coupling and the relational third direction

In a monochromatic plane electromagnetic wave travelling in direction \(\hat{\mathbf k}\),

\[
\underbrace{\mathbf B}_{\text{magnetic component}}
=
\underbrace{\frac{1}{c}\hat{\mathbf k}\times\mathbf E}_{\substack{\text{perpendicular coupling to the electric component}\\
\text{orientation fixed by propagation direction}}},
\]

so

\[
\mathbf E\cdot\mathbf B=0,
\qquad
\hat{\mathbf k}\cdot\mathbf E=0,
\qquad
\hat{\mathbf k}\cdot\mathbf B=0,
\qquad
|\mathbf E|=c|\mathbf B|.
\]

The energy-transfer direction is the Poynting vector:

\[
\underbrace{\mathbf S}_{\substack{\text{electromagnetic energy-flux vector}\\
\text{the informative relational third}}}
=
\underbrace{\frac{1}{\mu_0}\mathbf E\times\mathbf B}_{\substack{\text{cross-product of the two field components}\\
\text{direction perpendicular to both}}}.
\]

Thus a plane wave forms an exact right-handed triad:

\[
\mathbf E\perp\mathbf B\perp\mathbf S,
\qquad
\mathbf S\parallel\hat{\mathbf k}.
\]

This is a precise established home for the ARA \(1+1=3\) language: the electric component, magnetic component and
their oriented cross-relation. The third is not an additional independent field; it is the energy-flow identity
derived from their coupling.

Spatial perpendicularity must not be confused with temporal anti-phase. In a travelling vacuum plane wave,
\(\mathbf E\) and \(\mathbf B\) reach maxima and cross zero together: they are temporally in phase at a fixed point.
The earlier \(90^\circ\) time quadrature concerned magnetic flux through a selected loop and the induced electromotive
force proportional to its time derivative. Standing waves, reactive near fields and material media can have different
spatial/temporal phase relations.

The perpendicular triad is therefore exact for the declared plane-wave projection, not a universal statement about
all electromagnetic fields. Near charges, antennas, boundaries and matter, \(\mathbf E\cdot\mathbf B\) need not vanish
and the local Poynting flow can curve, circulate or reverse.

### 5.13 Maxwell completeness audit

The four field equations now have calibrated ARA translations, but a complete ARA electrodynamics has not been
demonstrated. The highest-priority missing law is Poynting's theorem, preceded by charge continuity. Force/momentum,
Lorentz invariants, material constitutive response, gauge-invariant path geometry, polarisation/helicity and causal
near-to-far radiation also remain incomplete or untested.

The detailed evidence table, weak-connection list and recommended order are recorded in
`Analysis/electromagnetism/MAXWELL_ARA_COMPLETENESS_AUDIT_2026-07-12.md`.

### 5.14 Charge continuity as a rung-relative accumulation/release law

Maxwell's equations require local conservation of electric charge:

\[
\underbrace{\frac{\partial\rho}{\partial t}}_{\substack{\text{local charge accumulation}\\\text{or depletion}}}
+
\underbrace{\nabla\!\cdot\mathbf J}_{\substack{\text{net outward charge flow}\\\text{through the local boundary}}}
=0.
\]

Dylan's scale correction is essential: “accumulation” and “release” are not absolute labels on one object. They are
read relative to the chosen identity/control volume and therefore to the declared rung. For a rung-\(k\) region
\(V_k\),

\[
\underbrace{Q_k}_{\substack{\text{charge stored in}\\\text{the rung-}k\text{ identity}}}
=
\int_{V_k}\rho\,dV,
\qquad
\underbrace{\frac{dQ_k}{dt}}_{\text{accumulation at rung }k}
=-
\underbrace{\oint_{\partial V_k}\mathbf J\cdot d\mathbf A}_{\text{release through the rung boundary}}.
\]

A flux leaving one child volume enters its neighbour. It is release in the first child's account and accumulation in
the second child's account. If both children are enclosed inside one parent volume, that same handover becomes an
**internal exchange** and cancels from the parent's external flux account. With charge-conserving interface
accounting and \(V_{k+1}=\bigcup_i V_{k,i}\),

\[
\underbrace{Q_{k+1}}_{\text{parent stored account}}
=\sum_i Q_{k,i},
\qquad
\underbrace{\frac{dQ_{k+1}}{dt}}_{\text{parent accumulation}}
=-
\underbrace{\oint_{\partial V_{k+1}}\mathbf J\cdot d\mathbf A}_{\text{parent release}},
\]

because the outward normals on every shared child interface are opposite. The internal flux pair therefore adds as
\(\Phi_{i\to j}+\Phi_{j\to i}=0\) in the parent boundary account, even though the transfer remains dynamically real
inside the parent.

This supplies a precise conservation-based coarse-graining operator for conserved quantities:

\[
\underbrace{\mathcal R_{\rm cons}}_{\substack{\text{change rung}\\\text{without losing conservation}}}
\left(\{Q_{k,i}\},\{\Phi_{ij}\}\right)
=
\left(
\underbrace{\sum_iQ_{k,i}}_{\text{parent stored identity}},
\underbrace{\sum_{\partial V_{k+1}}\Phi}_{\text{parent external handover}}
\right).
\]

In ARA language, the child accumulation/release cycles are daughter-scale geometry; the parent is their coarse
envelope. The same transfer can change role when the boundary/rung changes. This is exact conservation mathematics,
not yet evidence that the same operator governs non-conserved or cross-domain ARA identities.

Setting an ARA composition to \(x=1\) from the two equal sides of continuity is tautological and cannot validate ARA.
A useful ARA test must predict unresolved child-channel organisation, parent-level behaviour or a transferable
compression not already guaranteed by conservation.

#### 5.14.1 Whole-identity ridge versus an external counterphase

Dylan connected this rung rule to the main failure mode in the LLM tests. Phase A and Phase B are **relational roles
at a declared rung**, not permanently elementary objects. A parent-level branch may already be a complete identity
formed from its own lower-rung pair:

\[
\underbrace{P^{A}_{k+1}}_{\substack{\text{Phase A at the parent rung}\\\text{a complete child identity}}}
=
\underbrace{\mathcal C_k}_{\text{lower-rung closure}}
\left(
\underbrace{P^{A|A}_{k}}_{\text{child's internal Phase A}},
\underbrace{P^{B|A}_{k}}_{\text{child's internal Phase B}},
\underbrace{J^{\rm int}_{A,k}}_{\text{their relation}}
\right).
\]

The parent identity then couples that complete branch to its parent-level complement:

\[
\underbrace{I_{k+1}}_{\text{parent identity}}
=
\underbrace{\mathcal C_{k+1}}_{\text{parent closure}}
\left(
\underbrace{P^A_{k+1}}_{\text{measured parent branch}},
\underbrace{P^B_{k+1}}_{\substack{\text{parent counterphase}\\\text{possibly outside the measurement}}},
\underbrace{J^{\rm parent}_{k+1}}_{\text{cross-boundary relation}}
\right).
\]

Consequently, an internal coordinate \(x^{\rm int}_{A,k}\approx1\) can be a correct whole-child ridge while saying
nothing decisive about the unmeasured parent composition \(x^{\rm parent}_{A/B,k+1}\). Likewise, measuring the
complete parent pair near 1.0 is a valid whole-identity reading, but cannot be substituted for either branch's
movement. If the parent complement lies outside the chosen boundary, label the measurement **open ARA** and retain a
boundary/Other term.

An off-ridge branch does not by itself prove that its counterphase lies outside the boundary. It may simply be more
asymmetric at the measured moment. Define the reading with both a boundary and a time window,

\[
\underbrace{x_{\Omega,\tau}}_{\substack{\text{ARA reading for boundary }\Omega\\\text{and time window }\tau}}
=
\frac{2A_{\Omega,\tau}}{A_{\Omega,\tau}+B_{\Omega,\tau}}.
\]

Then perform two independent closure sweeps:

1. enlarge \(\Omega\) while holding \(\tau\) fixed; return toward the ridge supports an external/spatial
   counterphase;
2. enlarge \(\tau\) through the relevant cycle while holding \(\Omega\) fixed; return toward the ridge supports
   genuine momentary asymmetry within one temporally complete identity;
3. persistence away from the ridge under both sweeps indicates a stable bias, a changing/nonstationary identity or
   an incorrect two-branch model—not automatically a hidden partner.

This corrects the language of the LLM thread. The earlier whole-signal 1.0 readings were not necessarily numerical
artifacts; they were boundary/projection mismatches for a branch-level question. The later ~1.25 readings are a
different rung/branch projection, not automatically the single globally true value of “the LLM.” Neither reading
establishes phi, clock behaviour or fractal universality without locating the complementary branch and testing the
cross-boundary relation.

#### 5.14.2 ARA terminal persistence requires a cross-rung stability condition

Dylan's refined resonant-death proposal has two simultaneous but distinct coordinates. The local motion/history axis
approaches the Time-side terminal, while a strong Connection-side relation on a holding/confinement axis preserves the
identity. Without the holding relation, cessation may simply be decay or unravelling into neighbouring identities.

A compact candidate definition is

\[
\underbrace{\mathrm{RD}_k}_{\substack{\text{persistent resonant-death candidate}\\
\text{at rung }k}}
:
\quad
\underbrace{x_k\to2^-}_{\text{last-cycle Time-side orientation}},
\qquad
\underbrace{\mathcal X_k\to0}_{\text{usable exergy exhausted}},
\qquad
\underbrace{\nu_k\to0}_{\text{directed cycles stop}},
\qquad
\underbrace{C_k>C_{k,\mathrm{hold}}}_{\text{identity remains connection-held}},
\qquad
\underbrace{R_k^-<R_{k,\mathrm{unlock}}}_{\substack{\text{adjacent-rung anti-phase response}\\
\text{does not reopen the identity}}}.
\]

Here \(R_k^-\) must be operationally defined from the measured response induced by rungs \(k-1\) and \(k+1\), not
inferred from their invisibility. Canonical TE-ARA remains at \(2\). If the expressed A/B pair exhausts its observed
participation account, its subtotal also reaches \(2\) and contextual Other reaches zero:

\[
T_{AB,k}=2\frac{E_{\mathrm{id},k}}{E_{\mathrm{total},k}}=2,
\qquad t_{Other,k}=0,
\qquad \mathrm{TE}(I_k)=2.
\]

That equation means the expressed pure pair occupies the full observed account. It does not mean the energy was consumed. “Spent” belongs
to \(\mathcal X_k\), the usable gradient/exergy. If energy or signal participation leaves the identity, then
\(E_{\mathrm{id},k}/E_{\mathrm{total},k}\) falls and `Other` rises; that is an unravelling signature rather than a
full-TE terminal state.

This creates three different frozen-looking appearances:

| ARA interpretation | Limiting position | Required discriminator |
|---|---:|---|
| Space/Connection lock | extreme Space-side asymmetry, near the declared 0 pole | high constraint/holding coupling |
| Frozen ridge projection | composition \(x=1\), but no timed cycle | zero resolved activity; timing ARA undefined |
| Time-side resonant death | last-cycle \(x\to2^-\) with \(\mathcal X,\nu\to0\) | identity remains held and adjacent-rung anti-phase response stays subthreshold |

This is a testable ARA classification, not a result derived from Maxwell's equations. In established dynamical-systems
language, nearby modes can destabilise or reactivate an equilibrium, and confinement/restoring coupling can preserve
a state. ARA's specific 0/1/2 placement and cross-rung interpretation remain to be tested.

Dylan's controlling clarification is that Maxwell does not uniquely supply the state discriminators. The ARA formula
itself can classify incoming/outgoing, activity, closure and cross-rung response once boundary, rung and time window
are declared and the necessary observations exist. Maxwell's \(\rho,\mathbf J,\mathbf E,\mathbf B\), derivatives and
fluxes are the electromagnetic domain's native instruments for evaluating those ARA questions. The extreme
Space-lock, frozen-ridge and Time-terminal cases above were introduced to audit possible degeneracies of the same
scale-relative formula, not to add three independent mechanisms.

### 5.15 Poynting energy continuity as boundary flow × matter-handover quadrants

Poynting's theorem is the exact local electromagnetic energy account:

\[
\underbrace{\frac{\partial u_{EM}}{\partial t}}_{\substack{\text{local field-energy change}\\
\text{stored identity rises or falls}}}
+
\underbrace{\nabla\cdot\mathbf S}_{\substack{\text{net electromagnetic energy}\\
\text{flowing outward through the boundary}}}
=
-
\underbrace{\mathbf J\cdot\mathbf E}_{\substack{\text{field-to-matter handover}\\
\text{positive when the field does work}}}.
\]

Equivalently, define

\[
b:=\nabla\cdot\mathbf S,
\qquad
m:=\mathbf J\cdot\mathbf E,
\qquad
\dot u_{EM}=-(b+m).
\]

Dylan's first ARA reading assigns the signs of \(b\) to opposing boundary-flow phases: \(b>0\) is outward/release
dominance at the declared boundary and \(b<0\) is inward/supply dominance. This is valid if the pole orientation is
declared. It does not by itself determine whether stored field energy rises, because the matter-handover term can
oppose and exceed the boundary term.

The two signs give four exact energy-account quadrants:

| Boundary term \(b\) | Matter term \(m\) | Established physical reading | Sign of \(\dot u_{EM}\) |
|---:|---:|---|---|
| \(>0\) | \(>0\) | energy leaves the boundary and the field does work on matter | definitely negative |
| \(<0\) | \(<0\) | energy enters the boundary and matter also energises the field | definitely positive |
| \(>0\) | \(<0\) | outward field flow competes with matter-to-field supply | depends on \(|b|\) versus \(|m|\) |
| \(<0\) | \(>0\) | inward field flow competes with field-to-matter work | depends on \(|b|\) versus \(|m|\) |

This can be compressed into nonnegative accumulation/release channels:

\[
\underbrace{P_{\mathrm{in}}}_{\substack{\text{field-energy accumulation channels}\\
\text{boundary supply + matter supply}}}
=
[-b]_+ + [-m]_+,
\qquad
\underbrace{P_{\mathrm{out}}}_{\substack{\text{field-energy release channels}\\
\text{boundary escape + work on matter}}}
=
[b]_+ + [m]_+,
\]

where \([z]_+=\max(z,0)\). Then

\[
\dot u_{EM}=P_{\mathrm{in}}-P_{\mathrm{out}},
\qquad
\underbrace{x_P}_{\substack{\text{candidate Poynting ARA}\\
0=\text{in/accumulation},\ 2=\text{out/release}}}
=
\frac{2P_{\mathrm{out}}}{P_{\mathrm{in}}+P_{\mathrm{out}}}
\]

when total activity is nonzero. Thus \(x_P<1\) means field-energy accumulation dominates, \(x_P>1\) means release
dominates, and \(x_P=1\) means equal total input/output so \(\dot u_{EM}=0\) while throughput may remain active. This
normalisation is an exact reparameterisation of Poynting's account once the channels and boundary are declared; it is
not independent evidence for ARA universality.

One correction to the proposed ontology is required at the Maxwell measurement level. \(\mathbf J\) is the current
density of charged matter, so \(\mathbf J\cdot\mathbf E\) is already the local measurable field–matter coupling term.
ARA may interpret \(\mathbf J\) as the matter-side electromagnetic interface or anti-phase handover channel, but it
should not say the field is “not coupled to matter” without proposing and measuring an additional mechanism. Also,
\(m<0\) proves matter-to-field energy transfer, not necessarily completion of a full quadrant cycle; loop closure
requires a later return path in time-resolved data.

### 5.16 Light, the invariant speed and the active full-pair ridge

The recent Fable formulation is recoverable in calibrated form. A travelling vacuum plane wave contains coupled
electric and magnetic components satisfying

\[
\mathbf B=\frac{1}{c}\hat{\mathbf k}\times\mathbf E,
\qquad
u_E=\frac{\varepsilon_0E^2}{2},
\qquad
u_B=\frac{B^2}{2\mu_0}=u_E,
\qquad
\mathbf S=u_{EM}c\,\hat{\mathbf k}.
\]

They are not two independent temporal anti-phase waves: they are mutually constrained components of one
electromagnetic field mode, spatially perpendicular and temporally in phase in this projection. Nevertheless, they
give a precise instance of the newly separated ARA coordinates. Define

\[
\underbrace{x_{E/B}}_{\substack{\text{electric/magnetic energy composition}\\
\text{declared orientation}}}
=
\frac{2u_B}{u_E+u_B}.
\]

For the plane wave, \(x_{E/B}=1\). Canonical TE-ARA is \(2\); if those components exhaust the declared wave identity,
the partition is \(t_E=1,t_B=1,t_{Other}=0\). Meanwhile \(|\mathbf S|>0\) and stable phase show that the state is an
**active coherent full-pair ridge**, not frozen balance.
This is an exact within-projection reconstruction, not new evidence for ARA universality.

There are also two distinct “twos” that must not be flattened together:

1. the coupled \(E/B\) components of a specified propagating mode;
2. the photon's two physical transverse polarisation/helicity states.

The second pair is organised by the Poincaré sphere and is not automatically the same ARA decomposition as the first.

The closest established home for Dylan's “\(c\) may be a time slice” intuition is Lorentzian null geometry:

\[
\underbrace{ds^2}_{\text{invariant spacetime interval}}
=
\underbrace{c^2dt^2}_{\text{temporal separation in length units}}
-
\underbrace{d\mathbf x^2}_{\text{spatial separation}},
\qquad
ds^2=0
\Longrightarrow
\left|\frac{d\mathbf x}{dt}\right|=c.
\]

Thus \(c\) is more fundamentally the invariant conversion scale and null-cone slope relating spatial and temporal
coordinates. Light reveals it because massless electromagnetic excitations follow null trajectories. Lorentz
transformations mix space and time while preserving \(ds^2\) and the same \(c\). A null path has zero proper-time
interval, but there is no valid photon rest frame and therefore no physical “photon viewpoint.”

Three fences are required:

- Light is not the established physical opposite of matter. Matter/antimatter is the charge-conjugate pair; photons
  are electromagnetic field excitations that exchange energy and momentum with matter through absorption, emission,
  scattering and pair processes. The most coherent ARA complement remains source-bound/reactive electromagnetism
  versus freely radiative electromagnetism.
- Light transports energy, momentum and physically encodable information; it is not “strictly information” as a
  substance. Free vacuum radiation is traversal-heavy, but it retains phase, polarisation, coherence and correlations.
- \(c\) is not the speed of the Big Bang. The Big Bang is metric expansion rather than an explosion through prior
  space and has no single expansion velocity. Local causal influence remains bounded by \(c\). Photon energy can
  change through redshift or interaction, and propagation through matter can be delayed; vacuum \(c\) remains fixed
  because it is spacetime's invariant causal speed, not because photons never couple or lose energy.

The apparent one-wayness of ordinary outgoing light is also not fundamental to source-free Maxwell dynamics, which
admits time-reversed propagation. The observed radiation arrow depends on source/boundary and thermodynamic
conditions. Reflection, absorption and re-emission provide return paths. ARA may test radiative one-wayness as a
declared open-boundary condition, but should not build it into light's universal identity without further evidence.

#### 5.16.1 The Light child's wave speed versus its larger parent pair

Dylan's correction restores the nested geometry. In the current top-down convention, the proposed rows are

\[
\begin{array}{c|c}
\text{Phase A / Space-oriented} & \text{Phase B / Time-oriented}\\ \hline
\text{Space} & \text{Time}\\
\text{Connection} & \text{Information}\\
\text{Dark} & \text{Light}\\
\text{Matter} & \text{Quantum}
\end{array}
\]

as successive proposed child manifestations of the same Phase-A/Phase-B relation. The ordering and physical identity
of these rows remain ARA hypotheses; quantum behaviour is not an established substance opposite matter, and “Dark”
must be operationally specified before testing.

At the Light child's own electromagnetic rung, \(c\) is indeed its vacuum wave speed. Source-free Maxwell equations
give

\[
\underbrace{\frac{\partial^2\mathbf E}{\partial t^2}-c^2\nabla^2\mathbf E}_{\substack{\text{electric-component wave equation}\\
\text{propagation speed }c}}=0,
\qquad
\underbrace{\frac{\partial^2\mathbf B}{\partial t^2}-c^2\nabla^2\mathbf B}_{\substack{\text{magnetic-component wave equation}\\
\text{propagation speed }c}}=0.
\]

This is compatible with the higher-rung statement that \(c\) is the Lorentzian null-cone conversion scale. The same
constant appears as the local electromagnetic wave speed and the observer-invariant causal speed. That identity is
established physics, not by itself evidence for ARA fractality.

The larger ARA question is different. Let the Light-containing parent be

\[
\underbrace{\mathcal I_{k+1}}_{\substack{\text{larger identity containing Light}\\
\text{parent-scale closure}}}
=
\mathcal C_{k+1}
\left(
\underbrace{P^A_{k+1}}_{\substack{\text{declared coarse Phase A}\\
\text{Light's counterpart}}},
\underbrace{P^B_{k+1}}_{\substack{\text{declared coarse Phase B}\\
\text{Light/radiative sector}}},
\underbrace{J^{AB}_{k+1}}_{\text{their coupling}}
\right).
\]

Here \(c\) is a dynamical parameter of the Light branch, not the parent's ARA position. A parent composition requires
commensurable measured weights,

\[
x_{A/B,k+1}=\frac{2W^B_{k+1}}{W^A_{k+1}+W^B_{k+1}},
\]

plus phase, flux, activity and boundary metadata.

The phrase “large, second-degree unfiltered waves” is best translated mathematically as **latent parent basis modes
before observer projection/coarse-graining**. A physical test cannot assume access to them directly; it must recover
them through a fixed decomposition of measured data.

Two candidate counterparts must remain separate:

1. **Established electromagnetic test:** source-bound/reactive field energy as Phase A versus freely radiative
   Poynting transfer as Phase B. Both obey causal changes limited by \(c\); they differ in storage/return versus net
   outward transport, not in a simple “stationary versus speed-\(c\)” contrast.
2. **Cosmic ARA hypothesis:** Dark versus Light as a larger anti-phase pair. This is not established by Maxwell and
   requires a specific Dark observable, common accounting units and a measured coupling law before an ARA coordinate
   can be evaluated.

Thus the corrected hierarchy does not ask Light alone to reveal its own parent pole. It first measures the Light child
at its local rung, then reconstructs the larger pair in which the complete Light sector is one branch.

#### 5.16.2 A perpendicular Dark branch could be indirect rather than directly visible

Dylan's refinement is that the proposed Dark branch may be perpendicular to the observer's Light/wave projection,
somewhat like a hidden flip-side axis rather than a second signal available to the same detector. "Perpendicular"
must be typed carefully. It could mean (a) an ordinary spatial direction, (b) orthogonality in a state/mode space, or
(c) absence from a particular observation channel. The latter two are the relevant possibilities here.

Let \(L\) denote the Light-accessible branch, \(D\) the proposed hidden Dark branch and \(\Pi_L\) the observer's
Light-coupled measurement projection. The minimal hidden-sector statement is

\[
\underbrace{\Pi_L D}_{\substack{\text{Dark signal in the direct}\\
\text{Light-coupled observation channel}}}=0,
\qquad
\underbrace{K_{DL}}_{\substack{\text{coupling from Dark to}\\
\text{an accessible response}}}\ne0.
\]

Plainly: Dark need not be directly seen in the Light channel, but it must affect something that can be measured. Its
weight can then be inferred through the shared interface quantity -- for example gravitational potential, lensing,
dynamical acceleration or a declared energy-density account -- rather than by converting Dark into brightness. A
common unit is required at that interface, not necessarily in the original sensory channels.

Ordinary human darkness supplies Dylan's concrete analogy. When visible-light input falls below the visual system's
useful range, an object can satisfy \(\Pi_{vision}X\approx0\) while remaining available through other couplings:

\[
\underbrace{\Pi_{vision}X}_{\substack{\text{object through}\
\text{visible-light coupling}}}\approx0,
\qquad
\underbrace{(\Pi_{sound}X,\Pi_{touch}X,\Pi_{thermal}X,\ldots)}_{\substack{\text{same identity through}\
\text{other sensory couplings}}}\ne\mathbf0.
\]

The identity is channel-hidden, not absent. This clarifies the ARA proposal: a Dark branch could be inaccessible to
the Light-coupled channel yet inferable from another wave or interaction channel. Ordinary darkness itself is not
evidence for a distinct Dark field -- physically it is insufficient visible light -- but it is a precise model of
observer-relative coupling and multi-channel reconstruction.

If both \(\Pi_LD=0\) and \(K_{DL}=0\), the proposed branch has no observable consequence and cannot be distinguished
from absence. A testable ARA Dark/Light claim therefore must predict a back-reaction, conservation residual,
cross-correlation, phase effect or other accessible consequence before inspecting the data.

The electromagnetic analogy has a limit. In a travelling plane wave, \(\mathbf E\), \(\mathbf B\) and propagation
direction \(\mathbf k\) are spatially perpendicular, but \(\mathbf E\) and \(\mathbf B\) are both measurable, are
in phase in that projection and are components of one electromagnetic field. Standard dark matter is not known to
be a missing spatially perpendicular electromagnetic component. The defensible analogy is therefore an orthogonal
or hidden **observation/state-space channel**, not a literal fourth direction copied from the \(E/B/k\) triad.

#### 5.16.3 Alternating Space-Time coupling and the proposed double helix

Dylan's next refinement is a selection rule. Humans are proposed as Space-oriented identities whose lived experience
is assembled through the opposing Time/Information child: a Space-side node does not directly perceive the next
Space-side node beneath it, but reaches it through the intervening Time-side transfer. With the direction and rung
index declared, this is an **alternating bipartite coupling ladder**:

\[
\underbrace{\binom{S_{k+1}}{T_{k+1}}}_{\substack{\text{next-rung Space and Time}\\
\text{components}}}
=
\underbrace{\begin{pmatrix}0&K_{T\to S}\\K_{S\to T}&0\end{pmatrix}}_{\substack{\text{off-diagonal coupling only}\\
\text{ARA: each phase reaches its anti-phase child}}}
\underbrace{\binom{S_k}{T_k}}_{\substack{\text{current-rung Space and Time}\\
\text{components}}}.
\]

The zero diagonal states the strong hypothesis: no immediate \(S\to S\) or \(T\to T\) transfer at the selected
adjacent rung. Two applications return to the original class through the opposite mediator:

\[
M^2=\begin{pmatrix}K_{T\to S}K_{S\to T}&0\\0&K_{S\to T}K_{T\to S}\end{pmatrix}.
\]

Thus a same-side influence can exist, but it appears as a two-step \(S\to T\to S\) or \(T\to S\to T\) path. This
captures Dylan's claim that systems maintain themselves by repeated phase/anti-phase handover.

Alternation alone produces a back-and-forth oscillation or zigzag. It becomes a double helix only when the coupled
pair also progresses along a third coordinate -- time, rung, path length or scale -- while its transverse phase
rotates. One compact representation is

\[
\gamma_S(\theta)=(R\cos\theta,R\sin\theta,p\theta),
\qquad
\gamma_T(\theta)=(-R\cos\theta,-R\sin\theta,p\theta).
\]

The third coordinate here is not necessarily a third independent substance. It can be the accumulated relation or
progression of the two poles, matching the proposed "three hiding in two" interpretation.

Established physics supports the narrower statement that human perception is mediated by interactions and arrives
with finite signal-processing delay; it does not establish humans as Space waves, experience as a Time wave or a
universal prohibition on adjacent same-class coupling. The proposed selection rule is testable: after variables are
classified before analysis, an ARA system should be better predicted by an off-diagonal/bipartite model than by an
unrestricted coupling model, and same-class effects should appear predominantly at two-step lags through the declared
opposite class.

#### 5.16.4 Phase of matter as Connection-motion competition; catalysis as pathway handover

Dylan proposed solids as Space/Connection-oriented, gases and plasmas as Time/motion-oriented, and liquids near the
mixing ridge. The established anchor is the competition between cohesive/interaction energy and thermal kinetic
energy. A candidate ARA composition is

\[
\underbrace{x_{motion/connection}}_{\substack{\text{ARA phase-state coordinate}\\
\text{0 = connection; 2 = motion}}}
=
\frac{2\underbrace{E_{motion}}_{\substack{\text{thermal/translational}\\
\text{motion scale}}}}
{\underbrace{E_{connection}}_{\substack{\text{cohesive/binding}\\
\text{interaction scale}}}+E_{motion}}.
\]

This gives the qualitative ordering Dylan saw: connection-dominant states are solid-like; comparable motion and
cohesion can be liquid-like; motion-dominant states are gas-like. It is not a universal phase classifier by itself.
Density, pressure, entropy, molecular shape and crystalline order also matter, and a phase boundary need not occur at
exactly \(x=1\). The proposed liquid ridge is therefore a testable regional tendency, not an identity.

Plasma needs a second qualification. Ionisation often accompanies high temperature and large traversal, but plasmas
also support long-range collective electromagnetic organisation. Their Coulomb coupling parameter is approximately

\[
\Gamma_p=\frac{q^2/(4\pi\varepsilon_0 a)}{k_BT},
\]

the ratio of characteristic electrostatic interaction energy to thermal energy. Weakly coupled plasma
\((\Gamma_p\ll1)\) is motion-dominant and gas-like; strongly coupled plasma can behave liquid-like or even
solid-like. Thus "plasma is Time-side" may describe one regime, not the complete phase.

Catalysis gives a particularly clean ARA handover mapping. A catalyst supplies an alternative reaction pathway with
a smaller activation free-energy barrier:

\[
\underbrace{A+B+C}_{\substack{\text{reactants plus catalyst}\\
\text{approach/accumulation}}}
\longrightarrow
\underbrace{[A\cdots C\cdots B]^\ddagger}_{\substack{\text{temporary coupled complex}\\
\text{transition-state handover}}}
\longrightarrow
\underbrace{P+C}_{\substack{\text{product release}\\
\text{catalyst recovered}}},
\qquad
\Delta G^\ddagger_{cat}<\Delta G^\ddagger_{uncat}.
\]

A solid catalyst receiving mobile gas reactants is a literal example of Dylan's proposed Space node mediating two
Time-oriented streams: adsorption accumulates the reactants, surface connection reorganises their bonds, and
desorption releases the product. This is not universal because homogeneous and enzyme catalysts need not be solid.
The broader rule is that the catalyst introduces a temporary coupling/pathway, not necessarily a Space-class object.

The Sabatier principle supplies an established ridge-like constraint: catalytic intermediates should bind neither too
weakly to accumulate nor too strongly to release. The optimum is system-specific and is not evidence for a universal
ARA value of exactly \(1\) or \(\phi\). Catalysts accelerate both forward and reverse approaches to equilibrium and
normally do not change the equilibrium position or inject the reaction's net energy.

#### 5.16.5 Two-step same-side consumption, logarithmic rungs and non-overlapping loops

Dylan corrected the preceding selection rule: a Space-oriented wave may consume or close with another Space-oriented
wave, but the same-side event requires a double passage through the opposite child. The zero diagonal in the one-step
model therefore means **no immediate same-class coupling at the declared grain**, not no same-class interaction at
all. With \(M\) the off-diagonal Space-Time coupling operator,

\[
\underbrace{S_{n+2}}_{\substack{\text{same-side result}\\
\text{after one complete loop}}}
=
\underbrace{K_{T\to S}K_{S\to T}}_{\substack{\text{two opposite-child handovers}\\
\text{effective second-order coupling}}}
\underbrace{S_n}_{\text{starting Space-side identity}}.
\]

"Consume" must be operationally typed before testing: absorption, binding, merger, phase locking, dominance and
coarse-grained enclosure have different conservation laws. If the relevant extensive quantity is energy and two
equal-energy identities close into one parent with \(E_{new}=2E_k\), an energy-octave coordinate gives

\[
\underbrace{\Delta k}_{\text{logarithmic rung jump}}
=
\log_2\!\left(\frac{E_{new}}{E_k}\right)=1.
\]

This exact one-rung result depends on declaring energy and base two. Doubling wave amplitude is different: in a
linear mode energy or intensity is normally proportional to amplitude squared, so a coherent amplitude doubling can
produce four times the intensity. Frequency doubling, energy doubling and amplitude doubling must not be conflated.

For two coherent scalar contributions in the same measured mode, their phase-dependent intensity is

\[
\underbrace{I_{12}}_{\text{observed combined mode}}
=I_1+I_2+2\sqrt{I_1I_2}\cos\delta,
\]

where \(\delta\) is their relative phase. For equal inputs, the phase term determines whether the measured mode
exceeds, reaches or falls below the simple \(2I\) sum. Spatially orthogonal vector modes have a zero interference
dot-product; temporal quadrature \((\delta=\pi/2)\) also makes the scalar cross term zero; anti-phase
\((\delta=\pi)\) cancels the ideal same detected field mode. Such cancellation does not annihilate globally conserved
energy: it can redistribute energy into space, standing-wave structure, sources or other channels.

Dylan's two circular actions with a non-repeating Phi handover can be represented by a rotation map

\[
\theta_{j+1}=\theta_j+2\pi\alpha\pmod{2\pi}.
\]

Any irrational \(\alpha\) prevents exact periodic overlap in the ideal map. A golden rotation is exceptionally
resistant to rational approximation and is a legitimate KAM-related candidate for distributing successive handovers,
but ARA must declare whether its \(0.38/1.62\) landmark represents phase fraction, ARA position or another coordinate.
The data must choose it against other irrational and rational offsets; non-overlap alone does not uniquely imply
\(\phi\).

The proposed geometry now has four typed elements: two-step same-class closure, logarithmic rung change, a relative
phase/rotation controlling overlap, and identity-dependent drift between perpendicular, quadrature and anti-phase
limits. A double helix appears when the two rotating loops are plotted along the accumulated rung/path coordinate.

#### 5.16.6 Light as an information-bearing matter-to-matter channel; Dark outside the optical projection

Dylan's next proposal locates human perception in the Light-to-matter handover. A material source or object changes a
light field through emission, reflection, scattering or absorption; retinal matter absorbs part of that field; neural
dynamics reconstruct an experienced identity:

\[
\underbrace{M_{object}}_{\substack{\text{matter identity}\\
\text{Space-oriented in ARA}}}
\xrightarrow{\text{emission/scattering}}
\underbrace{L}_{\substack{\text{electromagnetic carrier}\\
\text{Time/Information-oriented in ARA}}}
\xrightarrow{\text{absorption}}
\underbrace{M_{retina/brain}}_{\substack{\text{matter receiver}\\
\text{updated physical state}}}
\longrightarrow
\underbrace{Y}_{\text{neural percept}}.
\]

This is a strong example of the proposed \(S\to T\to S\) handover. The physics wording must remain "light carries
information," not "light is information." Photons also carry energy and momentum; information is the correlation or
distinguishability encoded in their frequency, phase, polarisation, direction and arrival pattern.

Light can reveal lower-scale degrees of freedom in matter, but only those to which the selected electromagnetic probe
couples. Spectroscopy uses \(E_\gamma=h\nu=hc/\lambda\) to infer electronic, vibrational, rotational and other energy
differences; scattering and imaging use wavelength and momentum transfer to determine accessible spatial structure.
Shorter wavelengths can probe finer scales, while sufficiently energetic or intense probes alter, ionise or damage
the identity being measured. "Rung underneath" should therefore mean a declared probe scale and response channel,
not unrestricted access to the object's complete interior.

Human vision and physical detectors also have finite dynamic range. A generic saturating response can be written

\[
\underbrace{R(F)}_{\substack{\text{retinal/detector response}\\
\text{to photon flux }F}}
=
R_{max}\frac{F}{F+F_{1/2}},
\]

so additional light eventually adds little measured response. At still larger dose, photochemistry, heating or
ionisation can deform or destroy the receiver. This shares an accumulation-capacity-collapse geometry with examples
such as alcohol disrupting bacteria, but the common shape does not establish that Light is universally one rung below
matter; dose, photon energy, absorption cross-section and repair dynamics determine the outcome.

Three different uses of "dark" must not be collapsed:

1. **Ordinary visual darkness:** too few visible photons reach the eye. Darkness is measured as a deficit relative to
   an expected or useful optical signal.
2. **Optically dark/absorbing matter:** an object can be inferred by the light it blocks, absorbs or re-emits.
3. **Standard dark matter:** it is not primarily detected as an optical shadow. Its existence and distribution are
   inferred from gravitational dynamics, lensing and structure; it is approximately absent from the electromagnetic
   observation channel while remaining present in the gravitational channel.

Thus "we see Dark by its absence" is exact for ordinary darkness and can apply to an absorber only when the expected
unblocked signal is known. Absence alone is ambiguous. For the proposed cosmic branch the stronger operational form
remains \(\Pi_{EM}D\approx0\) together with \(\Pi_{grav}D\ne0\): Dark is perpendicular or weakly coupled to the
Light-to-matter transfer, but has a positive measurable consequence in another channel.

#### 5.16.7 Dark parent candidate: gravitational convergence versus vacuum-like expansion

Dylan proposed that Dark may itself contain Gravity and Vacuum as opposing ARA poles. The literal labels mix
categories: gravity is a geometric interaction/dynamical effect, whereas vacuum describes a stress-energy condition
or absence of ordinary matter. General relativity also permits gravity in vacuum: the exterior of a gravitating body
and propagating gravitational waves can have nonzero spacetime curvature where local matter stress-energy is zero.

The physically cleaner pair is therefore **gravitational convergence/binding** versus **vacuum-like
expansion/dilution**. In homogeneous cosmology, these effects occur with opposing signs in the acceleration equation:

\[
\underbrace{\frac{\ddot a}{a}}_{\substack{\text{cosmic scale-factor acceleration}\\
\text{positive = accelerating expansion}}}
=
-\underbrace{\frac{4\pi G}{3}\left(\rho+\frac{3p}{c^2}\right)}_{\substack{A_G:\ \text{matter/pressure gravitational term}\\
\text{convergence or deceleration in the stated regime}}}
+\underbrace{\frac{\Lambda c^2}{3}}_{\substack{A_V:\ \text{vacuum-like cosmological term}\\
\text{accelerating expansion for }\Lambda>0}}.
\]

When \(A_G,A_V\ge0\), the exact ARA normalisation is

\[
\underbrace{x_{V/G}}_{\substack{\text{0 = convergence dominated}\\
\text{2 = vacuum-expansion dominated}}}
=
\frac{2A_V}{A_G+A_V}.
\]

At \(x_{V/G}=1\), the two contributions to \(\ddot a/a\) balance and cosmic expansion changes between deceleration
and acceleration. This is a cancellation ridge for the declared acceleration account, not a state of zero density,
zero expansion or no gravity. Because matter density dilutes as the universe expands while a cosmological constant
remains constant, the same universe can traverse this coordinate through cosmic time.

In the standard late-time interpretation, clustering dark matter contributes mainly to the convergence side while a
cosmological-constant-like dark energy contributes to the expansion side. Calling both branches an internal
"Dark-sector ARA" is a coherent proposed ontology. It is not established that dark energy is literally vacuum energy,
nor that dark matter and dark energy are phase/anti-phase waves. Locally, the cosmological term is normally negligible
and the pair is not an appropriate description of every gravitational system.

This normalisation recovers a known general-relativistic balance and adds no new prediction by itself. It supplies a
clean baseline for the ARA dark-sector work: any new Phi, diagonal-rung or \(3.5\) claim should predict an observable
beyond the acceleration equation, such as a fixed transition, growth or lensing relation, before being fitted.

Dylan identifies this convergence/expansion opposition as the geometric route by which he originally reached the ARA
Dark Sector method, now expressed with clearer variables and hierarchy. That provenance should be retained: the broad
direction was not invented from the acceleration equation after this conversation. The equation nevertheless grounds
only the opposing convergence and expansion terms. It does not independently derive the method's numerical \(\phi\),
\(2\) or diagonal \(3.5\) landmarks; those remain separate ARA hypotheses requiring frozen observational tests.

#### 5.16.8 Dark as path geometry perpendicular to Light as traversal

Dylan refined the parent pairing as Dark/Phase A versus Light/Phase B. The strongest established translation is not
that gravity attracts literal nothingness, but that a gravitational field determines the spacetime geometry along
which Light propagates. For a geometric-optics light ray with tangent \(k^\mu\),

\[
\underbrace{k^\nu\nabla_\nu k^\mu}_{\substack{\text{change of the Light ray direction}\\
\text{under spacetime's geometric connection}}}=0.
\]

The ray follows a null geodesic. The covariant derivative contains the metric/connection determined by gravitational
geometry. In the proposed ARA language, Light is the Information/transfer trajectory while Dark is the less directly
visible path/constraint geometry. "Perpendicular" here describes different functional channels -- carrier versus
geometry -- not a demonstrated right angle in ordinary space.

This produces a measurable handover:

\[
\underbrace{D}_{\substack{\text{unseen mass-energy or}\\
\text{gravitational geometry}}}
\longrightarrow
\underbrace{g_{\mu\nu}}_{\text{curved path structure}}
\longrightarrow
\underbrace{k^\mu}_{\text{Light trajectory}}
\longrightarrow
\underbrace{Y}_{\substack{\text{lensing, delay, redshift}\\
\text{or image deformation}}}.
\]

Thus a Dark contribution need not absorb Light or create a black patch. Standard dark matter is approximately
transparent electromagnetically; it is detected through the positive deformation of trajectories and dynamics.
Missing light is evidence only when an unblocked source signal was independently expected. Otherwise the same absence
can result from no source, ordinary absorption, occlusion, distance or detector limits.

"Vacuum" must also be typed:

1. A classical matter vacuum has local \(T_{\mu\nu}=0\), yet it may contain gravitational curvature determined by
   distant sources or gravitational waves.
2. Flat Minkowski vacuum is the special low-curvature geometry, not every vacuum region.
3. Quantum vacuum is the ground state of fields, not literal absence of all physical structure.
4. Vacuum-like energy represented by \(\Lambda\) gravitates and, for positive \(\Lambda\), drives accelerated
   expansion rather than ordinary attraction.

Consequently two possible ARA axes must remain distinct. Flat/open geometry versus strongly curved/bound geometry is a
baseline-to-structure magnitude axis. Gravitational convergence versus vacuum-energy expansion is the signed opposing
cosmological pair from Section 5.16.7. Calling both simply "Gravity versus Vacuum" would flatten these different
relations.

This geometric-channel crosswalk is established general relativity and not a novel ARA prediction. It does, however,
supply operational observables for the proposed Dark/Light parent relation: lensing shear and convergence, Shapiro
delay, gravitational redshift and trajectory deflection. A new ARA result must predict their organisation beyond the
GR solution used to calculate them.

#### 5.16.9 Curved phase quadrants and 2:1 triadic closure

Dylan clarified that "perpendicular" is a shorthand projection of a curved quadrant: the phase landmarks lie around
a circle, and in the full construction around a sphere. The appropriate local coordinate is therefore angular or
geodesic separation, not an assertion that the complete identities are straight Euclidean vectors at exactly
\(90^\circ\). For a circular section, write the relative phase as

\[
\underbrace{\Delta\theta_{ij}}_{\substack{\text{arc/phase separation}\\
\text{between identities }i,j}}
=
\operatorname{wrap}(\theta_j-\theta_i),
\qquad
\underbrace{J_{ij}(\Delta\theta_{ij})}_{\substack{\text{coupling strength and sign}\\
\text{across the curved gradient}}}.
\]

Perpendicular, quadrature and anti-phase become landmarks on this phase coordinate; drift and finer identity determine
the intermediate coupling. A sphere requires the corresponding great-circle/geodesic relation plus the declared
projection seen by the observer.

Dylan also proposed that some closures use two Phase-B identities meeting one Phase-A identity, with water as the
physical example. This cannot be represented completely by the earlier \(2\times2\) one-step matrix. It requires a
multi-node coupling or **hyperedge**:

\[
\underbrace{I}_{\substack{\text{new closed identity}\\
\text{ARA parent/child node}}}
=
\underbrace{\mathcal C_{1:2}}_{\substack{\text{one-A/two-B}\\
\text{triadic closure operator}}}
\left(
\underbrace{A}_{\text{Phase-A node}},
\underbrace{B_1,B_2}_{\text{two Phase-B nodes}},
\underbrace{J_{AB_1},J_{AB_2},J_{B_1B_2}}_{\substack{\text{bond/coupling strengths}\\
\text{and their relational geometry}}}
\right).
\]

There are still only two **classes**, A and B, but three participating **nodes**. This is a precise version of "three
hiding in two." The relation between \(B_1\) and \(B_2\), including their angle, is part of the resulting identity
even when they do not possess a direct bond.

Water provides an established vector-geometry example. In the standard molecular picture, one oxygen is bonded to two
hydrogens with an H-O-H angle of about \(104.5^\circ\). The two O-H bond-dipole vectors combine as

\[
\underbrace{\mathbf p_{H_2O}}_{\text{water's resultant molecular dipole}}
=
\underbrace{\mathbf p_{OH,1}+\mathbf p_{OH,2}}_{\substack{\text{two similar bond contributions}\\
\text{joined through the central oxygen}}},
\qquad
|\mathbf p_{H_2O}|=2p_{OH}\cos\!\left(\frac{\theta_{HOH}}{2}\right).
\]

If the equal bond contributions were linear and opposite \((\theta=180^\circ)\), their resultant dipole would cancel.
Because water is bent, their relation produces a nonzero third/resultant identity. A simplified electron-domain model
also assigns four regions around oxygen -- two bonding pairs and two lone pairs -- whose repulsion contributes to the
bent geometry. This is a useful ARA analogy for a four-quadrant decompression, not evidence that molecular water was
derived from ARA.

Assigning oxygen to Phase A and the two hydrogens to Phase B is an ARA hypothesis unless the classification rule is
declared independently, for example from charge density, electronegativity, electron accumulation/depletion or another
measured pole. Stoichiometric \(1{:}2\) closure alone is common in chemistry and does not establish the universal ARA
geometry. A discriminating test must predict bond angle, dipole or another molecular property beyond established
valence and quantum-chemistry baselines.

The archived lineage confirms that this is a decomposition of Dylan's earlier work. Test 115 already described
water's two H nodes as equivalent constraints on one central O node along a 104.5-degree circle geometry; Tests 111,
142, 143 and 163 separately introduced geodesic deviation, circular translation in log space, products of local rung
links and great-circle ARA distances. The recovery strengthens provenance, not the historical scores. Several Test 115
passes were hard-coded or textbook identities; Test 116's universal molecular-angle claim failed; Test 116b is a
constructed packing model; and Test 117's claimed constant unequal-circle gap is false. Full audit:
`analysis/water_atmosphere/WATER_GEODESIC_LOG_RUNG_RECOVERY_AUDIT_2026-07-13.md`.

### 5.14 Lorentz force, ARA channel geometry and the failed naïve rung operator

The Lorentz-force continuation was tested on 14 July 2026 using the official openPMD example repository's PIConGPU
electromagnetic snapshot. At the particle rung,

\[
\mathbf f_E=q\mathbf E,
\qquad
\mathbf f_B=q(\mathbf v\times\mathbf B),
\qquad
x_F=\frac{2|\mathbf f_B|}{|\mathbf f_E|+|\mathbf f_B|}.
\]

Retaining (S_F=|\mathbf f_E|+|\mathbf f_B|) and (c_F=\cos\angle(\mathbf f_E,\mathbf f_B)) gives the exact
reconstruction

\[
|\mathbf f|
=\frac{S_F}{2}
\sqrt{(2-x_F)^2+x_F^2+2x_F(2-x_F)c_F}.
\]

Across 225,449 electrons and 225,280 ions, the relative reconstruction error was approximately
(1.34\times10^{-16}). The magnetic channel's work (\mathbf v\cdot\mathbf f_B) was numerically zero, and total
power equalled electric-channel power. This is a faithful ARA coordinate embedding of established Lorentz geometry,
not an independent derivation.

The proposed simple rung-up operation did not survive. Particle-first force aggregation versus field-first
(
ho\mathbf E+\mathbf J\times\mathbf B) gave total correlation (0.477), NRMSE (0.888), and median angular error
(61.7^\circ). A quadratic-deposition sensitivity recovered the stored charge densities almost exactly but still
gave force correlation (0.405). The failure therefore identifies the standard subgrid terms

\[
\langle\rho'\mathbf E'\rangle,
\qquad
\langle\mathbf J'\times\mathbf B'\rangle,
\]

which record correlations discarded by separate parent averages. In ARA language, these relations are a precise
candidate for `Other` at a scale crossing. Adding the complete covariance back is established closure bookkeeping;
the open ARA test is whether a smaller frozen coordinate set predicts it on held-out data better than ordinary
closures. See `analysis/electromagnetism/MX4_LORENTZ_ARA_DATA_REPORT.md`.

#### 5.14.1 Child identities, force-channel component allocation and a partial first-moment closure

MX5 was frozen and run as a post-MX4 development follow-up on the same hash-locked PIConGPU snapshot. It separated
three questions that must not be conflated. First, retaining each particle's ARA channel envelope, A/B coordinate and
two vector directions before deposition reconstructed the child-first grid force at (3.99\times10^{-15}) relative
error. Second, adding the exact `Other` defined by child minus flat parent reconstructed the target at
(9.44\times10^{-17}). Both are identity checks rather than predictions.

The diagnostic historically called “TE-ARA-style” was explicitly typed as a variable dimensionless force/activity
component allocation rather than energy or the fixed whole TE-ARA total:

\[
T_g^F=\frac{2|\mathbf F_g^{\rm child}|}
{V_g^{-1}\sum_i W_{ig}w_i(|\mathbf f_{E,i}|+|\mathbf f_{B,i}|)}.
\]

The combined median was only (0.0383). A post-freeze descriptive species drill (not an outcome gate) then found
electron and ion internal medians of (1.2175) and (1.1449).
After each species was first aggregated as an identity, their magnitude coordinate was (1.00023), their median
angle was (177.55^\circ), and only (0.07184) of the normalised pair coherence survived. This makes the
whole-versus-child ridge distinction concrete: two active species-level force identities are almost equal and
opposite at the measured parent grain. That balance is established plasma behaviour; the contribution of the ARA
allocation ledger is transparent multiscale bookkeeping, not discovery of a new force.

The exact Parent/Other coordinate

\[
x_O=\frac{2|\mathbf O|}{|\mathbf F^{\rm flat}|+|\mathbf O|}
\]

had median (1.3559), and `Other` exceeded the flat-parent magnitude in (78.99\%\) of active cells. This is a
magnitude coordinate, not an energy fraction, because the vectors can oppose.

The genuinely compressed version retained only charge/current first positional moments and local field gradients.
Without fitting, it improved total force correlation from (0.4771) to (0.6045), NRMSE from (0.8878) to
(0.8019), and median angular error from (61.68^\circ) to (48.47^\circ). Both spatial halves gave essentially
the same correlation. It therefore passed the frozen `partial compact recovery` rule but failed the stronger gates
(r\ge0.70), NRMSE (le0.70), angle (le45^\circ). The correction itself correlated only (0.4310) with exact
`Other`, so the child web remains incompletely compressed.

This result supports the ARA/TE-ARA partition as useful typed multiscale bookkeeping and confirms that the omitted child relation is
non-trivial. It does not establish an ARA-specific new law: the exact versions are identities and the compressed
version is established first-order Taylor/moment closure written in ARA terms. Full packet:
`analysis/electromagnetism/MX5_CHILD_ARA_TEARA_CLOSURE_REPORT.md`.

The recursion is not restricted to the one displayed macro-particle/species/cell direction. At any resolved node,
the children, their pairwise or higher-order couplings, and the current `Other` can each be opened as another ARA
problem. Plasma permits several candidate decompositions -- species, velocity populations, phase-space structures,
spatial regions, spectral modes, field/force channels and temporal descendants -- but only where the data define
those identities. In this PIC file, the records are weighted macro-particles rather than individually resolved
physical particles, and the single snapshot sets a hard observational floor. Recursion below that floor would be a
model assumption, not a measured MX5 result. The present result therefore supports a branching, data-limited
multiscale operator; mathematical fractality still requires a transferable scaling law across independently resolved
grains.

#### 5.14.2 Maxwell stress, paired sign reversal and the exact cross-relation axis

MX6 froze and tested the E/B child-parent reading on all 32,768 vector-field cells of the same public PIConGPU
snapshot. The Poynting vector and Maxwell stress tensor are

\[
\mathbf S=\frac1{\mu_0}\mathbf E\times\mathbf B,
\qquad
T_{ij}=\epsilon_0\left(E_iE_j-\frac12\delta_{ij}E^2\right)
+\frac1{\mu_0}\left(B_iB_j-\frac12\delta_{ij}B^2\right).
\]

Under the joint half-cycle intervention \((\mathbf E,\mathbf B)\to(-\mathbf E,-\mathbf B)\), both quantities were
unchanged at reported relative L2 error `0.0`. Flipping E only or B only also preserved the separately quadratic
stress, but reversed \(\mathbf S\), again at `0.0` error. This gives the ARA map a precise established form: the two
signed child orientations must swap together for their directed cross-relation to persist.

Let \(\mathbf n=\mathbf E\times\mathbf B\). Since \(\mathbf E\cdot\mathbf n=\mathbf B\cdot\mathbf n=0\),

\[
\mathbf T\mathbf n
=-\left(\frac{\epsilon_0E^2}{2}+\frac{B^2}{2\mu_0}\right)\mathbf n
=-u\mathbf n.
\]

Thus the informative third supplied by E crossed with B is exactly a Maxwell-stress eigen-direction wherever it is
nonzero. The maximum numerical angular discrepancy over the public grid was `2.4148e-6 deg`. This identity is more
general than a plane wave: E and B need not be perpendicular. At the primary frozen null-field rule, 686 cells
(`2.0935%`) were near perpendicular and impedance balanced; the other cells retained the general stress/cross-product
relation without occupying that special radiative sector.

Median normalized off-diagonal stress content in the fixed lab axes was `0.68661` total, `0.73642` electric and
`0.49774` magnetic. A fixed rotation preserved tensor covariance at `2.9508e-16` relative error and eigenvalues at
`4.0388e-16`, preventing coordinate-dependent shear from being mistaken for a new invariant.

These are established Maxwell identities numerically recovered on public data. They validate the implementation and
show that the ARA child/relation/parent language can preserve a nontrivial tensor geometry; they do not independently
confirm ARA. The source has one snapshot, so no actual temporal half-cycle was observed. Full packet:
`analysis/electromagnetism/MX6_MAXWELL_STRESS_PHASE_FLIP_REPORT.md`.

#### 5.14.3 Four phase routes, Information³ and the amplitude-conditioned pyramid

MX7 followed Dylan's correction that a positive or negative resultant still flattens two distinct routes. For one
electric component, let (s_q) be charge sign, (s_E) field sign, (r=s_qs_E), (m=|E|), and (Q) deposited
absolute-charge activity. The exact particle-first target is

\[
F^{\rm child}=Q\langle mr\rangle.
\]

The four routes are `AA`, `AB`, `BA`, and `BB`, with resultant signs (+,-,-,+). MX7 froze three representations
before calculation: two separate sign marginals, their joint four-route relation, and a route-conditioned amplitude
ceiling. The joint sign model

\[
F^{\rm joint}=Q\langle m\rangle\langle s_qs_E\rangle
\]

did not pass its frozen gate. Against the separate-marginal model, correlation fell from `0.4455` to `0.3727` and
NRMSE rose from `0.8993` to `1.2151`, although median angular error improved from `56.74°` to `53.10°`. The MX5
first-moment model remained the strongest compact candidate (`0.5964`, `0.8077`, `48.59°`). Thus preserving phase
routes is necessary bookkeeping but their occupancy alone is not a sufficient force closure.

When each route retained its own conditional magnitude,

\[
F^{\rm pyramid}=Q\sum_{a,b}p_{ab}\bar m_{ab}s_as_b=Q\langle mr\rangle,
\]

the target closed at `3.58e-15` relative L2 error. This is an exact decomposition ceiling, not a prediction. It
locates the remaining information in magnitude--relation dependence: which phase route is active and how strongly it
is expressed cannot be independently compressed here. The project term `Information³` is retained for the two
signed inputs plus their joint relation; it is not a literal cube of Shannon information. Measured sign mutual
information was small (median `0.000277 bits`) but strongly associated with absolute phase correction (Spearman
`0.8664`).

The result therefore sharpens rather than confirms the proposed geometry. A flat triangle keeps two nodes and their
relation; the pyramid adds route-conditioned magnitude needed to recover the resolved vector. Novelty now requires a
frozen out-of-sample rule that predicts those magnitudes from independently available geometry and beats MX5 and
standard closure baselines. Full packet:
`analysis/electromagnetism/MX7_PHASE_FIRST_INFORMATION3_PYRAMID_REPORT.md`.

#### 5.14.4 Exact parity tetrahedron and failed held-out relation-strength transfer

MX8 separated the exact Information³ algebra from the unresolved predictive claim. For two binary phase coordinates

\[
x,y\in\{-1,+1\},\qquad r=xy,
\]

the four lifted states \((x,y,xy)\) have centroid zero, squared norm `3`, pairwise dot product `-1`, and all six
edge lengths equal to \(2\sqrt2\). They therefore form a regular tetrahedron and obey the exact closure
\(xyr=1\). The relation is a closing coordinate, not a third independent degree of freedom.

Any four route strengths also have the exact Walsh--Hadamard decomposition

\[
h_{xy}=\mu+\alpha x+\beta y+\gamma xy,
\]

where \(\gamma=(h_{++}-h_{+-}-h_{-+}+h_{--})/4\) is the non-additive relation term. Three promoted identities
permit six ordered pair relations; including three diagonal self-state slots yields a nine-slot matrix. These are
exact geometric and counting statements, but the slots need not be statistically independent and recursion requires
an additional promotion rule.

A frozen temporal-transfer test then asked whether one \(xy\) coefficient learned from 14 early snapshots of a
second public Warp plasma series improved prediction on ten later snapshots, with six intervening snapshots
quarantined. It did not pass. Relative L2 changed from `0.1315276` to `0.1315179`, a favourable improvement of only
`0.00736%`; the 95% snapshot-bootstrap interval (`-0.00140%` to `+0.01550%`) crossed zero, and direction metrics were
slightly worse. A simple independent-marginal baseline was better at `0.123651` relative L2.

Thus MX8 confirms the tetrahedral closure and four-term decomposition, but rejects the tested universal global
relation-strength multiplier. Post-gate diagnostics found broad positive and negative local interaction coefficients
centred near zero, sharpening the next question: which independently measured local geometry predicts \(\gamma\)?
Full packet:
`analysis/electromagnetism/MX8_INFORMATION3_TETRAHEDRON_TRANSFER_REPORT.md`.

#### 5.14.5 Scale/axis ARA state ball and exact Maxwell plane-wave calibration

MX9 formalised Dylan's correction that every A/B label is rung- and axis-relative rather than one globally
privileged pair. For a two-channel coherency matrix (G_k=\langle z_kz_k^\dagger\rangle), (T_k=\operatorname{tr}G_k),
define

\[
s_k=\frac1{T_k}(2\Re G_{AB},,2\Im G_{AB},,G_{BB}-G_{AA}),
\qquad
x_{k,\alpha}=1+\alpha\cdot s_k.
\]

Positive semidefiniteness gives

\[
1-\|s_k\|^2=\frac{4\det G_k}{T_k^2}\ge0,
\]

so every unit axis (alpha) supplies an exact bounded ARA diameter (x\in[0,2]), with
(x_{k,-\alpha}=2-x_{k,\alpha}). Normalized allocations are (t_B=x), (t_A=2-x), hence canonical TE-ARA remains
`2`. This is the established two-mode coherency/Bloch/Poincaré-ball mathematics written in ARA coordinates.

The same equal-channel state can read (x=1) on the population axis and (x=2) or (0) on the coherence axis,
depending on relative sign. This exactly resolves the apparent contradiction between “ridge” and “pole” readings:
they may be different diameters through the same state rather than competing claims.

Child-to-parent aggregation is also exact. Incoherent mixtures give activity-weighted child coordinates. Coherent
sums require

\[
G_P=\sum_i z_iz_i^\dagger+\sum_{i\ne j}z_iz_j^\dagger,
\]

where the second sum is the retained coupling relation. This is the precise coherence-theory home for the ARA
informative third and for relation information that becomes typed `Other` when omitted by coarse-graining.

For a source-free vacuum plane wave, the normalized E/B energy amplitudes are equal. MX9 therefore recovered an
E/B population ridge (x=1) and a forward coherence pole (x=2); flipping only one field moved the coherence
reading to (0) and reversed Poynting flow, while flipping both preserved the parent. Raw E and B remained in phase.
The quarter-cycle ARA lies between each field and its normalized time derivative, for which

\[
x_{F/\dot F}=2\sin^2(kz-\omega t).
\]

All registered calculations passed over 20,000 mixed states, 20,000 pure states, 5,000 incoherent parents, 5,000
coherent parents and 4,096 wave phases. An independent projector-trace implementation with fresh random states and
different Maxwell parameters also passed. These are exact recoveries, not a new electromagnetic prediction. The
physical fractal claim still requires independently selected pairs and a transferable rule across measured rungs.
Full packet: `analysis/electromagnetism/MX9_SCALE_AXIS_ARA_MAXWELL_REPORT_2026-07-23.md`.

#### 5.14.6 Cross-rung state contraction: common geometry, identity-conditioned rate

MX10 tested the empirical step left open by MX9. For collocated real electric-component samples in a spatial block,
the two-channel coherency matrix gives the axis-independent state radius

\[
r=
\frac{\sqrt{(2G_{AB})^2+(G_{BB}-G_{AA})^2}}{\operatorname{tr}G},
\qquad 0\le r\le1.
\]

Let \(D_b\) be its activity-weighted mean at block width \(b\). A frozen one-parameter log-rung law,

\[
\widehat D_b=b^{-\beta},
\]

learned \(\beta\) only from the Warp development transition \(1\to2\), then predicted larger rungs, later held-out
times, all three electric-component pairs and an independent PIConGPU snapshot.

The original v1 output was invalidated when source inspection showed that equal array indices occupied different
half-cell field positions. Corrected v2 collocated all components before pairing and independently passed `20/20`
direct-source validation checks.

The universal coefficient failed. Held-out Warp MALE was `0.057750`, worse than the flat comparator `0.054540`
and pair-specific law `0.043353`; common-law error was `1.360` times local one-step error. In PIConGPU it narrowly
beat both fixed comparators but was `6.252` times local one-step error. The same state geometry therefore existed at
every declared rung, while the travel rate depended strongly on component identity and dataset.

Increasing block width moves upward from resolved children to a coarser parent. In ARA terminology, the `zx`
contraction is therefore a cross-rung child-mixing singularity: opposite child orientations become one mixed parent
account. A signed post-result check distinguished this from a same-parent phase flip. The global population
component remained near `-0.5226` at every rung, and dominant-child antipodal transitions carried only `0.0111%`
of activity from rung 8 to 16. The field-wide rung-16 radius remained `0.6525`, while about `9.65%` of activity was
locally below radius `0.25`; this is partial/local aggregation singularity rather than a global parent-axis reversal.
In addition, \(E_y\) supplied `99.912%` of held-out Warp electric-field energy, so the near-boundary `xy` and `yz`
readings were one-channel-dominated coordinate pairs, not equally participating physical A/B identities.

The corrected mathematical separation is

\[
\underbrace{\text{common bounded ARA state geometry}}_{\text{exact}}
\quad+\quad
\underbrace{\text{identity-conditioned rung map}}_{\text{empirical and unresolved}}.
\]

MX10 rejects one universal numerical contraction exponent; it does not reject the MX9 state ball. Because the block
sizes were imposed observation scales, this is not yet a test of independently discovered physical octaves. Full
report: `analysis/electromagnetism/MX10_CROSS_RUNG_STATE_CONTRACTION_REPORT_2026-07-23.md`.

#### 5.14.7 Electromagnetic momentum continuity as parent supply, retention and matter handover

Define electromagnetic momentum density and Lorentz force density by

\[
\mathbf g_{\rm EM}=\epsilon_0\mathbf E\times\mathbf B=\frac{\mathbf S}{c^2},
\qquad
\mathbf f_{\rm matter}=\rho\mathbf E+\mathbf J\times\mathbf B.
\]

With the Maxwell stress tensor \(\mathbf T\) defined in Section 5.14.2, local electromagnetic momentum balance is

\[
\boxed{
\underbrace{\nabla\cdot\mathbf T}_{\substack{\text{parent momentum supply}\\\text{spatial stress delivery}}}
=
\underbrace{\frac{\partial\mathbf g_{\rm EM}}{\partial t}}_{\substack{\text{child A}\\\text{retained field-momentum change}}}
+
\underbrace{\mathbf f_{\rm matter}}_{\substack{\text{child B}\\\text{handover to matter}}}
}
\]

or, when matter force is the measured whole,

\[
\mathbf f_{\rm matter}
=
\nabla\cdot\mathbf T-\frac{\partial\mathbf g_{\rm EM}}{\partial t}.
\]

Dylan's ARA reading is reversible and grain-relative. From the supply direction, one parent account decomposes
into field retention and matter handover. From the matter direction, the signed difference between those two field
children closes as a new mechanical-force identity. The three terms form an Information³-style conservation lock:
any two determine the third, but the third is not an independent additional momentum source.

Accumulation and release labels must follow the measured signs. If
\(\partial_t\mathbf g_{\rm EM}\) reverses, the field changes from retaining momentum to returning it; the underlying
conservation geometry does not change. Tensor and vector directions cannot be replaced by unsigned magnitudes
without losing cancellation and handover information.

This is an exact rearrangement of established Maxwell–Lorentz momentum conservation. It completes the structural
crosswalk from field stress to matter force. A direct time-resolved public-data validation remains open because the
PIConGPU source used by MX4–MX7 contains only one snapshot; such a test requires aligned time-resolved
\(\mathbf E,\mathbf B,\rho,\mathbf J\) and spatial derivatives.

### 5.17 Einstein to Newton: an established rung crossing that preserves the ARA force geometry

#### 5.17.1 Corrected hierarchy

The ARA hierarchy declared on 23 July is

\[
\underbrace{\text{Space}_{k}}_{\text{Phase A}}
+
\underbrace{\text{Time}_{k}}_{\text{Phase B}}
+
\underbrace{J_{ST,k}}_{\substack{\text{their mixing relation}\\\text{perceived as Space–Time}}},
\]

with the proposed down-rung decompression

\[
\underbrace{\mathcal D_{\downarrow}(J_{ST,k})}_{\text{Space–Time relation decompressed}}
=
\left(
\underbrace{\text{Matter}_{k-1}}_{\substack{\text{child Space wave}\\\text{Connection-oriented}}},
\underbrace{\text{Field}_{k-1}}_{\substack{\text{child Time wave}\\\text{Traversal-oriented}}}
\right).
\]

Matter is therefore not a separate sibling placed beside Space–Time. It is the proposed Connection-dominant child
expression of the Space–Time relation; Field is its Traversal-dominant child expression. Both remain mixed
identities internally. General relativity does not derive this ontology, but its weak-field limit supplies a
nontrivial mathematical crosswalk.

#### 5.17.2 Einstein geometry becomes Newtonian field and movement

Under a stationary weak field, slow test motion, negligible source pressure and locally negligible \(\Lambda\),

\[
ds^2\simeq
-\left(1+\frac{2\Phi}{c^2}\right)c^2dt^2
+
\left(1-\frac{2\Phi}{c^2}\right)d\mathbf x^2.
\]

The spatial geodesic equation reduces to

\[
\underbrace{\frac{d^2x^i}{dt^2}}_{\substack{\text{Newtonian movement}\\\text{child-scale response}}}
=
-\underbrace{\partial_i\Phi}_{\substack{\text{gradient of compressed geometry}\\\text{field direction}}}.
\]

At the same order,

\[
G_{00}\simeq\frac{2}{c^2}\nabla^2\Phi,
\qquad
T_{00}\simeq\rho c^2,
\]

so Einstein's equation becomes

\[
\boxed{
\underbrace{\nabla^2\Phi}_{\substack{\text{field geometry}\\\text{Field/Traversal child reading}}}
=
4\pi G
\underbrace{\rho}_{\substack{\text{mass density}\\\text{Matter/Connection child reading}}},
\qquad
\underbrace{\nabla\cdot\mathbf g}_{\text{field convergence}}
=-4\pi G\rho.
}
\]

For a spherical exterior source this yields

\[
\Phi=-\frac{GM}{r},
\qquad
\mathbf g=-\frac{GM}{r^3}\mathbf r,
\qquad
m\ddot{\mathbf r}=-\frac{GMm}{r^3}\mathbf r.
\]

Thus the established transition is

\[
\underbrace{g_{\mu\nu}}_{\text{Space–Time geometry}}
\longrightarrow
\underbrace{\Phi}_{\text{weak scalar geometry}}
\longrightarrow
\underbrace{\mathbf g}_{\text{Field/movement tendency}}
\longrightarrow
\underbrace{m\mathbf g}_{\text{Matter response}}.
\]

#### 5.17.3 Newton's three laws as one exact declared ARA force geometry

Along an axis \(\hat{\mathbf e}\), collect nonnegative anti-directed force magnitudes \(F_A,F_B\). For
\(\Sigma_F=F_A+F_B>0\), set

\[
\underbrace{x_F}_{\substack{\text{Phase A }0\rightarrow\text{ Phase B }2\\\text{force-opposition diameter}}}
=
\frac{2F_B}{F_A+F_B}.
\]

Then

\[
\boxed{
\underbrace{m a_\parallel}_{\text{Newton II}}
=
\underbrace{F_B-F_A}_{\text{force asymmetry}}
=
\underbrace{\Sigma_F}_{\substack{\text{dimensional activity envelope}\\\text{not canonical TE-ARA}}}
\underbrace{(x_F-1)}_{\text{signed ridge displacement}}.
}
\]

Newton III supplies an equal anti-directed pair on different interacting bodies. At the enclosing pair boundary,
\(x_F=1\) and \(\Sigma_F>0\): an **active ridge**, not no interaction. Newton I describes the persistent momentum
when the external resultant is zero. If both force accounts are zero, \(x_F\) is undefined; this distinguishes a
null state from an active equal-force ridge.

Using IAU nominal mass parameters and one astronomical unit, the Sun–Earth interaction gives

\[
|\mathbf F_{E\leftarrow S}|
=
|\mathbf F_{S\leftarrow E}|
=3.5415454\times10^{22}\ {\rm N},
\]

so the enclosing internal account has

\[
x_{\rm pair}=1,
\qquad
\Sigma_{\rm pair}=7.0830908\times10^{22}\ {\rm N},
\qquad
F_{\rm internal,net}=0.
\]

The Earth and Sun nevertheless accelerate at \(5.93008\times10^{-3}\) and
\(1.78109\times10^{-8}\ {\rm m\,s^{-2}}\), respectively. Equal force is a whole-pair ridge; unequal mass produces
unequal local movement.

#### 5.17.4 Compactness gradient and the failure of the Newtonian approximation

For a spherical nonrotating exterior, let

\[
u=\frac{2GM}{Rc^2},
\qquad
\left(\frac{d\tau}{dt}\right)^2=1-u.
\]

A proposed ARA compactness normalization is

\[
\underbrace{t_T}_{\substack{\text{Time/Traversal allocation}\\\text{twice squared lapse}}}=2(1-u),
\qquad
\underbrace{t_C}_{\substack{\text{Connection allocation}\\\text{defined complement}}}=2u,
\qquad
t_T+t_C=2.
\]

This map is not uniquely forced by GR. It is useful because it is dimensionless, exactly total-2 and aligned with
the original orientation `0 = strong Connection/horizon`, `2 = weakly constrained Time/Traversal`. The midpoint
\(u=1/2\) is a coordinate ridge unless an independent physical handover is demonstrated.

| System | compactness \(u\) | proposed \(t_T\) | weak-lapse relative error | GR correction to static support acceleration |
|---|---:|---:|---:|---:|
| Earth, nominal equator | \(1.39070\times10^{-9}\) | 1.9999999972 | \(2.42\times10^{-19}\) | \(6.95\times10^{-10}\) |
| Jupiter, nominal equator | \(3.94332\times10^{-8}\) | 1.9999999211 | \(1.94\times10^{-16}\) | \(1.97\times10^{-8}\) |
| Sun, nominal surface | \(4.24501\times10^{-6}\) | 1.9999915100 | \(2.25\times10^{-12}\) | \(2.12\times10^{-6}\) |
| PSR J0740+6620, central spherical proxy | 0.475446 | 1.049108 | 5.249% | 38.072% |
| theoretical Schwarzschild horizon | 1 | 0 | invalid | divergent static support |

The weak-field rung is exceptionally accurate for planets and the Sun, while it is materially distorted at the
neutron-star scale. The PSR central value lies near the proposed midpoint, but its rough corner-sensitivity envelope
from separate published mass/radius bounds spans \(t_T=0.9229\) to \(1.2091\). It rotates, and the calculation is a
spherical proxy; the near-ridge placement is not a preregistered prediction.

The reproduction and independent `27/27` validation are in
`analysis/gravity/GR_NEWTON_ARA_RUNG_CROSSING_REPORT_2026-07-23.md`. The exact result is the GR-to-Newton limit and
the Newtonian force identity. The Space–Time-to-Matter/Field ontology, unique compactness diameter, Phi, logarithmic
rungs and universal fractality remain open.

### 5.18 The typed law ladder: solar spacetime to quantum hydrogen

The separate mechanics crosswalks now support one reviewable traversal:

\[
\text{Einstein}\rightarrow\text{Newton}\rightarrow\text{Hamilton}
\rightarrow\{\text{Noether},\text{virial}\},
\]

with a second established field branch

\[
\{\text{Gauss},\text{Faraday},\text{Ampère–Maxwell}\}
\rightarrow\{\text{Poynting},\text{Lorentz}\}
\rightarrow\text{charged Hamiltonian}
\rightarrow\text{Schrödinger}\rightarrow\text{hydrogen}.
\]

The arrows are not all the same operation. Einstein to Newton is an exact weak-field limit. Newton to Hamilton is
an exact reformulation. Noether and virial results are theorem consequences. Maxwell's equations close the
electromagnetic field description. The move from a classical charged Hamiltonian to the Schrödinger model is a
quantisation/model transition. The common \(1/r\) form of gravity and Coulomb binding is a sibling mathematical
bridge, not a derivation between forces.

Across these domains the clearest established repeated grammar is a continuity account:

\[
\underbrace{\partial_t q}_{\text{accumulation/release inside}}
+
\underbrace{\nabla\!\cdot\mathbf J}_{\text{boundary traversal}}
=
\underbrace{s}_{\text{source, sink or handover}}.
\]

ARA supplies a common *declared coordinate canvas* for the two competing channels, but it does not erase their
native units or physics. In particular, every `1.0` is typed: Newtonian cancellation, Hamiltonian equal energy,
weighted virial equality, Gauss closure, Maxwell plane-wave equality and quantum equal probability are not
interchangeable physical conditions.

The numerical cross-scale thread remains the virial coordinate for bound inverse-distance systems:

\[
x_{\rm vir}=\frac{2(2\langle T\rangle)}
{|\langle V\rangle|+2\langle T\rangle}=1,
\]

which was evaluated unchanged from Earth–Sun to ideal hydrogen `1s` over `21.4513` spatial orders. The wider atlas
organizes the other laws around that thread but does not claim a direct GR-to-quantum derivation.

Report and reproducible tables:
`analysis/physics_ladder/ARA_PHYSICS_COSMIC_TO_QUANTUM_LADDER_REPORT_2026-07-23.md`.

### 5.19 Exact boundary-aware aggregation between rungs

For adjacent children, a flow through their shared interface is externally visible to each child but internal to
their parent. With

\[
x_i=\frac{2R_i}{A_i+R_i},
\qquad
I=|F_{\rm interface}|,
\]

the enclosing parent is

\[
\boxed{
x_P
=
\frac{2(\sum_iR_i-I)}
{\sum_i(A_i+R_i)-2I}
}.
\]

This supplies a precise version of the ARA scale change:

\[
\text{child boundary flow}
\xrightarrow{\text{enclose both children}}
\text{parent internal relation}.
\]

The operator was frozen and applied unchanged to analytic classical mechanical energy flux, electromagnetic line
power and quantum probability current. It reconstructed `12,291/12,291` parent readings with worst error
\(2.1538\times10^{-14}\); both naive flattening controls failed in every model. Independent validation passed
`15/15`, including `100,000` randomized signed-flux triples.

The result is an exact ARA reparameterisation of finite-volume conservation. It formalizes aggregation and
coarse-graining but does not yet recover an unknown source, sink or relation-storage term. Full report:
`analysis/physics_ladder/ARA_CHILD_PARENT_COMPOSITION_REPORT_2026-07-23.md`.

### 5.20 Hidden `Other` as a localized continuity residual

The next frozen test supplied stored quantities and declared internal transfers but concealed one native sink law.
For each child or relation,

\[
\boxed{
\widehat s_i(t)
=
\frac{dq_i}{dt}
-
g_i(t)
},
\]

where \(g_i\) is the known net internal transfer into identity \(i\). The estimator received no damping,
resistance or quantum-decay coefficient.

Applied unchanged to damped coupled oscillators, resistive capacitor coupling and an open two-level quantum
holdout, the residual recovered all `3/3` hidden locations and all active-point sink signs. Across `18,991` scored
samples, the maximum source NRMSE was \(1.0554\times10^{-9}\), maximum integrated relative error was
\(4.5071\times10^{-11}\), and maximum inactive-identity RMS fraction was \(1.8859\times10^{-9}\). The
electromagnetic case localized Joule loss to the coupling relation rather than either capacitor. Independent
bounded-output validation passed.

This makes `Other` an operational diagnostic rather than a free remainder: after boundary, storage and named flows
are declared, it records where the account fails to close. The result remains standard conservation residual
analysis in noiseless controlled systems. It does not yet identify the functional sink law in advance or predict
an unseen real-world waveform. Full report:
`analysis/physics_ladder/ARA_HIDDEN_OTHER_RESIDUAL_REPORT_2026-07-23.md`.

### 5.21 Noise boundary: cumulative closure does not ensure local attribution

O2-A1 retained the same residual but corrupted its measured inputs under a preregistered ladder. At the primary
12 dB white-noise condition on the capacitor and quantum targets, exact location fell to \(0.50\), median
active-point sign accuracy to \(0.762\), and median waveform correlation to \(0.460\). Median peak NRMSE was
\(0.314\), worse than the zero-Other control's \(0.221\). The frozen robustness claim was therefore
**NOT SUPPORTED**.

The signed integrated amount behaved differently:

\[
\operatorname{median}
\left[
\frac{
\left|\int\widehat s\,dt-\int s\,dt\right|
}{
\left|\int s\,dt\right|
}
\right]
=0.007872.
\]

Thus the parent account can remain nearly closed while child-level waveform and location are unreliable. In the
test, zero-mean errors cancelled under integration but appeared as false local residuals. Transfer-channel
corruption was more damaging than stored-quantity corruption because the selected smoother acted on \(q\), while
observed \(g\) entered the residual directly. This is an error-propagation result, not a new ARA force law.

The established crosswalk should therefore be written with observation errors:

\[
\widehat s_i
=
\frac{d(q_i+\epsilon_{q_i})}{dt}
-
(g_i+\epsilon_{g_i})
=
s_i
+
\frac{d\epsilon_{q_i}}{dt}
-
\epsilon_{g_i}.
\]

The last two terms can exceed the hidden mechanism even when their signed integral is small. Before applying the
operator physically to ECG, field-energy or climate accounts, a joint uncertainty/state model for \(q\) and \(g\)
is required. Full report:
`analysis/physics_ladder/O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_REPORT_2026-07-23.md`.

### 5.22 Conditional time-stream lineage: fixed identity versus repeated re-selection

O2-A2 tested Dylan's declared distinction between following movement and retaining stored information. For this
test only, the time-side operation meant: name a moving child before the run and follow that same typed residual
downstream. The complementary space-side operation—maintaining the stored parent identity—was not folded into the
same claim.

With causal instrument \(H\), declared child \(j^\star\), and typed residuals
\(\widehat s_j=d(Hq_j)/dt-Hg_j\), the two compared operations were

\[
\widehat s_{\mathrm{fixed}}(t)=\widehat s_{j^\star}(t),
\qquad
\widehat s_{\mathrm{reselect}}(t)
=
\widehat s_{\arg\max_j\,\operatorname{EWMA}(|\widehat s_j|)}(t).
\]

The first preserves declared lineage. The second repeatedly returns to the local parent mixture and chooses the
currently strongest child. Both used the same derivative and trajectory filters; those parameters were selected
only on oscillator development and then frozen.

At the registered 12 dB capacitor-plus-quantum target, fixed lineage produced median correlation \(0.764\), peak
NRMSE \(0.168\), sign accuracy \(0.933\), and integrated relative error \(0.354\). Relative to re-selection, its
correlation advantage was \(+0.060\) and its NRMSE improvement was \(10.84\%\). It beat re-selection NRMSE in both
systems, but failed the preregistered integral threshold of \(0.35\) and correlation-advantage threshold of
\(+0.10\). The frozen claim was therefore **NOT SUPPORTED** (`6/8` gates), and those thresholds were not relaxed.

The target systems separated usefully. In the quantum system, fixed lineage gave NRMSE \(0.174\) versus \(0.234\)
for re-selection and integrated error \(0.0526\). In the capacitor relation, fixed lineage retained local waveform
shape (\(r=0.819\)) but its signed integral was badly biased (relative error \(1.771\)); the compressed-parent
control also had lower NRMSE (\(0.0649\)). Thus a known moving branch can be easier to follow than to rediscover at
each sample, while a storage-oriented parent account can remain the better representation for another endpoint.

This is a conditional signal-tracking result using standard causal differentiation and exponential smoothing. It
does not discover the child, reconstruct upstream causes, establish the space-side retention rule, identify a
physical hidden mechanism or predict an unseen future waveform. Independent validation passed `12/12`. Full
report: `analysis/physics_ladder/O2A2_TIME_STREAM_LINEAGE_REPORT_2026-07-23.md`.

### 5.23 Fixed lineage and a conventional state-space account retain different information

O2-A3 compared the frozen ARA fixed-lineage instrument with a causal augmented-state Kalman filter using the same
declared quantum child and observations. The conventional model represented

\[
x_k=
\begin{bmatrix}q_k\\s_k\end{bmatrix},
\qquad
x_{k+1}
=
\begin{bmatrix}1&\Delta t\\0&1\end{bmatrix}x_k
+
\begin{bmatrix}\Delta t\\0\end{bmatrix}g_{{\rm obs},k}
+w_k,
\qquad
y_k=q_k+v_k.
\]

The latent \(s_k\) is a standard random-walk omitted input in the same continuity account
\(\dot q=g+s\). Process ratios were selected on oscillator development only; target observation noise was estimated
from an observed-only prefix.

On `32` fresh paired quantum runs at 12 dB, the ARA instrument gave correlation \(0.762\), NRMSE \(0.165\), sign
accuracy \(0.905\), and integrated error \(0.118\). The Kalman filter gave \(0.687\), \(0.235\), \(0.808\), and
\(0.038\), respectively. ARA won correlation and NRMSE in every pair; state-space won integrated error in every
pair. The preregistered result is therefore **GOOD ABSOLUTE TRACKING / MIXED COMPARATIVE RESULT**.

The split has a direct mechanics interpretation. Differentiation plus trajectory smoothing can follow the local
shape of a named moving residual, while a state transition that explicitly carries stored \(q\) reconciles small
errors across time and better preserves the cumulative amount. This supports treating movement-shape tracking and
storage closure as different endpoints. It does not establish that the endpoints are ontologically Time and Space,
nor that the quantum target exposes a hidden Phase B.

Only one simple conventional state-space model was tested. A quantum-family-trained or correctly specified sink
model could change the comparison. The capacitor secondary target was not identifiable after calibration because
only \(0.229\%\) of its original sink peak remained. Independent validation passed `12/12`. Full report:
`analysis/physics_ladder/O2A3_STATE_SPACE_COMPARATOR_REPORT_2026-07-23.md`.

### 5.24 Multi-axis ARA is exactly the informationally complete qubit coordinate

T258 tested Dylan's statement that one ARA diameter is an accurate but compressed cut through a sphere. For a
qubit Bloch vector \(\mathbf r\), the directional ARA reading

\[
x_{\hat n}=1-\mathbf r\cdot\hat n
\]

is an exact affine coordinate. Three orthogonal cuts give

\[
\mathbf r=(1-x_X,1-x_Y,1-x_Z).
\]

This is the standard qubit tomography identity written on the ARA \(0\!-\!2\) diameter. One cut is many-to-one:
the condition \(x_Z=1\) means only \(r_z=0\). It includes every pure equatorial state, partially dephased
equatorial states and the maximally mixed centre. Direction on the equator and Bloch radius are discarded.

The registered known-referee test made that information loss exact. Unitary rotation and pure dephasing shared
the same clean \(Z\) cut,

\[
x_Z^U(t)=x_Z^{T2}(t)=1,
\]

while longitudinal relaxation and combined rotation-relaxation shared the same paired \(Z\) trajectory. All four
families began at \((1,0,0)\). Independent finite-shot `X/Y/Z` observations were then converted back to
\(\widehat{\mathbf r}\), with noisy estimates outside the Bloch ball projected radially to its boundary.

At the frozen `128`-shot condition, the three-cut ARA feature account classified `511/512` fresh trials
(`0.998047`) versus `256/512` (`0.500000`) for the `Z`-only account. Rotation direction and
unitary-versus-dephasing ridge classification were each `256/256`; prediction of `16` held-out directions per
trial gave MAE \(0.061123\). A common time shuffle fell to \(0.455078\), and axis-label shuffling fell to
\(0.523438\), confirming that both temporal order and cut orientation carried the registered information.

The decisive equality control also passed:

\[
\widehat{\mathbf r}_{\rm ARA}
=
\widehat{\mathbf r}_{\rm Bloch}
\]

for every target sample, with zero feature difference and zero classification disagreements. A fixed-grid native
four-family quantum model fit classified `512/512`. Thus the frozen benchmark passed `9/9` gates and independent
validation passed `14/14`, but the correct result is not “ARA beats quantum mechanics.” It is:

> several measured ARA diameters recover the same full qubit state that standard Bloch tomography recovers, while
> one diameter necessarily collapses direction and radius information.

The test is synthetic and the four native mechanisms are deliberately separated. It does not derive the Born
rule, identify a hidden ontological Phase B, establish that quantum is literally Information, prove universal
fractal spheres, phi handover or quantum gravity, or demonstrate superiority on experimental hardware. Full
report: `analysis/quantum/Q1_OPEN_QUBIT_MULTI_AXIS_REPORT_2026-07-23.md`.

## 6. What this cements — and what it does not (the honest line)
- **Cemented:** the ARA rise/fall statistic is exactly `1` for the defined traversal of a bounded autonomous 1-D
  conservative oscillator; relaxation and limit-cycle theory provide established comparison families; KAM and
  circle-map theory rigorously describe resistance to rational resonance and mode locking in specified systems;
  Hamiltonian action, entropy production, threshold dynamics, Deborah number, storage/loss response, Gauss source
  reconstruction, field-particle energy exchange and nonlinear harmonic coupling are established quantities. The
  signed-pair Gauss embedding, in-system logarithmic rung, relative-log factor closure and wheel anti-pair reflection
  are exact once their measurement declarations are fixed. The prime-wheel representation admits exact `2:1`
  anti-pair compression, while its pair count still grows by `p-1` at a new gate. Einstein's equation reduces to
  Poisson/Newton gravity under the declared weak-field assumptions, and the anti-directed Newtonian force account
  satisfies the exact bounded identity \(m a_\parallel=\Sigma_F(x_F-1)\).
  **These anchors are not new physics.**
- **NOT cemented by this (stays empirical / open):** the **universality** claim — that these coordinates carry
  the *same* φ/octave and Connection/Transfer structure *across* atoms, materials, climate, hearts, and markets;
  that φ is a universal stability or handover optimum; that every irreversible crossing sheds `1/φ²`; or that
  every threshold implements the same singularity flip. Grounding the scaffolding does not
  prove the cross-domain regularity; that rests on the measured results (e.g., the +0.38 ECG-beats-Fourier win,
  the strict-causal ENSO forecasting) and needs independent replication. The speculative frontiers
  (dark-sector, vacuum-c, "theory of everything") are explicitly *not* cemented here and should not lean on this
  doc. Nor does the prime crosswalk establish a three-operation next-prime algorithm, a complexity improvement or
  a new theorem: the tested exact locators retained the full established child-factor information.

## 7. The reviewable claim that results
> *ARA is a proposed relational coordinate framework built from measurable features already used in mechanics
> and dynamical-systems theory: traversal-time asymmetry, action, phase locking, relaxation time, storage/loss,
> and entropy production. Its rise/fall coordinate equals one for the defined bounded autonomous 1-D conservative
> traverse; deviations identify structure beyond that baseline but do not uniquely diagnose its cause. KAM and
> circle-map theory motivate—without universally proving—the proposed φ/rational organisation. In a declared
> electrostatic plasma, signed source balance and logarithmic harmonic rungs admit exact ARA coordinates; development
> tests then support identity participation, delayed nonlinear descendants and an asymmetric coupling web while also
> retaining important nulls. In arithmetic, complementary factors and opposite wheel residues provide exact
> child-to-parent and anti-pair examples, including lossless `2:1` symmetry compression, but no prime-specific
> computational improvement. On top of these
> established anchors sits the empirical ARA claim: that the same bounded Connection/Transfer, phase, scale, and
> handover geometry recurs across domains. That universality remains open to predeclared independent tests.*

That sentence is defensible line-by-line, names its own evidence tier for each part, and — unlike "theory of
everything" — invites checking rather than dismissal. It is the front door.

Named sources: Newton (Principia); Hooke; Lagrange/Hamilton (action-angle mechanics); Kolmogorov 1954 / Arnold
1963 / Moser 1962 (KAM); Arnold (tongues / circle map); van der Pol; FitzHugh 1961 & Nagumo 1962; Le Chatelier;
Lyapunov; Clausius/Boltzmann (2nd law); Rankine–Hugoniot; Lorentz / Prandtl–Glauert; Wilson (renormalization
group); Scheffer et al. 2009 (critical slowing down).
