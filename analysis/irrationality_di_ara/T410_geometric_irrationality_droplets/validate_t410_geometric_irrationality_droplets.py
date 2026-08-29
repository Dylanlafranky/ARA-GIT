"""Independent validation of T410 outputs; does not import the primary runner."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
EXPECTED_HASH = "E9C820A2684680A80C4615FB97EAED626C116E7327F73A7DD7FEC07B054133D0"


def main() -> None:
    checks: dict[str, object] = {}
    protocol_hash = hashlib.sha256((HERE / "T410_FROZEN_PROTOCOL.md").read_bytes()).hexdigest().upper()
    checks["protocol_hash"] = protocol_hash
    checks["protocol_hash_ok"] = protocol_hash == EXPECTED_HASH

    data = pd.read_csv(OUT / "T410_HOLDOUT_GEOMETRY.csv")
    recorded = json.loads((OUT / "T410_RESULTS.json").read_text(encoding="utf-8"))
    rows = []
    candidate_hits = []
    for event_id, group in data.groupby("event_id", sort=True):
        target = group.iloc[int(np.argmin(np.abs(group.u_event.to_numpy() - 1.0)))]
        hit = bool(target.x_radial_ara < 1.0 and target.mixing_angle_deg <= 20.0)
        rows.append((event_id, float(target.mixing_angle_deg), hit))
        window = group[(group.u_event >= 0.20) & (group.u_event <= 1.35)]
        candidate_hits.append(
            (
                (window.x_radial_ara.to_numpy() < 1.0)
                & (window.mixing_angle_deg.to_numpy() <= 20.0)
            ).astype(int)
        )

    observed_hits = int(sum(row[2] for row in rows))
    median_gamma = float(np.median([row[1] for row in rows]))
    rng = np.random.default_rng(4102026)
    null = np.zeros(10_000, dtype=int)
    for i in range(len(null)):
        null[i] = sum(int(h[rng.integers(0, len(h))]) for h in candidate_hits)
    p_value = float((1 + np.count_nonzero(null >= observed_hits)) / 10_001)

    checks.update(
        {
            "event_ids_ok": sorted(data.event_id.unique().tolist()) == ["E3", "E4", "E6", "E8"],
            "observed_hits": observed_hits,
            "observed_hits_ok": observed_hits == recorded["observed_hits_20deg"],
            "median_gamma_deg": median_gamma,
            "median_gamma_ok": abs(median_gamma - recorded["median_target_gamma_deg"]) < 1e-12,
            "shift_p": p_value,
            "shift_p_ok": abs(p_value - recorded["circular_shift_p"]) < 1e-12,
            "target_vector_qa_ok": bool(
                data.groupby("event_id").apply(
                    lambda g: g.iloc[int(np.argmin(np.abs(g.u_event.to_numpy() - 1.0)))].valid_vectors >= 40,
                    include_groups=False,
                ).all()
            ),
            "ara_ranges_ok": bool(
                data.x_radial_ara.between(0, 2).all()
                and data.y_angular_ara.between(0, 2).all()
                and data.mixing_angle_deg.between(0, 90).all()
            ),
            "primary_supported_recomputed": bool(
                observed_hits >= 3 and median_gamma <= 20.0 and p_value < 0.05
            ),
        }
    )
    checks["all_checks_pass"] = bool(
        all(
            checks[key]
            for key in (
                "protocol_hash_ok", "event_ids_ok", "observed_hits_ok",
                "median_gamma_ok", "shift_p_ok", "target_vector_qa_ok",
                "ara_ranges_ok",
            )
        )
        and checks["primary_supported_recomputed"] == recorded["primary_supported"]
    )
    (OUT / "T410_VALIDATION.json").write_text(
        json.dumps(checks, indent=2), encoding="utf-8"
    )
    print(json.dumps(checks, indent=2))
    if not checks["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
