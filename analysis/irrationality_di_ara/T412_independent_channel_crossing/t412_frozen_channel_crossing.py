from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE = (
    HERE.parent
    / "T411_time_facing_filament_breakup"
    / "results"
    / "T411J_parity_oriented_closure"
    / "T411J_SCORED_SNAPSHOTS.csv"
)
OUT = HERE / "results"
SEED = 4122026
SHIFT_REPS = 2000


def weighted_auc(y: np.ndarray, score: np.ndarray, weight: np.ndarray) -> float:
    keep = np.isfinite(y) & np.isfinite(score) & np.isfinite(weight) & (weight > 0)
    y, score, weight = y[keep], score[keep], weight[keep]
    pos, neg = y == 1, y == 0
    if not pos.any() or not neg.any():
        return float("nan")
    total_pos_weight = float(weight[pos].sum())
    total_neg_weight = float(weight[neg].sum())
    order = np.argsort(score, kind="mergesort")
    y, score, weight = y[order], score[order], weight[order]
    starts = np.r_[0, np.flatnonzero(score[1:] != score[:-1]) + 1]
    pos_weight = np.add.reduceat(weight * (y == 1), starts)
    neg_weight = np.add.reduceat(weight * (y == 0), starts)
    neg_before = np.r_[0.0, np.cumsum(neg_weight)[:-1]]
    concordant = float(np.sum(pos_weight * (neg_before + 0.5 * neg_weight)))
    return concordant / (total_pos_weight * total_neg_weight)


def build_crossings(frame: pd.DataFrame, column: str, direction: str, persistence: int = 1) -> pd.DataFrame:
    records: list[dict] = []
    for (partition, name), group in frame.groupby(["partition", "Name"], sort=True):
        group = group.sort_values("time_s").reset_index(drop=True)
        x = group[column].to_numpy(float)
        if direction == "forward":
            candidates = np.flatnonzero((x[:-1] < 0) & (x[1:] >= 0)) + 1
            condition = lambda values: np.all(values >= 0)
        else:
            candidates = np.flatnonzero((x[:-1] >= 0) & (x[1:] < 0)) + 1
            condition = lambda values: np.all(values < 0)
        for index in candidates:
            stop = index + persistence
            if stop > len(group) or not condition(x[index:stop]):
                continue
            row = group.iloc[index]
            records.append({
                "partition": partition,
                "Name": name,
                "fluid": row.fluid,
                "direction": direction,
                "persistence": persistence,
                "time_s": float(row.time_s),
                "lead_s": float(row.lead_s),
                "lead_child_horizons": float(row.lead_child_horizons),
                "inside_event_window": bool(0 < row.lead_child_horizons <= 1),
            })
    return pd.DataFrame(records)


def crossing_metrics(crossings: pd.DataFrame, events: int) -> dict[str, float | int]:
    if crossings.empty:
        return {
            "crossings": 0,
            "event_window_crossings": 0,
            "event_window_concentration": float("nan"),
            "events_hit": 0,
            "event_hit_rate": 0.0,
            "early_crossings_per_event": 0.0,
            "median_warning_child_horizons": float("nan"),
        }
    event_crossings = crossings[crossings.inside_event_window]
    return {
        "crossings": int(len(crossings)),
        "event_window_crossings": int(len(event_crossings)),
        "event_window_concentration": float(len(event_crossings) / len(crossings)),
        "events_hit": int(event_crossings.Name.nunique()),
        "event_hit_rate": float(event_crossings.Name.nunique() / events),
        "early_crossings_per_event": float((~crossings.inside_event_window).sum() / events),
        "median_warning_child_horizons": float(event_crossings.lead_child_horizons.median()) if len(event_crossings) else float("nan"),
    }


def shifted_controls(primary: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    ordered = primary.sort_values(["Name", "time_s"]).reset_index(drop=True)
    groups = [indices.to_numpy(int) for _, indices in ordered.groupby("Name", sort=True).groups.items()]
    y = ordered.y.to_numpy(int)
    weight = ordered.event_weight.to_numpy(float)
    d = ordered.D.to_numpy(float)
    rng = np.random.default_rng(SEED)
    null_rows = []
    for repetition in range(SHIFT_REPS):
        shifted = np.empty_like(d)
        for indices in groups:
            if len(indices) <= 1:
                shifted[indices] = d[indices]
            else:
                shifted[indices] = np.roll(d[indices], int(rng.integers(1, len(indices))))
        crossing_total = 0
        event_window_crossings = 0
        events_hit = 0
        for indices in groups:
            values = shifted[indices]
            crossing_local = np.flatnonzero((values[:-1] < 0) & (values[1:] >= 0)) + 1
            crossing_total += len(crossing_local)
            if len(crossing_local):
                inside = y[indices[crossing_local]] == 1
                event_window_crossings += int(inside.sum())
                events_hit += int(inside.any())
        null_rows.append({
            "repetition": repetition,
            "auc": weighted_auc(y, shifted, weight),
            "crossing_concentration": event_window_crossings / crossing_total if crossing_total else np.nan,
            "event_hit_rate": events_hit / len(groups),
        })
    null = pd.DataFrame(null_rows)
    observed_auc = weighted_auc(y, d, weight)
    observed_crossings = crossing_metrics(
        build_crossings(ordered, "D", "forward", 1), ordered.Name.nunique()
    )
    summary = {
        "observed_auc": observed_auc,
        "auc_null_mean": float(null.auc.mean()),
        "auc_null_95": float(null.auc.quantile(0.95)),
        "p_auc_null_ge_observed": float((1 + (null.auc >= observed_auc).sum()) / (1 + len(null))),
        "observed_crossing_concentration": float(observed_crossings["event_window_concentration"]),
        "crossing_concentration_null_mean": float(null.crossing_concentration.mean()),
        "crossing_concentration_null_95": float(null.crossing_concentration.quantile(0.95)),
        "p_crossing_null_ge_observed": float(
            (1 + (null.crossing_concentration >= observed_crossings["event_window_concentration"]).sum())
            / (1 + len(null))
        ),
    }
    return null, summary


def svg_dashboard(profile: pd.DataFrame, null: pd.DataFrame, crossings: pd.DataFrame, performance: pd.DataFrame, result: dict) -> str:
    width, height = 1160, 760
    panels = [(40, 55, 520, 275), (600, 55, 520, 275), (40, 405, 520, 275), (600, 405, 520, 275)]
    parts = [f"<svg viewBox='0 0 {width} {height}' role='img' aria-label='T412 diagnostic charts'>",
             "<style>.t{font:13px system-ui;fill:#27313d}.h{font:700 17px system-ui;fill:#17202a}.g{stroke:#dfe5eb;stroke-width:1}.a{stroke:#56616f;stroke-width:1.2}.lab{font:11px system-ui;fill:#4b5563}</style>"]

    def frame(panel, title, xlabel, ylabel):
        x, y, w, h = panel
        parts.append(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='10' fill='#fff' stroke='#dce3ea'/><text class='h' x='{x+18}' y='{y+28}'>{title}</text>")
        parts.append(f"<line class='a' x1='{x+58}' y1='{y+45}' x2='{x+58}' y2='{y+h-48}'/><line class='a' x1='{x+58}' y1='{y+h-48}' x2='{x+w-18}' y2='{y+h-48}'/>")
        parts.append(f"<text class='lab' x='{x+w/2}' y='{y+h-13}' text-anchor='middle'>{xlabel}</text><text class='lab' x='{x+13}' y='{y+h/2}' transform='rotate(-90 {x+13} {y+h/2})' text-anchor='middle'>{ylabel}</text>")
        return x+58, y+45, w-76, h-93

    # Panel 1: lead profile.
    x0, y0, pw, ph = frame(panels[0], "Channel dominance approaches breakup", "Lead before breakup (child horizons)", "Mean score")
    ymin = float(min(-0.15, profile.min().min()))
    ymax = float(max(0.75, profile.max().max()))
    def py(v): return y0 + ph * (ymax - float(v)) / (ymax - ymin)
    labels = profile.index.astype(str).tolist()
    for value in np.linspace(ymin, ymax, 5):
        yy = py(value); parts.append(f"<line class='g' x1='{x0}' y1='{yy:.1f}' x2='{x0+pw}' y2='{yy:.1f}'/><text class='lab' x='{x0-7}' y='{yy+4:.1f}' text-anchor='end'>{value:.2f}</text>")
    colours = {"D":"#6f42c1", "H_child":"#d97706", "H_grandchild":"#0f766e"}
    for ci, column in enumerate(["D", "H_child", "H_grandchild"]):
        pts=[]
        for i, value in enumerate(profile[column]):
            xx=x0+pw*i/max(1,len(profile)-1); yy=py(value); pts.append(f"{xx:.1f},{yy:.1f}")
            parts.append(f"<circle cx='{xx:.1f}' cy='{yy:.1f}' r='3' fill='{colours[column]}'/>")
        parts.append(f"<polyline points='{' '.join(pts)}' fill='none' stroke='{colours[column]}' stroke-width='2.4'/><text class='lab' x='{x0+8+ci*120}' y='{y0+15}' fill='{colours[column]}'>{column}</text>")
    for i, label in enumerate(labels):
        xx=x0+pw*i/max(1,len(labels)-1); parts.append(f"<text class='lab' x='{xx:.1f}' y='{y0+ph+17}' text-anchor='middle'>{label}</text>")

    # Panel 2: shift-null histogram.
    x0, y0, pw, ph = frame(panels[1], "Time-shift control", "Event-balanced AUC", "Shifted runs")
    values = null.auc.dropna().to_numpy(float)
    counts, edges = np.histogram(values, bins=30)
    maxc=max(1,int(counts.max())); xmin=float(edges[0]); xmax=float(edges[-1])
    for i,c in enumerate(counts):
        bx=x0+pw*i/len(counts); bw=pw/len(counts)-1; bh=ph*c/maxc
        parts.append(f"<rect x='{bx:.1f}' y='{y0+ph-bh:.1f}' width='{bw:.1f}' height='{bh:.1f}' fill='#b7c9e2'/>")
    for value, colour, dash, label in [(result['shift_control']['observed_auc'],'#6f42c1','', 'observed'),(result['shift_control']['auc_null_95'],'#c0392b','5 4','null 95%')]:
        xx=x0+pw*(value-xmin)/(xmax-xmin); parts.append(f"<line x1='{xx:.1f}' y1='{y0}' x2='{xx:.1f}' y2='{y0+ph}' stroke='{colour}' stroke-width='2' stroke-dasharray='{dash}'/><text class='lab' x='{xx+4:.1f}' y='{y0+14}' fill='{colour}'>{label} {value:.3f}</text>")
    parts.append(f"<text class='lab' x='{x0}' y='{y0+ph+17}'>{xmin:.3f}</text><text class='lab' x='{x0+pw}' y='{y0+ph+17}' text-anchor='end'>{xmax:.3f}</text>")

    # Panel 3: every forward crossing by fluid.
    x0, y0, pw, ph = frame(panels[2], "Every causal forward crossing", "Lead before breakup (child horizons; clipped at 12)", "Fluid")
    fluids=["S1","S2","S3","S4"]; colours={"S1":"#1f77b4","S2":"#ff7f0e","S3":"#2ca02c","S4":"#d62728"}
    c=crossings[(crossings.partition=='diagnostic') & (crossings.direction=='forward') & (crossings.persistence==1)].copy()
    parts.append(f"<rect x='{x0}' y='{y0}' width='{pw/12:.1f}' height='{ph}' fill='#9fd5b3' opacity='.35'/>")
    for i,fluid in enumerate(fluids):
        yy=y0+ph*(i+.5)/4; parts.append(f"<text class='lab' x='{x0-7}' y='{yy+4:.1f}' text-anchor='end'>{fluid}</text>")
        group=c[c.fluid==fluid]
        for _,row in group.iterrows():
            lead=min(12,max(0,float(row.lead_child_horizons))); xx=x0+pw*lead/12
            parts.append(f"<circle cx='{xx:.1f}' cy='{yy:.1f}' r='2.4' fill='{colours[fluid]}' opacity='.55'/>")
    for value in [0,1,2,4,8,12]:
        xx=x0+pw*value/12; parts.append(f"<line class='g' x1='{xx:.1f}' y1='{y0}' x2='{xx:.1f}' y2='{y0+ph}'/><text class='lab' x='{xx:.1f}' y='{y0+ph+17}' text-anchor='middle'>{value}</text>")

    # Panel 4: principal metrics.
    x0, y0, pw, ph = frame(panels[3], "Frozen diagnostic comparisons", "Metric", "Value")
    diag=performance[(performance.partition=='diagnostic') & performance.metric.isin(['auc_D','auc_H_child','auc_H_grandchild','forward_p1_concentration','forward_p1_hit_rate'])].copy()
    barcols=['#6f42c1','#d97706','#0f766e','#457b9d','#8a9a5b']
    for i,(_,row) in enumerate(diag.iterrows()):
        bw=pw/len(diag)*.65; xx=x0+pw*(i+.5)/len(diag)-bw/2; bh=ph*float(row.value)
        parts.append(f"<rect x='{xx:.1f}' y='{y0+ph-bh:.1f}' width='{bw:.1f}' height='{bh:.1f}' fill='{barcols[i]}'/><text class='lab' x='{xx+bw/2:.1f}' y='{y0+ph-bh-5:.1f}' text-anchor='middle'>{row.value:.3f}</text><text class='lab' x='{xx+bw/2:.1f}' y='{y0+ph+17}' text-anchor='middle'>{row.metric.replace('_',' ')}</text>")
    yy=y0+ph*.5; parts.append(f"<line x1='{x0}' y1='{yy:.1f}' x2='{x0+pw}' y2='{yy:.1f}' stroke='#333' stroke-dasharray='5 4'/><text class='lab' x='{x0+4}' y='{yy-4:.1f}'>0.5</text>")
    parts.append("</svg>")
    return "".join(parts)


def make_report(
    frame: pd.DataFrame,
    performance: pd.DataFrame,
    crossings: pd.DataFrame,
    null: pd.DataFrame,
    result: dict,
) -> str:
    primary = frame[frame.partition == "diagnostic"].copy()
    # Lead profile.
    bins = [0, 0.5, 1, 2, 4, 8, np.inf]
    labels = ["0–0.5", "0.5–1", "1–2", "2–4", "4–8", ">8"]
    primary["lead_bin"] = pd.cut(primary.lead_child_horizons, bins=bins, labels=labels, right=True)
    profile = primary.groupby("lead_bin", observed=True).apply(
        lambda g: pd.Series({
            "D": np.average(g.D, weights=g.event_weight),
            "H_child": np.average(g.handover_child_flip, weights=g.event_weight),
            "H_grandchild": np.average(g.handover_grandchild_flip, weights=g.event_weight),
        }), include_groups=False
    )
    dashboard = svg_dashboard(profile, null, crossings, performance, result)

    gate_rows = "".join(
        f"<tr><td>{key.replace('_', ' ')}</td><td class={'pass' if value else 'fail'}>{'PASS' if value else 'FAIL'}</td></tr>"
        for key, value in result["gates"].items()
    )
    diag_rows = performance[performance.partition == "diagnostic"].to_html(index=False, float_format=lambda x: f"{x:.6f}")
    conclusion = result["conclusion"]
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>T412 frozen channel crossing</title>
<style>body{{font:16px/1.5 system-ui;margin:0;background:#f5f7fa;color:#19202a}}main{{max-width:1200px;margin:auto;padding:32px}}.card{{background:white;border:1px solid #d9e0e8;border-radius:14px;padding:22px;margin:18px 0;box-shadow:0 3px 14px #0000000d}}h1{{margin-bottom:4px}}.outcome{{font-size:1.2rem;font-weight:700}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #dfe5eb;padding:9px;text-align:left}}.pass{{color:#08783e;font-weight:700}}.fail{{color:#b42318;font-weight:700}}code{{background:#eef1f5;padding:2px 5px;border-radius:4px}}img{{width:100%;height:auto}}</style></head>
<body><main><h1>T412 — Frozen child-to-grandchild channel crossing</h1><p>123 filament-breakup events · primary diagnostic partition: 82 events · no fitted classifier</p>
<section class='card'><div class='outcome'>{conclusion}</div><p>The continuous difference <code>D = H_G − H_C</code> is stronger than either absolute channel, but support requires correct temporal alignment—not merely a plausible shape.</p></section>
<section class='card'><h2>ARA relation</h2><p><code>H_C = H(v,−u,w)</code>, <code>H_G = H(v,u,−w)</code>. The tested handover is the causal negative→nonnegative crossing of <code>D(t)=H_G−H_C</code>.</p></section>
<section class='card'>{dashboard}</section>
<section class='card'><h2>Frozen gates</h2><table>{gate_rows}</table></section>
<section class='card'><h2>Diagnostic numbers</h2>{diag_rows}</section>
<section class='card'><h2>Interpretation boundary</h2><p>This is a retrospective causal audit of a lead noticed in T411J. It can reject or retain that operational rule, but it is not an independent replication because the same 123 events exposed the lead.</p></section>
</main></body></html>"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(SOURCE).sort_values(["partition", "Name", "time_s"]).reset_index(drop=True)
    frame["D"] = frame.handover_grandchild_flip - frame.handover_child_flip

    perf_rows = []
    fluid_rows = []
    all_crossings = []
    for partition, part in frame.groupby("partition", sort=True):
        y = part.y.to_numpy(int)
        w = part.event_weight.to_numpy(float)
        metrics = {
            "auc_D": weighted_auc(y, part.D.to_numpy(float), w),
            "auc_H_child": weighted_auc(y, part.handover_child_flip.to_numpy(float), w),
            "auc_H_grandchild": weighted_auc(y, part.handover_grandchild_flip.to_numpy(float), w),
        }
        for metric, value in metrics.items():
            perf_rows.append({"partition": partition, "metric": metric, "value": value})
        for direction in ["forward", "reverse"]:
            for persistence in [1, 2]:
                crossing = build_crossings(part, "D", direction, persistence)
                all_crossings.append(crossing)
                cm = crossing_metrics(crossing, part.Name.nunique())
                perf_rows.extend([
                    {"partition": partition, "metric": f"{direction}_p{persistence}_concentration", "value": cm["event_window_concentration"]},
                    {"partition": partition, "metric": f"{direction}_p{persistence}_hit_rate", "value": cm["event_hit_rate"]},
                ])
        for fluid, group in part.groupby("fluid", sort=True):
            fluid_rows.append({
                "partition": partition,
                "fluid": fluid,
                "events": int(group.Name.nunique()),
                "auc_D": weighted_auc(group.y.to_numpy(int), group.D.to_numpy(float), group.event_weight.to_numpy(float)),
            })

    performance = pd.DataFrame(perf_rows)
    fluid_performance = pd.DataFrame(fluid_rows)
    crossings = pd.concat(all_crossings, ignore_index=True)
    primary = frame[frame.partition == "diagnostic"].copy()
    null, shift_summary = shifted_controls(primary)
    diag = performance[performance.partition == "diagnostic"].set_index("metric").value
    gates = {
        "diagnostic_D_auc_above_chance": bool(diag["auc_D"] > 0.5),
        "diagnostic_D_beats_both_absolute_channels": bool(diag["auc_D"] > max(diag["auc_H_child"], diag["auc_H_grandchild"])),
        "time_shift_auc_p_le_005": bool(shift_summary["p_auc_null_ge_observed"] <= 0.05),
        "forward_crossing_concentration_above_shift_95": bool(
            shift_summary["observed_crossing_concentration"] > shift_summary["crossing_concentration_null_95"]
        ),
        "D_auc_above_chance_in_at_least_three_of_four_fluids": bool((fluid_performance.auc_D > 0.5).sum() >= 3),
    }
    passed = sum(gates.values())
    conclusion = (
        "SUPPORTED in-source: the frozen channel crossing passed every gate."
        if passed == len(gates)
        else f"NOT YET SUPPORTED: the frozen channel crossing passed {passed}/{len(gates)} gates."
    )
    result = {
        "status": "frozen_retrospective_causal_channel_crossing",
        "source": str(SOURCE),
        "events": {p: int(g.Name.nunique()) for p, g in frame.groupby("partition")},
        "definition": "D(t)=H_grandchild_flip(t)-H_child_flip(t); crossing D(t-1)<0<=D(t)",
        "shift_control": shift_summary,
        "gates": gates,
        "gates_passed": passed,
        "gates_total": len(gates),
        "conclusion": conclusion,
        "claim_boundary": "same-source retrospective causal audit; not independent replication",
        "protocol_erratum": "Cross-fluid gate uses each fluid's prescribed partition because diagnostic contains only S2 and S4.",
        "validation": {
            "unique_partition_name_time": bool(not frame.duplicated(["partition", "Name", "time_s"]).any()),
            "all_predictors_precede_target": bool((frame.time_s < frame.target_t_s).all()),
            "stored_switch_matches_recalculation": bool(np.allclose(frame.D, frame.posthoc_channel_switch)),
            "coordinates_inside_0_2": bool(frame[["x_parent", "x_child", "x_grandchild"]].ge(0).all().all() and frame[["x_parent", "x_child", "x_grandchild"]].le(2).all().all()),
        },
    }

    performance.to_csv(OUT / "T412_PERFORMANCE.csv", index=False)
    fluid_performance.to_csv(OUT / "T412_FLUID_PERFORMANCE.csv", index=False)
    crossings.to_csv(OUT / "T412_CROSSINGS.csv", index=False)
    null.to_csv(OUT / "T412_TIME_SHIFT_NULL.csv", index=False)
    (OUT / "T412_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (OUT / "T412_FROZEN_CHANNEL_CROSSING_REPORT.html").write_text(
        make_report(frame, performance, crossings, null, result), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
