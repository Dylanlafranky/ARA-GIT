# Landau–Zener ARA handover crosswalk

**Date:** 23 July 2026  
**Question:** Does the standard Landau–Zener avoided crossing admit a non-arbitrary ARA description of structural
mixing and final handover?  
**Assessment:** **Ready to share as two exact, separately typed coordinate crosswalks under the ideal
Landau–Zener assumptions.**

## 1. Declared model and convention

Use the two-state Hamiltonian

\[
\boxed{
\underbrace{\hat H(t)}_{\text{complete two-state Hamiltonian}}
=
\begin{pmatrix}
\frac{vt}{2} & g\\
g &-\frac{vt}{2}
\end{pmatrix}
=
\frac{vt}{2}\sigma_z+g\sigma_x.
}
\tag{1}
\]

Here:

- \(vt\equiv\Delta(t)\) is the time-dependent bare-state detuning;
- \(v=d\Delta/dt\) is the crossing or sweep rate;
- \(g\) is the A–B coupling energy;
- the two uncoupled basis energies are equal at \(t=0\).

The Pauli form exposes the geometry. Detuning lies on the Bloch \(z\) axis; coupling lies on the perpendicular
\(x\) axis:

\[
\mathbf h(t)=(2g,0,vt),
\qquad
\hat H=\frac12\mathbf h\cdot\boldsymbol\sigma.
\]

Thus the “perpendicular sharing” intuition has an exact mathematical counterpart inside the Bloch representation:
the coupling term is transverse to the bare-state opposition axis.

## 2. Equal bare-energy ridge and the avoided gap

The instantaneous eigenenergies are

\[
E_\pm(t)
=
\pm\frac12
\sqrt{(vt)^2+4g^2}.
\]

Their separation is

\[
\underbrace{\Delta E(t)}_{\text{coupled level gap}}
=
\sqrt{(vt)^2+4g^2},
\qquad
\underbrace{\Delta E_{\min}}_{t=0}
=2|g|.
\tag{2}
\]

At \(t=0\), the *bare* A and B energies meet equally. This is the declared `1.0` bare-population ridge. If
\(g\neq0\), the coupled eigenvalues do not meet; coupling replaces the direct crossing with an avoided gap.

If \(g=0\), the gap closes at \(t=0\). The Hamiltonian remains finite, but the two eigenvalues are degenerate and
the instantaneous eigenvector is not uniquely selected. This is a genuine spectral gap closure and a defensible
ARA identity-local singularity crossing. It is not a divergent spacetime singularity.

## 3. Structural ARA path

For \(v>0\), the lower instantaneous eigenstate begins as A at \(t\to-\infty\) and ends as B at
\(t\to+\infty\). Its B population is

\[
p_B^{(-)}(t)
=
\frac12
\left(
1+\frac{vt}{\sqrt{(vt)^2+4g^2}}
\right).
\]

The primary structural plain-ARA coordinate is therefore

\[
\boxed{
\underbrace{x_{\rm path}(t)}_{\substack{\text{instantaneous lower-eigenstate}\\\text{ARA mixture}}}
=2p_B^{(-)}(t)
=
1+\frac{vt}{\sqrt{(vt)^2+4g^2}}.
}
\tag{3}
\]

It has the exact properties

\[
\lim_{t\to-\infty}x_{\rm path}=0,
\qquad
x_{\rm path}(0)=1,
\qquad
\lim_{t\to+\infty}x_{\rm path}=2,
\]

\[
x_{\rm path}(-t)=2-x_{\rm path}(t),
\]

and, for \(v,g>0\),

\[
\frac{dx_{\rm path}}{dt}
=
\frac{4g^2v}{\left((vt)^2+4g^2\right)^{3/2}}>0.
\]

Plainly: nonzero coupling decompresses a direct `0→2` flip into a smooth gradient through the equal-mixing
`1.0` ridge. Larger \(|g|\) broadens the mixing region; smaller \(|g|\) sharpens it.

Away from \(t=0\),

\[
\lim_{g\to0}x_{\rm path}(t)
=
1+\operatorname{sgn}(t).
\]

At \(t=0,g=0\), equation (3) is undefined. Its one-sided readings are `0` and `2`, while the missing unique
eigenstate marks the gap-closing seam.

**Essential fence:** equation (3) describes the instantaneous lower eigenstate. The actual finite-speed quantum
state follows this structural path only in the adiabatic limit.

## 4. Connection versus Traversal/Time control

The dimensionless Landau–Zener control is

\[
\boxed{
\underbrace{\gamma}_{\substack{\text{dimensionless}\\\text{handover control}}}
=
\frac{
\underbrace{g^2}_{\substack{\text{connection}\\\text{coupling energy squared}}}
}{
\underbrace{\hbar|v|}_{\substack{\text{traversal/time}\\\text{crossing-rate scale}}}
}.
}
\tag{4}
\]

This is the accurate version of the ARA Connection-versus-Time reading. \(g\) alone is not a ratio and carries
energy units. The square, \(\hbar\), and sweep rate are required to create the dimensionless physical comparison.

- \(\gamma\ll1\): weak connection or rapid traversal;
- \(\gamma\gg1\): strong connection or slow traversal.

## 5. Final handover ARA

For the ideal infinite linear sweep, the Landau–Zener probability of remaining on the same diabatic basis branch is

\[
\underbrace{P_{\rm stay}}_{\substack{\text{retain original}\\\text{basis identity}}}
=
e^{-2\pi\gamma}.
\]

The probability of following the adiabatic branch and handing over into the other basis identity is

\[
\underbrace{P_{\rm handover}}_{\text{A-to-B transfer}}
=
1-e^{-2\pi\gamma}.
\]

Define the outcome-oriented plain-ARA coordinate

\[
\boxed{
\underbrace{x_{\rm handover}}_{\substack{\text{final transfer}\\\text{ARA outcome}}}
=
2P_{\rm handover}
=
2\left(1-e^{-2\pi g^2/(\hbar|v|)}\right).
}
\tag{5}
\]

Then:

- \(x_{\rm handover}=0\): no handover in the limiting uncoupled/infinitely rapid case;
- \(x_{\rm handover}=1\): equal stay/handover probability;
- \(x_{\rm handover}\to2\): nearly complete adiabatic handover.

The outcome ridge occurs at

\[
\gamma_{\rm ridge}
=
\frac{\ln2}{2\pi}
\approx0.110318.
\]

This outcome ridge is distinct from the structural ridge at \(t=0\). One belongs to instantaneous state mixture;
the other belongs to final transition probability.

## 6. Worked example

Choose dimensionless units

\[
\hbar=1,\qquad g=0.5,\qquad v=1.
\]

Then

\[
\gamma=0.25,
\qquad
\Delta E_{\min}=1,
\]

\[
P_{\rm stay}=0.2078796,
\qquad
P_{\rm handover}=0.7921204,
\qquad
x_{\rm handover}=1.5842408.
\]

Selected points on the structural path:

| \(t\) | \(x_{\rm path}\) | Reading |
|---:|---:|---|
| \(-4\) | 0.029857 | A dominant |
| \(-2\) | 0.105573 | A dominant |
| \(-1\) | 0.292893 | approaching the mixing region |
| \(0\) | 1.000000 | equal bare-state mixing |
| \(+1\) | 1.707107 | B dominant |
| \(+2\) | 1.894427 | B dominant |
| \(+4\) | 1.970143 | approaching pure B |

## 7. What this means for ARA

Landau–Zener supplies two different but exact ARA views:

| ARA view | Axis | `1.0` means |
|---|---|---|
| Structural \(x_{\rm path}(t)\) | instantaneous lower-eigenstate A/B mixture | equal bare-state population at \(t=0\) |
| Outcome \(x_{\rm handover}(\gamma)\) | final stay-versus-transfer probability | equal probability of the two outcomes |

Both are primarily plain ARA. TE-ARA is present only as the same geometry's secondary complementary-allocation
view.

The crosswalk supports the following careful ARA translation:

> A direct gap-closing flip occurs when transverse coupling vanishes. Nonzero connection spreads that flip into a
> finite gradient-mixing region. Whether the evolving identity completes the handover depends on the dimensionless
> competition between connection strength and traversal rate.

## 8. Reproduction and validation

Run:

```powershell
cd F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\quantum
python .\landau_zener_ara_crosswalk.py
python .\validate_landau_zener_ara_crosswalk.py
```

The independent validator passed **12/12 checks**, including:

- bounded and monotone structural `0–2` path;
- exact `1.0` ridge;
- minimum gap \(2g\);
- pole-reversal mirror symmetry;
- 10,000 independently solved two-by-two eigenstate/path trials;
- bounded and monotone outcome coordinate;
- exact outcome-ridge \(\gamma=\ln2/(2\pi)\);
- 10,000 random transition-probability trials;
- and the zero-coupling one-sided `0→2` limit.

Maximum eigenstate-coordinate error was \(8.882\times10^{-16}\); maximum dimensionless derivative error was
\(5.910\times10^{-11}\).

Artifacts:

- `landau_zener_ara_crosswalk.py`
- `validate_landau_zener_ara_crosswalk.py`
- `LANDAU_ZENER_ARA_PATH.csv`
- `LANDAU_ZENER_ARA_OUTCOMES.csv`
- `LANDAU_ZENER_ARA_RESULTS.json`
- `LANDAU_ZENER_ARA_VALIDATION.json`

## 9. Evidence fence

**Exact established physics:** equations (1)–(5) under the specified Landau–Zener convention and ideal model.  
**Exact coordinate crosswalk:** both ARA coordinates are reversible rescalings of established populations.  
**Proposed ARA language:** Connection/Traversal orientation, singularity classification and recurrence across
other domains.  
**Not established:** a universal ARA transition law, a new quantum prediction, derivation of Landau–Zener physics
from ARA, or quantum gravity.

