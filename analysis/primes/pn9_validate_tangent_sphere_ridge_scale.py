"""Independent headline validation for PN9.

This script deliberately does not import the PN9 scorer.  It reconstructs the
24-bin coordinates, transfer models, divergences and observed information from
the frozen gap packets using separate code paths.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
RESULT = HERE / "PN9_TANGENT_SPHERE_RIDGE_SCALE_RESULTS.json"
DEV = HERE / "PN7C_DEVELOPMENT_GAPS.npz"
TARGET = HERE / "PN7C_R11_TARGET_GAPS.npz"
FIGURE = HERE / "PN9_TANGENT_SPHERE_RIDGE_SCALE_FIGURE.png"
OUT = HERE / "PN9_TANGENT_SPHERE_RIDGE_SCALE_VALIDATION.json"
B = 24
ALPHA = 0.5
STEP = 750_000
FIRST = {"R9": 1_000_000_007, "R10": 10_000_000_019, "R11": 100_000_000_003}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(1 << 20)
            if not block:
                return h.hexdigest().upper()
            h.update(block)


def make_states(g: np.ndarray, first: int) -> tuple[np.ndarray, np.ndarray, float]:
    n = g.size - 1
    xs = np.empty(n, np.uint8)
    ys = np.empty(n, np.uint8)
    offset = 0
    worst = 0.0
    for a in range(0, n, STEP):
        z = min(n, a + STEP)
        gl = g[a:z].astype(np.float64)
        gr = g[a + 1:z + 1].astype(np.float64)
        diameter_sum = gl + gr
        local = diameter_sum / 2.0
        pos = first + offset + np.cumsum(g[a:z].astype(np.int64), dtype=np.int64)
        offset += int(g[a:z].astype(np.int64).sum())
        home = np.log(pos.astype(np.float64))
        xf = 2.0 * gr / diameter_sum
        yf = 2.0 * local / (local + home)
        xs[a:z] = np.clip(np.floor(B * xf / 2.0), 0, B - 1).astype(np.uint8)
        ys[a:z] = np.clip(np.floor(B * yf / 2.0), 0, B - 1).astype(np.uint8)
        recovered_local = home * yf / (2.0 - yf)
        worst = max(
            worst,
            float(np.max(np.abs(xf * recovered_local - gr))),
            float(np.max(np.abs((2.0 - xf) * recovered_local - gl))),
        )
    return xs, ys, worst


def accumulate(x: np.ndarray, y: np.ndarray, out_x: np.ndarray, out_xy: np.ndarray) -> None:
    n = x.size - 2
    for a in range(0, n, STEP):
        z = min(n, a + STEP)
        xp = x[a:z].astype(np.int64)
        xc = x[a + 1:z + 1].astype(np.int64)
        yc = y[a + 1:z + 1].astype(np.int64)
        xt = x[a + 2:z + 2].astype(np.int64)
        cx = (xp * B + xc) * B + xt
        cxy = ((xp * B + xc) * B + yc) * B + xt
        out_x += np.bincount(cx, minlength=B**3).reshape(out_x.shape)
        out_xy += np.bincount(cxy, minlength=B**4).reshape(out_xy.shape)


def score(x: np.ndarray, y: np.ndarray, px: np.ndarray, pxy: np.ndarray) -> tuple[float, float]:
    total_x = total_xy = 0.0
    n = x.size - 2
    for a in range(0, n, STEP):
        z = min(n, a + STEP)
        xp = x[a:z].astype(np.int64)
        xc = x[a + 1:z + 1].astype(np.int64)
        yc = y[a + 1:z + 1].astype(np.int64)
        xt = x[a + 2:z + 2].astype(np.int64)
        total_x += float(np.sum(-np.log2(px[xp, xc, xt])))
        total_xy += float(np.sum(-np.log2(pxy[xp, xc, yc, xt])))
    return total_x / n, total_xy / n


def entropy(counts: np.ndarray) -> float:
    rows = counts.reshape(-1, B).astype(np.float64)
    totals = rows.sum(1)
    rows = rows[totals > 0]
    totals = totals[totals > 0]
    p = rows / totals[:, None]
    logp = np.zeros_like(p)
    np.log2(p, out=logp, where=p > 0)
    return float(-np.sum(totals[:, None] * p * logp) / totals.sum())


def js(a: np.ndarray, b: np.ndarray) -> float:
    p = a.astype(float) / a.sum()
    q = b.astype(float) / b.sum()
    m = (p + q) / 2
    lp = np.zeros_like(p)
    lq = np.zeros_like(q)
    positive_p = p > 0
    positive_q = q > 0
    lp[positive_p] = np.log2(p[positive_p] / m[positive_p])
    lq[positive_q] = np.log2(q[positive_q] / m[positive_q])
    return float((np.sum(p * lp) + np.sum(q * lq)) / 2)


def main() -> None:
    registered = json.loads(RESULT.read_text(encoding="utf-8"))
    with np.load(DEV) as f:
        gaps = {"R9": f["r9__gaps"].astype(np.uint16), "R10": f["r10__gaps"].astype(np.uint16)}
    with np.load(TARGET) as f:
        gaps["R11"] = f["r11__gaps"].astype(np.uint16)

    state = {}
    errors = {}
    for name in ("R9", "R10", "R11"):
        x, y, error = make_states(gaps[name], FIRST[name])
        state[name] = (x, y)
        errors[name] = error

    train_x = np.zeros((B, B, B), dtype=np.int64)
    train_xy = np.zeros((B, B, B, B), dtype=np.int64)
    accumulate(*state["R9"], train_x, train_xy)
    accumulate(*state["R10"], train_x, train_xy)
    px = (train_x + ALPHA) / (train_x.sum(2, keepdims=True) + ALPHA * B)
    pxy = (train_xy + ALPHA) / (train_xy.sum(3, keepdims=True) + ALPHA * B)
    ce_x, ce_xy = score(*state["R11"], px, pxy)

    empirical_x = np.zeros_like(train_x)
    empirical_xy = np.zeros_like(train_xy)
    accumulate(*state["R11"], empirical_x, empirical_xy)
    scale_information = entropy(empirical_x) - entropy(empirical_xy)
    hist = {name: np.bincount(state[name][1], minlength=B) for name in state}
    computed = {
        "R11_X_M2_cross_entropy_bits": ce_x,
        "R11_XY_M2_cross_entropy_bits": ce_xy,
        "R11_gain_bits": ce_x - ce_xy,
        "R9_R10_y_js_bits": js(hist["R9"], hist["R10"]),
        "R10_R11_y_js_bits": js(hist["R10"], hist["R11"]),
        "R11_conditional_scale_information_bits": scale_information,
        "maximum_gap_reconstruction_error": max(errors.values()),
    }
    expected = {
        "R11_X_M2_cross_entropy_bits": registered["scores"]["R11"]["24"]["X-M2"]["cross_entropy_bits"],
        "R11_XY_M2_cross_entropy_bits": registered["scores"]["R11"]["24"]["XY-M2"]["cross_entropy_bits"],
        "R11_gain_bits": registered["cross_entropy_gains_bits"]["R11"]["24"],
        "R9_R10_y_js_bits": registered["scale_distribution_js"]["R9_R10_bits"],
        "R10_R11_y_js_bits": registered["scale_distribution_js"]["R10_R11_bits"],
        "R11_conditional_scale_information_bits": registered["conditional_scale_information_controls"][0]["conditional_scale_information_bits"],
    }
    checks = {
        key: {"expected": value, "computed": computed[key], "absolute_difference": abs(value - computed[key]),
              "passed": abs(value - computed[key]) <= 1e-11}
        for key, value in expected.items()
    }
    with Image.open(FIGURE) as image:
        figure_check = {"width": image.width, "height": image.height, "mode": image.mode,
                        "passed": image.width == 1600 and image.height == 1040 and image.mode == "RGB"}
    validation = {
        "test_id": "PN9/INDEPENDENT-VALIDATION-v1",
        "does_not_import_main_scorer": True,
        "source_hashes": {DEV.name: digest(DEV), TARGET.name: digest(TARGET), RESULT.name: digest(RESULT)},
        "computed": computed,
        "headline_checks": checks,
        "figure_check": figure_check,
        "all_checks_passed": all(item["passed"] for item in checks.values()) and figure_check["passed"],
    }
    OUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
