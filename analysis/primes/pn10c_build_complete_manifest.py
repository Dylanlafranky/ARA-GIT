"""Build the complete, hash-addressed PN10C artifact manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE=Path(__file__).resolve().parent
OUT=HERE/"PN10C_COMPLETE_MANIFEST.json"
FILES=[
    "PN10C_MOD6_THREE_LANE_COUPLING_PROTOCOL.md",
    "pn10c_mod6_three_lane_coupling.py",
    "PN10C_MOD6_THREE_LANE_RESULTS.json",
    "PN10C_MOD6_OFFSET_PROFILE.csv",
    "PN10C_MOD6_LANE_SUMMARY.csv",
    "PN10C_MOD30_BLACK_CHILD_MATRIX.csv",
    "PN10C_MOD6_WORKED_EXAMPLES.csv",
    "PN10C_MOD6_THREE_LANE_FIGURE.png",
    "pn10c_validate_mod6_three_lane.py",
    "PN10C_MOD6_THREE_LANE_VALIDATION.json",
    "PN10C_MOD6_THREE_LANE_COUPLING_REPORT.md",
    "pn10c_build_notebook.py",
    "PN10C_MOD6_THREE_LANE_DIAGNOSTIC.ipynb",
    "PN10C_NOTEBOOK_EXECUTION_VALIDATION.json",
    "pn10c_report_offset_trace.sql",
    "pn10c_report_lane_summary.sql",
    "pn10c_report_mod30_matrix.sql",
    "pn10c_report_contrasts.sql",
    "pn10c_build_report_artifact.py",
    "PN10C_REPORT_ARTIFACT.json",
    "PN10C_REPORT_ARTIFACT_VALIDATION.json",
    "PN10C_REPORT_ARTIFACT_RENDER_RECEIPT.json",
]


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest().upper()


def main() -> None:
    missing=[name for name in FILES if not (HERE/name).exists()]
    if missing: raise FileNotFoundError(missing)
    results=json.loads((HERE/"PN10C_MOD6_THREE_LANE_RESULTS.json").read_text(encoding="utf-8"))
    validation=json.loads((HERE/"PN10C_MOD6_THREE_LANE_VALIDATION.json").read_text(encoding="utf-8"))
    notebook=json.loads((HERE/"PN10C_NOTEBOOK_EXECUTION_VALIDATION.json").read_text(encoding="utf-8"))
    artifact_validation=json.loads((HERE/"PN10C_REPORT_ARTIFACT_VALIDATION.json").read_text(encoding="utf-8"))
    manifest={
        "test_id":"PN10C/MOD6-THREE-LANE/POST-HOC-DIAGNOSTIC/v1",
        "status":results["status"],
        "registered_pn10b_verdict_unchanged":results["registered_pn10b_verdict_unchanged"],
        "protocol_timing_note":"The protocol file was written before the diagnostic script was first executed in the live Codex session. Hashes in this completion manifest were captured after execution and are an integrity record, not a cryptographic pre-registration claim.",
        "validation":{"arithmetic":validation["status"],"checks":f"{validation['checks_passed']}/{validation['checks_total']}","notebook":notebook["status"],"report_artifact_valid":artifact_validation["ok"]},
        "headline_contrasts":results["headline_contrasts"],
        "files":[{"path":name,"bytes":(HERE/name).stat().st_size,"sha256":sha256(HERE/name)} for name in FILES],
    }
    OUT.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(OUT)


if __name__=="__main__": main()
