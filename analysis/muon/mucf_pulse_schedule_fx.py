#!/usr/bin/env python3
r"""
mucf_pulse_schedule_fx.py
=========================

Numerical test of pulse-schedule dependence of the external-field overlap term
f_X in muon-catalysed fusion reactivation, following the framework of

    Kou & Chen, "External-Field-Assisted Muon Reactivation in Muon-Catalyzed
    Fusion: A Rate-Network Criterion for Reducing Alpha Sticking",
    arXiv:2606.07077.

Their decomposition:

    R_X = f_X * P_X * eta_X

    f_X   = space-time overlap between the external stripping field and the
            residual stuck (alpha-mu)+ population
    P_X   = microscopic stripping probability
    eta_X = probability the liberated muon rejoins the dt-mu fusion cycle

This script computes

    f_X = \int dt g(t) C(t)

for competing pulse schedules under MATCHED pulse count, pulse shape, peak
intensity and therefore total energy, exactly as the authors proposed.

--------------------------------------------------------------------------
WHAT IS BEING TESTED
--------------------------------------------------------------------------
The authors' correct objection: for a stationary Poisson arrival process with
identical non-overlapping pulses and matched count, the expected covered
fraction depends mainly on total temporal coverage, so REARRANGING the pulses
should not change mean f_X. Their stated exceptions are periodic/quasiperiodic
production structure, unknown cycle phase, pulse overlap, finite windows, and
correlated production.

They also noted, correctly, that for a KNOWN window and KNOWN pulse count,
uniformly spaced pulses already minimise the largest gap. The claimed
distinctive value of a golden-ratio (low-discrepancy) schedule is therefore
robustness when N or the phase is NOT fixed in advance.

This script tests exactly those claims, including the null.

--------------------------------------------------------------------------
NO FITTED PARAMETERS
--------------------------------------------------------------------------
Every schedule is generated from a closed form. The golden schedule uses
phi = (1+sqrt(5))/2 with no tuning. Nothing is optimised against the outcome
except the deliberately-advantaged 'uniform_opt' competitor, which is given
oracle knowledge of g(t) as an upper reference.

Author: Dylan La Franchi, July 2026.  Public domain / CC-BY-4.0.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

PHI = (1.0 + 5.0 ** 0.5) / 2.0
INV_PHI = 1.0 / PHI              # 0.6180339887498949

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# 1. Time grid and coverage
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Grid:
    """Normalised observation window [0, 1) discretised into `m` cells."""
    m: int = 200_000

    @property
    def dt(self) -> float:
        return 1.0 / self.m

    @property
    def t(self) -> np.ndarray:
        # cell centres
        return (np.arange(self.m) + 0.5) / self.m


def coverage(centres: np.ndarray, width: float, grid: Grid) -> np.ndarray:
    """
    Effective temporal coverage C(t) in [0, 1].

    Rectangular pulses of full width `width` (in window units), wrapped
    circularly so no schedule is penalised by edge truncation. Overlapping
    pulses do NOT accumulate above 1 -- overlap wastes energy, which is one of
    the mechanisms the authors listed.
    """
    m = grid.m
    c = np.zeros(m, dtype=np.float64)
    half = width / 2.0
    for t0 in centres:
        lo = int(math.floor((t0 - half) * m))
        hi = int(math.ceil((t0 + half) * m))
        idx = np.arange(lo, hi) % m
        c[idx] = 1.0
    return c


# ---------------------------------------------------------------------------
# 2. Schedules -- all closed form, matched count
# ---------------------------------------------------------------------------

def sched_periodic(n: int, phase: float = 0.0) -> np.ndarray:
    """Fixed period, fixed phase."""
    return np.mod((np.arange(n) + 0.5) / n + phase, 1.0)


def sched_golden(n: int, phase: float = 0.0) -> np.ndarray:
    """
    Low-discrepancy golden-ratio (Weyl) sequence.

    t_k = frac(k * 1/phi).  Every PREFIX of this sequence is near-uniform,
    which is the property that matters when n is not known in advance.
    """
    return np.mod(np.arange(n) * INV_PHI + phase, 1.0)


def sched_random(n: int, rng: np.random.Generator) -> np.ndarray:
    """i.i.d. uniform placements."""
    return rng.random(n)


def sched_jittered(n: int, rng: np.random.Generator, amp: float = 0.5) -> np.ndarray:
    """Periodic with uniform jitter of +/- amp * (1/n)."""
    base = (np.arange(n) + 0.5) / n
    return np.mod(base + (rng.random(n) - 0.5) * 2.0 * amp / n, 1.0)


def sched_uniform_opt(n: int, g: np.ndarray, width: float, grid: Grid,
                      n_scan: int = 512) -> np.ndarray:
    """
    ORACLE COMPETITOR. Evenly spaced pulses whose global phase is scanned to
    maximise f_X against the *known* g(t). This is the strongest schedule
    available to someone who knows the arrival distribution and the pulse
    count in advance -- i.e. the authors' 'uniformly optimised' case.
    """
    best_phase, best_f = 0.0, -1.0
    for j in range(n_scan):
        ph = j / n_scan / n
        f = f_x(g, coverage(sched_periodic(n, ph), width, grid), grid)
        if f > best_f:
            best_f, best_phase = f, ph
    return sched_periodic(n, best_phase)


# ---------------------------------------------------------------------------
# 3. Arrival densities g(t)
# ---------------------------------------------------------------------------

def normalise(g: np.ndarray, grid: Grid) -> np.ndarray:
    return g / (g.sum() * grid.dt)


def g_flat(grid: Grid, **_) -> np.ndarray:
    """Stationary Poisson intensity -- the authors' null. Golden must NOT win."""
    return normalise(np.ones(grid.m), grid)


def g_beam(grid: Grid, f_beam: float = 7.0, depth: float = 0.85,
           phase: float = 0.0, **_) -> np.ndarray:
    """
    Pulsed muon source: production modulated at the beam repetition frequency
    with unknown phase. f_beam is in cycles per observation window.
    """
    return normalise(1.0 + depth * np.cos(2 * np.pi * f_beam * grid.t + phase), grid)


def g_beam_cycle(grid: Grid, f_beam: float = 7.0, f_cycle: float = 23.0,
                 depth: float = 0.6, phase: float = 0.0, **_) -> np.ndarray:
    """
    Beam repetition AND catalytic cycling, incommensurate. Two-component
    quasiperiodic production -- the authors' second listed exception.
    """
    a = 1.0 + depth * np.cos(2 * np.pi * f_beam * grid.t + phase)
    b = 1.0 + depth * np.cos(2 * np.pi * f_cycle * grid.t + 1.7 * phase)
    return normalise(a * b, grid)


def g_decay_beam(grid: Grid, f_beam: float = 7.0, depth: float = 0.85,
                 phase: float = 0.0, tau: float = 0.45, **_) -> np.ndarray:
    """
    Realistic case: beam-modulated production under the muon decay envelope.
    tau is the muon lifetime in units of the observation window
    (tau_mu = 2.197 us; a 5 us window gives tau ~ 0.44).
    """
    env = np.exp(-grid.t / tau)
    mod = 1.0 + depth * np.cos(2 * np.pi * f_beam * grid.t + phase)
    return normalise(env * mod, grid)


ARRIVALS = {
    "poisson_flat":  g_flat,
    "beam_periodic": g_beam,
    "beam_x_cycle":  g_beam_cycle,
    "beam_decay":    g_decay_beam,
}


# ---------------------------------------------------------------------------
# 4. Objective
# ---------------------------------------------------------------------------

def f_x(g: np.ndarray, c: np.ndarray, grid: Grid) -> float:
    r"""f_X = \int dt g(t) C(t).  In [0, 1] because \int g = 1 and C <= 1."""
    return float((g * c).sum() * grid.dt)


# ---------------------------------------------------------------------------
# 5. Rate-network consequence (Kou & Chen numbers)
# ---------------------------------------------------------------------------

LAMBDA_MU = 4.55e5      # muon decay rate, s^-1
LAMBDA_C = 2.0e8        # catalytic cycle rate, s^-1 (unpolarised)
OMEGA_S0 = 0.0045       # bare alpha-sticking probability
R_COL = 0.0             # conventional collisional reactivation already applied
E_MU_GEV = 5.0          # energy cost per muon
E_FUS_MEV = 17.6        # per D-T fusion


def rate_network(f_x_value: float, p_x: float = 0.5, eta_x: float = 0.6) -> dict:
    """omega_s_eff = omega_s0 (1 - R_col)(1 - R_X);  X_mu;  Q."""
    r_x = f_x_value * p_x * eta_x
    omega_eff = OMEGA_S0 * (1.0 - R_COL) * (1.0 - r_x)
    x_mu = 1.0 / (LAMBDA_MU / LAMBDA_C + omega_eff)
    q = x_mu * E_FUS_MEV / (E_MU_GEV * 1000.0)
    return {"R_X": r_x, "omega_s_eff": omega_eff, "X_mu": x_mu, "Q": q}


# ---------------------------------------------------------------------------
# 6. Experiment
# ---------------------------------------------------------------------------

def run(n_pulses: int = 64,
        duty: float = 0.15,
        n_phase: int = 64,
        n_seed: int = 64,
        grid: Grid = Grid()) -> dict:
    """
    Matched comparison. Every schedule receives the same pulse count, the same
    rectangular pulse width, the same peak intensity, hence the same energy.

    For each arrival family the unknown production phase is swept over
    `n_phase` values; stochastic schedules are additionally averaged over
    `n_seed` seeds.
    """
    width = duty / n_pulses          # matched total coverage = duty
    out: dict = {
        "config": {
            "n_pulses": n_pulses, "duty": duty, "pulse_width": width,
            "n_phase": n_phase, "n_seed": n_seed, "grid_m": grid.m,
            "phi": PHI, "inv_phi": INV_PHI,
        },
        "arrivals": {},
    }

    for name, gfun in ARRIVALS.items():
        phases = np.linspace(0.0, 2 * np.pi, n_phase, endpoint=False)
        rows = {k: [] for k in
                ("periodic", "uniform_opt", "random", "jittered", "golden")}

        for ph in phases:
            g = gfun(grid, phase=float(ph))

            rows["periodic"].append(
                f_x(g, coverage(sched_periodic(n_pulses), width, grid), grid))
            rows["golden"].append(
                f_x(g, coverage(sched_golden(n_pulses), width, grid), grid))
            rows["uniform_opt"].append(
                f_x(g, coverage(sched_uniform_opt(n_pulses, g, width, grid),
                                width, grid), grid))

            rr, jj = [], []
            for s in range(n_seed):
                rng = np.random.default_rng(1_000_000 + s)
                rr.append(f_x(g, coverage(sched_random(n_pulses, rng), width, grid), grid))
                jj.append(f_x(g, coverage(sched_jittered(n_pulses, rng), width, grid), grid))
            rows["random"].append(float(np.mean(rr)))
            rows["jittered"].append(float(np.mean(jj)))

        stats = {}
        for k, v in rows.items():
            a = np.asarray(v)
            stats[k] = {
                "mean":   float(a.mean()),
                "std":    float(a.std()),
                "min":    float(a.min()),
                "p05":    float(np.percentile(a, 5)),
                "median": float(np.median(a)),
                "max":    float(a.max()),
            }
        out["arrivals"][name] = {"per_phase": rows, "stats": stats}

    # ---- prefix behaviour: the authors' 'N not fixed in advance' point ----
    prefix = {}
    for name, gfun in ARRIVALS.items():
        phases = np.linspace(0.0, 2 * np.pi, 16, endpoint=False)
        ns = list(range(4, n_pulses + 1, 2))
        per_curve, gold_curve = [], []
        for n in ns:
            w_n = duty / n                       # keep total duty matched at every n
            p_vals, g_vals = [], []
            for ph in phases:
                g = gfun(grid, phase=float(ph))
                p_vals.append(f_x(g, coverage(sched_periodic(n), w_n, grid), grid))
                g_vals.append(f_x(g, coverage(sched_golden(n_pulses)[:n], w_n, grid), grid))
            per_curve.append(float(np.mean(p_vals)))
            gold_curve.append(float(np.mean(g_vals)))
        prefix[name] = {"n": ns, "periodic": per_curve, "golden": gold_curve}
    out["prefix"] = prefix

    # ---- rate-network consequence for the realistic arrival family ----
    st = out["arrivals"]["beam_decay"]["stats"]
    out["rate_network"] = {
        sched: {
            "mean_case":  rate_network(st[sched]["mean"]),
            "worst_case": rate_network(st[sched]["p05"]),
        }
        for sched in st
    }
    return out


# ---------------------------------------------------------------------------
# 7. Self-checks
# ---------------------------------------------------------------------------

def selfcheck(grid: Grid = Grid()) -> list:
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"check": name, "passed": bool(ok), "detail": str(detail)})

    for name, gfun in ARRIVALS.items():
        g = gfun(grid, phase=0.3)
        chk(f"g normalised [{name}]", abs(g.sum() * grid.dt - 1.0) < 1e-9,
            g.sum() * grid.dt)
        chk(f"g non-negative [{name}]", bool((g >= 0).all()))

    n, duty = 64, 0.15
    w = duty / n
    for sname, s in (("periodic", sched_periodic(n)), ("golden", sched_golden(n))):
        c = coverage(s, w, grid)
        chk(f"coverage in [0,1] [{sname}]", bool(((c >= 0) & (c <= 1)).all()))
        chk(f"coverage ~ duty [{sname}]", abs(c.mean() - duty) < 5e-3, c.mean())

    g = g_flat(grid)
    fp = f_x(g, coverage(sched_periodic(n), w, grid), grid)
    fg = f_x(g, coverage(sched_golden(n), w, grid), grid)
    chk("NULL: flat arrivals give no golden advantage",
        abs(fp - fg) < 5e-3, f"periodic={fp:.6f} golden={fg:.6f}")

    chk("inv_phi value", abs(INV_PHI - 0.6180339887498949) < 1e-15, INV_PHI)
    chk("rate network monotone in f_X",
        rate_network(0.6)["Q"] > rate_network(0.1)["Q"])
    return checks


# ---------------------------------------------------------------------------
# 8. Figure (optional)
# ---------------------------------------------------------------------------

def figure(res: dict, path: Path) -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return False

    order = ["periodic", "uniform_opt", "random", "jittered", "golden"]
    names = list(ARRIVALS)
    fig, ax = plt.subplots(2, len(names), figsize=(4.4 * len(names), 8.2))

    for j, nm in enumerate(names):
        st = res["arrivals"][nm]["stats"]
        means = [st[k]["mean"] for k in order]
        lo = [st[k]["mean"] - st[k]["p05"] for k in order]
        cols = ["#8899aa"] * len(order)
        cols[order.index("golden")] = "#d4a843"
        cols[order.index("uniform_opt")] = "#4a9eff"
        ax[0, j].bar(order, means, yerr=[lo, [0] * len(order)],
                     color=cols, capsize=3)
        ax[0, j].set_title(f"{nm}\nmean f_X (bar to 5th pct)", fontsize=10)
        ax[0, j].tick_params(axis="x", rotation=40, labelsize=8)
        ax[0, j].set_ylim(0, 1)

        pf = res["prefix"][nm]
        ax[1, j].plot(pf["n"], pf["periodic"], label="periodic", color="#8899aa")
        ax[1, j].plot(pf["n"], pf["golden"], label="golden", color="#d4a843")
        ax[1, j].set_xlabel("pulses delivered so far (n)")
        ax[1, j].set_ylabel("mean f_X" if j == 0 else "")
        ax[1, j].set_title("prefix behaviour (N not known in advance)", fontsize=9)
        ax[1, j].legend(fontsize=8)

    fig.suptitle("Pulse-schedule dependence of f_X in muon reactivation "
                 "(matched pulse count, width, peak, energy)", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return True


# ---------------------------------------------------------------------------
# 9. Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("running matched-schedule f_X comparison ...")
    res = run()
    res["selfcheck"] = selfcheck()

    n_fail = sum(1 for c in res["selfcheck"] if not c["passed"])
    res["selfcheck_summary"] = {
        "total": len(res["selfcheck"]), "failed": n_fail,
        "status": "PASS" if n_fail == 0 else "FAIL",
    }

    (HERE / "MUCF_PULSE_SCHEDULE_FX_RESULTS.json").write_text(
        json.dumps(res, indent=2), encoding="utf-8")

    rows = ["arrival,schedule,mean_fX,p05_fX,std_fX"]
    for nm, blk in res["arrivals"].items():
        for k, s in blk["stats"].items():
            rows.append(f'{nm},{k},{s["mean"]:.6f},{s["p05"]:.6f},{s["std"]:.6f}')
    (HERE / "MUCF_PULSE_SCHEDULE_FX_SUMMARY.csv").write_text(
        "\n".join(rows), encoding="utf-8")

    made = figure(res, HERE / "MUCF_PULSE_SCHEDULE_FX.png")

    print(f"\nself-checks: {res['selfcheck_summary']['status']} "
          f"({len(res['selfcheck']) - n_fail}/{len(res['selfcheck'])})")
    for c in res["selfcheck"]:
        if not c["passed"]:
            print("  FAILED:", c["check"], c["detail"])

    print("\nmean f_X (matched count / width / peak / energy)")
    hdr = f'{"arrival":<15}' + "".join(f"{k:>13}" for k in
          ("periodic", "uniform_opt", "random", "jittered", "golden"))
    print(hdr)
    for nm, blk in res["arrivals"].items():
        s = blk["stats"]
        print(f"{nm:<15}" + "".join(
            f'{s[k]["mean"]:>13.5f}' for k in
            ("periodic", "uniform_opt", "random", "jittered", "golden")))

    print("\nworst case over unknown production phase (5th percentile)")
    print(hdr)
    for nm, blk in res["arrivals"].items():
        s = blk["stats"]
        print(f"{nm:<15}" + "".join(
            f'{s[k]["p05"]:>13.5f}' for k in
            ("periodic", "uniform_opt", "random", "jittered", "golden")))

    print("\nrate-network consequence, beam_decay arrivals "
          "(P_X = 0.5, eta_X = 0.6, omega_s0 = 0.0045)")
    print(f'{"schedule":<14}{"case":<8}{"R_X":>9}{"omega_eff":>12}{"X_mu":>9}{"Q":>8}')
    for sched, blk in res["rate_network"].items():
        for case, r in blk.items():
            print(f'{sched:<14}{case:<8}{r["R_X"]:>9.4f}{r["omega_s_eff"]:>12.6f}'
                  f'{r["X_mu"]:>9.1f}{r["Q"]:>8.3f}')

    print("\nwrote RESULTS.json, SUMMARY.csv" + (", PNG" if made else " (no matplotlib)"))


if __name__ == "__main__":
    main()
