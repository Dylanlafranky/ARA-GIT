#!/usr/bin/env python3
"""
T302 — empirical Phi handover in ordered Arabidopsis phyllotaxis.

Frozen protocol:
  ARA_PHI_EMPIRICAL_CALIBRATION_PROTOCOL_2026-07-30.md

Public source:
  Tameshige et al. (2025), Nature Communications
  DOI 10.1038/s41467-025-65792-y

The script downloads the publisher's source-data archive, verifies both the
archive and selected workbook hashes, reconstructs ordered meristem sequences,
and writes the complete ARA geometry and frozen endpoint results.
"""

from __future__ import annotations

import hashlib
import json
import math
import urllib.request
import zipfile
from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
ARCHIVE_PATH = DATA_DIR / "41467_2025_65792_MOESM9_ESM.zip"
WORKBOOK_PATH = DATA_DIR / "Source Data 21.xlsx"

SOURCE_URL = (
    "https://media.springernature.com/original/springer-static/esm/"
    "art%3A10.1038%2Fs41467-025-65792-y/MediaObjects/"
    "41467_2025_65792_MOESM9_ESM.zip"
)
ARCHIVE_SHA256 = "1D93DE8B177F7556525DBCA07D34F1D40880DA33F68DC44ECCF93BBC7CB0D563"
WORKBOOK_SHA256 = "E78372214B1386A486B25C8340C19F22BC74D3382F80A9B36A2972CC3D35ADFB"
WORKBOOK_MEMBER = (
    "Tameshige_et_al_codes_v251010/code_main/Figure6/Source Data 21.xlsx"
)

RESULT_JSON = HERE / "T302_PHI_PHYLLOTAXIS_RESULTS.json"
EVENT_CSV = HERE / "T302_PHI_PHYLLOTAXIS_EVENT_GEOMETRY.csv"
PLANT_CSV = HERE / "T302_PHI_PHYLLOTAXIS_PLANT_SUMMARY.csv"
CANDIDATE_CSV = HERE / "T302_PHI_PHYLLOTAXIS_CANDIDATES.csv"
VISUALIZATION_PATH = HERE / "T302_PHI_PHYLLOTAXIS_VISUALIZATION.html"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_A = PHI ** -2
PHI_B = PHI
RNG_SEED = 302
SHUFFLES = 10_000
BOOTSTRAPS = 5_000

FIXED_CANDIDATES = OrderedDict(
    [
        ("one_third", 1.0 / 3.0),
        ("one_over_e", 1.0 / math.e),
        ("three_eighths", 3.0 / 8.0),
        ("phi", PHI_A),
        ("eight_twenty_firsts", 8.0 / 21.0),
        ("two_fifths", 2.0 / 5.0),
        ("silver_conjugate", math.sqrt(2.0) - 1.0),
    ]
)

COLORS = {"Col": "#3569a8", "e2": "#d18a2c", "e1e2": "#9b4d87"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def ensure_source() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE_PATH.exists():
        print(f"Downloading public source data:\n  {SOURCE_URL}")
        urllib.request.urlretrieve(SOURCE_URL, ARCHIVE_PATH)
    observed_archive_hash = sha256(ARCHIVE_PATH)
    if observed_archive_hash != ARCHIVE_SHA256:
        raise RuntimeError(
            f"Archive SHA-256 mismatch: {observed_archive_hash} != {ARCHIVE_SHA256}"
        )

    if not WORKBOOK_PATH.exists():
        with zipfile.ZipFile(ARCHIVE_PATH) as archive:
            payload = archive.read(WORKBOOK_MEMBER)
        WORKBOOK_PATH.write_bytes(payload)
    observed_workbook_hash = sha256(WORKBOOK_PATH)
    if observed_workbook_hash != WORKBOOK_SHA256:
        raise RuntimeError(
            f"Workbook SHA-256 mismatch: {observed_workbook_hash} != {WORKBOOK_SHA256}"
        )


def circular_abs_turn(delta: np.ndarray | float) -> np.ndarray | float:
    return np.abs((np.asarray(delta) + 0.5) % 1.0 - 0.5)


def circular_mean_turn(values: np.ndarray) -> float:
    angles = 2.0 * np.pi * np.asarray(values, dtype=float)
    value = math.atan2(float(np.sin(angles).mean()), float(np.cos(angles).mean()))
    return (value / (2.0 * np.pi)) % 1.0


def add_plant_ids(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    plant_ids: list[int] = []
    counts: dict[str, int] = {}
    for row in output.itertuples(index=False):
        genotype = str(row.genotype)
        meristem = int(row.meristem)
        if genotype not in counts or meristem == 1:
            counts[genotype] = counts.get(genotype, 0) + 1
        plant_ids.append(counts[genotype])
    output["plant"] = plant_ids
    output["split"] = np.where(output["plant"] % 2 == 1, "development", "confirmation")

    failures: list[tuple[str, int, list[int]]] = []
    for (genotype, plant), group in output.groupby(["genotype", "plant"], sort=False):
        observed = group["meristem"].astype(int).tolist()
        expected = list(range(1, len(observed) + 1))
        if observed != expected:
            failures.append((str(genotype), int(plant), observed))
    if failures:
        raise RuntimeError(f"Non-sequential meristem records: {failures}")
    return output


def placement_geometry(turns: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    positions: list[float] = [0.0]
    cumulative: list[float] = []
    clearance: list[float] = []
    optimal_clearance: list[float] = []

    current = 0.0
    for turn in np.asarray(turns, dtype=float):
        ordered = np.sort(np.asarray(positions))
        gaps = np.diff(np.r_[ordered, ordered[0] + 1.0])
        best = 0.5 * float(gaps.max())

        current = (current + float(turn)) % 1.0
        nearest = min(float(circular_abs_turn(current - p)) for p in positions)
        score = nearest / best if best > 0.0 else np.nan

        cumulative.append(current)
        clearance.append(score)
        optimal_clearance.append(best)
        positions.append(current)

    return (
        np.asarray(cumulative),
        np.asarray(clearance),
        np.asarray(optimal_clearance),
    )


def bootstrap_median_ci(values: np.ndarray, rng: np.random.Generator) -> list[float]:
    values = np.asarray(values, dtype=float)
    draws = rng.choice(values, size=(BOOTSTRAPS, len(values)), replace=True)
    medians = np.median(draws, axis=1)
    return [float(np.quantile(medians, 0.025)), float(np.quantile(medians, 0.975))]


def spearman_rank(values_x: np.ndarray, values_y: np.ndarray) -> float:
    ranks_x = pd.Series(np.asarray(values_x)).rank(method="average").to_numpy()
    ranks_y = pd.Series(np.asarray(values_y)).rank(method="average").to_numpy()
    if np.std(ranks_x) == 0.0 or np.std(ranks_y) == 0.0:
        return float("nan")
    return float(np.corrcoef(ranks_x, ranks_y)[0, 1])


def spearman_permutation_p(
    values_x: np.ndarray, values_y: np.ndarray, observed: float, draws: int = 10_000
) -> float:
    rng = np.random.default_rng(RNG_SEED + 2)
    values_y = np.asarray(values_y)
    exceed = 0
    for _ in range(draws):
        permuted = rng.permutation(values_y)
        if abs(spearman_rank(values_x, permuted)) >= abs(observed):
            exceed += 1
    return float((exceed + 1) / (draws + 1))


def adjacent_error_geometry(
    groups: list[pd.DataFrame], rng_seed: int, draws: int = 10_000
) -> dict[str, float | int | list[dict[str, float]]]:
    sequences = [
        group.sort_values("meristem")["x_A"].to_numpy(dtype=float) - PHI_A
        for group in groups
    ]
    x = np.concatenate([sequence[:-1] for sequence in sequences])
    y = np.concatenate([sequence[1:] for sequence in sequences])
    rho = spearman_rank(x, y)
    individual = 0.5 * (np.abs(x) + np.abs(y))
    pair_mean = np.abs(0.5 * (x + y))

    rng = np.random.default_rng(rng_seed)
    null = np.empty(draws, dtype=float)
    for draw in range(draws):
        null_x: list[float] = []
        null_y: list[float] = []
        for sequence in sequences:
            permuted = rng.permutation(sequence)
            null_x.extend(permuted[:-1].tolist())
            null_y.extend(permuted[1:].tolist())
        null[draw] = spearman_rank(np.asarray(null_x), np.asarray(null_y))
    p_negative = float((1 + np.sum(null <= rho)) / (draws + 1))

    return {
        "pairs": int(len(x)),
        "spearman_rho": float(rho),
        "within_plant_order_shuffle_p_negative": p_negative,
        "shuffle_rho_median": float(np.median(null)),
        "shuffle_rho_95": [
            float(np.quantile(null, 0.025)),
            float(np.quantile(null, 0.975)),
        ],
        "median_individual_error_turn": float(np.median(individual)),
        "median_pair_mean_error_turn": float(np.median(pair_mean)),
        "pair_mean_over_individual_error_ratio": float(
            np.median(pair_mean) / np.median(individual)
        ),
        "pairs_xy": [
            {"previous_error": float(a), "next_error": float(b)}
            for a, b in zip(x, y)
        ],
    }


def constant_benchmark(candidates: OrderedDict[str, float]) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for name, step in candidates.items():
        for horizon in range(4, 56):
            positions = np.sort((np.arange(horizon, dtype=float) * step) % 1.0)
            gaps = np.diff(np.r_[positions, positions[0] + 1.0])
            rows.append(
                {
                    "candidate": name,
                    "horizon": horizon,
                    "largest_gap": float(gaps.max()),
                    "minimum_gap": float(gaps.min()),
                    "gap_cv": float(gaps.std(ddof=0) / gaps.mean()),
                }
            )
    benchmark = pd.DataFrame(rows)
    benchmark["largest_gap_rank"] = benchmark.groupby("horizon")["largest_gap"].rank(
        method="min", ascending=True
    )
    benchmark["minimum_gap_rank"] = benchmark.groupby("horizon")["minimum_gap"].rank(
        method="min", ascending=False
    )
    return benchmark


def representative_plant(plant_summary: pd.DataFrame, genotype: str) -> int:
    group = plant_summary[
        (plant_summary["genotype"] == genotype)
        & (plant_summary["split"] == "confirmation")
    ].copy()
    target = group["clearance_median"].median()
    idx = (group["clearance_median"] - target).abs().idxmin()
    return int(group.loc[idx, "plant"])


def make_visualization(
    events: pd.DataFrame,
    plant_summary: pd.DataFrame,
    candidate_summary: pd.DataFrame,
    shuffle_null: np.ndarray,
    development_median: float,
    result: dict,
) -> None:
    ara_points = (
        events[
            (events["split"] == "confirmation") & events["heldout"]
        ][["genotype", "plant", "meristem", "x_A", "x_B_assigned"]]
        .to_dict(orient="records")
    )
    candidate_records = (
        candidate_summary[candidate_summary["candidate_type"] == "fixed"]
        .assign(
            order=lambda frame: frame["candidate"].map(
                {name: index for index, name in enumerate(FIXED_CANDIDATES)}
            )
        )
        .sort_values("order")
        .drop(columns=["order"])
        .to_dict(orient="records")
    )
    clearance_records = plant_summary[
        plant_summary["split"] == "confirmation"
    ][["genotype", "plant", "clearance_median"]].to_dict(orient="records")

    trajectories: list[dict] = []
    for genotype in ["Col", "e2", "e1e2"]:
        plant = representative_plant(plant_summary, genotype)
        subset = events[
            (events["genotype"] == genotype)
            & (events["plant"] == plant)
            & (events["split"] == "confirmation")
        ].sort_values("meristem")
        trajectories.append(
            {
                "name": f"{genotype} plant {plant}",
                "color": COLORS[genotype],
                "turns": [0.0] + subset["observed_position_turn"].astype(float).tolist(),
            }
        )
    max_n = int(
        events[(events["genotype"] == "Col") & (events["split"] == "confirmation")]
        .groupby("plant")
        .size()
        .median()
    )
    trajectories.append(
        {
            "name": "exact Phi generator",
            "color": "#e8792e",
            "turns": [float((index * PHI_A) % 1.0) for index in range(max_n + 1)],
        }
    )

    payload = {
        "phiA": PHI_A,
        "phiB": PHI_B,
        "developmentMedian": development_median,
        "araPoints": ara_points,
        "candidates": candidate_records,
        "clearance": clearance_records,
        "shuffle": {
            "median": float(np.median(shuffle_null)),
            "lo": float(np.quantile(shuffle_null, 0.025)),
            "hi": float(np.quantile(shuffle_null, 0.975)),
        },
        "trajectories": trajectories,
        "frozen": result["frozen"],
        "adjacent": result["secondary"]["adjacent_error_geometry"]["Col_confirmation"],
    }
    embedded = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>T302 — empirical Phi handover calibration</title>
<style>
:root {{ --ink:#172033; --muted:#667085; --grid:#d8dee8; --panel:#ffffff;
  --bg:#f4f6f9; --phi:#e8792e; --wt:#3569a8; --e2:#d18a2c; --e1e2:#9b4d87; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink);
  font:15px/1.45 Inter, ui-sans-serif, system-ui, sans-serif; }}
main {{ max-width:1480px; margin:0 auto; padding:28px; }}
h1 {{ margin:0; font-size:30px; letter-spacing:-.02em; }}
.sub {{ color:var(--muted); margin:5px 0 20px; }}
.cards {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px;
  margin-bottom:16px; }}
.card,.panel {{ background:var(--panel); border:1px solid #dfe4ec; border-radius:14px;
  box-shadow:0 4px 18px rgba(20,32,54,.05); }}
.card {{ padding:14px 16px; }}
.card b {{ display:block; font-size:22px; margin-top:4px; }}
.pass {{ color:#147a54; }} .fail {{ color:#ba3a32; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
.panel {{ padding:16px; min-width:0; }}
.panel h2 {{ margin:0 0 2px; font-size:18px; }}
.panel p {{ color:var(--muted); margin:0 0 10px; font-size:13px; }}
svg {{ width:100%; height:auto; overflow:visible; }}
.legend {{ display:flex; flex-wrap:wrap; gap:14px; color:var(--muted);
  font-size:13px; margin-top:5px; }}
.key {{ display:inline-flex; align-items:center; gap:6px; }}
.dot {{ width:10px; height:10px; border-radius:50%; display:inline-block; }}
.wide {{ grid-column:1 / -1; }}
.note {{ margin-top:16px; padding:14px 16px; border-left:4px solid var(--phi);
  background:#fff8f1; border-radius:8px; }}
@media (max-width:900px) {{ .cards,.grid {{ grid-template-columns:1fr; }}
  .wide {{ grid-column:auto; }} main {{ padding:16px; }} }}
</style>
</head>
<body>
<main>
  <h1>T302 — empirical Phi handover in ordered phyllotaxis</h1>
  <div class="sub">359 measured divergence angles · 58 meristems · public biological controls · frozen ARA mapping</div>
  <section class="cards" id="cards"></section>
  <section class="grid">
    <article class="panel">
      <h2>A. ARA diameter reading</h2>
      <p>Filled points are measured. Open points are the assigned mirror 2−x, not a second measurement.</p>
      <svg id="ara" viewBox="0 0 720 350"></svg>
      <div class="legend">
        <span class="key"><i class="dot" style="background:var(--wt)"></i>wild type</span>
        <span class="key"><i class="dot" style="background:var(--e2)"></i>e2</span>
        <span class="key"><i class="dot" style="background:var(--e1e2)"></i>e1e2</span>
      </div>
    </article>
    <article class="panel">
      <h2>B. Exact Phi versus frozen rivals</h2>
      <p>Plant-clustered confirmation medians; lower is better.</p>
      <svg id="candidates" viewBox="0 0 720 350"></svg>
    </article>
    <article class="panel">
      <h2>C. Ordered open-space clearance</h2>
      <p>Each dot is one confirmation plant. The grey interval is the within-plant shuffle null.</p>
      <svg id="clearance" viewBox="0 0 720 350"></svg>
    </article>
    <article class="panel">
      <h2>D. Placement trajectories</h2>
      <p>Representative physical sequences versus a supplied exact-Phi generator.</p>
      <svg id="trajectories" viewBox="0 0 720 350"></svg>
    </article>
    <article class="panel wide">
      <h2>E. The local children breathe around the longer Phi carrier</h2>
      <p>Each point is one measured wild-type step error followed by the next.
      The upper-left/lower-right tilt is not forced by the ARA mirror.</p>
      <svg id="compensation" viewBox="0 0 1120 360"></svg>
    </article>
    <article class="panel wide">
      <h2>Reading boundary</h2>
      <div class="note"><b>This is a calibration, not a discovery claim.</b>
      The source paper already identifies the golden-angle neighbourhood. The
      informative questions are whether exact Phi beats close rivals and whether
      measured biological order preserves open space. A forced mirror can illustrate
      ARA symmetry but cannot count as independent evidence.</div>
    </article>
  </section>
</main>
<script id="payload" type="application/json">{embedded}</script>
<script>
const D=JSON.parse(document.getElementById("payload").textContent);
const NS="http://www.w3.org/2000/svg";
const colors={{Col:"#3569a8",e2:"#d18a2c",e1e2:"#9b4d87"}};
function add(svg,tag,attrs={{}},text="") {{
  const n=document.createElementNS(NS,tag);
  Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));
  if(text) n.textContent=text; svg.appendChild(n); return n;
}}
function label(svg,x,y,text,attrs={{}}) {{
  return add(svg,"text",{{x,y,fill:"#4b5563","font-size":12,...attrs}},text);
}}
function line(svg,x1,y1,x2,y2,attrs={{}}) {{
  return add(svg,"line",{{x1,y1,x2,y2,stroke:"#d8dee8","stroke-width":1,...attrs}});
}}
function cards() {{
  const host=document.getElementById("cards");
  const p=D.frozen.passes;
  const items=[
    ["Frozen verdict",`${{D.frozen.score}}/4 · ${{D.frozen.verdict}}`,D.frozen.score>=2],
    ["P1 ARA landmark",D.frozen.P1_confirmation_wt_coordinate.toFixed(6),p.P1_landmark_within_0.01],
    ["P2 step winner",D.frozen.P2_fixed_step_winner,p.P2_exact_phi_step_winner],
    ["P3 carrier winner",D.frozen.P3_fixed_cumulative_winner,p.P3_exact_phi_cumulative_winner]
  ];
  items.forEach(([name,value,pass])=>{{
    const el=document.createElement("div"); el.className="card";
    el.innerHTML=`<span>${{name}}</span><b class="${{pass?"pass":"fail"}}">${{value}}</b>`;
    host.appendChild(el);
  }});
}}
function ara() {{
  const s=document.getElementById("ara"), L=78,R=690,T=38,B=305;
  const x=v=>L+(R-L)*v/2, ys={{Col:92,e2:172,e1e2:252}};
  [0,.382,1,1.618,2].forEach(v=>{{
    const exact=v===.382?D.phiA:v===1.618?D.phiB:v;
    line(s,x(exact),T,x(exact),B,{{stroke:v===1?"#3f4652":(v===.382||v===1.618?"#e8792e":"#d8dee8"),
      "stroke-dasharray":v===.382||v===1.618?"6 5":"none","stroke-width":v===1?1.5:1}});
    label(s,x(exact),326,v===.382?"φ⁻²":v===1.618?"φ":String(v),{{"text-anchor":"middle"}});
  }});
  Object.entries(ys).forEach(([g,y])=>{{
    line(s,L,y,R,y,{{stroke:"#eef1f5"}});
    label(s,L-10,y+4,g==="Col"?"wild type":g,{{"text-anchor":"end"}});
  }});
  D.araPoints.forEach((d,i)=>{{
    const y=ys[d.genotype]+(((i*37)%17)-8)*1.5;
    add(s,"circle",{{cx:x(d.x_A),cy:y,r:4,fill:colors[d.genotype],"fill-opacity":.7}});
    add(s,"circle",{{cx:x(d.x_B_assigned),cy:y,r:3.3,fill:"white",stroke:colors[d.genotype],
      "stroke-width":1.3,"stroke-opacity":.62}});
  }});
  label(s,x(D.phiA),24,"measured-side Phi",{{"text-anchor":"middle",fill:"#a64e13"}});
  label(s,x(1),24,"ridge",{{"text-anchor":"middle"}});
  label(s,x(D.phiB),24,"assigned mirror",{{"text-anchor":"middle",fill:"#a64e13"}});
  label(s,(L+R)/2,348,"ARA coordinate (0–2)",{{"text-anchor":"middle"}});
}}
function candidateChart() {{
  const s=document.getElementById("candidates"), L=56,R=700,T=30,B=292;
  const max=Math.max(...D.candidates.flatMap(d=>[d.step_error_median_deg,d.cumulative_error_median_deg]))*1.12;
  const y=v=>B-(B-T)*v/max, names={{one_third:"1/3",one_over_e:"1/e",three_eighths:"3/8",
    phi:"Phi",eight_twenty_firsts:"8/21",two_fifths:"2/5",silver_conjugate:"silver"}};
  [0,.25,.5,.75,1].forEach(q=>{{ const v=max*q; line(s,L,y(v),R,y(v));
    label(s,L-8,y(v)+4,v.toFixed(1),{{"text-anchor":"end"}}); }});
  const slot=(R-L)/D.candidates.length;
  D.candidates.forEach((d,i)=>{{
    const cx=L+slot*(i+.5), bw=slot*.28;
    add(s,"rect",{{x:cx-bw-2,y:y(d.step_error_median_deg),width:bw,height:B-y(d.step_error_median_deg),fill:"#4c78a8"}});
    add(s,"rect",{{x:cx+2,y:y(d.cumulative_error_median_deg),width:bw,height:B-y(d.cumulative_error_median_deg),fill:"#f2a541"}});
    label(s,cx,B+19,names[d.candidate],{{"text-anchor":"middle","font-weight":d.candidate==="phi"?"700":"400"}});
  }});
  label(s,16,(T+B)/2,"degrees",{{transform:`rotate(-90 16 ${{(T+B)/2}})`,"text-anchor":"middle"}});
  add(s,"rect",{{x:475,y:8,width:12,height:12,fill:"#4c78a8"}}); label(s,492,18,"step");
  add(s,"rect",{{x:545,y:8,width:12,height:12,fill:"#f2a541"}}); label(s,562,18,"cumulative");
}}
function clearanceChart() {{
  const s=document.getElementById("clearance"), L=62,R=690,T=28,B=298;
  const y=v=>B-(B-T)*v, xs={{Col:150,e2:305,e1e2:460,shuffle:620}};
  [0,.25,.5,.75,1].forEach(v=>{{line(s,L,y(v),R,y(v));label(s,L-8,y(v)+4,v.toFixed(2),{{"text-anchor":"end"}});}});
  Object.entries(xs).forEach(([g,x])=>label(s,x,B+22,g==="Col"?"wild type":g,{{"text-anchor":"middle"}}));
  ["Col","e2","e1e2"].forEach(g=>{{
    const vals=D.clearance.filter(d=>d.genotype===g).map(d=>d.clearance_median).sort((a,b)=>a-b);
    vals.forEach((v,i)=>add(s,"circle",{{cx:xs[g]+(((i*31)%13)-6)*3,cy:y(v),r:5,fill:colors[g],stroke:"white","stroke-width":1}}));
    const med=vals[Math.floor(vals.length/2)];
    line(s,xs[g]-38,y(med),xs[g]+38,y(med),{{stroke:colors[g],"stroke-width":3}});
  }});
  add(s,"rect",{{x:xs.shuffle-32,y:y(D.shuffle.hi),width:64,height:y(D.shuffle.lo)-y(D.shuffle.hi),fill:"#9ca3af","fill-opacity":.45}});
  add(s,"path",{{d:`M ${{xs.shuffle}} ${{y(D.shuffle.median)-7}} l 7 7 l -7 7 l -7 -7 z`,fill:"#4b5563"}});
  label(s,18,(T+B)/2,"normalized clearance",{{transform:`rotate(-90 18 ${{(T+B)/2}})`,"text-anchor":"middle"}});
}}
function trajectories() {{
  const s=document.getElementById("trajectories"), centers=[[95,150],[270,150],[445,150],[620,150]], radius=67;
  D.trajectories.forEach((tr,j)=>{{
    const [cx,cy]=centers[j]; add(s,"circle",{{cx,cy,r:radius,fill:"none",stroke:"#cbd5e1","stroke-width":1.2}});
    const pts=tr.turns.map((t,i)=>{{
      const a=2*Math.PI*t-Math.PI/2, r=8+i*(radius-13)/(tr.turns.length-1);
      return [cx+r*Math.cos(a),cy+r*Math.sin(a)];
    }});
    add(s,"polyline",{{points:pts.map(p=>p.join(",")).join(" "),fill:"none",stroke:tr.color,"stroke-width":2.2}});
    pts.forEach((p,i)=>{{add(s,"circle",{{cx:p[0],cy:p[1],r:4,fill:tr.color,stroke:"white","stroke-width":1}});
      label(s,p[0]+6,p[1]-5,String(i),{{"font-size":9}});}});
    label(s,cx,246,tr.name,{{"text-anchor":"middle","font-weight":"600"}});
  }});
  label(s,360,286,"radius shows placement order; angle shows cumulative position",{{"text-anchor":"middle"}});
}}
function compensation() {{
  const s=document.getElementById("compensation"), L=86,R=760,T=28,B=308;
  const pairs=D.adjacent.pairs_xy;
  const maxAbs=Math.max(.04,...pairs.flatMap(d=>[Math.abs(d.previous_error),Math.abs(d.next_error)]))*1.08;
  const x=v=>L+(R-L)*(v+maxAbs)/(2*maxAbs), y=v=>B-(B-T)*(v+maxAbs)/(2*maxAbs);
  [-1,-.5,0,.5,1].forEach(q=>{{
    const v=q*maxAbs; line(s,x(v),T,x(v),B,{{stroke:q===0?"#444b56":"#e6e9ef","stroke-width":q===0?1.5:1}});
    line(s,L,y(v),R,y(v),{{stroke:q===0?"#444b56":"#e6e9ef","stroke-width":q===0?1.5:1}});
    label(s,x(v),B+20,v.toFixed(3),{{"text-anchor":"middle"}});
    label(s,L-10,y(v)+4,v.toFixed(3),{{"text-anchor":"end"}});
  }});
  line(s,x(-maxAbs),y(maxAbs),x(maxAbs),y(-maxAbs),{{stroke:"#e8792e","stroke-dasharray":"7 5","stroke-width":1.5}});
  pairs.forEach(d=>add(s,"circle",{{cx:x(d.previous_error),cy:y(d.next_error),r:5,fill:"#3569a8","fill-opacity":.72,stroke:"white","stroke-width":.7}}));
  label(s,(L+R)/2,350,"previous step error from Phi (turn)",{{"text-anchor":"middle"}});
  label(s,24,(T+B)/2,"next step error",{{transform:`rotate(-90 24 ${{(T+B)/2}})`,"text-anchor":"middle"}});
  const X=825;
  label(s,X,75,"confirmation wild type",{{"font-size":14,"font-weight":"700",fill:"#172033"}});
  label(s,X,112,`adjacent ρ = ${{D.adjacent.spearman_rho.toFixed(3)}}`,{{"font-size":19,fill:"#3569a8"}});
  label(s,X,143,`order-shuffle p = ${{D.adjacent.within_plant_order_shuffle_p_negative.toFixed(4)}}`);
  label(s,X,185,"pair-mean error / child error",{{"font-size":13}});
  label(s,X,218,`${{D.adjacent.pair_mean_over_individual_error_ratio.toFixed(3)}}`,{{"font-size":26,"font-weight":"700",fill:"#e8792e"}});
  label(s,X,258,"Below 1 means opposite local deviations",{{"font-size":12}});
  label(s,X,277,"partly cancel in their two-step parent.",{{"font-size":12}});
}}
cards(); ara(); candidateChart(); clearanceChart(); trajectories(); compensation();
</script>
</body>
</html>"""
    VISUALIZATION_PATH.write_text(html, encoding="utf-8")


def main() -> None:
    ensure_source()
    raw = pd.read_excel(WORKBOOK_PATH, sheet_name="EPFL_phyllo-angle")
    expected_columns = ["genotype", "meristem", "angle"]
    if raw.columns.tolist() != expected_columns:
        raise RuntimeError(f"Unexpected columns: {raw.columns.tolist()}")
    if len(raw) != 359:
        raise RuntimeError(f"Unexpected row count: {len(raw)}")

    events = add_plant_ids(raw)
    events["angle_deg"] = events["angle"].astype(float)
    events["x_A"] = events["angle_deg"] / 360.0
    events["x_B_assigned"] = 2.0 - events["x_A"]
    events["heldout"] = events["meristem"] >= 3
    events["observed_position_turn"] = np.nan
    events["clearance_score"] = np.nan
    events["optimal_clearance_turn"] = np.nan

    for (_, _), group in events.groupby(["genotype", "plant"], sort=False):
        turns = group["x_A"].to_numpy()
        positions, clearance, optimal = placement_geometry(turns)
        events.loc[group.index, "observed_position_turn"] = positions
        events.loc[group.index, "clearance_score"] = clearance
        events.loc[group.index, "optimal_clearance_turn"] = optimal

    # Freeze the fitted development control before confirmation scoring.
    dev_col = events[
        (events["genotype"] == "Col")
        & (events["split"] == "development")
        & events["heldout"]
    ]
    dev_plant_medians = dev_col.groupby("plant")["x_A"].median()
    development_median = float(dev_plant_medians.median())

    plant_rows: list[dict[str, float | int | str]] = []
    candidate_rows: list[dict[str, float | int | str]] = []
    for (genotype, plant), group in events.groupby(["genotype", "plant"], sort=False):
        group = group.sort_values("meristem")
        turns = group["x_A"].to_numpy()
        actual_positions = group["observed_position_turn"].to_numpy()
        held_mask = group["heldout"].to_numpy(dtype=bool)
        early_mean = circular_mean_turn(turns[:2])
        split = str(group["split"].iloc[0])
        held_clearance = group.loc[group["heldout"], "clearance_score"].to_numpy()
        held_x = group.loc[group["heldout"], "x_A"].to_numpy()

        plant_rows.append(
            {
                "genotype": str(genotype),
                "plant": int(plant),
                "split": split,
                "n_angles": int(len(group)),
                "heldout_n": int(held_mask.sum()),
                "x_A_median": float(np.median(held_x)),
                "x_A_abs_phi_median": float(np.median(np.abs(held_x - PHI_A))),
                "clearance_median": float(np.median(held_clearance)),
                "early_mean_turn": float(early_mean),
            }
        )

        candidates = OrderedDict(FIXED_CANDIDATES)
        candidates["development_median"] = development_median
        candidates["plant_early_mean"] = early_mean
        for name, step in candidates.items():
            candidate_type = (
                "fixed"
                if name in FIXED_CANDIDATES
                else ("fitted_global" if name == "development_median" else "fitted_plant")
            )
            step_error = np.abs(turns[held_mask] - step) * 360.0
            predicted_positions = actual_positions.copy()
            if len(turns) >= 3:
                anchor = actual_positions[1]
                held_indices = np.flatnonzero(held_mask)
                predicted_positions[held_indices] = (
                    anchor + (held_indices - 1) * step
                ) % 1.0
            cumulative_error = (
                circular_abs_turn(actual_positions[held_mask] - predicted_positions[held_mask])
                * 360.0
            )
            candidate_rows.append(
                {
                    "genotype": str(genotype),
                    "plant": int(plant),
                    "split": split,
                    "candidate": name,
                    "candidate_type": candidate_type,
                    "turn_fraction": float(step),
                    "step_error_median_deg": float(np.median(step_error)),
                    "cumulative_error_median_deg": float(np.median(cumulative_error)),
                }
            )

    plant_summary = pd.DataFrame(plant_rows)
    plant_candidates = pd.DataFrame(candidate_rows)

    confirmation_wt = plant_summary[
        (plant_summary["genotype"] == "Col")
        & (plant_summary["split"] == "confirmation")
    ]
    p1_coordinate = float(confirmation_wt["x_A_median"].median())
    p1_pass = abs(p1_coordinate - PHI_A) <= 0.01

    confirm_candidate = plant_candidates[
        (plant_candidates["genotype"] == "Col")
        & (plant_candidates["split"] == "confirmation")
    ]
    candidate_summary = (
        confirm_candidate.groupby(["candidate", "candidate_type"], as_index=False)
        .agg(
            turn_fraction=("turn_fraction", "median"),
            step_error_median_deg=("step_error_median_deg", "median"),
            cumulative_error_median_deg=("cumulative_error_median_deg", "median"),
        )
    )
    fixed_summary = candidate_summary[
        candidate_summary["candidate_type"] == "fixed"
    ].copy()
    p2_winner = str(
        fixed_summary.loc[fixed_summary["step_error_median_deg"].idxmin(), "candidate"]
    )
    p3_winner = str(
        fixed_summary.loc[
            fixed_summary["cumulative_error_median_deg"].idxmin(), "candidate"
        ]
    )
    p2_pass = p2_winner == "phi"
    p3_pass = p3_winner == "phi"

    clearance_group = (
        plant_summary[plant_summary["split"] == "confirmation"]
        .groupby("genotype")["clearance_median"]
        .median()
        .to_dict()
    )
    p4_group_pass = (
        clearance_group["Col"] > clearance_group["e2"]
        and clearance_group["Col"] > clearance_group["e1e2"]
    )

    rng = np.random.default_rng(RNG_SEED)
    wt_even_groups = [
        group.sort_values("meristem")
        for (_, _), group in events[
            (events["genotype"] == "Col") & (events["split"] == "confirmation")
        ].groupby(["genotype", "plant"], sort=False)
    ]
    actual_clearance_stat = float(clearance_group["Col"])
    shuffle_null = np.empty(SHUFFLES, dtype=float)
    for draw in range(SHUFFLES):
        per_plant: list[float] = []
        for group in wt_even_groups:
            shuffled = rng.permutation(group["x_A"].to_numpy())
            _, clearance, _ = placement_geometry(shuffled)
            per_plant.append(float(np.median(clearance[2:])))
        shuffle_null[draw] = float(np.median(per_plant))
    shuffle_p = float((1 + np.sum(shuffle_null >= actual_clearance_stat)) / (SHUFFLES + 1))
    p4_shuffle_pass = shuffle_p < 0.05
    p4_pass = bool(p4_group_pass and p4_shuffle_pass)

    # Secondary adjacent-error geometry: does one local deviation tend to be
    # followed by an opposite deviation while the parent carrier stays near Phi?
    adjacent_geometry: dict[str, dict] = {}
    seed_offset = 0
    for genotype in ["Col", "e2", "e1e2"]:
        for split in ["development", "confirmation"]:
            groups = [
                group.sort_values("meristem")
                for (_, _), group in events[
                    (events["genotype"] == genotype)
                    & (events["split"] == split)
                ].groupby(["genotype", "plant"], sort=False)
            ]
            adjacent_geometry[f"{genotype}_{split}"] = adjacent_error_geometry(
                groups, RNG_SEED + 10 + seed_offset
            )
            seed_offset += 1

    benchmark = constant_benchmark(FIXED_CANDIDATES)
    benchmark_summary = (
        benchmark.groupby("candidate", as_index=False)
        .agg(
            mean_largest_gap_rank=("largest_gap_rank", "mean"),
            mean_minimum_gap_rank=("minimum_gap_rank", "mean"),
            largest_gap_wins=("largest_gap_rank", lambda x: int(np.sum(x == 1))),
            minimum_gap_wins=("minimum_gap_rank", lambda x: int(np.sum(x == 1))),
        )
    )

    ci_rng = np.random.default_rng(RNG_SEED + 1)
    clearance_cis: dict[str, list[float]] = {}
    for genotype in ["Col", "e2", "e1e2"]:
        values = plant_summary[
            (plant_summary["genotype"] == genotype)
            & (plant_summary["split"] == "confirmation")
        ]["clearance_median"].to_numpy()
        clearance_cis[genotype] = bootstrap_median_ci(values, ci_rng)

    passes = {
        "P1_landmark_within_0.01": bool(p1_pass),
        "P2_exact_phi_step_winner": bool(p2_pass),
        "P3_exact_phi_cumulative_winner": bool(p3_pass),
        "P4_ordered_clearance_both_parts": bool(p4_pass),
    }
    score = int(sum(passes.values()))
    if score == 4:
        verdict = "SUPPORTED"
    elif score >= 2:
        verdict = "MIXED / SUGGESTIVE"
    else:
        verdict = "NOT SUPPORTED"

    result = {
        "test_id": "T302-PHI-PHYLLOTAXIS-v1",
        "ran_date": "2026-07-30",
        "status_boundary": (
            "Empirical calibration/retrodiction; source paper already identifies "
            "the golden-angle neighbourhood."
        ),
        "source": {
            "doi": "10.1038/s41467-025-65792-y",
            "url": SOURCE_URL,
            "archive_sha256": sha256(ARCHIVE_PATH),
            "workbook_sha256": sha256(WORKBOOK_PATH),
            "rows": int(len(events)),
            "plants": {
                key: int(value)
                for key, value in events.groupby("genotype")["plant"].nunique().items()
            },
        },
        "ara_mapping": {
            "measured": "x_A = divergence_angle_deg / 360",
            "assigned_not_measured": "x_B = 2 - x_A",
            "phi_A": PHI_A,
            "phi_B": PHI_B,
        },
        "development_median_turn": development_median,
        "frozen": {
            "passes": passes,
            "score": score,
            "verdict": verdict,
            "P1_confirmation_wt_coordinate": p1_coordinate,
            "P1_distance_from_phi": abs(p1_coordinate - PHI_A),
            "P2_fixed_step_winner": p2_winner,
            "P3_fixed_cumulative_winner": p3_winner,
            "P4_confirmation_clearance_medians": {
                key: float(value) for key, value in clearance_group.items()
            },
            "P4_clearance_bootstrap_95": clearance_cis,
            "P4_group_ordering_pass": bool(p4_group_pass),
            "P4_shuffle_p_one_sided": shuffle_p,
            "P4_shuffle_pass": bool(p4_shuffle_pass),
            "P4_actual_wt_stat": actual_clearance_stat,
            "P4_shuffle_median": float(np.median(shuffle_null)),
            "P4_shuffle_95": [
                float(np.quantile(shuffle_null, 0.025)),
                float(np.quantile(shuffle_null, 0.975)),
            ],
        },
        "secondary": {
            "adjacent_error_geometry": adjacent_geometry,
            "constant_benchmark": benchmark_summary.to_dict(orient="records"),
        },
        "artifacts": {
            "event_geometry_csv": EVENT_CSV.name,
            "plant_summary_csv": PLANT_CSV.name,
            "candidate_summary_csv": CANDIDATE_CSV.name,
            "visualization": VISUALIZATION_PATH.name,
        },
    }

    output_events = events.drop(columns=["angle"]).copy()
    output_events.to_csv(EVENT_CSV, index=False, float_format="%.12g")
    plant_summary.to_csv(PLANT_CSV, index=False, float_format="%.12g")
    candidate_summary.to_csv(CANDIDATE_CSV, index=False, float_format="%.12g")
    RESULT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    make_visualization(
        events,
        plant_summary,
        candidate_summary,
        shuffle_null,
        development_median,
        result,
    )

    print(json.dumps(result["frozen"], indent=2))
    print("\nWrote:")
    for path in [
        RESULT_JSON,
        EVENT_CSV,
        PLANT_CSV,
        CANDIDATE_CSV,
        VISUALIZATION_PATH,
    ]:
        print(f"  {path.relative_to(HERE.parent.parent)}")


if __name__ == "__main__":
    main()
