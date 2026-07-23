# Virial ARA cross-scale ladder: planetary motion to quantum hydrogen

**Date:** 23 July 2026  
**Status:** exact established-physics crosswalk under declared ideal assumptions  
**Question:** Can one frozen ARA relation be carried from a planetary orbit down to quantum hydrogen without
changing its mathematical meaning?

## Technical summary

Yes, for the deliberately restricted family of **bound inverse-distance systems**. Classical gravity and the
ideal Coulomb Hamiltonian both use a potential proportional to \(-1/r\). The established virial theorem then gives

\[
\underbrace{2\langle T\rangle}_{\substack{\text{twice mean kinetic energy}\\
\text{ARA: Traversal channel }R}}
=
\underbrace{-\langle V\rangle}_{\substack{\text{magnitude of mean binding energy}\\
\text{ARA: Connection channel }C}}.
\tag{1}
\]

**Plain explanation.** Over a sufficiently complete bound-system measurement, twice the average movement energy
equals the magnitude of the average binding energy. The system does not have to stop. Its two accumulated accounts
balance.

Define the Traversal-oriented virial ARA coordinate

\[
\boxed{
\underbrace{x_{\rm vir}}_{\substack{\text{plain ARA position}\\\text{on the declared }0\text{--}2\text{ diameter}}}
=
2\,
\frac{
\underbrace{R}_{\substack{2\langle T\rangle\\\text{Traversal}}}
}{
\underbrace{C}_{\substack{|\langle V\rangle|\\\text{Connection}}}
+
\underbrace{R}_{\substack{2\langle T\rangle\\\text{Traversal}}}
}.
}
\tag{2}
\]

Equation (1) makes \(C=R\), so equation (2) gives \(x_{\rm vir}=1\) on every rung tested.

**Plain explanation.** The ARA ridge is not inserted after seeing the result. The physical theorem supplies the
factor of two that puts the two independently named channels into common units. Once compared on that ruler, they
meet at the \(1.0\) ridge.

The same systems also have a different, raw energy-allocation view:

\[
\underbrace{t_T}_{\substack{\text{Traversal amount}\\\text{inside TE-ARA}}}
=
\frac{2\langle T\rangle}{\langle T\rangle+|\langle V\rangle|}
=\frac23,
\qquad
\underbrace{t_C}_{\substack{\text{Connection amount}\\\text{inside TE-ARA}}}
=
\frac{2|\langle V\rangle|}{\langle T\rangle+|\langle V\rangle|}
=\frac43,
\qquad
t_T+t_C=2.
\tag{3}
\]

**Plain explanation.** The raw energy budget is still asymmetric: one third of its magnitude is kinetic and two
thirds is binding. After normalizing the whole account to TE-ARA \(2\), those become \(2/3\) and \(4/3\).
Equation (2) asks a different question: whether the *virial-weighted* movement and binding channels balance.
Keeping these two measurements separate prevents a false flattening.

## Where the four rungs sit on ARA

The physical length scale changes by

\[
\log_{10}\!\left(\frac{1\ {\rm AU}}{a_0}\right)=21.4513
\]

orders of magnitude, but the declared virial coordinate remains at the same ridge:

```text
Connection pole                 equal virial ridge                 Traversal pole
      0                                  1.0                              2
      |-----------------------------------|--------------------------------|

Planetary: Earth–Sun            ─────────●─────────   x_vir = 1
Satellite: circular reference   ─────────●─────────   x_vir = 1
Classical Coulomb at a₀         ─────────●─────────   x_vir = 1
Quantum hydrogen 1s             ─────────●─────────   x_vir = 1

Scale direction:     planetary  →  satellite  →  Coulomb  →  quantum
Raw TE-ARA on every rung:       Traversal = 2/3; Connection = 4/3; total = 2
```

This picture displays the **virial comparison coordinate**. The TE-ARA values underneath it are component
amounts, not two extra locations on that same diameter.

## Two-column physics–ARA ladder

| Established physics equation | ARA math and version |
|---|---|
| **1. Planetary — Earth–Sun.** For a Newtonian bound orbit of semimajor axis \(a\): \(\langle T\rangle=GM_\odot M_\oplus/(2a)\), \(\langle V\rangle=-GM_\odot M_\oplus/a\). | **Parent across a completed orbit.** \(C=|\langle V\rangle|\), \(R=2\langle T\rangle\), hence \(x_{\rm vir}=2R/(C+R)=1\). The instantaneous orbital children can move to either side while the completed parent account sits at the ridge. |
| **2. Satellite — ideal circular 7000 km geocentric reference.** Per unit satellite mass, \(T=\mu_\oplus/(2r)\) and \(V=-\mu_\oplus/r\). | **Local circle already on the ridge.** \(C=|V|=R=2T\), so \(x_{\rm vir}=1\) at every point of the ideal circular orbit, rather than only after time averaging. |
| **3. Classical Coulomb comparison at the Bohr radius.** \(T=k_e e^2/(2a_0)=E_h/2\) and \(V=-k_e e^2/a_0=-E_h\). | **Same relation, different physical identity.** The interaction changes from gravitational mass to electric charge, but \(C:R\), \(x_{\rm vir}=1\), and the raw \(2/3:4/3\) allocation remain unchanged. This is a comparison model, not a classical description of the real hydrogen electron. |
| **4. Quantum hydrogen 1s.** In the ideal nonrelativistic Coulomb Hamiltonian, \(\langle T\rangle=E_h/2\) and \(\langle V\rangle=-E_h\). | **Expectation-value ridge.** \(C=|\langle V\rangle|\) and \(R=2\langle T\rangle\) give \(x_{\rm vir}=1\). This is a relation between quantum expectation values—not an electron completing a classical orbit. |

## The planetary child moves while the parent approaches the ridge

For an elliptical Kepler orbit, use the vis-viva relation at instantaneous radius \(r\):

\[
\underbrace{C(r)}_{\substack{\text{instantaneous binding}\\\text{Connection child}}}
=
\frac{GMm}{r},
\qquad
\underbrace{R(r)}_{\substack{\text{twice instantaneous kinetic}\\\text{Traversal child}}}
=
2GMm\left(\frac1r-\frac1{2a}\right).
\tag{4}
\]

**Plain explanation.** Near perihelion the moving child is more Traversal-heavy; near aphelion it is more
Connection-heavy. Those local readings are real and should not be erased.

For Earth's eccentricity \(e=0.01671123\), the instantaneous virial ARA range is

\[
0.9915739804
\le x_{\rm vir}(t)\le
1.0082863772.
\tag{5}
\]

The completed channel averages nevertheless satisfy equation (1), giving

\[
\underbrace{x_{\rm vir}^{\rm parent}}_{\substack{\text{coordinate formed from}\\
\text{completed mean channels}}}
=1.
\tag{6}
\]

**Plain explanation.** The planet never settles or stops. The *measurement* settles as it incorporates a complete
cycle. This is the rigorous version of the early rock intuition: a parent can look ridge-stable while its children
remain active, provided the boundary and time grain are declared.

## What the cross-scale result establishes

1. **One frozen coordinate works on all four rungs.** No ARA constant was refitted between gravitation,
   classical electromagnetism and quantum expectation values.
2. **The same normalized result survives more than 21 orders of spatial scale.**
3. **Plain ARA and TE-ARA remain distinguishable.** The virial coordinate is \(1\); the raw total-2 allocation is
   \(2/3+4/3=2\).
4. **The classical-to-quantum bridge is exact within the ideal Coulomb model.** Classical orbit language is not
   imported into the quantum row.
5. **The parent ridge does not imply dead children.** A complete average can be balanced while local dynamics
   remain asymmetric.

## Evidence fence

This is substantial evidence for the **scale consistency of a declared ARA crosswalk**, but it is not new physics
by itself. Standard mechanics already predicts the repetition because all four examples share a homogeneous
inverse-distance potential and the virial theorem. The result does not prove:

- that every physical system has the same virial coordinate;
- that ARA derives gravity, Coulomb's law or quantum mechanics;
- that the classical electron orbit is physically real;
- universal fractality, quantum gravity or a new force;
- that every apparent \(1.0\) measurement is virial equilibrium.

Driven, dissipative, unbound, relativistic, many-body and non-homogeneous systems can require pressure, surface,
time-derivative or other boundary terms. Those failures are the next useful controls rather than exceptions to
hide.

## Validation

`validate_virial_cross_scale_ladder.py` passed **13/13** checks:

- exact inverse-distance virial equality on all four rungs;
- exact \(x_{\rm vir}=1\);
- exact TE-ARA closure and asymmetric \(2/3:4/3\) allocation;
- classical/quantum ideal-Coulomb energy agreement;
- a \(21.4513\)-order spatial ladder;
- independently derived perihelion and aphelion endpoints;
- completed Earth-orbit channel closure at \(1.0000000000000002\);
- normalization invariance over 60 synthetic energy decades;
- 10,000 independent coordinate-identity checks;
- explicit confirmation that raw allocation and virial position were not merged.

Reproduction:

```powershell
cd F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\virial
python virial_cross_scale_ladder.py
python validate_virial_cross_scale_ladder.py
```

Generated evidence:

- `VIRIAL_CROSS_SCALE_LADDER.csv`
- `VIRIAL_ARA_MARKERS.csv`
- `EARTH_ORBIT_VIRIAL_ARA.csv`
- `VIRIAL_CROSS_SCALE_RESULTS.json`
- `VIRIAL_CROSS_SCALE_VALIDATION.json`
- `VIRIAL_CROSS_SCALE_REPORT_ARTIFACT.json`

## Next discriminating test

Freeze the general homogeneous-potential relation

\[
2\langle T\rangle=k\langle V\rangle
\quad\text{for}\quad
V(\lambda r)=\lambda^kV(r),
\tag{7}
\]

then test several \(k\) values plus an open or driven system where the simple \(1.0\) inverse-distance ridge should
fail. The valuable ARA question is whether a frozen residual/Other decomposition can correctly identify the
missing boundary, pressure or driving term without being retuned after the outcome is known.

