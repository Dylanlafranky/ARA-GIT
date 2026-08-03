from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
RESULTS = BASE / "results"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    summary_path = RESULTS / "temporal_ara_summary.json"
    target_path = RESULTS / "temporal_ara_target_results.csv"
    sample_path = RESULTS / "temporal_ara_window_sample.csv"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    split_total = sum(summary["splits"][split]["windows"] for split in summary["splits"])
    assert split_total == summary["diagnostics"]["eligible_windows"] == 152780
    assert summary["splits"]["evaluation"]["videos"] == 21
    assert summary["splits"]["holdout"]["videos"] == 7
    assert summary["splits"]["holdout"]["windows"] >= 20

    # Frozen joint ruler: Phi must beat every fixed competitor by mean distance.
    for split in ("evaluation", "holdout"):
        targets = summary["splits"][split]["targets"]
        phi = targets["phi"]["mean_distance"]
        assert all(phi < targets[name]["mean_distance"] for name in ("one", "sqrt2", "three_halves", "two"))
        for name, interval in summary["placement_bootstrap"][split].items():
            assert interval["ci_high"] < 0, (split, name, interval)

    # Audit: Phi must not be promoted as best under the fair direct-ratio ruler.
    eval_direct = summary["post_protocol_audit"]["evaluation"]["direct_targets"]
    hold_direct = summary["post_protocol_audit"]["holdout"]["direct_targets"]
    assert eval_direct["sqrt2"]["mean_direct_distance"] < eval_direct["phi"]["mean_direct_distance"]
    assert hold_direct["three_halves"]["mean_direct_distance"] < hold_direct["phi"]["mean_direct_distance"]

    # Real adjacent movement approaches the golden equality more than shifted movement.
    for split in ("evaluation", "holdout"):
        audit = summary["post_protocol_audit"][split]
        assert audit["golden_equality_mean"] < audit["golden_equality_shift_mean"]
        interval = audit["golden_equality_adjacent_minus_shift_bootstrap"]
        assert interval["ci_high"] < 0

    # Registered future-tension claim does not pass evaluation or non-overlap robustness.
    evaluation = summary["outcomes"]["evaluation"]
    assert evaluation["phi"]["future_turn_one_sided_p"] > 0.05
    assert evaluation["phi_nonoverlap"]["future_turn_one_sided_p"] > 0.05

    with target_path.open("r", newline="", encoding="utf-8") as handle:
        target_rows = list(csv.DictReader(handle))
    with sample_path.open("r", newline="", encoding="utf-8") as handle:
        sample_rows = list(csv.DictReader(handle))
    assert len(target_rows) == 33
    assert len(sample_rows) == 10000
    assert all(math.isfinite(float(row["q_whole"])) for row in sample_rows)

    print("VALIDATION PASSED")
    print(f"eligible_windows={split_total}")
    print(f"joint_free_target={summary['free_target_calibration']:.9f}")
    print(f"direct_free_target={summary['direct_free_target_calibration']:.9f}")
    for path in (summary_path, target_path, sample_path):
        print(f"{path.name}\t{sha256(path)}")


if __name__ == "__main__":
    main()
