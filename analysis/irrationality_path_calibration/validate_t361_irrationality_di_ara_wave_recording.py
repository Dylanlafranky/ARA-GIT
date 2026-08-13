"""Independent validation for T361. Does not import the analysis program."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PREFIX = HERE / "T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING"
SOURCE_ZIP = HERE / "T358_SOURCE_DATA.zip"
CYCLE = Path(f"{PREFIX}_CYCLE_METRICS.csv")
RECORD = Path(f"{PREFIX}_RECORD_SUMMARY.csv")
PARENT = Path(f"{PREFIX}_PARENT_WAVES.csv")
GATES = Path(f"{PREFIX}_FROZEN_GATES.csv")
EXAMPLE = Path(f"{PREFIX}_EXAMPLE_PATH.csv")
RESULTS = Path(f"{PREFIX}_RESULTS.json")
FIGURE = Path(f"{PREFIX}_FIGURE.png")
OUT_JSON = Path(f"{PREFIX}_VALIDATION.json")
OUT_MD = HERE / "T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_VALIDATION.md"


def digest(path: Path, kind: str = "sha256") -> str:
    h = hashlib.new(kind)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def close(a, b, atol=1e-10) -> bool:
    return bool(np.allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float), atol=atol, rtol=1e-9, equal_nan=True))


def main() -> None:
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    cycle = pd.read_csv(CYCLE)
    record = pd.read_csv(RECORD)
    parent = pd.read_csv(PARENT)
    gates = pd.read_csv(GATES)
    example = pd.read_csv(EXAMPLE)

    check("source MD5", digest(SOURCE_ZIP, "md5") == "abe81a3631481b58977925daf453ede5", digest(SOURCE_ZIP, "md5"))
    expected_hashes = {
        "T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_CLAIM_PACKET_v1.md": "180f60856b6a7ee45c3d1330f00c6396a380061b2f35f75d1950fda660c41dae",
        "T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_PROTOCOL_v1_FROZEN.md": "3d94fca5959a100d4e8b2824f6f8fa95c4ab4d7b8d0b42c6418c47ac8156bcbb",
        "T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_PROTOCOL_v2_FROZEN.md": "28cdbc84e614f97b0988fc46a62035ead253a8ad0caf8bb2c21ce15bdd75e44c",
        "T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_PROTOCOL_v3_FROZEN.md": "63e815b6d674bf2b377ffde52da7060461f5dac9cecbd17e5d990f2e86cda438",
    }
    for name, expected in expected_hashes.items():
        actual = digest(HERE / name)
        check(f"frozen hash {name}", actual == expected, actual)

    required_cycle = {"delta_r", "pair", "test_cycle", "method", "RMSE_ARA", "waveform_r", "direction_agreement", "quadrant_agreement", "turn_error", "endpoint_error", "angular_path_error"}
    check("cycle schema", required_cycle.issubset(cycle.columns), f"columns={len(cycle.columns)}")
    check("nine records", set(cycle.delta_r.unique()) == {0, 50, 100, 150, 170, 190, 240, 290, 340}, str(sorted(cycle.delta_r.unique())))
    check("forty pairs per record", bool((cycle.groupby("delta_r").pair.nunique() == 40).all()), str(cycle.groupby("delta_r").pair.nunique().to_dict()))
    check("four methods per cycle", bool((cycle.groupby(["delta_r", "pair", "test_cycle"]).method.nunique() == 4).all()), "all cycle groups have four methods")
    check("coordinate ranges", bool(cycle.direction_agreement.between(0, 1).all() and cycle.quadrant_agreement.between(0, 1).all() and cycle.turn_error.between(0, 1).all()), "agreement and turn metrics bounded")

    metrics = ["RMSE_ARA", "MAE_ARA", "waveform_r", "direction_agreement", "quadrant_agreement", "turn_error", "endpoint_error", "angular_path_error", "radial_path_error", "fallback_steps"]
    recomputed = cycle.groupby(["delta_r", "method"], as_index=False)[metrics].median().sort_values(["delta_r", "method"]).reset_index(drop=True)
    stored = record.sort_values(["delta_r", "method"]).reset_index(drop=True)
    check("record medians", all(close(recomputed[m], stored[m]) for m in metrics), "recomputed from complete cycle table")

    primary = recomputed[recomputed.method == "primary"].set_index("delta_r")
    blind = recomputed[recomputed.method == "direction_blind"].set_index("delta_r")
    wrong = recomputed[recomputed.method == "wrong_lineage"].set_index("delta_r")
    ps = parent.groupby("delta_r", as_index=True).first()
    masks = [
        (primary.waveform_r >= 0.80) & (primary.RMSE_ARA <= 0.30),
        (primary.direction_agreement >= 0.75) & (primary.quadrant_agreement >= 0.75) & (primary.turn_error <= 0.10),
        (primary.endpoint_error <= 0.20) & (primary.angular_path_error <= 0.15),
        ((blind.RMSE_ARA - primary.RMSE_ARA) >= 0.05) | ((primary.direction_agreement - blind.direction_agreement) >= 0.05),
        ((wrong.RMSE_ARA - primary.RMSE_ARA) >= 0.05) | ((primary.waveform_r - wrong.waveform_r) >= 0.05),
        (ps.parent_waveform_r >= 0.90) & (ps.parent_RMSE_ARA <= 0.20),
    ]
    hits = [int(x.sum()) for x in masks]
    passed = [hits[i] >= [7, 7, 7, 5, 5, 7][i] for i in range(6)]
    check("frozen gate hits", hits == gates.record_hits.astype(int).tolist(), f"recomputed={hits}")
    check("frozen gate verdicts", passed == gates.passed.astype(bool).tolist(), f"recomputed={passed}")
    check("overall verdict", bool(result["overall"]) == all(passed), f"recomputed={all(passed)}")

    err = example.child_primary.to_numpy() - example.child_actual.to_numpy()
    rmse = float(np.sqrt(np.mean(err**2)))
    check("example path arithmetic", np.isfinite(rmse) and len(example) == 64, f"rows=64; RMSE={rmse:.6f}")
    check("figure present", FIGURE.exists() and FIGURE.stat().st_size > 100_000, f"bytes={FIGURE.stat().st_size if FIGURE.exists() else 0}")

    ok = all(c["passed"] for c in checks)
    output = {"validation_passed": ok, "checks": checks, "recomputed_gate_hits": hits, "recomputed_gate_passes": passed}
    OUT_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")
    lines = ["# T361 independent validation", "", f"**Validation:** **{'PASS' if ok else 'FAIL'}**", "", "| check | result | detail |", "|---|---|---|"]
    lines.extend(f"| {c['check']} | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

