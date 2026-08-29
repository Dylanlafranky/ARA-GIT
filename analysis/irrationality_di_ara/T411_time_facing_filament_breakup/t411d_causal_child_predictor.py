"""T411D causal child-to-parent handover forecast.

Development and holdout are deliberately separate commands.  Development
freezes only two time offsets; holdout verifies the frozen file before scoring.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

import t411c_source_qualified_rate as t411c

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "T411D_causal_child_prediction"
PARAMS = HERE / "T411D_FROZEN_PARAMETERS.json"
DEV = {"S1", "S3"}
HOLD = {"S2", "S4"}
PERSISTENCE = 5
ARM_LEVEL = 1.0
SEED = 411004


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def causal_slope(y: np.ndarray, window: int, dt: float) -> np.ndarray:
    """Trailing least-squares slope; output i uses samples i-window+1..i."""
    out = np.full(len(y), np.nan)
    x = np.arange(window, dtype=float) * dt
    xc = x - x.mean()
    denom = float(np.dot(xc, xc))
    for i in range(window - 1, len(y)):
        z = y[i - window + 1:i + 1].astype(float)
        if np.all(np.isfinite(z)):
            out[i] = float(np.dot(xc, z - z.mean()) / denom)
    return out


def causal_confirmed_cross(t: np.ndarray, x: np.ndarray, parent_x: np.ndarray | None,
                           persistence: int = PERSISTENCE) -> tuple[float, float]:
    """Return (estimated crossing, causal issue time), or NaNs."""
    armed = False
    for i in range(len(x)):
        if not np.isfinite(x[i]):
            continue
        parent_ok = parent_x is None or (np.isfinite(parent_x[i]) and parent_x[i] < 1)
        if x[i] <= ARM_LEVEL and parent_ok:
            armed = True
        if not armed or i + 1 < persistence or not parent_ok:
            continue
        tail = x[i - persistence + 1:i + 1]
        if np.all(np.isfinite(tail)) and np.all(tail >= 1):
            j = i - persistence + 1
            if j > 0 and np.isfinite(x[j - 1]) and x[j] != x[j - 1]:
                frac = (1 - x[j - 1]) / (x[j] - x[j - 1])
                cross = float(t[j - 1] + np.clip(frac, 0, 1) * (t[j] - t[j - 1]))
            else:
                cross = float(t[j])
            return cross, float(t[i])
    return float("nan"), float("nan")


def capillary_forecast(m: pd.Series) -> float:
    fluid = str(m.Fluid)
    mu, _, sigma = t411c.fluid_properties(fluid, float(m.T_C))
    r_cap = 2 * t411c.ALPHA * sigma / mu * 1000
    d0 = float(m.D0_mm)
    h0 = d0 * float(m.H0_D0)
    v = float(m.v_mm_s)
    if v <= 0 or h0 <= 0 or r_cap <= 0:
        return float("nan")
    r0 = 0.75 * (v / h0) * d0
    ratio = r0 / r_cap
    if ratio <= 0:
        return float("nan")
    return float((h0 / v) * (ratio ** (1 / 1.75) - 1))


def analyse_event(group: pd.DataFrame, m: pd.Series, target_t: float) -> tuple[pd.DataFrame, dict]:
    g = group[np.isfinite(group.D_mm) & (group.D_px >= 5)].copy().sort_values("Time_s")
    tbrk = float(m.tbrk_s)
    coverage = float(g.Time_s.max() / tbrk) if len(g) else 0.0
    base = {"Name": str(m.Name), "fluid": str(m.Fluid), "D0_mm": float(m.D0_mm),
            "tbrk_s": tbrk, "target_t_s": target_t, "coverage": coverage}
    if len(g) < 40 or coverage < 0.90 or not np.isfinite(target_t):
        return pd.DataFrame(), {**base, "excluded": True, "reason": "qualification_or_target"}

    fluid = str(m.Fluid)
    mu, _, sigma = t411c.fluid_properties(fluid, float(m.T_C))
    d0 = float(m.D0_mm)
    h0 = d0 * float(m.H0_D0)
    v = float(m.v_mm_s)
    t = g.Time_s.to_numpy(float)
    d = g.D_mm.to_numpy(float)
    dt = float(np.median(np.diff(t)))
    r_cap = 2 * t411c.ALPHA * sigma / mu * 1000
    target_window = int(np.ceil((2 / float(m.px_per_mm)) / max(r_cap, 1e-12) / dt))
    parent_window = t411c.odd_window(len(g), target_window)
    child_window = max(5, parent_window // 2)
    if child_window % 2 == 0:
        child_window += 1
    first_parent_rate_t = float(t[parent_window - 1])
    if target_t < first_parent_rate_t:
        return pd.DataFrame(), {
            **base, "excluded": True, "reason": "target_before_causal_rate",
            "parent_window_frames": parent_window, "child_window_frames": child_window,
            "first_parent_rate_t_s": first_parent_rate_t,
        }

    r_parent_obs = -causal_slope(d, parent_window, dt)
    r_child_obs = -causal_slope(d, child_window, dt)
    r_mech = 0.75 * (v / h0) * d0 * np.power(1 + v * t / h0, -1.75)
    ri_parent = r_parent_obs - r_mech
    ri_child = r_child_obs - r_mech
    connection = np.maximum(ri_parent, 0)
    movement = np.abs(ri_child - ri_parent)
    child_total = connection + movement
    x_child = np.full(len(t), np.nan)
    okc = np.isfinite(child_total) & (child_total > 0)
    x_child[okc] = 2 * connection[okc] / child_total[okc]
    x_parent = np.full(len(t), np.nan)
    okp = np.isfinite(r_parent_obs) & (r_parent_obs > 0) & (ri_parent >= 0)
    x_parent[okp] = 2 * ri_parent[okp] / r_parent_obs[okp]

    child_cross, child_issue = causal_confirmed_cross(t, x_child, x_parent)
    parent_cross, parent_issue = causal_confirmed_cross(t, x_parent, None)
    cap_t = capillary_forecast(m)

    g["x_child_connection_ara"] = x_child
    g["x_parent_causal_ara"] = x_parent
    g["connection_child_mm_s"] = connection
    g["movement_child_mm_s"] = movement
    g["r_parent_unresolved_mm_s"] = ri_parent
    g["r_child_unresolved_mm_s"] = ri_child
    g["fluid"] = fluid
    g["target_t_s"] = target_t
    g["child_issue_t_s"] = child_issue
    g["parent_issue_t_s"] = parent_issue
    sm = {
        **base, "excluded": False, "reason": "", "parent_window_frames": parent_window,
        "child_window_frames": child_window, "child_cross_t_s": child_cross,
        "child_issue_t_s": child_issue, "parent_cross_t_s": parent_cross,
        "parent_issue_t_s": parent_issue, "capillary_forecast_t_s": cap_t,
        "child_issue_lead_s": target_t - child_issue if np.isfinite(child_issue) else np.nan,
        "parent_issue_lead_s": target_t - parent_issue if np.isfinite(parent_issue) else np.nan,
    }
    return g, sm


def load_events(fluids: set[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    meta = t411c.load_metadata()
    raw = t411c.load_raw()
    targets = []
    for fn in ["T411C_DEVELOPMENT_EVENT_SUMMARY.csv", "T411C_HOLDOUT_EVENT_SUMMARY.csv"]:
        p = HERE / "results" / fn
        if p.exists():
            targets.append(pd.read_csv(p)[["Name", "cross_t_s"]])
    target_map = pd.concat(targets).drop_duplicates("Name").set_index("Name").cross_t_s.to_dict()
    series, rows = [], []
    for _, m in meta[meta.Fluid.isin(fluids)].iterrows():
        name = str(m.Name)
        s, row = analyse_event(raw[raw.Name == name], m, float(target_map.get(name, np.nan)))
        rows.append(row)
        if not s.empty:
            s["Name"] = name
            series.append(s)
    return (pd.concat(series, ignore_index=True) if series else pd.DataFrame(), pd.DataFrame(rows))


def median_positive_offset(summary: pd.DataFrame, issue_col: str) -> float:
    d = summary.loc[summary[issue_col].notna() & summary.target_t_s.notna(), "target_t_s"] - summary.loc[
        summary[issue_col].notna() & summary.target_t_s.notna(), issue_col]
    return float(d.median()) if len(d) else float("nan")


def add_predictions(summary: pd.DataFrame, params: dict) -> pd.DataFrame:
    s = summary.copy()
    s["child_prediction_t_s"] = s.child_issue_t_s + params["child_offset_s"]
    s["parent_prediction_t_s"] = s.parent_issue_t_s + params["parent_offset_s"]
    for prefix, col in [("child", "child_prediction_t_s"), ("parent", "parent_prediction_t_s"),
                        ("capillary", "capillary_forecast_t_s")]:
        s[f"{prefix}_error_s"] = s[col] - s.target_t_s
        s[f"{prefix}_abs_error_s"] = s[f"{prefix}_error_s"].abs()
        s[f"{prefix}_abs_error_u"] = s[f"{prefix}_abs_error_s"] / s.tbrk_s
    return s


def shifted_control(series: pd.DataFrame, summary: pd.DataFrame, offset: float,
                    reps: int = 1000) -> dict:
    rng = np.random.default_rng(SEED)
    target = summary.set_index("Name").target_t_s.to_dict()
    tbrk = summary.set_index("Name").tbrk_s.to_dict()
    null = []
    groups = [(name, g.sort_values("Time_s")) for name, g in series.groupby("Name")]
    for _ in range(reps):
        errs = []
        for name, g in groups:
            x = g.x_child_connection_ara.to_numpy(float)
            xp = g.x_parent_causal_ara.to_numpy(float)
            t = g.Time_s.to_numpy(float)
            finite = np.isfinite(x)
            if finite.sum() < 10:
                continue
            shift = int(rng.integers(PERSISTENCE, len(x) - 1))
            xs = np.roll(x, shift)
            _, issue = causal_confirmed_cross(t, xs, xp)
            if np.isfinite(issue):
                errs.append(abs(issue + offset - target[name]) / tbrk[name])
        if errs:
            null.append(float(np.median(errs)))
    null = np.asarray(null)
    return {"reps": int(len(null)), "null_median_abs_error_u": float(np.median(null)),
            "null_q05_abs_error_u": float(np.quantile(null, 0.05)),
            "null_q95_abs_error_u": float(np.quantile(null, 0.95)), "values": null.tolist()}


def metrics(summary: pd.DataFrame, control: dict | None = None) -> dict:
    q = summary[~summary.excluded].copy()
    eligible = q[q.target_t_s.notna()]
    child = eligible[eligible.child_prediction_t_s.notna()]
    matched_parent = child[child.parent_prediction_t_s.notna()]
    out = {
        "eligible_events": int(len(eligible)), "child_forecasts": int(len(child)),
        "child_coverage": float(len(child) / len(eligible)) if len(eligible) else np.nan,
        "pre_target_issue_fraction": float((child.child_issue_t_s < child.target_t_s).mean()) if len(child) else np.nan,
        "median_issue_lead_s": float((child.target_t_s - child.child_issue_t_s).median()) if len(child) else np.nan,
        "median_child_abs_error_s": float(child.child_abs_error_s.median()) if len(child) else np.nan,
        "median_child_abs_error_u": float(child.child_abs_error_u.median()) if len(child) else np.nan,
        "median_parent_abs_error_u_matched": float(matched_parent.parent_abs_error_u.median()) if len(matched_parent) else np.nan,
        "median_capillary_abs_error_u_matched": float(child.capillary_abs_error_u.median()) if len(child) else np.nan,
        "median_parent_issue_lead_s_matched": float((matched_parent.target_t_s - matched_parent.parent_issue_t_s).median()) if len(matched_parent) else np.nan,
        "median_child_before_parent_issue_s": float((matched_parent.parent_issue_t_s - matched_parent.child_issue_t_s).median()) if len(matched_parent) else np.nan,
        "matched_parent_events": int(len(matched_parent)),
    }
    if control:
        obs = out["median_child_abs_error_u"]
        vals = np.asarray(control["values"], float)
        out["shift_p_le_observed"] = float((1 + np.sum(vals <= obs)) / (1 + len(vals)))
        out["shift_null_q05_abs_error_u"] = control["null_q05_abs_error_u"]
    return out


def svg_report(summary: pd.DataFrame, series: pd.DataFrame, result: dict, mode: str) -> str:
    good = summary[(~summary.excluded) & summary.child_prediction_t_s.notna()].copy()
    example = None
    if len(good):
        good["rank_error"] = (good.child_abs_error_u - good.child_abs_error_u.median()).abs()
        example = good.sort_values("rank_error").iloc[0]

    def line_path(x, y, x0, y0, w, h, xmin, xmax, ymin=0, ymax=2):
        ok = np.isfinite(x) & np.isfinite(y)
        pts = []
        for a, b in zip(x[ok], y[ok]):
            px = x0 + w * (a - xmin) / max(xmax - xmin, 1e-12)
            py = y0 + h * (1 - (b - ymin) / max(ymax - ymin, 1e-12))
            pts.append(f"{px:.1f},{py:.1f}")
        return "M" + " L".join(pts) if pts else ""

    example_svg = ""
    if example is not None:
        g = series[series.Name == example.Name].sort_values("Time_s")
        tx = g.Time_s.to_numpy(float)
        xmax = float(tx.max())
        pc = line_path(tx, g.x_child_connection_ara.to_numpy(float), 80, 140, 650, 270, 0, xmax)
        pp = line_path(tx, g.x_parent_causal_ara.to_numpy(float), 80, 140, 650, 270, 0, xmax)
        def vx(v): return 80 + 650 * float(v) / xmax
        marks = [(example.child_issue_t_s, "#c47c00", "child issue"),
                 (example.child_prediction_t_s, "#1769aa", "forecast"),
                 (example.target_t_s, "#252525", "offline parent target")]
        vertical = "".join(f'<line x1="{vx(v):.1f}" y1="140" x2="{vx(v):.1f}" y2="410" stroke="{c}" stroke-width="2" stroke-dasharray="7 5"/><text x="{vx(v)+4:.1f}" y="{128-14*i}" fill="{c}" font-size="12">{lab}: {v:.3f}s</text>' for i,(v,c,lab) in enumerate(marks))
        example_svg = f'<path d="{pc}" fill="none" stroke="#c47c00" stroke-width="2.5"/><path d="{pp}" fill="none" stroke="#1769aa" stroke-width="2.5"/>{vertical}'

    # predicted versus observed
    vals = good[["target_t_s", "child_prediction_t_s"]].to_numpy(float) if len(good) else np.empty((0,2))
    vmax = float(np.nanmax(vals)) if vals.size else 1.0
    dots = "".join(f'<circle cx="{810+500*a/vmax:.1f}" cy="{410-270*b/vmax:.1f}" r="4" fill="#1769aa" opacity=".55"/>' for a,b in vals)
    # error bars
    keys = [("Child", result.get("median_child_abs_error_u", np.nan), "#c47c00"),
            ("Parent-only", result.get("median_parent_abs_error_u_matched", np.nan), "#8a96a3"),
            ("Capillary", result.get("median_capillary_abs_error_u_matched", np.nan), "#8a96a3")]
    emax = max([v for _,v,_ in keys if np.isfinite(v)] + [0.1]) * 1.15
    bars = "".join(f'<rect x="{120+170*i}" y="{760-220*v/emax:.1f}" width="90" height="{220*v/emax:.1f}" fill="{c}" stroke="#252525"/><text x="{165+170*i}" y="{785}" text-anchor="middle">{k}</text><text x="{165+170*i}" y="{748-220*v/emax:.1f}" text-anchor="middle" font-family="monospace">{v:.4f}</text>' for i,(k,v,c) in enumerate(keys) if np.isfinite(v))

    gates = [
        ("coverage >= .75", result.get("child_coverage", 0) >= .75, result.get("child_coverage", np.nan)),
        ("pre-target >= .70", result.get("pre_target_issue_fraction", 0) >= .70, result.get("pre_target_issue_fraction", np.nan)),
        ("median lead > 0", result.get("median_issue_lead_s", -1) > 0, result.get("median_issue_lead_s", np.nan)),
        ("median |error| u <= .10", result.get("median_child_abs_error_u", 1) <= .10, result.get("median_child_abs_error_u", np.nan)),
        ("issues before parent-only", result.get("median_child_before_parent_issue_s", -1) > 0, result.get("median_child_before_parent_issue_s", np.nan)),
        ("shift p <= .05", result.get("shift_p_le_observed", 1) <= .05, result.get("shift_p_le_observed", np.nan)),
    ]
    gate_rows = "".join(f'<text x="810" y="{665+31*i}" font-size="15">{("PASS" if ok else "FAIL"):4s}  {lab}</text><text x="1270" y="{665+31*i}" text-anchor="end" font-family="monospace">{val:.5f}</text>' for i,(lab,ok,val) in enumerate(gates))
    overall = all(x[1] for x in gates)
    title = f"T411D — {mode} causal child-to-parent forecast"
    subtitle = f"{result.get('child_forecasts',0)} forecasts / {result.get('eligible_events',0)} eligible · {'SUPPORTED' if overall else 'NOT SUPPORTED'} by frozen six-gate rule"
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>{title}</title><style>body{{font:15px system-ui;margin:28px;color:#20262d;background:#fff}}h1{{margin:0}}p{{max-width:1300px}}svg{{border:1px solid #ccd3da;background:#fbfcfd}}code{{background:#eef1f4;padding:2px 5px}}table{{border-collapse:collapse}}td,th{{padding:6px 10px;border-bottom:1px solid #ddd;text-align:right}}td:first-child,th:first-child{{text-align:left}}</style></head><body><h1>{title}</h1><p>{subtitle}</p><p><b>Reading:</b> orange is the connection-heavy child ARA; blue is the causal parent ARA. Every forecast line is generated from past frames only. The black target is the earlier centred T411C reconstruction and is used only for scoring.</p><svg width="1380" height="930" viewBox="0 0 1380 930"><text x="80" y="85" font-size="20" font-weight="700">Representative event — causal coordinates through physical time</text><text x="80" y="108">ARA coordinate (0 movement-heavy · 1 ridge · 2 connection-heavy); time in seconds</text><line x1="80" y1="275" x2="730" y2="275" stroke="#252525" stroke-dasharray="5 5"/><text x="85" y="268">ridge 1.0</text><line x1="80" y1="410" x2="730" y2="410" stroke="#59636e"/><line x1="80" y1="140" x2="80" y2="410" stroke="#59636e"/>{example_svg}<text x="810" y="85" font-size="20" font-weight="700">Forecast versus offline parent target</text><text x="810" y="108">Each dot is one eligible filament; both axes in seconds</text><line x1="810" y1="410" x2="1310" y2="140" stroke="#252525" stroke-dasharray="6 5"/><line x1="810" y1="410" x2="1310" y2="410" stroke="#59636e"/><line x1="810" y1="140" x2="810" y2="410" stroke="#59636e"/>{dots}<text x="1060" y="438" text-anchor="middle">observed offline parent target (s)</text><text x="80" y="510" font-size="20" font-weight="700">Median normalized absolute timing error</text><text x="80" y="533">Fraction of each filament's directly observed breakup lifetime; lower is better</text><line x1="90" y1="760" x2="650" y2="760" stroke="#59636e"/>{bars}<text x="810" y="510" font-size="20" font-weight="700">Frozen holdout gates</text><text x="810" y="533">Values are printed beside every decision; no hidden pass/fail labels</text>{gate_rows}</svg><h2>Exact event values</h2>{good[['Name','fluid','target_t_s','child_issue_t_s','child_prediction_t_s','child_error_s','child_abs_error_u','parent_abs_error_u','capillary_abs_error_u']].round(6).to_html(index=False)}<p><b>Source:</b> T411 source-qualified filament data and supplementary metadata. <b>Protocol:</b> <code>T411D_CAUSAL_CHILD_PROTOCOL.md</code>.</p></body></html>'''


def run_development() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    series, summary = load_events(DEV)
    active = summary[~summary.excluded].copy()
    child_offset = median_positive_offset(active, "child_issue_t_s")
    # A negative parent offset backdates an alarm and is not a deployable
    # forecast.  Parent-only therefore alarms at its causal issue time when
    # the development median offset is negative.
    parent_offset = max(0.0, median_positive_offset(active, "parent_issue_t_s"))
    params = {
        "version": "T411D-v1", "development_fluids": sorted(DEV), "holdout_fluids": sorted(HOLD),
        "persistence_frames": PERSISTENCE, "arm_level": ARM_LEVEL,
        "child_scale_fraction": 0.5, "child_offset_s": child_offset,
        "parent_offset_s": parent_offset, "development_events": int(len(active)),
        "protocol_sha256": sha256(HERE / "T411D_CAUSAL_CHILD_PROTOCOL.md"),
        "script_sha256": sha256(Path(__file__)),
        "source_data_sha256": sha256(t411c.RAW),
    }
    pred = add_predictions(summary, params)
    control = shifted_control(series, pred, child_offset)
    result = metrics(pred, control)
    result["mode"] = "development"
    (OUT / "T411D_DEVELOPMENT_PARAMETERS_CANDIDATE.json").write_text(json.dumps(params, indent=2), encoding="utf-8")
    pred.to_csv(OUT / "T411D_DEVELOPMENT_EVENTS.csv", index=False)
    series.to_csv(OUT / "T411D_DEVELOPMENT_TIMESERIES.csv", index=False)
    (OUT / "T411D_DEVELOPMENT_RESULTS.json").write_text(json.dumps({**result, "shift_control": {k:v for k,v in control.items() if k != 'values'}}, indent=2), encoding="utf-8")
    (OUT / "T411D_DEVELOPMENT_REPORT.html").write_text(svg_report(pred, series, result, "development"), encoding="utf-8")
    print(json.dumps({"parameters": params, "results": result}, indent=2))


def freeze() -> None:
    candidate = OUT / "T411D_DEVELOPMENT_PARAMETERS_CANDIDATE.json"
    if not candidate.exists():
        raise RuntimeError("Run development before freeze")
    PARAMS.write_text(candidate.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Frozen {PARAMS}")


def run_holdout() -> None:
    if not PARAMS.exists():
        raise RuntimeError("Frozen parameters missing")
    params = json.loads(PARAMS.read_text(encoding="utf-8"))
    if params["protocol_sha256"] != sha256(HERE / "T411D_CAUSAL_CHILD_PROTOCOL.md"):
        raise RuntimeError("Protocol changed after freeze")
    if params["script_sha256"] != sha256(Path(__file__)):
        raise RuntimeError("Script changed after freeze")
    if params["source_data_sha256"] != sha256(t411c.RAW):
        raise RuntimeError("Source data changed after freeze")
    series, summary = load_events(HOLD)
    pred = add_predictions(summary, params)
    control = shifted_control(series, pred, params["child_offset_s"])
    result = metrics(pred, control)
    result["mode"] = "sealed_holdout"
    result["frozen_parameters"] = params
    pred.to_csv(OUT / "T411D_HOLDOUT_EVENTS.csv", index=False)
    series.to_csv(OUT / "T411D_HOLDOUT_TIMESERIES.csv", index=False)
    (OUT / "T411D_HOLDOUT_RESULTS.json").write_text(json.dumps({**result, "shift_control": {k:v for k,v in control.items() if k != 'values'}}, indent=2), encoding="utf-8")
    (OUT / "T411D_HOLDOUT_REPORT.html").write_text(svg_report(pred, series, result, "sealed holdout"), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["development", "freeze", "holdout"])
    args = ap.parse_args()
    {"development": run_development, "freeze": freeze, "holdout": run_holdout}[args.mode]()
