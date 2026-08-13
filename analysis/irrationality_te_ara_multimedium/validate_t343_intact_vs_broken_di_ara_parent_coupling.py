#!/usr/bin/env python3
"""Independent artifact validator for frozen T343.

This script does not import the runner. It reconstructs all primary scores,
randomisation p-values, gates, and the cross-domain verdict from the exported
tables.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
STEM = "T343_INTACT_VS_BROKEN_DI_ARA_PARENT_COUPLING"
PROTOCOL = HERE / f"{STEM}_PROTOCOL_v1_FROZEN.md"
COMP_ADDENDUM = HERE / f"{STEM}_COMPUTATIONAL_ADDENDUM_v1_FROZEN.md"
INF_ADDENDUM = HERE / f"{STEM}_INFERENCE_ADDENDUM_v1_FROZEN.md"
EXPECTED = {
    PROTOCOL: "4820C769B1B54377A6B6A9250A86DB5053F1777825A20F8D57C9C67DF98E6212",
    COMP_ADDENDUM: "90C41E1DA2781F4233C2633EAB8AACA4AE6CB41838C72688FD1B82830E9ECBBC",
    INF_ADDENDUM: "6C867E57F1F0FE3BDDEFFE41439F0B12D4C0B2503CE9AE9F953A002BB85680EC",
}
SUMMARY = HERE / f"{STEM}_SUMMARY.csv"
COUNTS = HERE / f"{STEM}_MODEL_COUNTS.csv"
BROKEN = HERE / f"{STEM}_BROKEN_NULLS.csv"
EFFECTS = HERE / f"{STEM}_BLOCK_EFFECTS.csv"
QUALITY = HERE / f"{STEM}_DATA_QUALITY.csv"
RESULTS = HERE / f"{STEM}_RESULTS.json"
MANIFEST = HERE / f"{STEM}_SOURCE_MANIFEST.json"
FIGURE = HERE / f"{STEM}_FIGURE.png"
EXPLORER = HERE / f"{STEM}_EXPLORER_3D.html"
REPORT = HERE / f"{STEM}_REPORT_2026-08-05.md"
DOMAIN_FIGURES = HERE / "t343_domain_figures"

ALPHA = 0.5
SIGN_FLIPS = 10_000
BROKEN_CONTROLS = 1000
SIGN_SEED = 34320260806
DOMAINS = ("pendulum", "hydraulic", "bubbles", "cold_room", "acoustics", "qutrit", "river")
LABELS = ("bA", "aB", "Ab", "Ba")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def close(a: float, b: float, name: str, tol: float = 2e-12) -> None:
    require(math.isfinite(float(a)) and math.isfinite(float(b)), f"non-finite {name}")
    require(abs(float(a) - float(b)) <= tol, f"{name}: {a} != {b}")


def matrix(frame: pd.DataFrame, domain: str, split: str, model: str) -> np.ndarray:
    current = LABELS if model == "parent" else (("A-", "A+") if model == "radial" else ("B-", "B+"))
    part = frame[(frame.domain == domain) & (frame.split == split) & (frame.model == model)]
    pivot = part.pivot(index="current_state", columns="target_state", values="count")
    return pivot.reindex(index=current, columns=LABELS).fillna(0).to_numpy(dtype=np.int64)


def loss(cal: np.ndarray, hold: np.ndarray) -> float:
    probs = (cal + ALPHA) / (cal + ALPHA).sum(axis=1, keepdims=True)
    return float(-np.sum(hold * np.log(probs)) / hold.sum())


def sign_flip_p(values: np.ndarray, seed: int) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    observed = float(values.mean())
    rng = np.random.default_rng(seed)
    exceed = 0
    remaining = SIGN_FLIPS
    while remaining:
        batch = min(250, remaining)
        signs = rng.integers(0, 2, size=(batch, len(values)), dtype=np.int8) * 2 - 1
        exceed += int(np.count_nonzero(np.mean(signs * values[None, :], axis=1) >= observed))
        remaining -= batch
    return observed, float((1 + exceed) / (SIGN_FLIPS + 1))


def main() -> None:
    for path, expected in EXPECTED.items():
        require(sha256(path) == expected, f"frozen hash mismatch: {path.name}")
    for path in (SUMMARY, COUNTS, BROKEN, EFFECTS, QUALITY, RESULTS, MANIFEST, FIGURE, EXPLORER, REPORT):
        require(path.exists() and path.stat().st_size > 0, f"missing artifact: {path.name}")

    summary = pd.read_csv(SUMMARY)
    counts = pd.read_csv(COUNTS)
    broken = pd.read_csv(BROKEN)
    effects = pd.read_csv(EFFECTS)
    quality = pd.read_csv(QUALITY).set_index("domain")
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    require(tuple(summary.domain) == DOMAINS, "domain order changed")
    require(len(broken) == len(DOMAINS) * BROKEN_CONTROLS, "broken-control row count")
    require(manifest["t343_protocol_sha256"] == EXPECTED[PROTOCOL], "manifest protocol hash")
    require(manifest["t343_computational_addendum_sha256"] == EXPECTED[COMP_ADDENDUM], "manifest computational hash")
    require(manifest["t343_inference_addendum_sha256"] == EXPECTED[INF_ADDENDUM], "manifest inference hash")

    recomputed_passes = []
    for offset, row in enumerate(summary.itertuples(index=False)):
        domain = row.domain
        model_losses = {}
        for model in ("parent", "radial", "angular"):
            cal = matrix(counts, domain, "calibration", model)
            hold = matrix(counts, domain, "holdout", model)
            model_losses[model] = loss(cal, hold)
        close(model_losses["parent"], row.parent_log_loss, f"{domain} parent loss")
        close(model_losses["radial"], row.radial_child_log_loss, f"{domain} radial loss")
        close(model_losses["angular"], row.angular_child_log_loss, f"{domain} angular loss")
        close(model_losses["radial"] - model_losses["parent"], row.delta_radial, f"{domain} radial delta")
        close(model_losses["angular"] - model_losses["parent"], row.delta_angular, f"{domain} angular delta")

        eb = effects[effects.domain == domain]
        observed_r, p_r = sign_flip_p(eb.delta_radial.to_numpy(float), SIGN_SEED + offset * 2)
        observed_a, p_a = sign_flip_p(eb.delta_angular.to_numpy(float), SIGN_SEED + offset * 2 + 1)
        close(observed_r, row.block_mean_delta_radial, f"{domain} radial block mean")
        close(observed_a, row.block_mean_delta_angular, f"{domain} angular block mean")
        close(p_r, row.p_radial, f"{domain} radial p")
        close(p_a, row.p_angular, f"{domain} angular p")

        bn = broken[broken.domain == domain].sort_values("replicate")
        require(len(bn) == BROKEN_CONTROLS, f"{domain} broken controls")
        require(np.array_equal(bn.replicate.to_numpy(int), np.arange(1, BROKEN_CONTROLS + 1)), f"{domain} replicate ids")
        expected_axes = np.where(np.arange(1, BROKEN_CONTROLS + 1) % 2, "radial_a", "angular_b")
        require(np.array_equal(bn.axis_shifted.to_numpy(), expected_axes), f"{domain} axis alternation")
        vals = bn.holdout_log_loss.to_numpy(float)
        close(np.median(vals), row.broken_median_log_loss, f"{domain} broken median")
        close(np.quantile(vals, 0.05), row.broken_q05_log_loss, f"{domain} broken q05")
        close(np.quantile(vals, 0.95), row.broken_q95_log_loss, f"{domain} broken q95")
        p_b = float((1 + np.count_nonzero(vals <= row.parent_log_loss)) / (BROKEN_CONTROLS + 1))
        close(p_b, row.p_broken, f"{domain} broken p")

        q = quality.loc[domain]
        eligible = bool(
            int(row.holdout_transitions) >= 1000
            and int(row.holdout_blocks) >= 20
            and min(int(getattr(row, f"states_{name}")) for name in LABELS) >= 20
            and all(math.isfinite(float(x)) for x in (
                row.parent_log_loss, row.radial_child_log_loss, row.angular_child_log_loss,
                row.broken_median_log_loss, row.p_broken, row.p_radial, row.p_angular,
            ))
        )
        require(eligible == bool(row.eligible), f"{domain} eligibility")
        require(int(q.holdout_transitions) == int(row.holdout_transitions), f"{domain} quality transitions")
        passed = bool(
            eligible
            and row.delta_radial > 0 and row.p_radial <= 0.05
            and row.delta_angular > 0 and row.p_angular <= 0.05
            and row.broken_median_log_loss > row.parent_log_loss and row.p_broken <= 0.05
        )
        require(passed == bool(row.domain_pass), f"{domain} pass gate")
        recomputed_passes.append(passed)
        require((DOMAIN_FIGURES / f"T343_{domain}_PARENT_COUPLING.png").exists(), f"{domain} figure")

    eligible_count = int(summary.eligible.sum())
    passing_count = int(np.count_nonzero(recomputed_passes))
    if eligible_count >= 5 and passing_count / eligible_count >= 0.70:
        verdict = "SUPPORTED AS A TRANSFERABLE PARENT-COUPLING RULE"
    elif passing_count >= 2:
        verdict = "PARTIAL / PAIR-SPECIFIC"
    else:
        verdict = "NOT SUPPORTED BY THIS CONSTRUCTION"
    require(results["eligible_domains"] == eligible_count, "eligible-domain result")
    require(results["passing_domains"] == passing_count, "passing-domain result")
    require(results["verdict"] == verdict, "cross-domain verdict")
    print(f"PASS: T343 independently validated ({passing_count}/{eligible_count}; {verdict}).")


if __name__ == "__main__":
    main()
