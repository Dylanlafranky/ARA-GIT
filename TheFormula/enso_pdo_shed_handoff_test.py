"""Test Dylan's 0.382 handoff: at the green/gold pump, gold engine sheds 1/phi^2 (0.382) to PDO,
keeps 1/phi. So PDO should = cumulative leaky integral of ENSO gold-engine shed (ENSO->PDO downstream).
Strict-causal. Real NINO3.4 1870+ & ERSST PDO.

Formalization: gold engine = causal_bandpass(NINO,55mo); energy E=amp^2; shed flux=max(0,-dE/dt);
PDO_recon = leaky-integrate(0.382*sign(NINO)*shed, tau). Test corr + lead/lag; free-fit shed fraction.

RESULT (NOT supported):
 - signed recon peaks r~0.26 but pins at +60mo lag boundary (artifact); unsigned ~0.
 - shed fraction f is correlation-scale-invariant (corr flat -0.248 for f=0.2..0.6) -> 0.382 not
   identifiable from correlation.
 - DECISIVE: lead/lag runs WRONG way for a handoff. low-pass NINO vs PDO peaks at lag -5..-15
   (PDO LEADS/simultaneous, NOT ENSO leading PDO). Plain low-pass NINO (+0.49) beats the shed recon.
 => 0.382 ENSO->PDO energy handoff unsupported. Consistent with PDO = slow background partner
    (contemporaneous corr +0.41, PDO slightly leads), NOT a downstream sink. Logic in /tmp run.
"""
