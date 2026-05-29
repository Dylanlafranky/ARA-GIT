#!/usr/bin/env python3
"""
Action-spectrum ladder null test (KAM Route 3, screening pass)
===============================================================

Question: do the mapped systems' action/pi values sit on an OCTAVE (x2) rung
ladder more than chance would give, and does octave beat phi / sqrt2 / e / 3 as
the ladder base?

This is the framework's corrected structural claim (rung SPACING = octave x2;
phi lives only in the coupling), tested in ACTION space (T*E/pi = the classical
action variable, the quantity KAM theory organises into a fractal rung
structure). If octave structure beats chance here, it ties the mapping to the
proven KAM action-space picture.

HONEST DATA CAVEAT
------------------
All action_pi values in the atlas trace to ONE archived early visualization, so
the per-system energies are hand-curated, NOT independently sourced, and they
span ~87 orders of magnitude (log10). This is therefore a SCREENING pass, not a
publishable result. A real KAM test needs independently-sourced T and E for a
small set of precision systems (see RECOMMENDED list printed at the end).

METHOD (strict, fair null)
--------------------------
For a candidate ladder base b:
  * rung phase of an action value a:  ph = frac( log_b(a) - offset )
  * rung distance:                    d  = min(ph, 1-ph)  in [0, 0.5]
  * a tight ladder => mean(d) well below the random expectation 0.25.
  * the zero-point `offset` is a free parameter, so we FIT it (grid) to minimise
    mean(d) for the real data -- AND we give the null the same free parameter
    (the offset is re-fit on every shuffle). Otherwise the real data would get a
    fitted knob the null does not, inflating significance.
Null: redraw the action values uniformly in log over the OBSERVED log range,
re-fit offset, recompute mean(d); repeat N times. z and p come from each base's
OWN null, so denser ladders (smaller b) do not get an unfair edge -- we compare
bases by how far each beats its own chance level, not by raw mean(d).

No framework constant is used to build the null. Bases are fixed before running.
"""
import json, math, sys
import numpy as np

BASES = {
    "sqrt2 (1.414)": math.sqrt(2),
    "phi (1.618)": (1 + 5 ** 0.5) / 2,
    "octave (2.0)": 2.0,
    "e (2.718)": math.e,
    "base 3.0": 3.0,
}
N_NULL = 5000
OFFSET_GRID = np.linspace(0, 1, 60, endpoint=False)
SEED = 42


def best_offset_meand(log_vals_base):
    """Minimise mean rung-distance over the offset grid; return (best_mean, best_offset)."""
    # log_vals_base: 1-D
    ph = np.mod(log_vals_base[None, :] - OFFSET_GRID[:, None], 1.0)  # (G, n)
    d = np.minimum(ph, 1.0 - ph).mean(axis=1)                       # (G,)
    j = int(np.argmin(d))
    return float(d[j]), float(OFFSET_GRID[j])


def _meand_matrix(draws):
    """draws: (N, n) -> for each row, min over offsets of mean rung-distance. Returns (N,)."""
    N, n = draws.shape
    best = np.full(N, 1.0)
    for off in OFFSET_GRID:
        ph = np.mod(draws - off, 1.0)
        d = np.minimum(ph, 1.0 - ph).mean(axis=1)
        best = np.minimum(best, d)
    return best


def test_base(actions, base, rng):
    log_vals = np.log(actions) / math.log(base)
    real_mean, real_off = best_offset_meand(log_vals)

    lo, hi = log_vals.min(), log_vals.max()
    n = len(log_vals)
    draws = rng.uniform(lo, hi, size=(N_NULL, n))
    null_means = _meand_matrix(draws)
    mu, sd = null_means.mean(), null_means.std()
    z = (real_mean - mu) / sd if sd > 0 else 0.0  # negative z = tighter than chance = good
    p = (np.sum(null_means <= real_mean) + 1) / (N_NULL + 1)  # one-sided: as tight or tighter
    return {
        "base": base,
        "real_mean_d": real_mean,
        "fitted_offset": real_off,
        "null_mean_d": mu,
        "null_sd": sd,
        "z": z,
        "p_one_sided": p,
    }


def run(actions, label, rng):
    actions = np.asarray([a for a in actions if a is not None and a > 0], float)
    print(f"\n================  {label}  (n={len(actions)})  ================")
    print(f"action/pi log10 span: {math.log10(actions.max())-math.log10(actions.min()):.1f}")
    rows = []
    for name, b in BASES.items():
        r = test_base(actions, b, rng)
        rows.append((name, r))
    print(f"\n{'base':14s} {'real mean-d':>11s} {'chance':>8s} {'z':>7s} {'p':>9s}  verdict")
    print("-" * 64)
    best = min(rows, key=lambda x: x[1]["z"])
    for name, r in rows:
        verdict = ""
        if r["p_one_sided"] < 0.05:
            verdict = "tighter than chance"
        if name == best[0]:
            verdict += "  <-- best"
        print(f"{name:14s} {r['real_mean_d']:11.4f} {r['null_mean_d']:8.4f} "
              f"{r['z']:7.2f} {r['p_one_sided']:9.4f}  {verdict}")
    return {label: {name: r for name, r in rows}}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "ara_mapping_atlas_data.json"
    d = json.load(open(path))
    nodes = [n for n in d["nodes"] if n.get("action_pi") not in (None, "")]
    rng = np.random.default_rng(SEED)

    out = {}
    # 1) full set
    allact = [n["action_pi"] for n in nodes]
    out.update(run(allact, "ALL mapped systems", rng))

    # 2) within clean 0..2 ARA band only (drop the flagged overflow/snap nodes)
    band = [n["action_pi"] for n in nodes
            if isinstance(n.get("ara"), (int, float)) and 0.0 < n["ara"] < 2.0]
    out.update(run(band, "ARA in clean 0..2 band", rng))

    # 3) one dense scale domain at a time (cross-domain mixing can wash structure)
    import collections
    bydom = collections.defaultdict(list)
    for n in nodes:
        bydom[n.get("scale_domain", "?")].append(n["action_pi"])
    for dom, acts in sorted(bydom.items(), key=lambda x: -len(x[1])):
        if len(acts) >= 12:
            out.update(run(acts, f"domain: {dom}", rng))

    json.dump(out, open("action_ladder_null_result.json", "w"), indent=1, default=float)
    print("\nWrote action_ladder_null_result.json")
    print("\nNOTE: energies are single-source/hand-curated -> SCREENING ONLY.")
    # end


if __name__ == "__main__":
    main()
