"""Independent artifact validator for T357.

This file does not import the analysis script.  It recomputes window metrics,
record medians, frozen gates and hashes from saved artifacts.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
PREFIX = HERE / "T357_PENDULUM_IRRATIONALITY_DI_ARA"
SERIES = Path(f"{PREFIX}_WINDOW_SERIES.csv")
METRICS = Path(f"{PREFIX}_WINDOW_METRICS.csv")
CLOSURE = Path(f"{PREFIX}_CLOSURE_CURVES.csv")
SUMMARY = Path(f"{PREFIX}_RECORD_SUMMARY.csv")
GATES = Path(f"{PREFIX}_FROZEN_GATES.csv")
QA = Path(f"{PREFIX}_DATA_QA.csv")
RESULTS = Path(f"{PREFIX}_RESULTS.json")
FIGURE = Path(f"{PREFIX}_FIGURE.png")
REPORT = HERE / "T357_PENDULUM_IRRATIONALITY_DI_ARA_REPORT_2026-08-11.md"
CLAIM = HERE / "T357_PENDULUM_IRRATIONALITY_DI_ARA_CLAIM_PACKET_v1.md"
PROTOCOL = HERE / "T357_PENDULUM_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md"
CLAIM_HASH = HERE / "T357_PENDULUM_IRRATIONALITY_DI_ARA_CLAIM_PACKET_v1.sha256"
PROTOCOL_HASH = HERE / "T357_PENDULUM_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.sha256"
OUT_JSON = Path(f"{PREFIX}_VALIDATION.json")
OUT_MD = Path(f"{PREFIX}_VALIDATION.md")

RESOLUTIONS = np.array([4, 8, 16, 32], dtype=int)
K = 3
MAX_LAG = 16


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def expected_hash(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip().split()[0].upper()


def cmean(z: np.ndarray) -> float:
    v = np.mean(np.exp(2j * np.pi * z))
    return 0.0 if abs(v) < 1e-15 else float((np.angle(v) / (2 * np.pi)) % 1.0)


def loss(a: np.ndarray, p: np.ndarray) -> np.ndarray:
    return 1.0 - np.cos(2 * np.pi * (a - p))


def recompute(z: np.ndarray):
    occ = []
    for bins in RESOLUTIONS:
        idx = np.minimum((np.mod(z, 1.0) * bins).astype(int), bins - 1)
        occ.append(len(np.unique(idx)))
    slope = np.polyfit(np.log(RESOLUTIONS), np.log(np.maximum(occ, 1)), 1)[0]
    xp = 2 * np.clip(slope, 0, 1)

    split = len(z) // 2
    tx, ty = z[: split - 1], z[1:split]
    qx, qy = z[split:-1], z[split + 1 :]
    dist = np.abs(qx[:, None] - tx[None, :])
    dist = np.minimum(dist, 1 - dist)
    near = np.argpartition(dist, kth=K - 1, axis=1)[:, :K]
    vec = np.mean(np.exp(2j * np.pi * ty[near]), axis=1)
    pred = np.mod(np.angle(vec) / (2 * np.pi), 1.0)
    pred[np.abs(vec) < 1e-12] = cmean(ty)
    local = float(np.mean(loss(qy, pred)))
    null = float(np.mean(loss(qy, np.full_like(qy, cmean(ty)))))
    xr = 2 * min(1.0, local / max(null, 1e-12))

    rhos, misses = [], []
    for lag in range(1, MAX_LAG + 1):
        v = np.mean(np.exp(2j * np.pi * (z[lag:] - z[:-lag])))
        rhos.append(abs(v))
        misses.append(np.angle(v) / (2 * np.pi))
    rhos, misses = np.asarray(rhos), np.asarray(misses)
    best = int(np.argmax(rhos))
    orient = np.angle(np.mean(np.exp(2j * np.pi * (z[1:] - z[:-1])))) / (2 * np.pi)
    return {
        "x_p": float(xp), "x_r": float(xr), "local_loss": local, "null_loss": null,
        "cycle_rho": float(rhos[7]), "cycle_miss_signed": float(misses[7]),
        "cycle_miss_abs": float(abs(misses[7])), "best_rho": float(rhos[best]),
        "best_lag": best + 1, "best_miss_abs": float(abs(misses[best])),
        "median_rho": float(np.median(rhos)), "orientation": float(orient),
    }, rhos, misses


def one(summary: pd.DataFrame, family: str, stratum: str, condition: str):
    d = summary[(summary.family == family) & (summary.stratum == stratum) & (summary.condition == condition)]
    assert len(d) == 1
    return d.iloc[0]


def recalc_grouped(summary: pd.DataFrame):
    strata = ["free", "driven1", "driven2"]
    s = {k: one(summary, "single", k, "chronological") for k in strata}
    d = {k: one(summary, "double", k, "chronological") for k in strata}
    sh = {k: one(summary, "double", k, "shuffled") for k in strata}
    br = {k: one(summary, "double", k, "broken_lineage") for k in strata}
    g1 = sum((r.x_p < 1) and (r.x_r < 1) and (r.cycle_rho >= .8) and (r.cycle_miss_abs <= .03) for r in s.values()) >= 2
    dxp = [d[k].x_p - s[k].x_p for k in strata]
    g2 = sum(v >= .2 for v in dxp) >= 2 and np.median(dxp) > 0
    g3a = sum(d[k].x_r < 1.25 for k in strata) >= 2
    g3b = sum(sh[k].x_r - d[k].x_r >= .25 for k in strata) >= 2
    g3c = sum(d[k].best_rho - sh[k].best_rho >= .15 for k in strata) >= 2
    all_xp = []
    for fam in ["single", "double"]:
        for k in strata:
            all_xp.append(abs(one(summary, fam, k, "shuffled").x_p - one(summary, fam, k, "chronological").x_p))
    g3d = max(all_xp) <= .02
    g4 = sum((r.cycle_rho >= .8) and (r.cycle_miss_abs > .03) and (r.cycle_closure_share < .5) and (r.coherent_return_share > 0) for r in d.values()) >= 2
    g5 = sum(max(br[k].x_r - d[k].x_r, d[k].best_rho - br[k].best_rho) >= .15 for k in strata) >= 2
    dxp_rev, drho_rev, do_rev = [], [], []
    for fam in ["single", "double"]:
        for k in strata:
            c, r = one(summary, fam, k, "chronological"), one(summary, fam, k, "reversed")
            dxp_rev.append(abs(r.x_p - c.x_p)); drho_rev.append(abs(r.best_rho - c.best_rho)); do_rev.append(abs(r.orientation + c.orientation))
    g6 = max(dxp_rev) <= .02 and max(drho_rev) <= .05 and sum(v <= .02 for v in do_rev) >= 5
    return {"G1": bool(g1), "G2": bool(g2), "G3": bool(g3a and g3b and g3c and g3d), "G4": bool(g4), "G5": bool(g5), "G6": bool(g6), "overall": bool(g1 and g2 and g3a and g3b and g3c and g3d and g4 and g5 and g6)}


def main():
    required = [SERIES, METRICS, CLOSURE, SUMMARY, GATES, QA, RESULTS, FIGURE, REPORT, CLAIM, PROTOCOL, CLAIM_HASH, PROTOCOL_HASH]
    checks = {f"exists:{p.name}": p.exists() and p.stat().st_size > 0 for p in required}
    if not all(checks.values()):
        raise AssertionError("Missing required artifact")
    checks["claim_hash"] = digest(CLAIM) == expected_hash(CLAIM_HASH)
    checks["protocol_hash"] = digest(PROTOCOL) == expected_hash(PROTOCOL_HASH)

    series = pd.read_csv(SERIES)
    metrics = pd.read_csv(METRICS)
    closure = pd.read_csv(CLOSURE)
    summary = pd.read_csv(SUMMARY)
    qa = pd.read_csv(QA)
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    checks["six_physical_records"] = len(qa) == 6 and qa[["family", "stratum"]].drop_duplicates().shape[0] == 6
    checks["all_records_have_windows"] = bool((qa.complete_windows >= 1).all())
    checks["series_natural_key"] = not series.duplicated(["identity", "condition", "window", "sample"]).any()
    checks["metrics_natural_key"] = not metrics.duplicated(["identity", "condition", "window"]).any()
    checks["closure_natural_key"] = not closure.duplicated(["identity", "condition", "window", "lag"]).any()
    checks["phase_range"] = bool(series.phase.between(0, 1, inclusive="left").all())
    checks["coordinate_range"] = bool(metrics.x_p.between(0, 2).all() and metrics.x_r.between(0, 2).all())

    max_metric_error = 0.0
    max_curve_error = 0.0
    metric_columns = ["x_p", "x_r", "local_loss", "null_loss", "cycle_rho", "cycle_miss_signed", "cycle_miss_abs", "best_rho", "best_lag", "best_miss_abs", "median_rho", "orientation"]
    for key, d in series.groupby(["identity", "condition", "window"], sort=False):
        d = d.sort_values("sample")
        z = d.phase.to_numpy(float)
        values, rhos, misses = recompute(z)
        row = metrics[(metrics.identity == key[0]) & (metrics.condition == key[1]) & (metrics.window == key[2])].iloc[0]
        max_metric_error = max(max_metric_error, max(abs(float(row[c]) - float(values[c])) for c in metric_columns))
        q = closure[(closure.identity == key[0]) & (closure.condition == key[1]) & (closure.window == key[2])].sort_values("lag")
        max_curve_error = max(max_curve_error, float(np.max(np.abs(q.rho.to_numpy() - rhos))), float(np.max(np.abs(q.miss_signed.to_numpy() - misses))))
    checks["window_metrics_recomputed"] = max_metric_error < 1e-10
    checks["closure_curves_recomputed"] = max_curve_error < 1e-10

    numeric = ["x_p", "x_r", "local_loss", "null_loss", "cycle_rho", "cycle_miss_signed", "cycle_miss_abs", "best_rho", "best_lag", "best_miss_abs", "median_rho", "orientation"]
    rebuilt = metrics.groupby(["identity", "family", "stratum", "condition"], as_index=False)[numeric].median()
    shares = metrics.groupby(["identity", "family", "stratum", "condition"], as_index=False).agg(windows=("window", "size"), cycle_closure_share=("cycle_closure", "mean"), coherent_return_share=("any_coherent_return", "mean"))
    rebuilt = rebuilt.merge(shares, on=["identity", "family", "stratum", "condition"])
    merged = summary.merge(rebuilt, on=["identity", "family", "stratum", "condition"], suffixes=("_saved", "_rebuilt"))
    summary_cols = numeric + ["windows", "cycle_closure_share", "coherent_return_share"]
    max_summary_error = max(float(np.max(np.abs(merged[f"{c}_saved"] - merged[f"{c}_rebuilt"]))) for c in summary_cols)
    checks["record_summaries_recomputed"] = max_summary_error < 1e-10
    grouped = recalc_grouped(rebuilt)
    checks["grouped_gates_recomputed"] = grouped == results["grouped_gates"]
    checks["expected_frozen_verdict"] = (not grouped["overall"]) and grouped == {"G1": True, "G2": True, "G3": True, "G4": False, "G5": True, "G6": True, "overall": False}

    with Image.open(FIGURE) as im:
        checks["figure_dimensions"] = im.width >= 1800 and im.height >= 1800
        fig_size = [im.width, im.height]
    all_pass = all(checks.values())
    payload = {
        "all_validation_checks_pass": all_pass,
        "checks": checks,
        "max_window_metric_error": max_metric_error,
        "max_closure_curve_error": max_curve_error,
        "max_record_summary_error": max_summary_error,
        "recomputed_grouped_gates": grouped,
        "figure_pixels": fig_size,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = ["# T357 independent validation", "", f"**Overall:** {'PASS' if all_pass else 'FAIL'}", ""]
    lines += [f"- {'PASS' if ok else 'FAIL'}: `{name}`" for name, ok in checks.items()]
    lines += ["", f"Maximum window-metric error: `{max_metric_error:.3e}`", f"Maximum closure-curve error: `{max_curve_error:.3e}`", f"Maximum record-summary error: `{max_summary_error:.3e}`", "", f"Recomputed grouped gates: `{json.dumps(grouped, sort_keys=True)}`"]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

