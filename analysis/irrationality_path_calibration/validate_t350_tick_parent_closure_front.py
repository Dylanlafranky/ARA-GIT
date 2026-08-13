#!/usr/bin/env python3
"""Independent artifact validator for T350. Does not import the run script."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
V_REF = 0.05
K = 5
RESOLUTIONS = np.array((16, 32, 64, 128, 256), dtype=int)
LAG_FRACTIONS = np.array((1 / 64, 1 / 32, 1 / 16, 1 / 8, 1 / 4, 1 / 2))
EXPECTED_CLAIM = "C4C5CE519F1F596172D1209AF033C88915004E6B04002EFF16F3B606B15241A5"
EXPECTED_PROTOCOL = "C68DD4A2EB60A18034CF8A7B504F5FAE8D3ADBE7AC7ABC2E14BD32E3132EB35E"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def openness(phase: np.ndarray) -> float:
    counts = []
    for bins in RESOLUTIONS:
        idx = np.minimum((phase * bins).astype(int), bins - 1)
        counts.append(max(1, len(np.unique(idx))))
    slope = np.polyfit(np.log(RESOLUTIONS), np.log(counts), 1)[0]
    return 2 * float(np.clip(slope, 0, 1))


def cmean(x: np.ndarray) -> float:
    v = np.mean(np.exp(2j * np.pi * x))
    return 0.0 if abs(v) < 1e-15 else float((np.angle(v) / (2 * np.pi)) % 1)


def loss(actual: np.ndarray, predicted: np.ndarray) -> np.ndarray:
    return 1 - np.cos(2 * np.pi * (actual - predicted))


def predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    order = np.argsort(train_x)
    sx, sy = train_x[order], train_y[order]
    insertion = np.searchsorted(sx, test_x)
    radius = max(K + 2, 7)
    offsets = np.arange(-radius, radius + 1)
    candidates = (insertion[:, None] + offsets[None, :]) % len(sx)
    d = np.abs(sx[candidates] - test_x[:, None])
    d = np.minimum(d, 1 - d)
    pos = np.argpartition(d, K - 1, axis=1)[:, :K]
    nearest = np.take_along_axis(candidates, pos, axis=1)
    vectors = np.mean(np.exp(2j * np.pi * sy[nearest]), axis=1)
    out = (np.angle(vectors) / (2 * np.pi)) % 1
    out[np.abs(vectors) < 1e-12] = cmean(train_y)
    return out


def residual(phase: np.ndarray) -> float:
    split = len(phase) // 2
    tx, ty = phase[: split - 1], phase[1:split]
    qx, qy = phase[split:-1], phase[split + 1 :]
    local = np.mean(loss(qy, predict(tx, ty, qx)))
    null = np.mean(loss(qy, np.full_like(qy, cmean(ty))))
    return 2 * min(1.0, float(local) / max(float(null), 1e-12))


def vector(unwrapped: np.ndarray) -> np.ndarray:
    phase = np.mod(unwrapped, 1)
    unit = np.exp(2j * np.pi * phase)
    rho = []
    for fraction in LAG_FRACTIONS:
        lag = int(np.clip(round(fraction * (len(phase) - 1)), 1, len(phase) - 2))
        rho.append(abs(np.mean(unit[lag:] * np.conj(unit[:-lag]))))
    return np.r_[openness(phase) / 2, residual(phase) / 2, rho]


def main() -> None:
    result = json.loads((HERE / "T350_TICK_PARENT_CLOSURE_FRONT_RESULTS.json").read_text(encoding="utf-8"))
    paths = pd.read_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_PATHS.csv")
    prefixes = pd.read_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_PREFIXES.csv")
    curves = pd.read_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_PAIR_CURVES.csv")
    pairs = pd.read_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_PAIR_SUMMARY.csv")
    cadence = pd.read_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_CADENCE.csv")
    closure = pd.read_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_LOCAL_CLOSURE.csv")
    gates = pd.read_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_FROZEN_GATES.csv")
    examples = pd.read_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_EXAMPLES.csv")

    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    claim_hash = digest(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_CLAIM_PACKET_v1.md")
    protocol_hash = digest(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_PROTOCOL_v1_FROZEN.md")
    check("claim hash", claim_hash == EXPECTED_CLAIM == result["claim_hash"], claim_hash)
    check("protocol hash", protocol_hash == EXPECTED_PROTOCOL == result["protocol_hash"], protocol_hash)
    check("path row count", len(paths) == result["counts"]["trajectories"] == 672, f"rows={len(paths)}")
    check("prefix row count", len(prefixes) == result["counts"]["prefix_measurements"] == 6048, f"rows={len(prefixes)}")
    check("matched-pair count", len(pairs) == result["counts"]["matched_pairs"] == 588, f"rows={len(pairs)}")
    check("cadence-pair count", len(cadence) == result["counts"]["cadence_pairs"] == 192, f"rows={len(cadence)}")
    natural = ["split", "duration", "turns", "amplitude", "seed", "variant"]
    check("path natural key unique", not paths.duplicated(natural).any(), f"duplicates={paths.duplicated(natural).sum()}")
    check("all common suffixes exact", float(pairs.suffix_error.max()) < 1e-12 and float(pairs.recent_tick_error.max()) < 1e-12, f"suffix={pairs.suffix_error.max():.3g}; recent={pairs.recent_tick_error.max():.3g}")

    hp = paths[paths.split == "holdout"]
    hpair = pairs[pairs.split == "holdout"]
    hc = closure[closure.split == "holdout"]
    recomputed = {
        "max_reconstruction_error": float(hp.reconstruction_error.max()),
        "retained_share": float((hpair.final_history_distance >= 0.02).mean()),
        "median_retention": float(hpair.retention_ratio.median()),
        "median_emergence": float(hpair.emergence_progress.dropna().median()),
        "median_closure_jump": float(hpair.closure_jump_share.median()),
        "cadence_median": float(cadence.history_distance.median()),
        "cadence_share": float((cadence.history_distance <= 0.12).mean()),
    }
    for key, value in recomputed.items():
        expected = float(result["parent_checks"][key])
        check(f"parent metric {key}", abs(value - expected) < 1e-12, f"{value:.12g}")

    front = {
        "final_small_share": float((hpair.final_history_distance <= 0.02).mean()),
        "median_final_distance": float(hpair.final_history_distance.median()),
        "median_emergence": recomputed["median_emergence"],
        "median_closure_jump": recomputed["median_closure_jump"],
        "local_median_error": float(hc.absolute_error.median()),
        "local_p95_error": float(hc.absolute_error.quantile(0.95)),
    }
    for key, value in front.items():
        expected = float(result["front_checks"][key])
        check(f"front metric {key}", abs(value - expected) < 1e-10, f"{value:.12g}")

    p1 = recomputed["max_reconstruction_error"] < 1e-9
    p2 = recomputed["retained_share"] >= 0.70 and recomputed["median_retention"] >= 0.30
    p3 = recomputed["median_emergence"] <= 0.75 and recomputed["median_closure_jump"] < 0.25
    p4 = recomputed["cadence_median"] <= 0.08 and recomputed["cadence_share"] >= 0.80
    f1 = front["final_small_share"] >= 0.90 and front["median_final_distance"] <= 0.01
    f2 = front["median_emergence"] >= 0.90 and front["median_closure_jump"] >= 0.50
    f3 = front["local_median_error"] < 1 and front["local_p95_error"] < 2
    expected_gate_values = [p1, p2, p3, p4, f1, f2, f3]
    check("gate rows", list(gates.passed.astype(str).str.lower() == "true") == expected_gate_values, str(expected_gate_values))
    check("parent verdict", result["parent_supported"] is bool(p1 and p2 and p3 and p4), str(result["parent_supported"]))
    check("pure-front verdict", result["pure_closure_front_supported"] is bool(f1 and f2), str(result["pure_closure_front_supported"]))
    check("local-front verdict", result["local_closure_locator_supported"] is bool(f3), str(result["local_closure_locator_supported"]))

    # Reconstruct every complete raw example path from x_motion.
    max_recon = 0.0
    for _, group in examples.groupby("variant"):
        group = group.sort_values("tick")
        xm = group.x_motion.to_numpy()
        delta = V_REF * np.arctanh(np.clip(xm[1:] - 1, -1 + 1e-14, 1 - 1e-14))
        reconstructed_path = np.r_[group.unwrapped.iloc[0], group.unwrapped.iloc[0] + np.cumsum(delta)]
        max_recon = max(max_recon, float(np.max(np.abs(reconstructed_path - group.unwrapped.to_numpy()))))
    check("raw-example tick reconstruction", max_recon < 1e-9, f"max={max_recon:.3e}")

    # Independently recompute final history distances for all seven raw pairs.
    gradual = examples[examples.variant == "gradual reference"].sort_values("tick").unwrapped.to_numpy()
    gv = vector(gradual)
    raw_failures = 0
    for variant, group in examples[examples.variant != "gradual reference"].groupby("variant"):
        u = group.sort_values("tick").unwrapped.to_numpy()
        distance = math.sqrt(float(np.mean((vector(u) - gv) ** 2)))
        saved = curves[(curves.split == "holdout") & (curves.duration == 769) & (curves.turns == 5) & (np.isclose(curves.amplitude, 0.24)) & (curves.seed == 10) & (curves.variant == variant) & (np.isclose(curves.progress, 1.0))].history_distance.iloc[0]
        raw_failures += int(abs(distance - saved) >= 1e-10)
    check("raw-example history vectors", raw_failures == 0, f"failures={raw_failures}")

    with Image.open(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_FIGURE.png") as im:
        size = im.size
    check("figure dimensions", size == (2400, 1500), f"size={size}")

    passed = all(item["passed"] for item in checks)
    payload = {"test": "T350 independent artifact validation", "passed": passed, "checks_passed": sum(item["passed"] for item in checks), "checks_total": len(checks), "checks": checks}
    (HERE / "T350_TICK_PARENT_CLOSURE_FRONT_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# T350 independent validation",
        "",
        f"**Verdict:** **{'PASS' if passed else 'FAIL'} — {payload['checks_passed']}/{payload['checks_total']} checks**",
        "",
        "The validator does not import the T350 run script. It recomputes frozen hashes, row integrity, all headline metrics and gates, tick reconstruction from every raw example, and all seven complete raw-example history vectors.",
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
    ]
    lines.extend(f"| {c['check']} | {'PASS' if c['passed'] else 'FAIL'} | `{c['detail']}` |" for c in checks)
    (HERE / "T350_TICK_PARENT_CLOSURE_FRONT_VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
