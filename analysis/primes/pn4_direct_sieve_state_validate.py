from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "PN3A_ADULT_SIEVE_DIAGNOSTIC_DATA.npz"
PROTOCOL = HERE / "PN4_DIRECT_SIEVE_STATE_ARA_PROTOCOL.md"
PRIMARY = HERE / "pn4_direct_sieve_state_ara.py"
RESULTS = HERE / "PN4_DIRECT_SIEVE_STATE_RESULTS.json"
PATHS = HERE / "PN4_DIRECT_SIEVE_STATE_PATHS.csv"
ARTIFACT = HERE / "PN4_DIRECT_SIEVE_STATE_ARTIFACT.json"
OUTPUT = HERE / "PN4_DIRECT_SIEVE_STATE_VALIDATION.json"

WINDOW_HIGH = {"r6": 1_010_000, "r7": 10_100_000, "r8": 101_000_000, "r9": 1_010_000_000}
CELLS = 24
EPS = 1e-12


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            data = stream.read(524_288)
            if not data:
                break
            h.update(data)
    return h.hexdigest().upper()


def primes_to(n: int) -> np.ndarray:
    flags = bytearray(b"\x01") * (n + 1)
    flags[0:2] = b"\x00\x00"
    for p in range(2, math.isqrt(n) + 1):
        if flags[p]:
            flags[p * p : n + 1 : p] = b"\x00" * (((n - p * p) // p) + 1)
    return np.fromiter((i for i, flag in enumerate(flags) if flag and i > 29), dtype=np.int64)


def independent_and_cells(rung: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    q = primes_to(math.isqrt(WINDOW_HIGH[rung] - 1))
    t = np.log(q.astype(float) / 31.0) / math.log(float(q[-1]) / 31.0)
    cell = np.minimum((t * CELLS).astype(int), CELLS - 1)
    products = np.ones(CELLS, dtype=float)
    for j in range(CELLS):
        selected = q[cell == j]
        if len(selected):
            products[j] = np.prod(1.0 - 1.0 / selected.astype(float))
    return q, cell, np.cumprod(products)


def direct_path(death: np.ndarray, q: np.ndarray, cell: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    alive = len(death)
    before = np.zeros(CELLS, dtype=np.int64)
    removed = np.zeros(CELLS, dtype=np.int64)
    survival = np.zeros(CELLS, dtype=float)
    for j in range(CELLS):
        before[j] = alive
        gate_values = q[cell == j]
        removed[j] = sum(int(np.count_nonzero(death == gate)) for gate in gate_values)
        alive -= int(removed[j])
        survival[j] = alive / len(death)
    return before, removed, survival


def monotone(values: np.ndarray) -> np.ndarray:
    return np.minimum.accumulate(np.clip(values.astype(float), EPS, 1.0))


def path_score(prediction: np.ndarray, before: np.ndarray, deaths: np.ndarray, actual: np.ndarray) -> dict[str, float]:
    pth = monotone(prediction)
    previous = np.concatenate(([1.0], pth[:-1]))
    hazard = np.clip(1.0 - pth / previous, EPS, 1.0 - EPS)
    d = deaths.astype(float)
    n = before.astype(float)
    loss = -(d * np.log2(hazard) + (n - d) * np.log2(1.0 - hazard))
    return {
        "log_loss_bits_per_at_risk_event": float(loss.sum() / n.sum()),
        "survival_rmse": float(np.sqrt(np.mean((pth - actual) ** 2))),
        "terminal_prediction": float(pth[-1]),
        "terminal_actual": float(actual[-1]),
        "terminal_absolute_relative_error": float(abs(pth[-1] - actual[-1]) / actual[-1]),
    }


def close(a: float, b: float, tolerance: float = 2e-12) -> bool:
    return abs(a - b) <= tolerance * max(1.0, abs(a), abs(b))


def main() -> None:
    checks: dict[str, bool] = {}
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    archive = np.load(SOURCE, allow_pickle=False)
    checks["cell_count_24"] = results["cells"] == CELLS
    checks["source_hash"] = results["source_sha256"] == file_hash(SOURCE)
    checks["protocol_hash"] = results["protocol_sha256"] == file_hash(PROTOCOL)
    checks["primary_script_hash"] = results["script_sha256"] == file_hash(PRIMARY)
    for path in (SOURCE, PROTOCOL, PRIMARY, RESULTS, PATHS):
        checks[f"artifact_hash__{path.name}"] = artifact["files"][path.name] == file_hash(path)

    rebuilt: dict[str, dict[str, np.ndarray]] = {}
    for rung in WINDOW_HIGH:
        q, cell, independent = independent_and_cells(rung)
        cb, cd, cs = direct_path(archive[f"{rung}__candidate_death"], q, cell)
        eb, ed, es = direct_path(archive[f"{rung}__edge_death"], q, cell)
        rebuilt[rung] = {
            "candidate_before": cb,
            "candidate_deaths": cd,
            "candidate_survival": cs,
            "edge_before": eb,
            "edge_deaths": ed,
            "edge_survival": es,
            "candidate_independent": independent,
            "edge_independent": independent**2,
            "j": np.log(es / cs**2),
        }
        summary = results["rung_summaries"][rung]
        checks[f"{rung}_candidate_terminal"] = close(summary["candidate_terminal_survival"], float(cs[-1]))
        checks[f"{rung}_edge_terminal"] = close(summary["edge_terminal_survival"], float(es[-1]))
        checks[f"{rung}_coupling_j"] = close(summary["terminal_coupling_j"], float(rebuilt[rung]["j"][-1]))

    csv_rows = list(csv.DictReader(PATHS.open("r", encoding="utf-8", newline="")))
    checks["csv_row_count"] = len(csv_rows) == 4 * CELLS
    for rung in WINDOW_HIGH:
        rows = [row for row in csv_rows if row["rung"] == rung]
        checks[f"{rung}_csv_count"] = len(rows) == CELLS
        for field in ("candidate_survival", "edge_survival", "candidate_independent", "edge_independent", "coupling_j"):
            values = np.array([float(row[field]) for row in rows])
            source_field = "j" if field == "coupling_j" else field
            checks[f"{rung}_csv_{field}"] = bool(np.allclose(values, rebuilt[rung][source_field], rtol=0.0, atol=2e-12))

    r7, r8, r9 = rebuilt["r7"], rebuilt["r8"], rebuilt["r9"]
    candidate_models = {
        "independent_sieve": r9["candidate_independent"],
        "ara_same_form_residual": r9["candidate_independent"] + (r8["candidate_survival"] - r8["candidate_independent"]),
        "raw_multiplicative_ratio": r9["candidate_independent"] * r8["candidate_survival"] / r8["candidate_independent"],
    }
    candidate_two = 1.0 - (
        2.0 * (1.0 - r9["candidate_independent"])
        + 2.0 * (2.0 * (1.0 - r8["candidate_survival"]) - 2.0 * (1.0 - r8["candidate_independent"]))
        - (2.0 * (1.0 - r7["candidate_survival"]) - 2.0 * (1.0 - r7["candidate_independent"]))
    ) / 2.0
    candidate_models["ara_two_rung_residual"] = candidate_two

    edge_models = {
        "independent_pair": r9["edge_independent"],
        "ara_direct_edge_residual": r9["edge_independent"] + (r8["edge_survival"] - r8["edge_independent"]),
        "ara_coupled_relation": monotone(candidate_models["ara_same_form_residual"]) ** 2 * np.exp(r8["j"]),
        "raw_multiplicative_edge_ratio": r9["edge_independent"] * r8["edge_survival"] / r8["edge_independent"],
    }
    score_sets = {
        "candidate": (
            candidate_models,
            r9["candidate_before"],
            r9["candidate_deaths"],
            r9["candidate_survival"],
        ),
        "edge": (edge_models, r9["edge_before"], r9["edge_deaths"], r9["edge_survival"]),
    }
    for entity, (models, before, deaths, actual) in score_sets.items():
        saved = results["transfers"]["r8_to_r9"]["scores"][entity]
        for model, prediction in models.items():
            recomputed = path_score(prediction, before, deaths, actual)
            for metric, value in recomputed.items():
                checks[f"r9_{entity}_{model}_{metric}"] = close(value, saved[model][metric], tolerance=5e-12)

    factor = math.exp(0.5772156649015329) / 2.0
    terminal = results["terminal_established_comparators"]
    checks["mertens_candidate"] = close(
        terminal["candidate"]["mertens_pnt_factor_prediction"], float(r9["candidate_independent"][-1] * factor)
    )
    checks["mertens_edge"] = close(
        terminal["edge"]["mertens_pnt_factor_squared_prediction"], float(r9["edge_independent"][-1] * factor**2)
    )

    failed = sorted(key for key, passed in checks.items() if not passed)
    output = {
        "test_id": results["test_id"],
        "validator_independence": "Does not import pn4_direct_sieve_state_ara.py; independently rebuilds cells, paths, R9 formulas and scores.",
        "checks_passed": int(sum(checks.values())),
        "checks_total": len(checks),
        "all_passed": not failed,
        "failed": failed,
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: output[key] for key in ("checks_passed", "checks_total", "all_passed", "failed")}, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
