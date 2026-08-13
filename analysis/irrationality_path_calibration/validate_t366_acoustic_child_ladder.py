"""Independent QA for T366 acoustic child-ladder outputs."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
STEM = "T366_ACOUSTIC_CHILD_LADDER"
SCRIPT = HERE / "t366_acoustic_child_ladder.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_module():
    spec = importlib.util.spec_from_file_location("t366", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    t366 = load_module()
    result_path = HERE / f"{STEM}_RESULTS.json"
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    summary = pd.read_csv(HERE / f"{STEM}_SUMMARY.csv")
    gates = pd.read_csv(HERE / f"{STEM}_FROZEN_GATES.csv")
    source_qa = pd.read_csv(HERE / f"{STEM}_SOURCE_QA.csv")
    bouts = pd.read_csv(HERE / f"{STEM}_BOUTS.csv")
    order = pd.read_csv(HERE / f"{STEM}_EVENT_ORDER.csv")
    addresses = pd.read_csv(HERE / f"{STEM}_IRRATIONALITY_ADDRESS.csv")
    controls = pd.read_csv(HERE / f"{STEM}_CONTROLS.csv")
    timeseries = pd.read_csv(HERE / f"{STEM}_TIMESERIES.csv")

    checks = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    add("protocol digest", payload["protocol_sha256"] == digest(t366.PROTOCOL), digest(t366.PROTOCOL))
    hash_ok = True
    for row in source_qa.itertuples(index=False):
        base = t366.SOURCE_DIR if row.kind == "stress" else t366.CATALOG_DIR
        hash_ok &= digest(base / row.file) == row.sha256
    add("source hashes", hash_ok, f"Verified {len(source_qa)} published source files.")

    recomputed = {}
    for number in (20, 23):
        record = t366.load_record(number)
        analysis = t366.analyze_record(record)
        recomputed[number] = analysis
        row = summary[summary.record == f"Wgn{number}"].iloc[0]
        add(f"Wgn{number} stress monotonic", bool(np.all(np.diff(record["time"]) > 0)), f"dt={record['dt']:.6f}s")
        add(f"Wgn{number} calibration boundary", bool(record["split"] < record["failure_index"]), f"split={record['split']}, failure={record['failure_index']}")
        add(f"Wgn{number} synchronized event count", int(analysis["bins"]["count"].sum()) == int(row.ae_events_synchronized), str(int(analysis["bins"]["count"].sum())))
        associated = t366.first_associated(analysis["acoustic_bouts"])
        expected = bool(row.acoustic_associated)
        add(f"Wgn{number} associated acoustic bout", (associated is not None) == expected, f"expected={expected}")
        if associated is not None:
            add(f"Wgn{number} lead", np.isclose(float(associated.lead_s), float(row.acoustic_lead_s), atol=1e-10), f"{float(associated.lead_s):.6f}s")
            add(f"Wgn{number} causal alarm", int(associated.start_index) < record["failure_index"], f"alarm={int(associated.start_index)}, failure={record['failure_index']}")

    holdout = recomputed[23]
    associated = t366.first_associated(holdout["acoustic_bouts"])
    order_recomputed = t366.event_order_metrics(holdout["record"], holdout["acoustic"], associated)
    saved_order = order.iloc[0]
    order_ok = (
        int(saved_order.grandchild_half_index) == order_recomputed["grandchild_half_index"]
        and int(saved_order.child_half_index) == order_recomputed["child_half_index"]
        and int(saved_order.current_full_or_failure_index) == order_recomputed["current_full_or_failure_index"]
        and bool(saved_order.ordered) == order_recomputed["ordered"]
    )
    add("holdout child order", order_ok and order_recomputed["ordered"], str(order_recomputed))

    holdout_bouts = bouts[(bouts.record == "Wgn23") & (bouts.channel == "acoustic")]
    add("false bouts retained", int(holdout_bouts.earlier_false.sum()) == 31, f"{int(holdout_bouts.earlier_false.sum())} earlier bouts")
    add("pseudo specificity failure retained", not bool(gates.loc[gates.gate == 6, "pass"].iloc[0]), "Real and median pseudo horizon errors both equal zero.")
    add("control rows", len(controls) == 6 and set(controls.control) == {"reversed_holdout", "joint_bin_permutation", "polarity_permutation"}, f"{len(controls)} rows")
    add("holdout addresses", len(addresses[addresses.record == "Wgn23"]) == 5 and addresses[addresses.record == "Wgn23"][["x_P", "x_R"]].notna().all().all(), "Five finite rung addresses.")
    add("timeseries grain", len(timeseries[timeseries.record == "Wgn23"]) == 25399 and len(timeseries[timeseries.record == "Wgn20"]) == 25140, f"{len(timeseries)} rows")
    add("frozen verdict consistency", payload["status"] == "NOT SUPPORTED UNDER THE FROZEN T366 GATES" and not gates["pass"].all(), payload["status"])
    add("figure present", (HERE / f"{STEM}_FIGURE.png").stat().st_size > 100_000, f"{(HERE / f'{STEM}_FIGURE.png').stat().st_size} bytes")

    frame = pd.DataFrame(checks)
    frame.to_csv(HERE / f"{STEM}_VALIDATION.csv", index=False)
    status = "PASS" if frame["pass"].all() else "FAIL"
    validation = {
        "validation": f"{STEM} independent QA", "status": status,
        "checks_passed": int(frame["pass"].sum()), "checks_total": len(frame),
        "checks": json.loads(frame.to_json(orient="records")),
    }
    (HERE / f"{STEM}_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    markdown = "\n".join(f"- [{'x' if row['pass'] else ' '}] **{row['check']}** - {row['detail']}" for row in checks)
    (HERE / f"{STEM}_VALIDATION.md").write_text(
        f"# T366 independent validation\n\n**Status:** **{status}** ({int(frame['pass'].sum())}/{len(frame)})\n\n{markdown}\n",
        encoding="utf-8",
    )
    print(status, f"{int(frame['pass'].sum())}/{len(frame)}")
    print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
