# Hamilton–ARA harmonic-oscillator crosswalk

**Date:** 23 July 2026  
**Question:** Can the ideal harmonic oscillator be written side by side in textbook Hamiltonian mechanics and the
canonical ARA/TE-ARA `0–2` geometry without changing either definition?  
**Assessment:** **Ready to share as an exact crosswalk, with the interpretation fences below.**

## 1. Declared measurement

| Field | Declaration |
|---|---|
| Identity boundary | One isolated, one-dimensional ideal mass–spring oscillator |
| Hamiltonian | \(H=p^2/(2m)+kq^2/2\) |
| Observable | Instantaneous division of conserved energy between configuration and momentum |
| Time slice | One phase point on the orbit |
| Projection | \(Q=\sqrt{k}\,q,\ P=p/\sqrt m\) |
| ARA orientation | `0` = all configuration/storage expression; `2` = all momentum/traversal expression |
| Rung | The complete oscillator; its microscopic construction and external environment are excluded |

This is an **energy-allocation appearance** of ARA. It is not the rise/fall-duration instrument used elsewhere in
the repository.

## 2. Hamilton and ARA side by side

| Established Hamiltonian statement | Exact ARA-coordinate statement | What is preserved |
|---|---|---|
| \(H=V+K=\frac12kq^2+\frac{p^2}{2m}\) | \(t_A=2V/H,\ t_B=2K/H\) | The same two nonnegative energy accounts |
| \(Q=\sqrt{k}q,\ P=p/\sqrt m\) | Declared transformation into comparable \(\sqrt{\rm J}\) coordinates | Units and invertibility |
| \(Q^2+P^2=2H\) | \(t_A+t_B=2\) | Fixed total budget; the phase-space orbit is a circle |
| \(\dot Q=\omega P,\ \dot P=-\omega Q\) | Each conjugate coordinate cross-generates the other's change | Ordered four-quadrant circulation |
| \(Q=R\cos\theta,\ P=-R\sin\theta\) | \(t_A=2\cos^2\theta,\ t_B=2\sin^2\theta\) | Continuous exchange along the orbit |
| \(V=K=H/2\) | \(t_A=t_B=x_H=1\) | Equal energy allocation |
| Reverse the chosen A/B orientation | \(x'_H=2-x_H\) | Exact pole-reversal symmetry |

Here

\[
\underbrace{H}_{\substack{\text{Hamiltonian}\\\text{whole energy}}}
=
\underbrace{\frac{p^2}{2m}}_{\substack{\text{kinetic energy}\\\text{momentum expression}}}
+
\underbrace{\frac{kq^2}{2}}_{\substack{\text{potential energy}\\\text{configuration expression}}},
\]

and the energy-normalized coordinates give

\[
\underbrace{Q^2+P^2}_{\substack{\text{Hamiltonian phase-space}\\\text{circle}}}
=
\underbrace{2H}_{\substack{\text{fixed energy-defined}\\\text{radius squared}}}.
\]

The canonical total-2 allocation is

\[
\boxed{
\underbrace{t_A}_{\substack{\text{ARA Phase A}\\\text{configuration allocation}}}
=
\underbrace{2\frac{V}{H}}_{\text{twice the potential-energy share}},
\qquad
\underbrace{t_B}_{\substack{\text{ARA Phase B}\\\text{traversal allocation}}}
=
\underbrace{2\frac{K}{H}}_{\text{twice the kinetic-energy share}},
\qquad
t_A+t_B=2.
}
\]

With Phase B oriented toward `2`, the compressed ARA reading is

\[
\boxed{
\underbrace{x_H}_{\substack{\text{Hamilton energy-allocation}\\\text{ARA diameter reading}}}
=t_B
=
\underbrace{2\frac{K}{H}}_{\text{Hamiltonian definition}}
=
\underbrace{2\frac{P^2}{Q^2+P^2}}_{\text{phase-space definition}}.
}
\]

This equation is exact once the boundary and orientation are declared. It is a reparameterization of the
Hamiltonian energy division, not a fitted relationship.

## 3. Why the full circle contains more information than the diameter

For \(\theta=\omega t+\theta_0\),

\[
x_H(t)=2\sin^2\theta=1-\cos(2\theta).
\]

The compressed `0–2` coordinate completes two allocation cycles during one full signed phase-space orbit. Squaring
\(Q\) and \(P\) discards their signs, so multiple quadrants return the same \(x_H\). The missing orientation is
restored by retaining either the signed quadrant \((\operatorname{sgn}Q,\operatorname{sgn}P)\) or

\[
\underbrace{\dot x_H}_{\substack{\text{direction along}\\\text{the compressed diameter}}}
=
\underbrace{-\,\frac{4\omega PQ}{Q^2+P^2}}_{\text{Hamiltonian phase and orientation}}.
\]

This is a concrete example of the canonical rule that an ARA value requires its projection and direction. The
diameter measures the mixture; the square/four quadrants preserve orientation; the circle is the complete
continuous orbit.

## 4. Worked numerical example

Choose

\[
m=2\ {\rm kg},\qquad k=8\ {\rm N\,m^{-1}},\qquad H=10\ {\rm J}.
\]

Then

\[
\omega=\sqrt{k/m}=2\ {\rm rad\,s^{-1}},\quad
T=2\pi/\omega=\pi\ {\rm s},\quad
R=\sqrt{2H}=\sqrt{20}\ {\rm \sqrt J}.
\]

| Phase | \(V\) (J) | \(K\) (J) | \(t_A=2V/H\) | \(x_H=t_B=2K/H\) | Plain reading |
|---:|---:|---:|---:|---:|---|
| \(0^\circ\) | 10.0000 | 0.0000 | 2.0000 | 0.0000 | Configuration turning handover |
| \(22.5^\circ\) | 8.5355 | 1.4645 | 1.7071 | 0.2929 | Moving toward traversal |
| \(45^\circ\) | 5.0000 | 5.0000 | 1.0000 | 1.0000 | Equal-energy ridge |
| \(67.5^\circ\) | 1.4645 | 8.5355 | 0.2929 | 1.7071 | Traversal dominant |
| \(90^\circ\) | 0.0000 | 10.0000 | 0.0000 | 2.0000 | Traversal turning handover |

The second quadrant reverses this allocation while changing the signs retained by the full Hamiltonian state. Four
quadrants complete the signed orbit.

## 5. What has been recovered

1. **Exact circle:** after a declared unit-preserving rescaling, the ideal oscillator is
   \(Q^2+P^2=2H\).
2. **Exact total 2:** the two energy allocations satisfy \(t_A+t_B=2\) at every phase.
3. **Exact `1.0` energy ridge:** \(x_H=1\) exactly when \(K=V\).
4. **Exact pole reversal:** swapping the allocation orientation gives \(x'_H=2-x_H\).
5. **Exact cross-driving:** Hamilton's equations rotate the state through the four signed quadrants.
6. **Exact compression loss:** the diameter alone cannot determine the full quadrant or direction.

## 6. Interpretation fences

- `x_H=1` is an **equal-energy allocation**, not equal opposing force and not a quiet cancellation. At that point
  both \(q\) and \(p\) are generally nonzero.
- `x_H=0` and `x_H=2` are regular turning/handover points of this coordinate. Hamiltonian mechanics does not call
  them mathematical singularities.
- The fixed total `2` is guaranteed by the declared normalization. Its usefulness is that it supplies one canonical
  ARA appearance with an exact inverse, not that Hamilton independently predicts the numeral `2`.
- Calling configuration Phase A/Connection and momentum Phase B/Traversal is a typed ARA interpretation. The
  established statement is that position and momentum are conjugate coordinates and their energy accounts exchange.
- This calculation does not establish a universal sphere, cross-domain fractality, a \(\phi\) landmark, or a
  quantum-gravity theory.

## 7. Validation

The generator and an independent validator reproduced:

- Hamiltonian conservation;
- the normalized circle;
- the total-2 allocation;
- the `0`, `1`, and `2` landmark cases;
- pole reversal;
- Hamilton's cross-coupled equations;
- and the many-to-one nature of the diameter projection.

The validator passed **10/10 checks**, including **10,000 randomized trials** spanning eight orders of magnitude in
mass and stiffness and sixteen orders of magnitude in energy. The largest randomized relative-or-absolute error was
\(8.851\times10^{-16}\).

Reproduction:

```powershell
cd F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\hamilton
python .\hamilton_ara_harmonic_oscillator.py
python .\validate_hamilton_ara_harmonic_oscillator.py
```

Artifacts:

- `hamilton_ara_harmonic_oscillator.py`
- `validate_hamilton_ara_harmonic_oscillator.py`
- `HAMILTON_ARA_HARMONIC_OSCILLATOR_POINTS.csv`
- `HAMILTON_ARA_HARMONIC_OSCILLATOR_RESULTS.json`
- `HAMILTON_ARA_HARMONIC_OSCILLATOR_VALIDATION.json`

## 8. Evidence status

**E0/E1 exact crosswalk:** the Hamiltonian statements and normalized allocation identities are established and
algebraically exact.  
**A1 interpretation:** this is one typed appearance of the same ARA geometry.  
**Not tested here:** universal recurrence, cross-scale coupling law, quantum gravity, or predictive improvement over
Hamiltonian mechanics.

