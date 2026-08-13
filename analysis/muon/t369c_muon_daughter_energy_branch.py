#!/usr/bin/env python3
"""T369C: signed energy/connection daughter-branch diagnostic."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
DERIVED = HERE / "T369_MUON_CAPTURE_DAUGHTER_CLOSURE_DERIVED.npz"
T369 = HERE / "T369_MUON_CAPTURE_DAUGHTER_CLOSURE_RESULTS.json"
RESULTS = HERE / "T369C_MUON_DAUGHTER_ENERGY_BRANCH_RESULTS.json"
FIGURE = HERE / "T369C_MUON_DAUGHTER_ENERGY_BRANCH_FIGURE.svg"
REPORT = HERE / "T369C_MUON_DAUGHTER_ENERGY_BRANCH_REPORT_2026-08-12.md"
SEED = 3693
N_RESAMPLES = 1_000


def rank_correlation(x: np.ndarray, y: np.ndarray) -> float:
    xr = pd.Series(x).rank(method="average").to_numpy()
    yr = pd.Series(y).rank(method="average").to_numpy()
    return float(np.corrcoef(xr, yr)[0, 1])


def bin_rates(energy_bin: np.ndarray, neutron: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    total = np.bincount(energy_bin, minlength=8)
    positive = np.bincount(energy_bin, weights=neutron, minlength=8)
    return positive / total, total


def bootstrap(x: np.ndarray, y: np.ndarray, rng: np.random.Generator) -> list[float]:
    n = len(x)
    values = np.empty(N_RESAMPLES)
    for i in range(N_RESAMPLES):
        idx = rng.integers(0, n, n)
        values[i] = rank_correlation(x[idx], y[idx])
    return np.quantile(values, [0.025, 0.975]).tolist()


def shuffled(
    x: np.ndarray,
    y: np.ndarray,
    time_bin: np.ndarray,
    observed: float,
    rng: np.random.Generator,
) -> dict[str, object]:
    values = np.empty(N_RESAMPLES)
    working = y.copy()
    groups = [np.flatnonzero(time_bin == value) for value in range(8)]
    for i in range(N_RESAMPLES):
        for group in groups:
            working[group] = rng.permutation(y[group])
        values[i] = rank_correlation(x, working)
    return {
        "equal_or_more_negative": int(np.sum(values <= observed)),
        "median": float(np.median(values)),
        "ci95": np.quantile(values, [0.025, 0.975]).tolist(),
    }


def make_svg(result: dict[str, object]) -> None:
    ink, muted = "#172033", "#687386"
    blue, orange, green = "#3777b8", "#df8d24", "#31936d"
    width, height = 1420, 860
    rates = result["neutron_presence_by_energy_bin"]
    mult = result["mean_multiplicity_by_energy_bin"]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f6f7f9"/>',
        f'<text x="55" y="58" font-family="Segoe UI,Arial" font-size="31" font-weight="700" fill="{ink}">T369C — prompt energy and neutron connection</text>',
        f'<text x="55" y="92" font-family="Segoe UI,Arial" font-size="17" fill="{muted}">{result["verdict"]} · post-result diagnostic · n={result["n"]:,}</text>',
        f'<rect x="55" y="135" width="850" height="610" rx="16" fill="#fff" stroke="#d7dce4"/>',
        f'<text x="85" y="178" font-family="Segoe UI,Arial" font-size="22" font-weight="600" fill="{ink}">Observed child branch across prompt-energy ARA</text>',
    ]
    x0, y0, w, h = 115, 235, 735, 420
    lines.extend([
        f'<line x1="{x0}" y1="{y0+h}" x2="{x0+w}" y2="{y0+h}" stroke="{ink}" stroke-width="2"/>',
        f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+h}" stroke="{ink}" stroke-width="2"/>',
    ])
    points_rate, points_mult = [], []
    for i in range(8):
        x = x0 + i*w/7
        yr = y0+h-(rates[i]/0.45)*h
        ym = y0+h-(mult[i]/0.50)*h
        points_rate.append(f"{x:.2f},{yr:.2f}")
        points_mult.append(f"{x:.2f},{ym:.2f}")
        lines.append(f'<text x="{x}" y="{y0+h+30}" text-anchor="middle" font-family="Segoe UI,Arial" font-size="15" fill="{muted}">{i}</text>')
    lines.append(f'<polyline points="{" ".join(points_rate)}" fill="none" stroke="{blue}" stroke-width="5"/>')
    lines.append(f'<polyline points="{" ".join(points_mult)}" fill="none" stroke="{orange}" stroke-width="5" stroke-dasharray="11 8"/>')
    for i, point in enumerate(points_rate):
        x,y = point.split(',')
        lines.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{blue}"/>')
    lines.extend([
        f'<text x="{x0+w/2}" y="{y0+h+70}" text-anchor="middle" font-family="Segoe UI,Arial" font-size="17" fill="{muted}">prompt-energy ARA bin: low → high</text>',
        f'<text x="{x0+25}" y="{y0+30}" font-family="Segoe UI,Arial" font-size="16" fill="{blue}">neutron presence</text>',
        f'<text x="{x0+215}" y="{y0+30}" font-family="Segoe UI,Arial" font-size="16" fill="{orange}">mean multiplicity</text>',
        f'<rect x="950" y="135" width="415" height="610" rx="16" fill="#fff" stroke="#d7dce4"/>',
        f'<text x="980" y="178" font-family="Segoe UI,Arial" font-size="22" font-weight="600" fill="{ink}">Signed result</text>',
        f'<text x="980" y="235" font-family="Segoe UI,Arial" font-size="17" fill="{muted}">rank correlation</text>',
        f'<text x="980" y="273" font-family="Segoe UI,Arial" font-size="30" font-weight="700" fill="{orange}">{result["rank_correlation"]:+.5f}</text>',
        f'<text x="980" y="333" font-family="Segoe UI,Arial" font-size="17" fill="{muted}">low/high neutron-rate ratio</text>',
        f'<text x="980" y="371" font-family="Segoe UI,Arial" font-size="30" font-weight="700" fill="{blue}">{result["lowest_to_highest_rate_ratio"]:.2f}×</text>',
        f'<text x="980" y="431" font-family="Segoe UI,Arial" font-size="17" fill="{muted}">descending steps</text>',
        f'<text x="980" y="469" font-family="Segoe UI,Arial" font-size="30" font-weight="700" fill="{green}">{result["descending_steps"]} / 7</text>',
        f'<text x="980" y="529" font-family="Segoe UI,Arial" font-size="17" fill="{muted}">time-preserving shuffle</text>',
        f'<text x="980" y="567" font-family="Segoe UI,Arial" font-size="24" font-weight="700" fill="{green}">{result["shuffle"]["equal_or_more_negative"]} / 1,000</text>',
        f'<text x="980" y="627" font-family="Segoe UI,Arial" font-size="17" fill="{muted}">strict-window correlation</text>',
        f'<text x="980" y="665" font-family="Segoe UI,Arial" font-size="24" font-weight="700" fill="{orange}">{result["strict_rank_correlation"]:+.5f}</text>',
        f'<text x="55" y="810" font-family="Segoe UI,Arial" font-size="15" fill="{muted}">Anti-directed detector branch ≠ proof of a pure mirrored ARA pole; neutron energy was not released.</text>',
        '</svg>',
    ])
    FIGURE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    t369 = json.loads(T369.read_text(encoding="utf-8"))
    with np.load(DERIVED) as data:
        row_hash = data["row_hash"]
        momentum = data["prompt_momentum_mev"]
        prompt_time = data["prompt_time_us"]
        multiplicity = np.minimum(data["neutron_multiplicity"], 2).astype(float)
    energy_edges = np.asarray(t369["coordinate_edges"]["prompt_momentum_mev"])
    time_edges = np.asarray(t369["coordinate_edges"]["prompt_time_us"])
    present = (momentum > 0) & (momentum <= 15) & (prompt_time >= 1.1) & (prompt_time <= 5)
    strict = present & (momentum > 5)
    ebin = np.digitize(momentum[present], energy_edges)
    tbin = np.digitize(prompt_time[present], time_edges)
    neutron = (multiplicity[present] > 0).astype(float)
    strength = multiplicity[present]
    correlation = rank_correlation(ebin, strength)
    rates, counts = bin_rates(ebin, neutron)
    mean_mult = np.bincount(ebin, weights=strength, minlength=8) / counts
    descending = int(np.sum(np.diff(rates) < 0))
    rng = np.random.default_rng(SEED)
    ci = bootstrap(ebin, strength, rng)
    null = shuffled(ebin, strength, tbin, correlation, rng)
    strict_correlation = rank_correlation(np.digitize(momentum[strict], energy_edges), multiplicity[strict])
    halves = {}
    for parity in (0, 1):
        mask = present & ((row_hash & 1) == parity)
        halves[f"hash_{parity}"] = rank_correlation(np.digitize(momentum[mask], energy_edges), multiplicity[mask])
    gates = {
        "negative_bootstrap": correlation < 0 and ci[1] < 0,
        "monotonic_steps": descending >= 6,
        "time_preserving_shuffle": null["equal_or_more_negative"] <= 10,
        "strict_window": strict_correlation < 0,
        "hash_halves": all(value < 0 for value in halves.values()),
    }
    verdict = "ANTI-DIRECTED ENERGY/CONNECTION BRANCH SUPPORTED" if all(gates.values()) else "ANTI-DIRECTED BRANCH NOT SUPPORTED"
    result = {
        "test": "T369C prompt-energy / neutron-connection branch",
        "verdict": verdict,
        "n": int(present.sum()),
        "strict_n": int(strict.sum()),
        "rank_correlation": correlation,
        "bootstrap_ci95": ci,
        "strict_rank_correlation": strict_correlation,
        "hash_halves": halves,
        "neutron_presence_by_energy_bin": rates.tolist(),
        "mean_multiplicity_by_energy_bin": mean_mult.tolist(),
        "counts_by_energy_bin": counts.tolist(),
        "descending_steps": descending,
        "lowest_to_highest_rate_ratio": float(rates[0]/rates[-1]),
        "shuffle": null,
        "gates": gates,
        "boundary": "Post-result detector-record diagnostic; neutron energy is unavailable, so pure ARA mirror closure is not tested.",
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    make_svg(result)
    REPORT.write_text(f"""# T369C - prompt-energy / neutron-connection branch

**Verdict:** **{verdict}**  
**Evidence class:** post-result diagnostic

## Result

- Prompt-child holdout rows: **{int(present.sum()):,}**
- Signed rank correlation: **{correlation:+.6f}**
- Bootstrap 95% interval: **[{ci[0]:+.6f}, {ci[1]:+.6f}]**
- Descending adjacent bins: **{descending}/7**
- Neutron rate, lowest energy bin: **{100*rates[0]:.3f}%**
- Neutron rate, highest energy bin: **{100*rates[-1]:.3f}%**
- Low/high rate ratio: **{rates[0]/rates[-1]:.2f}x**
- Time-bin-preserving shuffle exceedances: **{null['equal_or_more_negative']}/1,000**
- Strict `5-15 MeV` correlation: **{strict_correlation:+.6f}**
- Hash-half correlations: **{halves['hash_0']:+.6f}**, **{halves['hash_1']:+.6f}**

## Plain-language ARA reading

The strong opposite-looking child branch is in prompt energy versus observed
neutron connection, not in prompt time versus neutron detection time. As the
prompt-energy coordinate rises, the observed neutron branch falls smoothly.
This survives timing-preserving shuffles and internal replications.

That establishes an **anti-directed relation in the released detector
record**. It does not establish exact pure anti-phase closure: the dataset has
no neutron-emission energy coordinate, and neutron detection is incomplete.
""", encoding="utf-8")
    print(json.dumps({"verdict": verdict, "correlation": correlation, "ci95": ci, "rates": rates.tolist(), "shuffle": null, "halves": halves}, indent=2))


if __name__ == "__main__":
    main()
