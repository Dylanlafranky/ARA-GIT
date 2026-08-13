"""T341: frozen pure-axis Di-ARA gradient test."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
STEM = "T341_PURE_AXIS_DI_ARA_GRADIENT"
PROTOCOL = HERE / f"{STEM}_PROTOCOL_v1_FROZEN.md"
QUTRIT = REPO / "analysis" / "quantum" / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_EVENTS.npz"
BUBBLES = REPO / "analysis" / "vertical_ara_bubbles" / "results" / "T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT_EVENTS.csv"
RIVER = REPO / "analysis" / "hydraulics" / "results" / "T335_RIVER_IRRATIONALITY_DI_ARA_EVENTS.csv"

OUT_RESULTS = HERE / f"{STEM}_RESULTS.json"
OUT_EVENTS = HERE / f"{STEM}_EVENTS.csv"
OUT_SUMMARY = HERE / f"{STEM}_SUMMARY.csv"
OUT_PAIRS = HERE / f"{STEM}_FIXED_PAIRS.csv"
OUT_NULLS = HERE / f"{STEM}_NULLS.csv"
OUT_SENS = HERE / f"{STEM}_CONE_SENSITIVITY.csv"
OUT_FIGURE = HERE / f"{STEM}_FIGURE.png"
OUT_REPORT = HERE / f"{STEM}_REPORT_2026-08-05.md"

EXPECTED_HASHES = {
    PROTOCOL: "61555C08A9B021076E46F4E9182D63FCBF2E6051D7B38970433B7CE59E89457E",
    QUTRIT: "B84918CFF03F2D268DF1C8317CFE16BD93B507BD8CF4CA44A0DBAC79F9F0CE12",
    BUBBLES: "262DC32FEE54973223FB4BF4F0D544EAAAB6449761852A3A29F0DCF8AC3D3BA7",
    RIVER: "A50C13E1F93C0E0115897DDE7F7763B93DC880DBD2DF5BAA6E0EE66FD394FC26",
}

PHI = (1.0 + math.sqrt(5.0)) / 2.0
TAU_PHI = 1.0 / (PHI * PHI)
PLASTIC = 1.324717957244746
RADIAL = {
    "plastic": PLASTIC,
    "sqrt2": math.sqrt(2.0),
    "three_halves": 1.5,
    "phi": PHI,
    "octave": 2.0,
    "e": math.e,
}
ANGULAR = {
    "quarter": 0.25,
    "third": 1.0 / 3.0,
    "one_over_e": 1.0 / math.e,
    "three_eighths": 3.0 / 8.0,
    "phi_inverse_squared": TAU_PHI,
    "two_fifths": 0.4,
    "sqrt2_minus_1": math.sqrt(2.0) - 1.0,
}
PLANES = ("psi0_psi1", "psi1_psi2", "psi2_psi0")
EPS = 1e-12


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def verify_sources() -> dict[str, dict[str, object]]:
    audit = {}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"checksum mismatch for {path}: {actual} != {expected}")
        audit[str(path.relative_to(REPO))] = {"sha256": actual, "bytes": path.stat().st_size}
    return audit


def wrap(values: np.ndarray) -> np.ndarray:
    return np.arctan2(np.sin(values), np.cos(values))


def load_qutrit() -> pd.DataFrame:
    archive = np.load(QUTRIT)
    frames = []
    for plane in PLANES:
        time = np.asarray(archive[f"{plane}_time"], dtype=np.int64)
        residual = np.asarray(archive[f"{plane}_residual"], dtype=float)
        amp = np.asarray(archive[f"{plane}_circle_strength"], dtype=float)
        heading = np.asarray(archive[f"{plane}_circle_heading"], dtype=float)
        eligible = np.isfinite(amp) & np.isfinite(heading) & np.isfinite(residual) & (amp >= 0.01) & (residual <= 0.25)
        continuous = np.diff(time) <= 2200
        midpoint = len(time) // 2
        for split, start, stop in (("calibration", 0, midpoint), ("holdout", midpoint, len(time))):
            left = np.arange(start, stop - 1, dtype=np.int64)
            keep = eligible[left] & eligible[left + 1] & continuous[left]
            left = left[keep]
            radial = amp[left + 1] / amp[left]
            delta = wrap(2.0 * math.pi * (heading[left + 1] - heading[left]))
            frames.append(pd.DataFrame({
                "domain": "recorded_qutrit",
                "population": "three_planes_circle_lag1",
                "split": split,
                "cell": plane,
                "radial": radial,
                "delta": delta,
                "evidence_role": "real_data_primary",
            }))
    return pd.concat(frames, ignore_index=True)


def load_bubbles() -> pd.DataFrame:
    src = pd.read_csv(BUBBLES)
    src = src[src["source_kind"] == "observed"].copy()
    return pd.DataFrame({
        "domain": "recorded_bubbles",
        "population": "octave_relative_roots",
        "split": src["split"],
        "cell": "level=" + src["level"].astype(str),
        "radial": src["u"].astype(float),
        "delta": src["delta_rad"].astype(float),
        "evidence_role": "real_data_transfer",
    })


def load_river() -> pd.DataFrame:
    src = pd.read_csv(RIVER)
    src = src[src["source_kind"] == "observed"].copy()
    return pd.DataFrame({
        "domain": "recorded_river",
        "population": "all_41_intact_rank_paths",
        "split": src["split"],
        "cell": "rank=" + src["elevation_rank"].astype(str),
        "radial": src["scale_ratio_s"].astype(float),
        "delta": src["turn_delta_rad"].astype(float),
        "evidence_role": "real_data_primary",
        "path_type": src["path_type"].astype(str),
    })


def enrich(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    radial = out["radial"].to_numpy(float)
    delta = wrap(out["delta"].to_numpy(float))
    valid = np.isfinite(radial) & (radial > 0) & np.isfinite(delta)
    out = out.loc[valid].copy().reset_index(drop=True)
    radial = radial[valid]
    delta = delta[valid]
    x = 2.0 * radial / (1.0 + radial)
    y = 1.0 + delta / math.pi
    dr = np.abs(x - 1.0)
    dc = np.abs(y - 1.0)
    out["delta"] = delta
    out["x_radial_ara"] = x
    out["y_angular_ara"] = y
    out["d_radial"] = dr
    out["d_angular"] = dc
    out["gamma_deg"] = np.degrees(np.arctan2(dc, dr))
    out["R_abs_log_radial"] = np.abs(np.log(radial))
    out["C_abs_turns"] = np.abs(delta) / (2.0 * math.pi)
    out["quadrant"] = np.where(np.log(radial) < 0, "contracting", "expanding") + np.where(delta < 0, "_reverse", "_forward")
    return out


def budget_loss(r: np.ndarray, c: np.ndarray, alpha: float, tau: float, euclidean: bool = False) -> float:
    rr = r / math.log(alpha)
    cc = c / tau
    budget = np.sqrt(rr * rr + cc * cc) if euclidean else rr + cc
    return float(np.median(np.abs(budget - 1.0)))


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2:
        return float("nan")
    xr = pd.Series(x).rank(method="average").to_numpy(float)
    yr = pd.Series(y).rank(method="average").to_numpy(float)
    return float(np.corrcoef(xr, yr)[0, 1])


def cone_values(part: pd.DataFrame, degrees: float = 15.0) -> tuple[pd.DataFrame, pd.DataFrame]:
    line = part[part["gamma_deg"] <= degrees]
    circle = part[part["gamma_deg"] >= 90.0 - degrees]
    return line, circle


def calibration_controls(events: pd.DataFrame) -> dict[str, tuple[float, float]]:
    controls = {}
    for domain, part in events[events["split"] == "calibration"].groupby("domain", sort=True):
        line, circle = cone_values(part)
        controls[domain] = (
            float(line["R_abs_log_radial"].median()) if len(line) else float("nan"),
            float(circle["C_abs_turns"].median()) if len(circle) else float("nan"),
        )
    return controls


def fixed_pair_rows(part: pd.DataFrame, domain: str, split: str) -> list[dict[str, object]]:
    r = part["R_abs_log_radial"].to_numpy(float)
    c = part["C_abs_turns"].to_numpy(float)
    rows = []
    for r_name, alpha in RADIAL.items():
        for c_name, tau in ANGULAR.items():
            rows.append({
                "domain": domain,
                "split": split,
                "radial_candidate": r_name,
                "angular_candidate": c_name,
                "alpha": alpha,
                "tau": tau,
                "linear_budget_loss": budget_loss(r, c, alpha, tau),
                "euclidean_budget_loss": budget_loss(r, c, alpha, tau, True),
            })
    return rows


def summarize(part: pd.DataFrame, fitted: tuple[float, float], domain: str, split: str, seed: int) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    line, circle = cone_values(part)
    r_med = float(line["R_abs_log_radial"].median()) if len(line) else float("nan")
    c_med = float(circle["C_abs_turns"].median()) if len(circle) else float("nan")
    r_scores = {name: abs(r_med - math.log(value)) for name, value in RADIAL.items()}
    c_scores = {name: abs(c_med - value) for name, value in ANGULAR.items()}
    r_winner = min(r_scores, key=r_scores.get) if math.isfinite(r_med) else "ineligible"
    c_winner = min(c_scores, key=c_scores.get) if math.isfinite(c_med) else "ineligible"
    line_eligible = len(line) >= 30 and int((line["radial"] < 1 - EPS).sum()) >= 10 and int((line["radial"] > 1 + EPS).sum()) >= 10
    circle_eligible = len(circle) >= 30 and int((circle["delta"] < -EPS).sum()) >= 10 and int((circle["delta"] > EPS).sum()) >= 10
    fit_r, fit_c = fitted
    e_fit_score = abs(r_med - fit_r) if math.isfinite(fit_r) and math.isfinite(r_med) else float("nan")
    phi_fit_score = abs(c_med - fit_c) if math.isfinite(fit_c) and math.isfinite(c_med) else float("nan")
    line_fixed_pass = bool(line_eligible and r_winner == "e" and r_scores.get("e", math.inf) <= 0.10)
    circle_fixed_pass = bool(circle_eligible and c_winner == "phi_inverse_squared" and c_scores.get("phi_inverse_squared", math.inf) <= 0.05)
    line_pass = bool(line_fixed_pass and r_scores["e"] <= e_fit_score)
    circle_pass = bool(circle_fixed_pass and c_scores["phi_inverse_squared"] <= phi_fit_score)

    pairs = fixed_pair_rows(part, domain, split)
    best = min(pairs, key=lambda row: row["linear_budget_loss"])
    target = next(row for row in pairs if row["radial_candidate"] == "e" and row["angular_candidate"] == "phi_inverse_squared")
    r = part["R_abs_log_radial"].to_numpy(float)
    c = part["C_abs_turns"].to_numpy(float)
    null_rows = []
    p_value = float("nan")
    if split != "calibration":
        rng = np.random.default_rng(seed)
        null_losses = np.empty(1000, dtype=float)
        for i in range(1000):
            perm = rng.permutation(c)
            null_losses[i] = budget_loss(r, perm, math.e, TAU_PHI)
            null_rows.append({"domain": domain, "split": split, "replicate": i, "linear_budget_loss": null_losses[i]})
        p_value = float((1 + np.count_nonzero(null_losses <= target["linear_budget_loss"])) / 1001.0)
    gradient_pass = bool(best["radial_candidate"] == "e" and best["angular_candidate"] == "phi_inverse_squared" and target["linear_budget_loss"] <= 0.15 and math.isfinite(p_value) and p_value < 0.05)

    row = {
        "domain": domain,
        "population": str(part["population"].iloc[0]),
        "split": split,
        "evidence_role": str(part["evidence_role"].iloc[0]),
        "n": len(part),
        "line_n": len(line),
        "line_contracting_n": int((line["radial"] < 1 - EPS).sum()),
        "line_expanding_n": int((line["radial"] > 1 + EPS).sum()),
        "line_R_median": r_med,
        "line_s_equivalent": float(math.exp(r_med)) if math.isfinite(r_med) else float("nan"),
        "line_fixed_winner": r_winner,
        "line_e_score": r_scores.get("e", float("nan")),
        "line_fitted_cal_R": fit_r,
        "line_fitted_score": e_fit_score,
        "line_eligible": line_eligible,
        "line_fixed_pass": line_fixed_pass,
        "line_pass": line_pass,
        "circle_n": len(circle),
        "circle_reverse_n": int((circle["delta"] < -EPS).sum()),
        "circle_forward_n": int((circle["delta"] > EPS).sum()),
        "circle_C_median_turns": c_med,
        "circle_fixed_winner": c_winner,
        "circle_phi_score": c_scores.get("phi_inverse_squared", float("nan")),
        "circle_fitted_cal_C": fit_c,
        "circle_fitted_score": phi_fit_score,
        "circle_eligible": circle_eligible,
        "circle_fixed_pass": circle_fixed_pass,
        "circle_pass": circle_pass,
        "mixed_n": int(((part["gamma_deg"] >= 30) & (part["gamma_deg"] <= 60)).sum()),
        "target_linear_budget_loss": target["linear_budget_loss"],
        "target_euclidean_budget_loss": target["euclidean_budget_loss"],
        "best_pair_radial": best["radial_candidate"],
        "best_pair_angular": best["angular_candidate"],
        "best_pair_loss": best["linear_budget_loss"],
        "target_pair_rank": 1 + sorted(x["linear_budget_loss"] for x in pairs).index(target["linear_budget_loss"]),
        "radial_angular_spearman": spearman(r, c),
        "shuffle_p": p_value,
        "gradient_pass": gradient_pass,
        "joint_pass": bool(line_pass and circle_pass and gradient_pass),
    }
    sens = []
    for deg in (10.0, 15.0, 20.0):
        lsub, csub = cone_values(part, deg)
        sens.append({
            "domain": domain,
            "split": split,
            "cone_degrees": deg,
            "line_n": len(lsub),
            "line_R_median": float(lsub["R_abs_log_radial"].median()) if len(lsub) else float("nan"),
            "line_e_distance": abs(float(lsub["R_abs_log_radial"].median()) - 1.0) if len(lsub) else float("nan"),
            "circle_n": len(csub),
            "circle_C_median": float(csub["C_abs_turns"].median()) if len(csub) else float("nan"),
            "circle_phi_distance": abs(float(csub["C_abs_turns"].median()) - TAU_PHI) if len(csub) else float("nan"),
        })
    return row, pairs, null_rows, sens


def font(size: int, bold: bool = False):
    paths = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for path in paths:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def make_figure(events: pd.DataFrame, summary: pd.DataFrame, verdict: str) -> None:
    hold = summary[summary["split"] == "holdout"].copy()
    colors = {"recorded_qutrit": "#3975b9", "recorded_bubbles": "#e3a32c", "recorded_river": "#429b78"}
    image = Image.new("RGB", (1800, 1200), "#f5f7fa")
    draw = ImageDraw.Draw(image, "RGBA")
    title_f, sub_f, head_f, body_f, small_f = font(42, True), font(22), font(27, True), font(19), font(16)
    ink, muted, border = "#17283d", "#68788c", "#cbd5e1"
    draw.text((55, 35), "T341 — pure-axis Di-ARA gradient", fill=ink, font=title_f)
    draw.text((55, 90), "Line and circle are pure limits; observed movements occupy their shared gradient", fill=muted, font=sub_f)
    panels = [(45, 140, 885, 640), (915, 140, 1755, 640), (45, 675, 885, 1155), (915, 675, 1755, 1155)]
    for box in panels:
        draw.rounded_rectangle(box, radius=18, fill="#ffffff", outline=border, width=2)

    # Gradient scatter.
    draw.text((70, 165), "Holdout movement against the frozen gradient", fill=ink, font=head_f)
    left, top, right, bottom = 110, 235, 835, 585
    draw.line((left, bottom, right, bottom), fill=ink, width=2)
    draw.line((left, bottom, left, top), fill=ink, width=2)
    draw.line((left, bottom, right, top), fill="#d04d72", width=4)
    draw.text((310, 595), "line contribution |log s|", fill=muted, font=small_f)
    draw.text((115, 205), "circle contribution / phi^-2", fill=muted, font=small_f)
    for domain, part in events[events["split"] == "holdout"].groupby("domain"):
        sample = part.iloc[::max(1, len(part)//1800)]
        for r, c in zip(sample["R_abs_log_radial"], sample["C_abs_turns"] / TAU_PHI):
            if 0 <= r <= 1.25 and 0 <= c <= 1.25:
                x = left + r / 1.25 * (right-left)
                y = bottom - c / 1.25 * (bottom-top)
                draw.ellipse((x-2, y-2, x+2, y+2), fill=colors[domain] + "55")

    # Pure line.
    draw.text((940, 165), "Pure-line limit (15° cone)", fill=ink, font=head_f)
    x0, x1 = 1080, 1695
    draw.line((x0, 570, x1, 570), fill=ink, width=2)
    target_x = x0 + 1.0 / 1.2 * (x1-x0)
    draw.line((target_x, 230, target_x, 580), fill="#3975b9", width=4)
    draw.text((target_x-35, 590), "e: R=1", fill="#3975b9", font=small_f)
    for i, (_, row) in enumerate(hold.iterrows()):
        y = 280 + i*85
        val = float(row["line_R_median"])
        x = x0 + min(val, 1.2)/1.2*(x1-x0)
        label = row["domain"].replace("recorded_", "")
        draw.text((945, y-10), label, fill=ink, font=body_f)
        draw.ellipse((x-8, y-8, x+8, y+8), fill=colors[row["domain"]])
        draw.text((x+14, y-11), f"{val:.3f}", fill=muted, font=body_f)

    # Pure circle.
    draw.text((70, 700), "Pure-circle limit (15° cone)", fill=ink, font=head_f)
    x0, x1 = 230, 825
    draw.line((x0, 1100, x1, 1100), fill=ink, width=2)
    target_x = x0 + TAU_PHI / 0.5 * (x1-x0)
    draw.line((target_x, 765, target_x, 1110), fill="#d04d72", width=4)
    draw.text((target_x-70, 1115), "golden turn", fill="#d04d72", font=small_f)
    for i, (_, row) in enumerate(hold.iterrows()):
        y = 820 + i*85
        val = float(row["circle_C_median_turns"])
        x = x0 + min(val, 0.5)/0.5*(x1-x0)
        label = row["domain"].replace("recorded_", "")
        draw.text((75, y-10), label, fill=ink, font=body_f)
        draw.ellipse((x-8, y-8, x+8, y+8), fill=colors[row["domain"]])
        draw.text((x+14, y-11), f"{val:.3f}", fill=muted, font=body_f)

    # Gate panel.
    draw.text((940, 700), "Frozen holdout gates", fill=ink, font=head_f)
    y = 770
    for _, row in hold.iterrows():
        label = row["domain"].replace("recorded_", "")
        draw.text((945, y), label, fill=ink, font=body_f)
        line_label = f"line {'YES' if row['line_fixed_pass'] else 'NO'}/{'S' if row['line_pass'] else '-'}"
        circle_label = f"circle {'YES' if row['circle_fixed_pass'] else 'NO'}/{'S' if row['circle_pass'] else '-'}"
        draw.text((1125, y), line_label, fill="#2c8a65" if row["line_fixed_pass"] else "#d65d64", font=body_f)
        draw.text((1280, y), circle_label, fill="#2c8a65" if row["circle_fixed_pass"] else "#d65d64", font=body_f)
        draw.text((1475, y), f"gradient {'YES' if row['gradient_pass'] else 'NO'}", fill="#2c8a65" if row["gradient_pass"] else "#d65d64", font=body_f)
        y += 72
    draw.text((945, 1045), f"Cross-domain verdict: {verdict}", fill="#d04d72", font=head_f)
    image.save(OUT_FIGURE)


def make_report(summary: pd.DataFrame, results: dict[str, object]) -> None:
    hold = summary[summary["split"] == "holdout"]
    rows = []
    for _, r in hold.iterrows():
        rows.append(f"| {r['domain'].replace('recorded_', '')} | {int(r['line_n']):,} | {r['line_R_median']:.6f} ({r['line_fixed_winner']}) | {'yes' if r['line_fixed_pass'] else 'no'}/{'yes' if r['line_pass'] else 'no'} | {int(r['circle_n']):,} | {r['circle_C_median_turns']:.6f} ({r['circle_fixed_winner']}) | {'yes' if r['circle_fixed_pass'] else 'no'}/{'yes' if r['circle_pass'] else 'no'} | {r['target_linear_budget_loss']:.6f} | {r['shuffle_p']:.6f} | {'yes' if r['joint_pass'] else 'no'} |")
    text = f"""# T341 — pure-axis Di-ARA gradient result

**Run:** 5 August 2026  
**Protocol:** `T341_PURE_AXIS_DI_ARA_GRADIENT_PROTOCOL_v1_FROZEN.md`  
**Protocol SHA-256:** `{results['protocol_sha256']}`  
**Cross-domain verdict:** **{results['verdict']}**

## Frozen question

Do mixed Di-ARA observations approach `1/e <-> e` at the pure radial/line axis, approach the golden non-closing turn at the pure angular/circle axis, and trade between those limits through one linear ARA budget?

## Holdout results

| Domain | line N | line median R (winner) | fixed/strong line | circle N | circle median turns (winner) | fixed/strong circle | target budget loss | shuffle p | joint |
|---|---:|---:|---|---:|---:|---|---:|---:|---|
{chr(10).join(rows)}

## Interpretation

{results['plain_language']}

The strongest component result is in the recorded qutrit holdout. Its 15-degree line cone gives `R=1.016128`, equivalent to `s=2.762479`; `e` is the closest fixed landmark and the absolute fixed gate passes. The tighter 10-degree cone moves still closer (`R=1.010681`). The strong transfer gate nevertheless remains failed because the calibration-fitted `R=1.025085` is slightly closer to the holdout median than exact `R=1`. On the circular side, qutrit gives `0.350769` turns: within `0.031197` of the golden target but closer to `1/e=0.367879`. Its radial and angular magnitudes are essentially uncorrelated (`rho=0.000180`), and shuffling their pairing does not worsen the target budget (`p=0.510490`). Thus the line limit is a real lead here, while the proposed coupled `e/Phi` gradient is not recovered.

Coverage is asymmetric in the other domains. The bubble holdout contains only `12` circle-cone events and the river holdout only `3` line-cone events, below the frozen eligibility floor. Their measurable opposite cones also sit far from the proposed constants. The cross-domain rejection is therefore decisive for the universal joint package, while the individual pure-axis limits still require datasets that actually visit both poles densely.

The four sign quadrants are not the tested discovery here. The load-bearing result is whether movement near each pure axis selects the frozen constant and whether intermediate magnitudes compensate event by event. A failed constant gate does not erase the already-established usefulness of the two-axis Di-ARA coordinate.

## Evidence boundary

All three archives were previously opened. This is a frozen new conditional question on inherited data, not a pristine discovery test. The 15-degree cones were fixed before the conditional medians were calculated.

## Reproduction

```powershell
$python = 'C:\\Users\\Dylan\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe'
& $python analysis/phi_calibration/t341_pure_axis_di_ara_gradient.py
& $python analysis/phi_calibration/validate_t341_pure_axis_di_ara_gradient.py
```
"""
    OUT_REPORT.write_text(text, encoding="utf-8")


def clean(value):
    if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, list): return [clean(v) for v in value]
    if isinstance(value, (np.integer,)): return int(value)
    if isinstance(value, (np.floating,)): return float(value)
    if isinstance(value, (np.bool_,)): return bool(value)
    return value


def main() -> None:
    audit = verify_sources()
    events = enrich(pd.concat([load_qutrit(), load_bubbles(), load_river()], ignore_index=True))
    controls = calibration_controls(events)
    summary_rows, pair_rows, null_rows, sens_rows = [], [], [], []
    offsets = {"recorded_qutrit": 0, "recorded_bubbles": 10000, "recorded_river": 20000}
    for (domain, split), part in events.groupby(["domain", "split"], sort=True):
        row, pairs, nulls, sens = summarize(part, controls[domain], domain, split, 3412026 + offsets[domain] + (0 if split == "evaluation" else 1))
        summary_rows.append(row); pair_rows.extend(pairs); null_rows.extend(nulls); sens_rows.extend(sens)
    summary = pd.DataFrame(summary_rows)
    pairs = pd.DataFrame(pair_rows)
    nulls = pd.DataFrame(null_rows)
    sens = pd.DataFrame(sens_rows)
    primary_holdouts = summary[summary["split"] == "holdout"]
    joint_count = int(primary_holdouts["joint_pass"].sum())
    verdict = "SUPPORTED" if joint_count >= 2 else ("PARTIAL / IDENTITY-SPECIFIC" if joint_count == 1 else "NOT SUPPORTED")
    if verdict == "NOT SUPPORTED":
        plain = "The proposed universal pure-axis constants and one-budget interpolation were not jointly recovered in at least two real-data holdouts. The result distinguishes failure of those constants from failure of Di-ARA itself: each observation still has radial and angular participation and moves through their gradient."
    elif verdict.startswith("PARTIAL"):
        plain = "One domain recovered the complete pure-axis and gradient package, but it did not transfer across identities. This is an identity-specific lead rather than a universal law."
    else:
        plain = "At least two independent real-data holdouts recovered the exponential line limit, golden circle limit and coupled intermediate budget under the frozen rules."
    results = {
        "test": "T341 pure-axis Di-ARA gradient",
        "protocol_sha256": sha256(PROTOCOL),
        "source_audit": audit,
        "constants": {"phi": PHI, "tau_phi": TAU_PHI, "line_alpha": math.e, "line_cone_degrees": 15, "circle_cone_degrees": 15},
        "summary_rows": len(summary), "event_rows": len(events), "pair_rows": len(pairs), "null_rows": len(nulls), "sensitivity_rows": len(sens),
        "joint_holdout_domains": joint_count,
        "verdict": verdict,
        "plain_language": plain,
    }
    events.to_csv(OUT_EVENTS, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    pairs.to_csv(OUT_PAIRS, index=False)
    nulls.to_csv(OUT_NULLS, index=False)
    sens.to_csv(OUT_SENS, index=False)
    OUT_RESULTS.write_text(json.dumps(clean(results), indent=2), encoding="utf-8")
    make_figure(events, summary, verdict)
    make_report(summary, results)
    print(json.dumps({"verdict": verdict, "joint_holdout_domains": joint_count, "summary": str(OUT_SUMMARY), "report": str(OUT_REPORT), "figure": str(OUT_FIGURE)}, indent=2))


if __name__ == "__main__":
    main()
