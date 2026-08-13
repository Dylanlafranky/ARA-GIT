#!/usr/bin/env python3
"""T369B: post-result signed timing-orientation diagnostic."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DERIVED = HERE / "T369_MUON_CAPTURE_DAUGHTER_CLOSURE_DERIVED.npz"
T369 = HERE / "T369_MUON_CAPTURE_DAUGHTER_CLOSURE_RESULTS.json"
RESULTS = HERE / "T369B_MUON_DAUGHTER_ANTIPHASE_RESULTS.json"
FIGURE = HERE / "T369B_MUON_DAUGHTER_ANTIPHASE_FIGURE.svg"
REPORT = HERE / "T369B_MUON_DAUGHTER_ANTIPHASE_REPORT_2026-08-12.md"
SEED = 3692
N_RESAMPLES = 1_000


def ecdf(values: np.ndarray, reference_edges: np.ndarray) -> np.ndarray:
    # T369 stored seven development quantile edges. Mid-bin coordinates avoid
    # pretending the holdout supplies a new calibration distribution.
    return 2.0 * (np.digitize(values, reference_edges) + 0.5) / 8.0


def orientation_metrics(xg: np.ndarray, xn: np.ndarray) -> dict[str, float]:
    aligned_error = float(np.mean(np.abs(xn - xg)))
    anti_error = float(np.mean(np.abs(xn - (2.0 - xg))))
    return {
        "aligned_error": aligned_error,
        "antiphase_error": anti_error,
        "aligned_effect": 1.0 - aligned_error / (2.0 / 3.0),
        "antiphase_effect": 1.0 - anti_error / (2.0 / 3.0),
        "antiphase_minus_aligned": aligned_error - anti_error,
        "rank_correlation": float(np.corrcoef(xg, xn)[0, 1]),
    }


def bootstrap(xg: np.ndarray, xn: np.ndarray, rng: np.random.Generator) -> dict[str, list[float]]:
    n = len(xg)
    aligned = np.empty(N_RESAMPLES)
    anti = np.empty(N_RESAMPLES)
    for i in range(N_RESAMPLES):
        idx = rng.integers(0, n, n)
        metric = orientation_metrics(xg[idx], xn[idx])
        aligned[i] = metric["aligned_effect"]
        anti[i] = metric["antiphase_effect"]
    return {
        "aligned_effect_ci95": np.quantile(aligned, [0.025, 0.975]).tolist(),
        "antiphase_effect_ci95": np.quantile(anti, [0.025, 0.975]).tolist(),
    }


def shuffle_null(
    xg: np.ndarray,
    xn: np.ndarray,
    multiplicity: np.ndarray,
    observed: dict[str, float],
    rng: np.random.Generator,
) -> dict[str, object]:
    aligned = np.empty(N_RESAMPLES)
    anti = np.empty(N_RESAMPLES)
    groups = [np.flatnonzero(multiplicity == value) for value in (1, 2)]
    working = xn.copy()
    for i in range(N_RESAMPLES):
        for group in groups:
            working[group] = rng.permutation(xn[group])
        metric = orientation_metrics(xg, working)
        aligned[i] = metric["aligned_effect"]
        anti[i] = metric["antiphase_effect"]
    return {
        "aligned_equal_or_greater": int(np.sum(aligned >= observed["aligned_effect"])),
        "antiphase_equal_or_greater": int(np.sum(anti >= observed["antiphase_effect"])),
        "aligned_median": float(np.median(aligned)),
        "antiphase_median": float(np.median(anti)),
        "aligned_ci95": np.quantile(aligned, [0.025, 0.975]).tolist(),
        "antiphase_ci95": np.quantile(anti, [0.025, 0.975]).tolist(),
    }


def svg(result: dict[str, object], matrix: np.ndarray) -> None:
    ink, muted = "#172033", "#687386"
    blue, orange, green = "#3677ba", "#df8d25", "#2f936b"
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1420" height="860" viewBox="0 0 1420 860">',
        '<rect width="100%" height="100%" fill="#f6f7f9"/>',
        f'<text x="55" y="58" font-family="Segoe UI,Arial" font-size="31" font-weight="700" fill="{ink}">T369B — is the delayed child anti-phase?</text>',
        f'<text x="55" y="92" font-family="Segoe UI,Arial" font-size="17" fill="{muted}">{result["verdict"]} · post-result diagnostic · n={result["n"]:,}</text>',
    ]
    # Matrix.
    x0, y0, cell = 85, 170, 57
    maxv = max(float(matrix.max()), 1.0)
    lines.append(f'<text x="{x0}" y="140" font-family="Segoe UI,Arial" font-size="22" font-weight="600" fill="{ink}">Prompt-time ARA → first-neutron-time ARA</text>')
    for i in range(8):
        for j in range(8):
            opacity = 0.08 + 0.9 * matrix[i, j] / maxv
            lines.append(f'<rect x="{x0+j*cell}" y="{y0+(7-i)*cell}" width="{cell-2}" height="{cell-2}" fill="{blue}" fill-opacity="{opacity:.3f}"/>')
    # Diagonals.
    lines.append(f'<line x1="{x0}" y1="{y0+8*cell}" x2="{x0+8*cell}" y2="{y0}" stroke="{green}" stroke-width="5" stroke-dasharray="12 9"/>')
    lines.append(f'<line x1="{x0}" y1="{y0}" x2="{x0+8*cell}" y2="{y0+8*cell}" stroke="{orange}" stroke-width="5" stroke-dasharray="12 9"/>')
    lines.extend([
        f'<text x="{x0+228}" y="{y0+8*cell+42}" text-anchor="middle" font-family="Segoe UI,Arial" font-size="17" fill="{muted}">prompt-time ARA 0 → 2</text>',
        f'<text x="{x0-48}" y="{y0+228}" text-anchor="middle" transform="rotate(-90 {x0-48} {y0+228})" font-family="Segoe UI,Arial" font-size="17" fill="{muted}">neutron-time ARA 0 → 2</text>',
        f'<text x="690" y="168" font-family="Segoe UI,Arial" font-size="22" font-weight="600" fill="{ink}">Frozen orientation scores</text>',
    ])
    metrics = result["metrics"]
    rows = [
        ("same-phase effect", metrics["aligned_effect"], green),
        ("anti-phase effect", metrics["antiphase_effect"], orange),
        ("rank correlation", metrics["rank_correlation"], blue),
    ]
    for k, (label, value, color) in enumerate(rows):
        y = 235 + k * 115
        lines.append(f'<text x="690" y="{y}" font-family="Segoe UI,Arial" font-size="18" fill="{ink}">{label}</text>')
        xzero, scale = 945, 270
        lines.append(f'<line x1="{xzero-scale}" y1="{y+28}" x2="{xzero+scale}" y2="{y+28}" stroke="#cad0d9" stroke-width="2"/>')
        lines.append(f'<line x1="{xzero}" y1="{y+14}" x2="{xzero}" y2="{y+42}" stroke="{ink}" stroke-width="2"/>')
        length = max(-scale, min(scale, value*scale*4))
        start = min(xzero, xzero+length)
        lines.append(f'<rect x="{start}" y="{y+18}" width="{abs(length)}" height="20" fill="{color}"/>')
        lines.append(f'<text x="1245" y="{y+34}" font-family="Segoe UI,Arial" font-size="19" font-weight="700" fill="{color}">{value:+.5f}</text>')
    controls = result["shuffle"]
    lines.extend([
        f'<rect x="680" y="590" width="650" height="165" rx="14" fill="#ffffff" stroke="#d7dce4"/>',
        f'<text x="710" y="630" font-family="Segoe UI,Arial" font-size="21" font-weight="600" fill="{ink}">Multiplicity-preserving shuffle control</text>',
        f'<text x="710" y="674" font-family="Segoe UI,Arial" font-size="18" fill="{muted}">same phase: {controls["aligned_equal_or_greater"]} / 1,000 shuffles equalled or exceeded</text>',
        f'<text x="710" y="711" font-family="Segoe UI,Arial" font-size="18" fill="{muted}">anti-phase: {controls["antiphase_equal_or_greater"]} / 1,000 shuffles equalled or exceeded</text>',
        f'<text x="55" y="820" font-family="Segoe UI,Arial" font-size="15" fill="{muted}">Green dashed: xN≈xG · orange dashed: xN≈2−xG · detector timing, not neutron emission timing</text>',
        '</svg>',
    ])
    FIGURE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    t369 = json.loads(T369.read_text(encoding="utf-8"))
    with np.load(DERIVED) as data:
        momentum = data["prompt_momentum_mev"]
        prompt_time = data["prompt_time_us"]
        multiplicity = data["neutron_multiplicity"]
        neutron_time = data["first_neutron_time_us"]
    time_edges = np.asarray(t369["coordinate_edges"]["prompt_time_us"])
    neutron_edges = np.asarray(t369["coordinate_edges"]["first_neutron_time_us"])
    present = (momentum > 0) & (momentum <= 15) & (prompt_time >= 1.1) & (prompt_time <= 5) & (multiplicity > 0)
    strict = present & (momentum > 5)
    xg = ecdf(prompt_time[present], time_edges)
    xn = ecdf(neutron_time[present], neutron_edges)
    mult = np.minimum(multiplicity[present], 2)
    observed = orientation_metrics(xg, xn)
    strict_metrics = orientation_metrics(ecdf(prompt_time[strict], time_edges), ecdf(neutron_time[strict], neutron_edges))
    rng = np.random.default_rng(SEED)
    boot = bootstrap(xg, xn, rng)
    null = shuffle_null(xg, xn, mult, observed, rng)
    aligned_pass = observed["aligned_effect"] >= 0.01 and null["aligned_equal_or_greater"] <= 10 and boot["aligned_effect_ci95"][0] > 0 and strict_metrics["aligned_effect"] > 0
    anti_pass = observed["antiphase_effect"] >= 0.01 and null["antiphase_equal_or_greater"] <= 10 and boot["antiphase_effect_ci95"][0] > 0 and strict_metrics["antiphase_effect"] > 0
    verdict = "ANTI-PHASE TIMING SUPPORTED" if anti_pass else "SAME-PHASE TIMING SUPPORTED" if aligned_pass else "NO ORIENTED TIMING RELATION"
    gbin = np.digitize(prompt_time[present], time_edges)
    nbin = np.digitize(neutron_time[present], neutron_edges)
    matrix = np.bincount(gbin*8+nbin, minlength=64).reshape(8, 8)
    result = {
        "test": "T369B daughter timing anti-phase diagnostic",
        "verdict": verdict,
        "n": int(present.sum()),
        "strict_n": int(strict.sum()),
        "metrics": observed,
        "strict_metrics": strict_metrics,
        "bootstrap": boot,
        "shuffle": null,
        "gates": {"same_phase": bool(aligned_pass), "antiphase": bool(anti_pass)},
        "contingency_8x8": matrix.tolist(),
        "boundary": "Post-result diagnostic; first-neutron detection time is not neutron-emission time.",
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    svg(result, matrix)
    REPORT.write_text(f"""# T369B - daughter timing anti-phase diagnostic

**Verdict:** **{verdict}**  
**Evidence class:** post-result diagnostic, not untouched confirmation

## Result

- Both-child rows: **{int(present.sum()):,}**
- Same-phase effect: **{100*observed['aligned_effect']:+.4f}%**
- Anti-phase effect: **{100*observed['antiphase_effect']:+.4f}%**
- Rank correlation: **{observed['rank_correlation']:+.6f}**
- Same-phase shuffle exceedances: **{null['aligned_equal_or_greater']} / 1,000**
- Anti-phase shuffle exceedances: **{null['antiphase_equal_or_greater']} / 1,000**
- Strict-window anti-phase effect: **{100*strict_metrics['antiphase_effect']:+.4f}%**

## Reading

The negative T369 prediction score is not itself an opposite ARA pole. A true
timing anti-phase must make the relation `x_N ~= 2-x_G` closer than shuffled
pairs. This diagnostic tests exactly that while retaining neutron
multiplicity during shuffling.
""", encoding="utf-8")
    print(json.dumps({"verdict": verdict, "metrics": observed, "shuffle": null, "strict": strict_metrics}, indent=2))


if __name__ == "__main__":
    main()
