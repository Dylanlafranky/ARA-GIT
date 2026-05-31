#!/usr/bin/env python3
"""
Precision-systems action-ladder test  (clean-data check on the atlas screen)
============================================================================
Same action variable as the atlas (J/pi = E*T/pi, the classical KAM action), but
every E and T is INDEPENDENTLY SOURCED and CITED. We pit five ladder bases against
each system's OWN shuffle null with a fitted phase offset (fair to all bases):
octave(2), tri-harmonic(2^1/3), bi/sqrt2(2^1/2), phi, e.

HONEST RESULT (2026-05-30)
--------------------------
* Full set incl. a built-in H n=1..4 ladder: tri-harmonic z=-3.25, p=0.0024.
  -> NOT TRUSTWORTHY. The four consecutive hydrogen levels are a DETERMINISTIC
     integer-hbar (Bohr-Sommerfeld) ladder we fed in. That ladder, not the
     independent systems, drives the signal. Classic input-leakage.
* Leak-check (planets + Moon only, n=7, no built-in ladder): NOTHING significant.
  octave p=0.20, tri p=0.24, sqrt2 p=0.094 (weak best), phi p=0.47.
* Adding one H n=1 anchor (n=8): still nothing significant (tri p=0.084).

CONCLUSION: on honestly independent data the action-ladder does not reach
significance for octave OR tri-harmonic. Only ~7 truly independent precision
systems exist at these scales, too few to power the test without circular inputs.
This route is a weak shore-up; prefer the blind-prediction stack and the phi
ablation. Kept for the record + reproducibility.

HONESTY NOTES baked in:
- Quantum oscillators have E=h*nu, T=1/nu -> E*T=h degenerate (Cs clock = one rung).
- The choice of "characteristic E and T" per system is a stated modelling decision.
"""
import math, numpy as np

hbar = 1.054571817e-34      # J s   CODATA 2018
h    = 6.62607015e-34       # J s   SI exact
G    = 6.67430e-11          # CODATA
Msun = 1.98892e30           # kg
Ry_J = 2.1798723611e-18     # J     Rydberg energy (CODATA) = H ionization
T_bohr = 1.519829e-16       # s     H(1s) classical orbital period (Bohr model)

# Each entry: name, T_seconds, E_joules, source, note
SYS = [
 # --- quantum bound states: Bohr-Sommerfeld, J_n = n*hbar (textbook) ---
 ("H atom n=1", T_bohr*1**3, Ry_J/1**2, "CODATA Rydberg + Bohr period", "J=1 hbar"),
 ("H atom n=2", T_bohr*2**3, Ry_J/2**2, "Bohr scaling T~n^3, E~1/n^2", "J=2 hbar"),
 ("H atom n=3", T_bohr*3**3, Ry_J/3**2, "Bohr scaling", "J=3 hbar"),
 ("H atom n=4", T_bohr*4**3, Ry_J/4**2, "Bohr scaling", "J=4 hbar"),
 # --- atomic clock: E=h*nu, T=1/nu -> E*T=h degenerate (kept to show collapse) ---
 ("Cs-133 hyperfine", 1/9.192631770e9, h*9.192631770e9, "SI second definition", "E*T=h exactly"),
 # --- planetary orbits: E_orb = G*Msun*m/(2a); T,a,m from NASA fact sheets ---
 ("Mercury orbit", 7.6005e6,  G*Msun*3.301e23 /(2*5.7909e10), "NASA Mercury fact sheet", "a=0.387AU"),
 ("Earth orbit",   3.1558e7,  G*Msun*5.972e24 /(2*1.4960e11), "NASA Earth fact sheet",   "a=1AU"),
 ("Mars orbit",    5.9354e7,  G*Msun*6.417e23 /(2*2.2794e11), "NASA Mars fact sheet",    "a=1.524AU"),
 ("Jupiter orbit", 3.7434e8,  G*Msun*1.898e27 /(2*7.7857e11), "NASA Jupiter fact sheet", "a=5.20AU"),
 ("Saturn orbit",  9.2935e8,  G*Msun*5.683e26 /(2*1.4335e12), "NASA Saturn fact sheet",  "a=9.58AU"),
 ("Neptune orbit", 5.2005e9,  G*Msun*1.024e26 /(2*4.4951e12), "NASA Neptune fact sheet", "a=30.05AU"),
 ("Moon orbit", 2.3606e6, G*5.972e24*7.342e22/(2*3.844e8), "NASA Moon fact sheet", "Earth-Moon"),
]

actions = np.array([T*E/math.pi for _,T,E,_,_ in SYS])

BASES = {"octave (2.000)":2.0, "tri-harm (1.260)":2**(1/3),
         "bi/sqrt2 (1.414)":2**0.5, "phi (1.618)":(1+5**0.5)/2, "e (2.718)":math.e}
OG=np.linspace(0,1,120,endpoint=False); N=20000; rng=np.random.default_rng(42)

def best(lv):
    ph=np.mod(lv[None,:]-OG[:,None],1.0); return np.minimum(ph,1-ph).mean(1).min()
def nullmat(draws):
    b=np.full(draws.shape[0],1.0)
    for o in OG:
        ph=np.mod(draws-o,1.0); b=np.minimum(b,np.minimum(ph,1-ph).mean(1))
    return b
def test(acts,base):
    lv=np.log(acts)/math.log(base); rm=best(lv)
    nm=nullmat(rng.uniform(lv.min(),lv.max(),(N,len(lv))))
    mu,sd=nm.mean(),nm.std(); z=(rm-mu)/sd; p=(np.sum(nm<=rm)+1)/(N+1)
    return rm,mu,z,p

if __name__ == "__main__":
    print(f"n = {len(SYS)} precision systems, all T and E independently sourced")
    print(f"action/pi log10 span: {math.log10(actions.max())-math.log10(actions.min()):.1f}\n")
    print(f"{'base':18s}{'mean-d':>9s}{'chance':>9s}{'z':>8s}{'p':>9s}  verdict")
    print("-"*62)
    rows=[(name,)+test(actions,b) for name,b in BASES.items()]
    bestrow=min(rows,key=lambda r:r[3])
    for name,rm,mu,z,p in rows:
        v="tighter than chance" if p<0.05 else ""
        if name==bestrow[0]: v+="  <-- best (BUT SEE LEAK NOTE IN DOCSTRING)"
        print(f"{name:18s}{rm:9.4f}{mu:9.4f}{z:8.2f}{p:9.4f}  {v}")
    print("\nLEAK-CHECK: drop the built-in H ladder -> nothing significant. See docstring.")
