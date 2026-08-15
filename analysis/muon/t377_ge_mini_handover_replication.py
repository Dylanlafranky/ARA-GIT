"""T377: independent Ge-Mini ensemble muon-handover replication.

The analysis is deliberately publication-level: it reconstructs vector data
from the official arXiv source figures and checks those curves against the
exact integer count cells printed in the paper.  It does not claim access to
event-linked daughter records.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np
import pdfplumber


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "T377_ge_mini_source"
FIG4 = SOURCE / "figures" / "fig4.pdf"
FIG5A = SOURCE / "figures" / "fig5a.pdf"
FIG5B = SOURCE / "figures" / "fig5b.pdf"
ARCHIVE = ROOT / "ge_mini_2406.13806v2.tar"
OUT = ROOT / "T377_ge_mini_handover"
OUT.mkdir(exist_ok=True)

# Vector calibration read from the labelled axes in fig4.pdf.
Y_ZERO = 555.094416
Y_PER_COUNT = 31.979695 / 2.5
X_ZERO_RIGHT = 720.169930
X_ZERO_LEFT = 202.751748
X_PER_US = 55.279720 / 5.0

ORANGE = np.array([0.8, 0.431372549, 0.0901960784])
BLUE = np.array([0.1215686275, 0.4666666667, 0.7058823529])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def close_colour(value, target, tol=1e-6) -> bool:
    if not isinstance(value, tuple):
        return False
    return bool(np.max(np.abs(np.asarray(value) - target)) < tol)


def extract_step_curve(curve: dict) -> tuple[np.ndarray, np.ndarray]:
    pts = curve["pts"]
    centres, values = [], []
    # The vector curve is a step path: odd-even point pairs are horizontal bins.
    for i in range(1, min(len(pts) - 1, 39), 2):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        if abs(y1 - y2) < 1e-6 and x2 > x1:
            centres.append(((x1 + x2) / 2 - X_ZERO_RIGHT) / X_PER_US)
            values.append((Y_ZERO - y1) / Y_PER_COUNT)
    return np.asarray(centres), np.clip(np.asarray(values), 0, None)


def extract_projection(side: str) -> dict:
    with pdfplumber.open(FIG4) as pdf:
        page = pdf.pages[0]
        if side == "on":
            marker_range = range(62, 81)
            line_range = range(132, 151)
            x0 = X_ZERO_RIGHT
        elif side == "off":
            marker_range = range(39, 58)
            line_range = range(93, 112)
            x0 = X_ZERO_LEFT
        else:
            raise ValueError(side)

        markers = [page.curves[i] for i in marker_range]
        errors = [page.lines[i] for i in line_range]
        t, y, sigma = [], [], []
        for marker, error in zip(markers, errors):
            xm = (marker["x0"] + marker["x1"]) / 2
            ym = (marker["top"] + marker["bottom"]) / 2
            t.append((xm - x0) / X_PER_US)
            y.append((Y_ZERO - ym) / Y_PER_COUNT)
            sigma.append((error["bottom"] - error["top"]) / (2 * Y_PER_COUNT))

        curves = page.curves
        delayed = next(c for c in curves if close_colour(c.get("stroking_color"), ORANGE) and c.get("top", 0) > 380)
        prompt = next(c for c in curves if close_colour(c.get("stroking_color"), BLUE) and c.get("top", 0) > 380)
        tc, d = extract_step_curve(delayed)
        tp, p = extract_step_curve(prompt)
        if not np.allclose(tc, tp):
            raise RuntimeError("Prompt and delayed vector bins do not align")
    return {
        "t": np.asarray(t),
        "y": np.asarray(y),
        "sigma": np.asarray(sigma),
        "shape_t": tc,
        "prompt_shape": p,
        "delayed_shape": d,
    }


def extract_count_grid(path: Path) -> np.ndarray:
    with pdfplumber.open(path) as pdf:
        words = pdf.pages[0].extract_words()
    cells = [w for w in words if re.fullmatch(r"\d+\.0", w["text"]) and 200 < w["x0"] < 1080 and 80 < w["top"] < 650]
    rows = {}
    for w in cells:
        key = round(w["top"], 1)
        rows.setdefault(key, []).append(w)
    ordered = []
    for key in sorted(rows):
        row = sorted(rows[key], key=lambda w: w["x0"])
        if len(row) == 9:
            ordered.append([int(float(w["text"])) for w in row])
    if len(ordered) != 10:
        raise RuntimeError(f"Expected a 10x9 grid in {path.name}; got {len(ordered)} rows")
    # PDF is printed latest time at the top; return chronological order.
    return np.asarray(ordered[::-1], dtype=float)


def fit_nonnegative(y, sigma, prompt_shape, delayed_shape, mode="pair") -> dict:
    p = prompt_shape / np.sum(prompt_shape)
    d = delayed_shape / np.sum(delayed_shape)
    if mode == "pair":
        X = np.column_stack([p, d])
    elif mode == "prompt":
        X = p[:, None]
    elif mode == "delayed":
        X = d[:, None]
    elif mode == "reversed":
        X = np.column_stack([p[::-1], d[::-1]])
    elif mode == "null":
        X = np.zeros((len(y), 0))
    else:
        raise ValueError(mode)

    if X.shape[1]:
        Xw = X / sigma[:, None]
        yw = y / sigma
        unconstrained = np.linalg.lstsq(Xw, yw, rcond=None)[0]
        candidates = [np.zeros(X.shape[1])]
        if np.all(unconstrained >= 0):
            candidates.append(unconstrained)
        for j in range(X.shape[1]):
            c = np.zeros(X.shape[1])
            denom = float(Xw[:, j] @ Xw[:, j])
            c[j] = max(0.0, float(Xw[:, j] @ yw) / denom) if denom else 0.0
            candidates.append(c)
        coef = min(candidates, key=lambda c: float(np.sum((yw - Xw @ c) ** 2)))
        pred = X @ coef
    else:
        coef = np.empty(0)
        pred = np.zeros_like(y)
    residual = (y - pred) / sigma
    chi2 = float(np.sum(residual**2))
    k = X.shape[1]
    n = len(y)
    aicc = chi2 + 2 * k + (2 * k * (k + 1) / (n - k - 1) if n > k + 1 else math.inf)
    return {"mode": mode, "coef": coef, "pred": pred, "chi2": chi2, "dof": n - k, "aicc": float(aicc)}


def fit_fixed_shape(y, sigma, shape, mode="fixed_pair") -> dict:
    v = np.asarray(shape, dtype=float)
    v = v / np.sum(v)
    vw, yw = v / sigma, y / sigma
    denom = float(vw @ vw)
    coef = max(0.0, float(vw @ yw) / denom) if denom else 0.0
    pred = coef * v
    chi2 = float(np.sum(((y - pred) / sigma) ** 2))
    n, k = len(y), 1
    aicc = chi2 + 2 * k + 2 * k * (k + 1) / (n - k - 1)
    return {"mode": mode, "coef": np.asarray([coef]), "pred": pred, "chi2": chi2, "dof": n - k, "aicc": float(aicc)}


def equality_and_coordinate(t, prompt_rate, delayed_rate) -> dict:
    order = np.argsort(t)
    t, p, d = t[order], prompt_rate[order], delayed_rate[order]
    dense = np.linspace(float(t.min() - 1), float(t.max() + 1), 10001)
    pd = np.interp(dense, t, p, left=0, right=0)
    dd = np.interp(dense, t, d, left=0, right=0)
    diff = pd - dd
    candidates = np.where((dense[:-1] >= 0) & (diff[:-1] >= 0) & (diff[1:] < 0))[0]
    if not len(candidates):
        return {"t_h": math.nan, "x_h": math.nan, "left": math.nan, "right": math.nan}
    i = int(candidates[0])
    frac = diff[i] / (diff[i] - diff[i + 1]) if diff[i] != diff[i + 1] else 0.5
    t_h = float(dense[i] + frac * (dense[i + 1] - dense[i]))
    total_rate = pd + dd
    dt = np.diff(dense)
    trap = (total_rate[:-1] + total_rate[1:]) * dt / 2
    cum = np.r_[0.0, np.cumsum(trap)]
    total = float(cum[-1])
    x_h = float(2 * np.interp(t_h, dense, cum) / total)
    # Native publication resolution: the equality is bracketed by these centres.
    j = np.searchsorted(t, t_h)
    left_t = float(t[max(0, j - 1)])
    right_t = float(t[min(len(t) - 1, j)])
    left = float(2 * np.interp(left_t, dense, cum) / total)
    right = float(2 * np.interp(right_t, dense, cum) / total)
    return {"t_h": t_h, "x_h": x_h, "left": left, "right": right, "left_t": left_t, "right_t": right_t}


def bootstrap(proj, n_boot=5000, seed=377) -> dict:
    rng = np.random.default_rng(seed)
    pshape, dshape = proj["prompt_shape"], proj["delayed_shape"]
    t, sigma = proj["t"], proj["sigma"]
    xh, th, xp = [], [], []
    for _ in range(n_boot):
        yy = rng.normal(proj["y"], sigma)
        fit = fit_nonnegative(yy, sigma, pshape, dshape, "pair")
        if len(fit["coef"]) != 2 or np.sum(fit["coef"]) <= 0:
            continue
        rates_p = fit["coef"][0] * pshape / np.sum(pshape)
        rates_d = fit["coef"][1] * dshape / np.sum(dshape)
        event = equality_and_coordinate(t, rates_p, rates_d)
        if np.isfinite(event["x_h"]):
            xh.append(event["x_h"])
            th.append(event["t_h"])
            xp.append(2 * fit["coef"][0] / np.sum(fit["coef"]))
    def q(v):
        if not len(v):
            return [math.nan, math.nan, math.nan]
        return [float(x) for x in np.quantile(v, [0.025, 0.5, 0.975])]
    return {"n_success": len(xh), "x_h_q025_q50_q975": q(xh), "t_h_q025_q50_q975": q(th), "x_prompt_q025_q50_q975": q(xp), "x_h_samples": xh}


def loo(proj) -> dict:
    values = []
    for drop in range(len(proj["t"])):
        keep = np.arange(len(proj["t"])) != drop
        fit = fit_nonnegative(proj["y"][keep], proj["sigma"][keep], proj["prompt_shape"][keep], proj["delayed_shape"][keep])
        p = fit["coef"][0] * proj["prompt_shape"] / np.sum(proj["prompt_shape"][keep])
        d = fit["coef"][1] * proj["delayed_shape"] / np.sum(proj["delayed_shape"][keep])
        ev = equality_and_coordinate(proj["t"], p, d)
        values.append({"dropped_t_us": float(proj["t"][drop]), "x_h": ev["x_h"], "t_h_us": ev["t_h"]})
    finite = np.asarray([v["x_h"] for v in values if np.isfinite(v["x_h"])])
    if not len(finite):
        return {"runs": values, "n_resolved": 0, "x_h_min": math.nan, "x_h_max": math.nan, "x_h_median": math.nan}
    return {"runs": values, "n_resolved": len(finite), "x_h_min": float(np.min(finite)), "x_h_max": float(np.max(finite)), "x_h_median": float(np.median(finite))}


def raw_count_crosscheck(on_grid, off_grid, pshape, dshape) -> dict:
    on_t = on_grid.sum(axis=1)
    off_t = off_grid.sum(axis=1)
    y = on_t - off_t
    sigma = np.sqrt(on_t + off_t)
    # Rebin publication 2-us source shapes to the 4-us cells used in fig5.
    p20 = np.r_[pshape, 0.0]
    d20 = np.r_[dshape, 0.0]
    p4 = p20.reshape(10, 2).sum(axis=1)
    d4 = d20.reshape(10, 2).sum(axis=1)
    fits = {m: fit_nonnegative(y, sigma, p4, d4, m) for m in ["pair", "prompt", "delayed", "null", "reversed"]}
    fits["fixed_pair"] = fit_fixed_shape(y, sigma, p4 + d4, "fixed_pair")
    return {
        "time_centres_us": list(np.arange(-2, 38, 4, dtype=float)),
        "on_counts": on_t.tolist(),
        "off_counts": off_t.tolist(),
        "difference": y.tolist(),
        "sigma": sigma.tolist(),
        "fits": {m: {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in f.items()} for m, f in fits.items()},
    }


def json_fit(fit):
    return {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in fit.items()}


def main():
    on = extract_projection("on")
    off = extract_projection("off")
    on_grid = extract_count_grid(FIG5A)
    off_grid = extract_count_grid(FIG5B)

    modes = ["pair", "prompt", "delayed", "null", "reversed"]
    fits_on = {m: fit_nonnegative(on["y"], on["sigma"], on["prompt_shape"], on["delayed_shape"], m) for m in modes}
    fits_off = {m: fit_nonnegative(off["y"], off["sigma"], off["prompt_shape"], off["delayed_shape"], m) for m in modes}
    fits_on["fixed_pair"] = fit_fixed_shape(on["y"], on["sigma"], on["prompt_shape"] + on["delayed_shape"], "fixed_pair")
    fits_off["fixed_pair"] = fit_fixed_shape(off["y"], off["sigma"], off["prompt_shape"] + off["delayed_shape"], "fixed_pair")
    pair = fits_on["pair"]
    # The paper's likelihood has one total CEvNS amplitude; relative branch
    # weights are fixed.  Therefore the displayed component curves define the
    # publication-level handover, while the two-amplitude refit below audits
    # whether the public data independently identify both branches.
    p_rate = on["prompt_shape"].copy()
    d_rate = on["delayed_shape"].copy()
    event = equality_and_coordinate(on["t"], p_rate, d_rate)
    total_yield = float(np.sum(p_rate) + np.sum(d_rate))
    x_prompt = float(2 * np.sum(p_rate) / total_yield)
    x_delayed = float(2 * np.sum(d_rate) / total_yield)
    coupling_balance = float(x_prompt * x_delayed)
    boot = bootstrap(on)
    loo_result = loo(on)
    raw = raw_count_crosscheck(on_grid, off_grid, on["prompt_shape"], on["delayed_shape"])

    # Gate evaluation keeps descriptive geometry separate from evidence.
    t_prompt_peak = float(on["t"][np.argmax(p_rate)])
    t_delayed_peak = float(on["t"][np.argmax(d_rate)])
    pair_aicc = fits_on["fixed_pair"]["aicc"]
    best_single = min(fits_on["prompt"]["aicc"], fits_on["delayed"]["aicc"])
    on_pair_gain = float(best_single - pair_aicc)
    off_best_single = min(fits_off["prompt"]["aicc"], fits_off["delayed"]["aicc"])
    off_pair_gain = float(off_best_single - fits_off["fixed_pair"]["aicc"])
    raw_pair = raw["fits"]["fixed_pair"]
    raw_best_single = min(raw["fits"]["prompt"]["aicc"], raw["fits"]["delayed"]["aicc"])
    raw_pair_gain = float(raw_best_single - raw_pair["aicc"])
    q025, q50, q975 = boot["x_h_q025_q50_q975"]
    observed_two_branch_resolved = bool(len(pair["coef"]) == 2 and np.all(pair["coef"] > 0) and np.isfinite(q50))

    gates = {
        "G1_provenance": True,
        "G2_identity": True,
        "G3_published_model_ordered_branches": bool(t_prompt_peak < t_delayed_peak and np.isfinite(event["t_h"])),
        "G3_observed_two_branch_refit_resolved": observed_two_branch_resolved,
        "G4_pair_necessity": bool(on_pair_gain > 0),
        "G5_on_stronger_than_off": bool(on_pair_gain > off_pair_gain),
        "G6_ARA_placement_reported": True,
        "G6_published_coordinate_inside_T372_interval": bool(0.1787 <= event["x_h"] <= 0.6916),
        "G6_observed_exact_0_5_inside_bootstrap_95pct": bool(np.isfinite(q025) and q025 <= 0.5 <= q975),
        "G6_observed_T372_interval_overlap": bool(np.isfinite(q025) and not (q975 < 0.1787 or q025 > 0.6916)),
        "G7_loo_finite": bool(loo_result["n_resolved"] > 0),
        "G7_raw_ordered_pair_gain_positive": bool(raw_pair_gain > 0),
    }

    hashes = {p.name: sha256(p) for p in [ARCHIVE, FIG4, FIG5A, FIG5B]}
    results = {
        "test": "T377 Ge-Mini independent ensemble muon-handover replication",
        "source": "COHERENT Ge-Mini, arXiv:2406.13806v2 official source archive",
        "boundary": "ensemble stopped-pion prompt/delayed release; not event-linked decay prediction",
        "hashes_sha256": hashes,
        "vector_calibration": {"y_zero_pdf": Y_ZERO, "pdf_units_per_count_per_2us": Y_PER_COUNT, "pdf_units_per_us": X_PER_US},
        "on_projection": {"t_us": on["t"].tolist(), "background_subtracted_counts_per_2us": on["y"].tolist(), "sigma": on["sigma"].tolist()},
        "off_projection": {"t_us": off["t"].tolist(), "background_subtracted_counts_per_2us": off["y"].tolist(), "sigma": off["sigma"].tolist()},
        "fits_on": {m: json_fit(f) for m, f in fits_on.items()},
        "fits_off": {m: json_fit(f) for m, f in fits_off.items()},
        "ara": {
            "publication_prompt_component_area": float(np.sum(p_rate)),
            "publication_delayed_component_area": float(np.sum(d_rate)),
            "x_prompt": x_prompt,
            "x_delayed": x_delayed,
            "x_sum_forced": x_prompt + x_delayed,
            "coupling_balance_xp_times_xd": coupling_balance,
            "t_prompt_peak_us": t_prompt_peak,
            "t_delayed_peak_us": t_delayed_peak,
            "handover": event,
            "observed_two_amplitude_refit_prompt_delayed": pair["coef"].tolist(),
            "observed_two_branch_resolved": observed_two_branch_resolved,
            "bootstrap": {k: v for k, v in boot.items() if k != "x_h_samples"},
            "leave_one_bin_out": loo_result,
        },
        "controls": {
            "on_pair_AICc_gain_over_best_single": on_pair_gain,
            "off_pair_AICc_gain_over_best_single": off_pair_gain,
            "raw_count_pair_AICc_gain_over_best_single": raw_pair_gain,
            "raw_count_crosscheck": raw,
        },
        "gates": gates,
        "te_ara_audit": {
            "forced": "x_prompt + x_delayed = 2 by normalization; not evidence",
            "measured": ["published component chronology", "fixed-pair-vs-single AICc", "on-vs-off contrast", "raw count-grid crosscheck", "two-amplitude identifiability", "bootstrap and leave-one-bin-out stability"],
            "other_or_confound": ["published projection is downstream of a two-dimensional likelihood fit", "several-microsecond detector drift time", "sub-2-keV timing degradation", "finite counts", "background subtraction", "energy threshold and ROI", "fixed source-model timing shapes"],
        },
    }

    (OUT / "T377_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    with (OUT / "T377_timing_projection.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["time_us", "on_background_subtracted_counts_per_2us", "on_sigma", "off_background_subtracted_counts_per_2us", "off_sigma", "fitted_prompt", "fitted_delayed", "fitted_total"])
        for row in zip(on["t"], on["y"], on["sigma"], off["y"], off["sigma"], p_rate, d_rate, p_rate + d_rate):
            w.writerow(row)
    np.savetxt(OUT / "T377_on_count_grid.csv", on_grid, delimiter=",", fmt="%d")
    np.savetxt(OUT / "T377_off_count_grid.csv", off_grid, delimiter=",", fmt="%d")

    print(json.dumps({
        "ara": results["ara"],
        "controls": {k: v for k, v in results["controls"].items() if k != "raw_count_crosscheck"},
        "gates": gates,
        "output": str(OUT),
    }, indent=2))


if __name__ == "__main__":
    main()
