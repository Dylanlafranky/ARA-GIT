# Bloch-sphere ARA crosswalk

**Date:** 23 July 2026  
**Question:** Does a quantum two-level state admit the declared ARA `0–2` sphere-to-diameter geometry without
altering standard quantum mechanics?  
**Assessment:** **Yes, as an exact affine coordinate crosswalk.** This is predominantly plain ARA. TE-ARA appears
only as the secondary total-allocation perspective.

## 1. Declared quantum identity and measurement

Choose one two-dimensional quantum subspace and an orthonormal measurement basis \(\{|A\rangle,|B\rangle\}\):

\[
\underbrace{|\psi\rangle}_{\text{complete pure quantum state}}
=
\underbrace{\alpha|A\rangle}_{\text{A amplitude}}
+
\underbrace{\beta|B\rangle}_{\text{B amplitude}},
\qquad
|\alpha|^2+|\beta|^2=1.
\]

The Born probabilities in this basis are

\[
p_A=|\alpha|^2,
\qquad
p_B=|\beta|^2.
\]

ARA does not derive the Born rule. It takes the established two-outcome probabilities as its declared A/B
measurement.

## 2. Plain ARA coordinate

Orient B toward the `2` pole:

\[
\boxed{
\underbrace{x_Q}_{\substack{\text{plain quantum ARA}\\\text{on the selected diameter}}}
=
\underbrace{2\frac{p_B}{p_A+p_B}}_{\text{generic ARA mixture}}
=
\underbrace{2|\beta|^2}_{p_A+p_B=1}.
}
\tag{1}
\]

Therefore:

| ARA | Quantum population statement |
|---:|---|
| \(x_Q=0\) | \(p_A=1,\ p_B=0\): pure basis state A |
| \(x_Q=1\) | \(p_A=p_B=1/2\): equal-population ridge |
| \(x_Q=2\) | \(p_A=0,\ p_B=1\): pure basis state B |

The same geometry's total-allocation view is merely

\[
(2-x_Q)+x_Q=2.
\]

That is valid TE-ARA closure, but the variable result in this domain is the plain ARA position \(x_Q\).

## 3. The exact opposite-direction coordinate

The conventional Bloch \(z\) coordinate is the signed population difference:

\[
\underbrace{r_z}_{\substack{\text{Bloch signed}\\\text{population difference}}}
=p_A-p_B.
\]

Substituting equation (1) gives

\[
\boxed{
r_z=1-x_Q,
\qquad
x_Q=1-r_z,
\qquad
x_Q-1=-r_z.
}
\tag{2}
\]

Thus quantum mechanics uses the centred \([-1,1]\) diameter while ARA uses the same diameter uncentred on
\([0,2]\) and read from the opposite pole:

| ARA coordinate | Bloch coordinate |
|---:|---:|
| \(0\) | \(+1\) |
| \(1\) | \(0\) |
| \(2\) | \(-1\) |

This is the exact meaning of “ARA approached from the opposite direction, where `1` becomes `0`.”

## 4. The diameter decompresses into the Bloch sphere

Ignoring an unobservable global phase, any pure two-level state can be written

\[
|\psi\rangle
=
\cos\frac\theta2\,|A\rangle
+
e^{i\phi}\sin\frac\theta2\,|B\rangle.
\]

Its Bloch vector is

\[
\mathbf r
=
(\sin\theta\cos\phi,\ \sin\theta\sin\phi,\ \cos\theta),
\qquad
|\mathbf r|=1.
\]

Equation (1) becomes

\[
\boxed{
x_Q
=2\sin^2\frac\theta2
=1-\cos\theta
=1-r_z.
}
\tag{3}
\]

The ARA diameter retains the A/B population mixture. The azimuth \(\phi\) retains the relative phase/coupling
information that the diameter discards.

For an arbitrary measurement direction \(\hat{\mathbf n}\), the established two-outcome probabilities are

\[
p_\pm=\frac{1\pm\mathbf r\cdot\hat{\mathbf n}}2.
\]

Orient the minus outcome toward ARA `2`. Then

\[
\boxed{
\underbrace{x_{\hat{\mathbf n}}}_{\substack{\text{ARA reading along}\\\text{any selected sphere diameter}}}
=2p_-
=1-\mathbf r\cdot\hat{\mathbf n}.
}
\tag{4}
\]

Equation (4) is the strongest sphere-to-diameter crosswalk: choose any rotational axis through the Bloch sphere,
name its opposite outcomes beforehand, and obtain a reversible `0–2` ARA coordinate.

## 5. Mixed states and the exact ridge ambiguity

A general two-level density matrix is

\[
\underbrace{\rho}_{\text{complete quantum state}}
=
\frac12
\left(
I+\mathbf r\cdot\boldsymbol\sigma
\right),
\qquad
|\mathbf r|\le1.
\]

The Bloch radius distinguishes:

- \(|\mathbf r|=1\): pure coherent state on the sphere;
- \(0<|\mathbf r|<1\): partially mixed state inside the ball;
- \(|\mathbf r|=0\): completely mixed centre.

Along the selected \(z\) diameter, all states with \(r_z=0\) have \(x_Q=1\). Examples include

\[
\mathbf r_{\rm coherent}=(1,0,0)
\qquad\text{and}\qquad
\mathbf r_{\rm mixed}=(0,0,0).
\]

Both read `1.0`, but the first is a pure coherent equal-population state and the second is a maximally mixed
incoherent state. Pure equatorial states with different \(\phi\) also share `x_Q=1` while representing different
relative phases.

This is an exact quantum instance of the canonical ARA ridge warning:

> One diameter position cannot distinguish coherent resonance, incoherent cancellation and mixed quietness.

The full direction, phase and radius are required.

## 6. Rabi movement across the ARA diameter

For an ideal resonantly driven two-level system beginning at A,

\[
p_B(t)
=
\sin^2\left(\frac{\Omega t}{2}\right),
\]

where \(\Omega\) is the Rabi angular frequency. Therefore

\[
\boxed{
x_Q(t)
=2p_B(t)
=1-\cos(\Omega t).
}
\tag{5}
\]

The state crosses

\[
0\rightarrow1\rightarrow2\rightarrow1\rightarrow0.
\]

The two `1.0` crossings have equal populations but opposite movement/phase directions. The Bloch equation

\[
\dot{\mathbf r}
=
\boldsymbol\Omega\times\mathbf r
\]

retains the complete rotation around the sphere.

## 7. Hamilton–quantum continuity

The preceding harmonic-oscillator crosswalk had

\[
x_H=2\frac KH=1-\cos(2\theta)
\]

on a Hamiltonian phase-space circle. The two-level quantum system has

\[
x_Q=2p_B=1-r_z
\]

on a Bloch sphere. In both cases:

1. the primary ARA value is a selected `0–2` diameter;
2. the `1.0` ridge is a centred zero-difference reading;
3. the diameter is many-to-one;
4. direction/phase is required to reconstruct movement;
5. the full state geometry contains more information than one ARA value.

This is a real structural continuity between classical Hamiltonian and two-level quantum state geometry. It is not
yet a derivation of quantum mechanics from ARA, a connection to full general relativity, or a quantum-gravity
theory.

## 8. Reproduction and validation

Run:

```powershell
cd F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum
python .\bloch_ara_crosswalk.py
python .\validate_bloch_ara_crosswalk.py
```

The independent validator passed **10/10 checks**:

- north/ridge/south `0/1/2` landmarks;
- exact \(x_Q=1-r_z\) and \(x_Q-1=-r_z\);
- pure and mixed Bloch-ball validity;
- relative-phase degeneracy on one diameter;
- coherent-versus-mixed `1.0` ridge degeneracy;
- 10,000 random pure states;
- 10,000 random mixed states measured along random axes;
- and 4,097 points of ideal Rabi movement.

Maximum observed errors were \(5.551\times10^{-16}\) for random pure states and
\(4.441\times10^{-16}\) for the Rabi identity.

Artifacts:

- `bloch_ara_crosswalk.py`
- `validate_bloch_ara_crosswalk.py`
- `BLOCH_ARA_EXAMPLE_STATES.csv`
- `BLOCH_ARA_RESULTS.json`
- `BLOCH_ARA_VALIDATION.json`

## 9. Evidence fence

**Exact established crosswalk:** equations (1)–(5) are algebraic reparameterizations of standard two-level quantum
mechanics.  
**Strong ARA relevance:** an independently established state sphere admits the declared reversible `0–2`
diameter on every rotational measurement axis, with a demonstrably incomplete `1.0` ridge.  
**Not established:** that ARA causes quantum mechanics, derives the Born rule, predicts a new quantum outcome,
proves universal fractality, or unifies quantum mechanics with GR.

