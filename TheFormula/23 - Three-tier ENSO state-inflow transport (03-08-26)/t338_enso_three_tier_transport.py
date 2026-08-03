#!/usr/bin/env python3
"""T338: frozen three-tier ENSO state/inflow transport test.

The protocol is frozen in T338_ENSO_THREE_TIER_TRANSPORT_PROTOCOL_v1_FROZEN.md.
This runner deliberately retains all three atmospheric-flow cuts and scores
positive leads only. It does not fit a forecasting model.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
DEV_START = pd.Timestamp("1980-01-01")
DEV_END = pd.Timestamp("2004-12-01")
HOLD_START = pd.Timestamp("2005-01-01")
HOLD_END = pd.Timestamp("2025-12-01")
LEADS = range(1, 19)
SEED = 338
BOOT_REPS = 2000
BLOCK = 24


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def numeric_tokens(line: str) -> list[float]:
    return [
        float(x)
        for x in re.findall(
            r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?", line
        )
    ]


def rows_to_series(rows: list[tuple[pd.Timestamp, float]], name: str) -> pd.Series:
    s = pd.Series(dict(rows), name=name, dtype=float).sort_index()
    s.index = pd.DatetimeIndex(s.index)
    return s[~s.index.duplicated(keep="last")]


def load_nino(path: Path) -> pd.Series:
    rows: list[tuple[pd.Timestamp, float]] = []
    with path.open(encoding="utf-8-sig", errors="replace") as fh:
        reader = csv.reader(fh)
        next(reader)
        for row in reader:
            if len(row) < 2:
                continue
            try:
                dt = pd.Timestamp(row[0].strip()).replace(day=1)
                value = float(row[1])
            except (ValueError, TypeError):
                continue
            if value > -90:
                rows.append((dt, value))
    return rows_to_series(rows, "nino34_raw")


def load_year_table(path: Path, name: str, section: str | None = None) -> pd.Series:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = 0
    if section:
        matches = [i for i, line in enumerate(lines) if section.upper() in line.upper()]
        if not matches:
            raise ValueError(f"Section {section!r} not found in {path}")
        start = matches[-1] + 1
    rows: list[tuple[pd.Timestamp, float]] = []
    for line in lines[start:]:
        vals = numeric_tokens(line)
        if len(vals) < 13:
            continue
        year = int(vals[0])
        if year < 1800 or year > 2100:
            continue
        for month, value in enumerate(vals[1:13], start=1):
            if value > -90 and value < 90:
                rows.append((pd.Timestamp(year=year, month=month, day=1), value))
    return rows_to_series(rows, name)


def load_wwv(path: Path, name: str) -> pd.Series:
    rows: list[tuple[pd.Timestamp, float]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        vals = numeric_tokens(line)
        if len(vals) < 3:
            continue
        code = int(vals[0])
        year, month = code // 100, code % 100
        if year < 1900 or not 1 <= month <= 12:
            continue
        anomaly = vals[2]
        if math.isfinite(anomaly):
            rows.append((pd.Timestamp(year=year, month=month, day=1), anomaly))
    return rows_to_series(rows, name)


def fixed_scale(s: pd.Series, dev_mask: pd.Series) -> tuple[pd.Series, float]:
    scale = float(s[dev_mask].std(ddof=0))
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError(f"Invalid development scale for {s.name}: {scale}")
    return s / scale, scale


def bacc_from_sign(driver: np.ndarray, target: np.ndarray) -> tuple[float, float, float, int]:
    driver = np.asarray(driver, dtype=float)
    target = np.asarray(target, dtype=float)
    ok = np.isfinite(driver) & np.isfinite(target) & (driver != 0) & (target != 0)
    driver = np.sign(driver[ok])
    target = np.sign(target[ok])
    pos = target > 0
    neg = target < 0
    rec_pos = float(np.mean(driver[pos] > 0)) if np.any(pos) else float("nan")
    rec_neg = float(np.mean(driver[neg] < 0)) if np.any(neg) else float("nan")
    bacc = float(np.nanmean([rec_pos, rec_neg]))
    return bacc, rec_pos, rec_neg, int(ok.sum())


def spearman(driver: np.ndarray, target: np.ndarray) -> float:
    driver = np.asarray(driver, dtype=float)
    target = np.asarray(target, dtype=float)
    ok = np.isfinite(driver) & np.isfinite(target)
    if ok.sum() < 3:
        return float("nan")
    x = pd.Series(driver[ok]).rank(method="average").to_numpy()
    y = pd.Series(target[ok]).rank(method="average").to_numpy()
    return float(np.corrcoef(x, y)[0, 1])


def block_boot_ci(driver: np.ndarray, target: np.ndarray, seed: int) -> tuple[float, float]:
    driver = np.asarray(driver, dtype=float)
    target = np.asarray(target, dtype=float)
    ok = np.isfinite(driver) & np.isfinite(target) & (driver != 0) & (target != 0)
    driver, target = driver[ok], target[ok]
    n = len(driver)
    if n < BLOCK * 2:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    starts = np.arange(max(1, n - BLOCK + 1))
    values: list[float] = []
    blocks_needed = int(math.ceil(n / BLOCK))
    for _ in range(BOOT_REPS):
        chosen = rng.choice(starts, size=blocks_needed, replace=True)
        idx = np.concatenate([np.arange(s, min(s + BLOCK, n)) for s in chosen])[:n]
        score, _, _, _ = bacc_from_sign(driver[idx], target[idx])
        if math.isfinite(score):
            values.append(score)
    if not values:
        return float("nan"), float("nan")
    return tuple(float(x) for x in np.quantile(values, [0.025, 0.975]))


def month_preserving_shuffle(s: pd.Series, seed: int) -> pd.Series:
    rng = np.random.default_rng(seed)
    out = s.copy()
    for month in range(1, 13):
        idx = np.flatnonzero(s.index.month == month)
        vals = s.iloc[idx].to_numpy(copy=True)
        rng.shuffle(vals)
        out.iloc[idx] = vals
    return out


@dataclass
class PathSpec:
    name: str
    driver: str
    state: str
    family: str


def aligned_arrays(df: pd.DataFrame, driver: str, state: str, lead: int, mask: pd.Series):
    future_change = df[state].shift(-lead) - df[state]
    valid = mask & df[driver].notna() & future_change.notna()
    return df.loc[valid, driver].to_numpy(), future_change.loc[valid].to_numpy(), valid


def score_at_lead(df: pd.DataFrame, spec: PathSpec, lead: int, mask: pd.Series) -> dict:
    driver, target, valid = aligned_arrays(df, spec.driver, spec.state, lead, mask)
    bacc, rec_pos, rec_neg, n = bacc_from_sign(driver, target)
    rho = spearman(driver, target) if n >= 3 else float("nan")
    return {
        "path": spec.name,
        "family": spec.family,
        "driver": spec.driver,
        "state": spec.state,
        "lead": lead,
        "bacc": bacc,
        "recall_el_nino_direction": rec_pos,
        "recall_la_nina_direction": rec_neg,
        "spearman": rho,
        "n": n,
        "valid_mask": valid,
        "driver_values": driver,
        "target_values": target,
    }


def select_lead(df: pd.DataFrame, spec: PathSpec, dev_mask: pd.Series) -> tuple[int, list[dict]]:
    grid = [score_at_lead(df, spec, h, dev_mask & (df.index + pd.offsets.MonthBegin(h) <= DEV_END)) for h in LEADS]
    finite = [r for r in grid if math.isfinite(r["bacc"])]
    if not finite:
        raise ValueError(f"No finite development scores for {spec.name}")
    best = sorted(finite, key=lambda r: (-r["bacc"], r["lead"]))[0]
    return int(best["lead"]), grid


def clean_result(r: dict) -> dict:
    return {k: v for k, v in r.items() if k not in {"valid_mask", "driver_values", "target_values"}}


def json_safe(value):
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (float, np.floating)) and not math.isfinite(float(value)):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def main() -> None:
    inputs = sorted(DATA.iterdir())
    hashes = {p.name: sha256(p) for p in inputs if p.is_file()}

    series = {
        "nino34_raw": load_nino(DATA / "nino34_long_anom.csv"),
        "soi_raw": load_year_table(DATA / "soi.data", "soi_raw"),
        "wwv_east_raw": load_wwv(DATA / "wwv_east.dat", "wwv_east_raw"),
        "wwv_west_raw": load_wwv(DATA / "wwv_west.dat", "wwv_west_raw"),
        "wind_w_raw": load_year_table(DATA / "wpac850.data", "wind_w_raw", "STANDARDIZED"),
        "wind_c_raw": load_year_table(DATA / "cpac850.data", "wind_c_raw", "STANDARDIZED"),
        "wind_e_raw": load_year_table(DATA / "epac850.data", "wind_e_raw", "STANDARDIZED"),
        "olr_raw": load_year_table(DATA / "olr.data", "olr_raw", "STANDARDIZED"),
        "heat_raw": load_year_table(DATA / "heatcentra.data", "heat_raw"),
    }
    df = pd.concat(series.values(), axis=1).sort_index()
    df = df.loc[DEV_START:HOLD_END].copy()
    dev_mask = pd.Series((df.index >= DEV_START) & (df.index <= DEV_END), index=df.index)
    hold_mask = pd.Series((df.index >= HOLD_START) & (df.index <= HOLD_END), index=df.index)

    # Fixed development-only unit translations.
    scales: dict[str, float] = {}
    df["ocean_state"], scales["nino34"] = fixed_scale(df["nino34_raw"], dev_mask)
    soi_z, scales["soi"] = fixed_scale(df["soi_raw"], dev_mask)
    df["atmos_state"] = -soi_z
    olr_z, scales["olr"] = fixed_scale(df["olr_raw"], dev_mask)
    df["atmos_state_olr"] = -olr_z

    redistribution = df["wwv_east_raw"] - df["wwv_west_raw"]
    df["wwv_redistribution_raw"] = redistribution
    ocean_flow_raw = redistribution.diff()
    df["ocean_flow"], scales["wwv_redistribution_change"] = fixed_scale(ocean_flow_raw, dev_mask)

    for region in ["w", "c", "e"]:
        z, scales[f"wind_{region}"] = fixed_scale(df[f"wind_{region}_raw"], dev_mask)
        df[f"atmos_flow_{region}"] = -z
    df["atmos_flow_median"] = df[["atmos_flow_w", "atmos_flow_c", "atmos_flow_e"]].median(axis=1)

    heat_flow_raw = df["heat_raw"].diff()
    df["heat_flow"], scales["heat_change"] = fixed_scale(heat_flow_raw, dev_mask)

    # Uncompressed four-grandchild state and declared parent ARA compression.
    df["la_ocean"] = (-df["ocean_state"]).clip(lower=0)
    df["la_atmos"] = (-df["atmos_state"]).clip(lower=0)
    df["el_ocean"] = df["ocean_state"].clip(lower=0)
    df["el_atmos"] = df["atmos_state"].clip(lower=0)
    la_sum = df["la_ocean"] + df["la_atmos"]
    el_sum = df["el_ocean"] + df["el_atmos"]
    df["ara_la_child"] = np.where(la_sum > 0, 2 * df["la_atmos"] / la_sum, np.nan)
    df["ara_el_child"] = np.where(el_sum > 0, 2 * df["el_atmos"] / el_sum, np.nan)
    parent_sum = la_sum + el_sum
    df["ara_parent"] = np.where(parent_sum > 0, 2 * el_sum / parent_sum, 1.0)
    df["parent_signed"] = df["ara_parent"] - 1.0

    # Supplementary relation of the two inflow branches.
    flow_total = df["ocean_flow"].abs() + df["atmos_flow_median"].abs()
    el_flow = df["ocean_flow"].clip(lower=0) + df["atmos_flow_median"].clip(lower=0)
    df["ara_parent_flow"] = np.where(flow_total > 0, 2 * el_flow / flow_total, 1.0)
    df["parent_flow_signed"] = df["ara_parent_flow"] - 1.0

    specs = [
        PathSpec("ocean WWV redistribution → Niño3.4", "ocean_flow", "ocean_state", "ocean"),
        PathSpec("west trade wind → SOI", "atmos_flow_w", "atmos_state", "atmosphere"),
        PathSpec("central trade wind → SOI", "atmos_flow_c", "atmos_state", "atmosphere"),
        PathSpec("east trade wind → SOI", "atmos_flow_e", "atmos_state", "atmosphere"),
        PathSpec("nested inflow relation → ENSO parent", "parent_flow_signed", "parent_signed", "parent"),
        PathSpec("west trade wind → OLR replication", "atmos_flow_w", "atmos_state_olr", "replication"),
        PathSpec("central trade wind → OLR replication", "atmos_flow_c", "atmos_state_olr", "replication"),
        PathSpec("east trade wind → OLR replication", "atmos_flow_e", "atmos_state_olr", "replication"),
        PathSpec("heat-content change → Niño3.4 replication", "heat_flow", "ocean_state", "replication"),
    ]

    results: list[dict] = []
    dev_grids: dict[str, list[dict]] = {}
    control_results: dict[str, dict] = {}
    chosen_leads: dict[str, int] = {}

    for i, spec in enumerate(specs):
        lead, grid = select_lead(df, spec, dev_mask)
        chosen_leads[spec.name] = lead
        dev_grids[spec.name] = [clean_result(r) for r in grid]
        hold = score_at_lead(df, spec, lead, hold_mask & (df.index + pd.offsets.MonthBegin(lead) <= HOLD_END))
        ci_low, ci_high = block_boot_ci(hold["driver_values"], hold["target_values"], SEED + i)
        hold["ci95_low"] = ci_low
        hold["ci95_high"] = ci_high
        hold["pass"] = bool(
            hold["bacc"] > 0.55
            and ci_low > 0.50
            and hold["spearman"] > 0
            and hold["recall_el_nino_direction"] > 0.50
            and hold["recall_la_nina_direction"] > 0.50
        )
        results.append(clean_result(hold))

        # Frozen controls at the selected lead.
        driver_name = spec.driver
        original = df[driver_name].copy()
        controls: dict[str, dict] = {}
        for cname, controlled in {
            "wrong_orientation": -original,
            "time_reversed": pd.Series(original.to_numpy()[::-1], index=original.index),
            "month_preserving_shuffled_years": month_preserving_shuffle(original, SEED + 100 + i),
        }.items():
            tmp = df.copy()
            tmp["_control"] = controlled
            cspec = PathSpec(spec.name, "_control", spec.state, spec.family)
            cr = score_at_lead(tmp, cspec, lead, hold_mask & (tmp.index + pd.offsets.MonthBegin(lead) <= HOLD_END))
            controls[cname] = clean_result(cr)
        momentum = df[spec.state].diff()
        tmp = df.copy()
        tmp["_momentum"] = momentum
        cspec = PathSpec(spec.name, "_momentum", spec.state, spec.family)
        controls["last_movement_persistence"] = clean_result(
            score_at_lead(tmp, cspec, lead, hold_mask & (tmp.index + pd.offsets.MonthBegin(lead) <= HOLD_END))
        )
        control_results[spec.name] = controls

    primary_ocean = next(r for r in results if r["family"] == "ocean")
    primary_atmos = [r for r in results if r["family"] == "atmosphere"]
    passing_atmos = sum(bool(r["pass"]) for r in primary_atmos)
    if primary_ocean["pass"] and passing_atmos >= 2:
        verdict = "SUPPORTED"
    elif primary_ocean["pass"] or passing_atmos > 0:
        verdict = "MIXED"
    else:
        verdict = "NOT_SUPPORTED"

    coverage = {
        name: {
            "start": str(s.dropna().index.min().date()) if s.notna().any() else None,
            "end": str(s.dropna().index.max().date()) if s.notna().any() else None,
            "n": int(s.notna().sum()),
        }
        for name, s in series.items()
    }
    payload = {
        "test": "T338",
        "verdict": verdict,
        "architecture_gate": {
            "ocean_pass": bool(primary_ocean["pass"]),
            "atmospheric_paths_passing": passing_atmos,
            "atmospheric_paths_required": 2,
        },
        "protocol_sha256": sha256(HERE / "T338_ENSO_THREE_TIER_TRANSPORT_PROTOCOL_v1_FROZEN.md"),
        "input_sha256": hashes,
        "coverage": coverage,
        "development": [str(DEV_START.date()), str(DEV_END.date())],
        "holdout": [str(HOLD_START.date()), str(HOLD_END.date())],
        "development_scales": scales,
        "chosen_leads": chosen_leads,
        "holdout_results": results,
        "controls": control_results,
        "development_lead_grids": dev_grids,
    }
    payload = json_safe(payload)
    (HERE / "T338_ENSO_THREE_TIER_TRANSPORT_RESULTS.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8"
    )

    export_cols = [
        "nino34_raw", "soi_raw", "olr_raw", "wwv_east_raw", "wwv_west_raw",
        "wind_w_raw", "wind_c_raw", "wind_e_raw", "heat_raw", "ocean_state",
        "atmos_state", "atmos_state_olr", "la_ocean", "la_atmos", "el_ocean",
        "el_atmos", "ara_la_child", "ara_el_child", "ara_parent", "ocean_flow",
        "atmos_flow_w", "atmos_flow_c", "atmos_flow_e", "ara_parent_flow",
    ]
    out_df = df.loc[DEV_START:HOLD_END, export_cols].copy()
    out_df.index.name = "date"
    out_df.to_csv(HERE / "T338_ENSO_THREE_TIER_TRANSPORT_COORDINATES.csv", float_format="%.17g")

    make_figure(df, results, dev_grids, verdict)
    print(json.dumps({"verdict": verdict, "architecture_gate": payload["architecture_gate"]}, indent=2))


def make_figure(df: pd.DataFrame, results: list[dict], dev_grids: dict[str, list[dict]], verdict: str) -> None:
    """Write a dependency-free SVG overview."""
    width, height = 1500, 1460
    left, right = 90, 1450
    panel_h = 285
    starts = [100, 425, 750, 1075]

    def esc(s: str) -> str:
        return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

    def line_path(values: pd.Series, y0: float, ymin: float, ymax: float) -> str:
        vals = values.to_numpy(dtype=float)
        points = []
        for i, v in enumerate(vals):
            if not math.isfinite(v):
                continue
            x = left + (right - left) * i / max(1, len(vals) - 1)
            y = y0 + panel_h - 35 - (panel_h - 70) * (v - ymin) / (ymax - ymin)
            points.append((x, y))
        return " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(points))

    def hline(y0: float, value: float, ymin: float, ymax: float, color: str, dash: str = "") -> str:
        y = y0 + panel_h - 35 - (panel_h - 70) * (value - ymin) / (ymax - ymin)
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        return f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="{color}" stroke-width="1"{extra}/>'

    hold_idx = int(np.searchsorted(df.index.to_numpy(), HOLD_START.to_datetime64()))
    hold_x = left + (right - left) * hold_idx / max(1, len(df) - 1)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#111827}.title{font-size:28px;font-weight:700}.panel{font-size:20px;font-weight:700}.small{font-size:14px}.axis{font-size:13px;fill:#4b5563}</style>',
        '<text x="70" y="45" class="title">T338 — ENSO three-tier ARA state/inflow transport</text>',
    ]
    for y0 in starts:
        svg.append(f'<rect x="50" y="{y0}" width="1420" height="{panel_h}" rx="8" fill="white" stroke="#cbd5e1"/>')
        svg.append(f'<line x1="{hold_x:.1f}" y1="{y0+45}" x2="{hold_x:.1f}" y2="{y0+panel_h-25}" stroke="#7c3aed" stroke-width="2" stroke-dasharray="5,5"/>')

    y0 = starts[0]
    svg += [
        f'<text x="70" y="{y0+30}" class="panel">Parent: 0 La Niña ↔ 2 El Niño</text>',
        hline(y0, 0, 0, 2, "#2563eb", "4,4"), hline(y0, 1, 0, 2, "#111827"), hline(y0, 2, 0, 2, "#dc2626", "4,4"),
        f'<path d="{line_path(df["ara_parent"], y0, 0, 2)}" fill="none" stroke="#6b7280" stroke-width="1.5"/>',
        f'<text x="{hold_x+6:.1f}" y="{y0+62}" class="small">holdout</text>',
    ]

    y0 = starts[1]
    svg += [
        f'<text x="70" y="{y0+30}" class="panel">Children retained separately: 0 ocean-led ↔ 2 atmosphere-led</text>',
        hline(y0, 1, 0, 2, "#111827"),
        f'<path d="{line_path(df["ara_la_child"], y0, 0, 2)}" fill="none" stroke="#2563eb" stroke-width="1.2"/>',
        f'<path d="{line_path(df["ara_el_child"], y0, 0, 2)}" fill="none" stroke="#dc2626" stroke-width="1.2"/>',
        f'<text x="100" y="{y0+58}" class="small" fill="#2563eb">La Niña child</text>',
        f'<text x="220" y="{y0+58}" class="small" fill="#dc2626">El Niño child</text>',
    ]

    y0 = starts[2]
    flow_cols = [("ocean_flow", "#0f766e"), ("atmos_flow_w", "#f59e0b"), ("atmos_flow_c", "#ea580c"), ("atmos_flow_e", "#9a3412")]
    all_flow = df[[c for c, _ in flow_cols]].to_numpy(dtype=float)
    bound = float(np.nanquantile(np.abs(all_flow), .99))
    svg += [
        f'<text x="70" y="{y0+30}" class="panel">Uncompressed inflows: positive El-Niño-directed, negative La-Niña-directed</text>',
        hline(y0, 0, -bound, bound, "#111827"),
    ]
    for col, color in flow_cols:
        svg.append(f'<path d="{line_path(df[col], y0, -bound, bound)}" fill="none" stroke="{color}" stroke-width="1" opacity="0.75"/>')
    svg.append(f'<text x="100" y="{y0+58}" class="small">ocean / west / central / east atmospheric cuts</text>')

    y0 = starts[3]
    primary = [r for r in results if r["family"] in {"ocean", "atmosphere", "parent"}]
    svg += [
        f'<text x="70" y="{y0+30}" class="panel">Holdout balanced directional accuracy — architecture verdict: {esc(verdict)}</text>',
        hline(y0, .5, .35, .8, "#111827"), hline(y0, .55, .35, .8, "#7c3aed", "5,5"),
    ]
    bar_space = (right - left) / len(primary)
    base_y = y0 + panel_h - 35
    for i, r in enumerate(primary):
        x = left + i * bar_space + 20
        bw = bar_space - 40
        top = y0 + panel_h - 35 - (panel_h - 70) * (r["bacc"] - .35) / (.8 - .35)
        color = "#16a34a" if r["pass"] else "#9ca3af"
        svg.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{base_y-top:.1f}" fill="{color}" stroke="#374151"/>')
        svg.append(f'<text x="{x+bw/2:.1f}" y="{top-7:.1f}" text-anchor="middle" class="small">{r["bacc"]:.3f} · h{r["lead"]}</text>')
        short = r["path"].split(" → ")[0]
        svg.append(f'<text x="{x+bw/2:.1f}" y="{base_y+20:.1f}" text-anchor="middle" class="small">{esc(short)}</text>')

    svg.append('</svg>')
    (HERE / "T338_ENSO_THREE_TIER_TRANSPORT_VISUAL.svg").write_text("\n".join(svg), encoding="utf-8")


if __name__ == "__main__":
    main()
