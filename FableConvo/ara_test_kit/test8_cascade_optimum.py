"""
TEST 8 — MULTI-STAGE CASCADE OPTIMUM (pure engineering; nothing gated)
=======================================================================
PRE-REGISTERED (2 Jul 2026): compare plateau-spacing rules for a multi-stage
hydride cascade with REAL per-stage costs:
  A) golden-ratio spacing (each stage's plateau pressure = phi x previous)
  B) equal-log spacing (geometric, ratio = (P_out/P_in)^(1/n))
  C) status quo (2-3 stages, literature designs)
OUTCOMES: A wins -> the framework's first engineering prediction with
commercial relevance. B wins -> the octave/log family takes another round.
C wins -> per-stage taxes dominate; the "headroom" claim of the battery doc
Section 13 dies honestly.
MODEL: per-stage efficiency = (1 - hysteresis_loss(stage)) * (1 - thermal_tax).
Hysteresis loss per stage ~ (1/2)*ln(Pa/Pd) fraction of stage work (edit with
sourced ln(Pa/Pd) values per alloy family). Total = product over stages, for a
fixed overall compression P_in -> P_out on a fixed temperature swing.
EDIT THE PARAMETER TABLE with your sourced numbers before trusting output.
"""
import numpy as np

# ---------------- PARAMETERS (edit with sourced values) ----------------
P_IN, P_OUT = 12.0, 200.0        # bar, the real 3-stage benchmark span
HYST_LN = {                       # ln(Pa/Pd) hysteresis by alloy family (sourced!)
    "AB5":  0.10,                 # LaNi5-class, narrow loop  (placeholder)
    "AB2":  0.13,                 # Ti-Cr-Mn-Fe, low-modest   (placeholder)
    "AB":   0.35,                 # plain TiFe, large 2-step  (placeholder)
}
FAMILY = "AB2"                    # assume ladder built from one family
THERMAL_TAX = 0.03                # per-stage thermal-management overhead (edit)
R_T = 0.055                       # RT/DeltaH-ish work scale factor (edit)
# ------------------------------------------------------------------------

PHI = (1 + 5**0.5) / 2

def stage_ratios(rule, n):
    total = P_OUT / P_IN
    if rule == "equal-log":
        return [total ** (1 / n)] * n
    if rule == "golden":
        # golden-weighted: ratios r, r*phi^0 ... normalized so product = total
        w = np.array([PHI ** i for i in range(n)])
        return list(total ** (w / w.sum()))
    raise ValueError(rule)

def efficiency(rule, n):
    eff = 1.0
    for r in stage_ratios(rule, n):
        work = np.log(r)                       # ideal isothermal work ~ ln(r)
        hyst = HYST_LN[FAMILY] * R_T / max(work, 1e-9)   # loop area / stage work
        hyst = min(hyst, 0.95)
        eff *= (1 - hyst) * (1 - THERMAL_TAX)
    return eff

def main():
    print(f"span {P_IN}->{P_OUT} bar, family {FAMILY} (ln Pa/Pd = {HYST_LN[FAMILY]}), "
          f"thermal tax {THERMAL_TAX}/stage")
    print(f"{'n stages':>9} | {'equal-log':>10} {'golden':>10}")
    best = {}
    for n in range(1, 13):
        el, go = efficiency("equal-log", n), efficiency("golden", n)
        for k, v in (("equal-log", el), ("golden", go)):
            if k not in best or v > best[k][1]:
                best[k] = (n, v)
        print(f"{n:>9} | {el:>10.4f} {go:>10.4f}")
    print(f"\noptima: equal-log n*={best['equal-log'][0]} eff={best['equal-log'][1]:.4f} | "
          f"golden n*={best['golden'][0]} eff={best['golden'][1]:.4f}")
    print("status quo benchmark: n=3 equal-log =", f"{efficiency('equal-log',3):.4f}")
    print("\nHONEST FENCES: placeholder hysteresis values MUST be replaced with")
    print("sourced ln(Pa/Pd) per alloy; thermal tax is a guess; the hysteresis/")
    print("work model is first-order. The COMPARISON between rules is the claim,")
    print("not the absolute efficiencies. If golden != equal-log by less than")
    print("the parameter uncertainty, report 'indistinguishable' — that is the")
    print("crowded-neighborhood rule applied to engineering.")

if __name__ == "__main__":
    main()
