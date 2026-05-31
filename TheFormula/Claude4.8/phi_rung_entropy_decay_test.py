#!/usr/bin/env python3
"""
Per-phi-rung predictability / entropy decay test.

Claim under test (Dylan, 2026-05-30):
  Space packs in octaves (ratio 2). Time packs in phi (ratio 1.618).
  The shortfall 2 - phi = 1/phi^2 = 0.382 is "packet loss" / entropy.
  1/phi + 1/phi^2 = 1  ->  per phi-rung of forward time the signal should
  FORWARD ~1/phi = 0.618 of its information and SHED ~1/phi^2 = 0.382.

So: as the forecast horizon multiplies by phi, retained predictability
should fall to ~0.618 of the previous rung.

Two independent measures, both model-free, on REAL data:
  (A) Linear autocorrelation envelope rho(h)  -- the skill a persistence/AR
      forecaster gets at horizon h (no train/test leakage; rho(h) IS that skill).
  (B) Auto-mutual-information I(x_t ; x_{t+h})  -- the ENTROPY measure:
      I(h) = H(future) - H(future | past) = entropy the past removes from the
      future. Always >= 0, captures nonlinear structure, this is "actual entropy".

For each system, sample the measure at phi-spaced rungs h_n = h0 * phi^n inside
the decaying regime, compute retention ratio M(h_{n+1})/M(h_n), and compare its
geometric mean to 1/phi = 0.618.

Key honesty point: constant per-rung retention <=> power-law decay in h
(exponent = log_phi(retention); retention 0.618 <=> exponent -1). Ordinary
systems decay EXPONENTIALLY, which gives a per-rung retention that shrinks with
h. So "constant retention" is itself a real test, and "constant AND ~0.618" is a
second, separate result. We fit both models and report which wins.

Data (all real, public):
  ENSO  : NOAA Nino3.4 monthly anomaly 1870+  (nino34_long_anom.csv)
  Solar : SILSO monthly total sunspot number 1749+ (fetched SN_m_tot.csv)
  ECG   : PhysioNet nsrdb RR-interval series (per-beat), via wfdb
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
import numpy as np

PHI = (1.0 + 5.0**0.5) / 2.0
INV_PHI = 1.0 / PHI           # 0.6180339887  (forwarded fraction)
INV_PHI2 = 1.0 / PHI**2       # 0.3819660113  (shed fraction / entropy)
HERE = Path(__file__).resolve().parent
RNG = np.random.default_rng(7)

# ---------------------------------------------------------------------------
# Model-free measures
# ---------------------------------------------------------------------------

def autocorr_envelope(x, max_h):
    """Linear lagged autocorrelation rho(h), and its running |envelope|.
    rho(h) is exactly the correlation a persistence forecast achieves at lag h."""
    x = np.asarray(x, float)
    x = x - x.mean()
    n = len(x)
    var = np.dot(x, x) / n
    rho = np.empty(max_h + 1)
    for h in range(max_h + 1):
        rho[h] = np.dot(x[:n-h], x[h:]) / ((n - h) * var)
    return rho


def _equiprob_bins(v, B):
    """Assign each value to one of B equiprobable (quantile) bins."""
    ranks = np.argsort(np.argsort(v))
    return (ranks * B // len(v)).astype(int)


def mutual_information(a, b, B=8):
    """Discrete MI (nats) of two equal-length series via equiprobable binning,
    with Miller-Madow bias correction. Equiprobable bins fix marginals ~log B."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    n = len(a)
    ai = _equiprob_bins(a, B); bi = _equiprob_bins(b, B)
    joint = np.bincount(ai * B + bi, minlength=B*B).astype(float).reshape(B, B)
    joint /= n
    px = joint.sum(1); py = joint.sum(0)
    def H(p):
        p = p[p > 0]
        return -np.sum(p * np.log(p))
    Hx, Hy, Hxy = H(px), H(py), H(joint)
    mi = Hx + Hy - Hxy
    # Miller-Madow: bias of entropy ~ -(occupied_bins - 1)/(2n)
    mm = ((np.count_nonzero(px) - 1) + (np.count_nonzero(py) - 1)
          - (np.count_nonzero(joint) - 1)) / (2.0 * n)
    return mi + mm


def ami_curve(x, lags, B=8, n_shuffle=20):
    """Auto-mutual-information I(x_t ; x_{t+h}) for each h in lags, with a
    shuffle-derived noise floor (mean + 2 sd of MI under random pairing)."""
    x = np.asarray(x, float)
    n = len(x)
    out = np.empty(len(lags)); floor = np.empty(len(lags))
    for k, h in enumerate(lags):
        a = x[:n-h]; b = x[h:]
        out[k] = mutual_information(a, b, B)
        sh = np.empty(n_shuffle)
        for s in range(n_shuffle):
            sh[s] = mutual_information(a, RNG.permutation(b), B)
        floor[k] = sh.mean() + 2.0 * sh.std()
    return out, floor


# ---------------------------------------------------------------------------
# Per-rung retention
# ---------------------------------------------------------------------------

def fit_decay(h_vals, m_vals):
    """Given a decaying positive measure m at horizons h, fit:
       power law   : log m = a + p * log h        (constant per-rung retention)
       exponential : log m = a + (-1/tau) * h
    Return both R^2 and the implied per-phi-rung retention from the power law:
       retention = phi^p .
    """
    h = np.asarray(h_vals, float); m = np.asarray(m_vals, float)
    good = m > 0
    h, m = h[good], m[good]
    if len(h) < 3:
        return None
    lm = np.log(m)
    # power law
    A = np.vstack([np.ones_like(h), np.log(h)]).T
    coef_p, *_ = np.linalg.lstsq(A, lm, rcond=None)
    pred_p = A @ coef_p
    r2_p = 1 - np.sum((lm - pred_p)**2) / np.sum((lm - lm.mean())**2)
    p_exp = coef_p[1]
    retention_per_phi_rung = PHI ** p_exp
    # exponential
    A2 = np.vstack([np.ones_like(h), h]).T
    coef_e, *_ = np.linalg.lstsq(A2, lm, rcond=None)
    pred_e = A2 @ coef_e
    r2_e = 1 - np.sum((lm - pred_e)**2) / np.sum((lm - lm.mean())**2)
    return {
        "power_law_slope_in_h": float(p_exp),
        "power_law_R2": float(r2_p),
        "retention_per_phi_rung": float(retention_per_phi_rung),
        "exp_decay_tau": float(-1.0 / coef_e[1]) if coef_e[1] != 0 else None,
        "exp_R2": float(r2_e),
        "better_model": "power_law" if r2_p > r2_e else "exponential",
    }


def rung_ratios(h0, m_func_h, m_vals, h_vals):
    """Sample measure at h0*phi^n, return consecutive retention ratios."""
    hv = np.asarray(h_vals, float); mv = np.asarray(m_vals, float)
    def interp_log(h):
        if h < hv[0] or h > hv[-1]:
            return None
        return float(np.interp(h, hv, mv))
    rungs = []
    n = 0
    while True:
        h = h0 * PHI**n
        if h > hv[-1]:
            break
        val = interp_log(h)
        rungs.append((h, val))
        n += 1
    ratios = []
    for i in range(len(rungs) - 1):
        a = rungs[i][1]; b = rungs[i+1][1]
        if a and b and a > 0 and b > 0:
            ratios.append(b / a)
    geo = float(np.exp(np.mean(np.log(ratios)))) if ratios else None
    return {"anchor_h0": float(h0),
            "rung_horizons": [float(r[0]) for r in rungs],
            "rung_values": [r[1] for r in rungs],
            "consecutive_retentions": [float(x) for x in ratios],
            "geomean_retention": geo}


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_enso():
    p = HERE / "nino34_long_anom.csv"
    vals = []
    for line in p.read_text().splitlines()[1:]:
        parts = line.split(",")
        if len(parts) < 2:
            continue
        v = float(parts[1])
        if v <= -99:  # missing
            continue
        vals.append(v)
    return np.array(vals), "ENSO Nino3.4 monthly anomaly", "months"


def load_solar():
    p = HERE / "SN_m_tot.csv"
    if not p.exists():
        import shutil
        shutil.copy("/tmp/SN_m_tot.csv", p)
    vals = []
    for line in p.read_text().splitlines():
        f = line.split(";")
        if len(f) < 4:
            continue
        sn = float(f[3])
        if sn < 0:
            continue
        vals.append(sn)
    return np.array(vals), "SILSO monthly sunspot number", "months"


def load_ecg_rr(record="16265"):
    import wfdb
    ann = wfdb.rdann(record, "atr", pn_dir="nsrdb")
    fs = 128.0
    samp = np.asarray(ann.sample, float)
    sym = np.asarray(ann.symbol)
    keep = np.isin(sym, ["N"])  # normal beats only
    samp = samp[keep]
    rr = np.diff(samp) / fs * 1000.0  # ms
    rr = rr[(rr > 300) & (rr < 2000)]  # physiologic
    if len(rr) > 8000:                  # cap for MI speed (continuous segment)
        rr = rr[:8000]
    return rr, f"ECG RR intervals (nsrdb {record})", "beats"


# ---------------------------------------------------------------------------
# Per-system driver
# ---------------------------------------------------------------------------

def analyse(x, name, unit, max_h, h0, B=8):
    print(f"\n{'='*64}\n{name}   (N={len(x)}, unit={unit})\n{'='*64}")
    lags = np.unique(np.round(np.geomspace(1, max_h, 40)).astype(int))
    lags = lags[lags >= 1]

    rho = autocorr_envelope(x, int(max_h))
    rho_env = np.abs(rho[lags])  # envelope of linear skill

    ami, floor = ami_curve(x, lags, B=B)
    ami_clean = np.maximum(ami - floor, 0.0)  # above-floor MI

    # decaying regime for fits: from h0 out to where AMI hits floor
    above = ami > floor
    # find last lag above floor (contiguous-ish): use all lags >= h0 that are above floor
    mask = (lags >= h0) & above
    h_fit = lags[mask]; ami_fit = ami_clean[mask]
    rho_fit = rho_env[mask]

    res = {"name": name, "unit": unit, "N": int(len(x)), "max_h": int(max_h),
           "h0_anchor": float(h0), "bins": B}

    if len(h_fit) >= 3:
        res["entropy_AMI_fit"] = fit_decay(h_fit, ami_fit)
        res["entropy_AMI_rungs"] = rung_ratios(h0, None, ami_clean[lags >= 1], lags[lags >= 1])
    res["linear_corr_fit"] = fit_decay(rho_fit, rho_fit) if False else fit_decay(h_fit, rho_fit)
    res["linear_corr_rungs"] = rung_ratios(h0, None, rho_env, lags)

    # report
    def show(tag, fit, rungs):
        if fit:
            print(f"  [{tag}] power-law R2={fit['power_law_R2']:.3f}  exp R2={fit['exp_R2']:.3f}"
                  f"  better={fit['better_model']}")
            print(f"        retention/phi-rung = {fit['retention_per_phi_rung']:.3f}"
                  f"   (target 1/phi = {INV_PHI:.3f})")
        if rungs and rungs['geomean_retention']:
            print(f"        rung geomean retention = {rungs['geomean_retention']:.3f}")
    show("ENTROPY  AMI", res.get("entropy_AMI_fit"), res.get("entropy_AMI_rungs"))
    show("FORECAST rho", res.get("linear_corr_fit"), res.get("linear_corr_rungs"))

    res["_curves"] = {"lags": lags.tolist(), "ami": ami.tolist(),
                      "ami_floor": floor.tolist(), "rho_env": rho_env.tolist()}
    return res


def main():
    systems = []
    # ENSO: home ~ 12 mo seasonal -> anchor at 6 mo; quasi-period 40-60 mo
    x, nm, u = load_enso();   systems.append(analyse(x, nm, u, max_h=160, h0=6))
    # Solar: 11yr=132mo cycle; anchor at 24 mo, go to ~3 cycles
    x, nm, u = load_solar();  systems.append(analyse(x, nm, u, max_h=400, h0=24))
    # ECG: per-beat; anchor at 4 beats, out to ~600 beats
    x, nm, u = load_ecg_rr(); systems.append(analyse(x, nm, u, max_h=600, h0=4))

    out = {"phi": PHI, "inv_phi_forwarded": INV_PHI, "inv_phi2_shed": INV_PHI2,
           "claim": "per phi-rung retention ~ 1/phi = 0.618; shed ~ 1/phi^2 = 0.382",
           "systems": systems}
    (HERE / "phi_rung_entropy_decay_result.json").write_text(json.dumps(out, indent=2))
    print(f"\nSaved phi_rung_entropy_decay_result.json")

    # cross-system summary
    print(f"\n{'='*64}\nSUMMARY  (retention per phi-rung; target {INV_PHI:.3f})\n{'='*64}")
    for s in systems:
        ef = s.get("entropy_AMI_fit"); lf = s.get("linear_corr_fit")
        if ef and lf:
            nm34 = s["name"][:34]
            er = ef["retention_per_phi_rung"]; epr2 = ef["power_law_R2"]; ebm = ef["better_model"][:3]
            lr = lf["retention_per_phi_rung"]; lpr2 = lf["power_law_R2"]; lbm = lf["better_model"][:3]
            print("  %-34s  AMI %.3f (pl R2 %.2f/%s)   rho %.3f (pl R2 %.2f/%s)"
                  % (nm34, er, epr2, ebm, lr, lpr2, lbm))
        else:
            print("  %s: n/a" % s["name"])

if __name__ == "__main__":
    main()
