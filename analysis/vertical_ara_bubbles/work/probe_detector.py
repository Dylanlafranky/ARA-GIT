from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

from bubble_lineage import detect_candidates, load_run


def quantiles(values):
    values = sorted(values)
    if not values:
        return None
    def q(p):
        i = (len(values) - 1) * p
        lo = int(i)
        hi = min(lo + 1, len(values) - 1)
        w = i - lo
        return values[lo] * (1 - w) + values[hi] * w
    return {"min": values[0], "q25": q(0.25), "median": q(0.5), "q75": q(0.75), "max": values[-1]}


def main(root: str):
    configs = {
        "strict": {},
        "moderate": {
            "min_child_age": 2,
            "min_parent_life": 5,
            "closure_min": 0.65,
            "closure_max": 1.35,
            "separation_max": 2.25,
            "center_max": 1.15,
            "isolation_radius": 1.15,
        },
        "broad": {
            "min_child_age": 2,
            "min_parent_life": 4,
            "closure_min": 0.60,
            "closure_max": 1.40,
            "separation_max": 2.50,
            "center_max": 1.25,
            "isolation_radius": 1.00,
            "ambiguity_min": 1.05,
        },
    }
    runs = [load_run(path) for path in sorted(Path(root).glob("V0[1-7]_*.csv"))]
    results = []
    for config_name, config in configs.items():
        events = [event for run in runs for event in detect_candidates(run, **config)]
        results.append({
            "config": config_name,
            "events": len(events),
            "by_file": {run.path.name: len(detect_candidates(run, **config)) for run in runs},
            "closure": quantiles([e.closure for e in events]),
            "separation": quantiles([e.separation_norm for e in events]),
            "center": quantiles([e.center_norm for e in events]),
            "score": quantiles([e.score for e in events]),
        })
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
