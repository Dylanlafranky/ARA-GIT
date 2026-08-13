"""Independent table and gate validation for the frozen T356 rung diagnostic."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


HERE=Path(__file__).resolve().parent
PROTOCOL=HERE/"T356_PHYSICAL_RUNG_DIAGNOSTIC_ADDENDUM_v1_FROZEN.md"
EVENTS=HERE/"T356_PHYSICAL_RUNG_DIAGNOSTIC_EVENTS.csv"
SUMMARY=HERE/"T356_PHYSICAL_RUNG_DIAGNOSTIC_SUMMARY.csv"
RESULTS=HERE/"T356_PHYSICAL_RUNG_DIAGNOSTIC_RESULTS.json"
OUT=HERE/"T356_PHYSICAL_RUNG_DIAGNOSTIC_VALIDATION.json"
EXPECTED="77C74B1862B236320E0332BCA9C2835B213D52C67B4BAD947457572DD974D53A"


def med(rows,key): return float(np.median([float(r[key]) for r in rows]))
def close(a,b,tol=1e-12): return bool(abs(float(a)-float(b))<=tol)


def main():
    rows=list(csv.DictReader(EVENTS.open(encoding="utf-8")))
    summ=list(csv.DictReader(SUMMARY.open(encoding="utf-8")))
    result=json.loads(RESULTS.read_text(encoding="utf-8"))
    checks={}
    digest=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest().upper()
    checks["protocol_hash"]=digest==EXPECTED==result["protocol_sha256"]
    checks["event_ids_unique"]=len({r["event_id"] for r in rows})==len(rows)
    checks["all_four_runs"]={r["run"] for r in rows}=={"double1","double2","double3","double4"}
    checks["both_arms"]={r["arm"] for r in rows}=={"1","2"}
    checks["both_directions"]={r["direction"] for r in rows}=={"increasing","decreasing"}
    checks["phase_in_bounds"]=all(0<float(r["target_phase"])<1 for r in rows)
    checks["error_identity"]=all(close(abs(float(r["target_phase"])-.5),r["error_plain"]) for r in rows)

    pooled={}
    for arm in (1,2):
        z=[r for r in rows if int(r["arm"])==arm]
        p=result["pooled"][f"arm{arm}"]
        pooled[arm]=z
        checks[f"arm{arm}_n"]=len(z)==p["n"]
        checks[f"arm{arm}_error"]=close(med(z,"error_plain"),p["median_error_plain"])
        checks[f"arm{arm}_flow"]=close(med(z,"flow_fraction"),p["median_flow_fraction"])
        checks[f"arm{arm}_phase"]=close(med(z,"target_phase"),p["median_target_phase"])
        checks[f"arm{arm}_signed"]=close(med(z,"signed_phase_offset"),p["median_signed_phase_offset"])

    smap={(r["run"],int(r["arm"])):r for r in summ}
    for run in ("double1","double2","double3","double4"):
        for arm in (1,2):
            z=[r for r in rows if r["run"]==run and int(r["arm"])==arm]
            s=smap[(run,arm)]
            checks[f"{run}_a{arm}_n"]=len(z)==int(s["n"])
            checks[f"{run}_a{arm}_error"]=close(med(z,"error_plain"),s["median_error_plain"])
            checks[f"{run}_a{arm}_flow"]=close(med(z,"flow_fraction"),s["median_flow_fraction"])
            checks[f"{run}_a{arm}_phase"]=close(med(z,"target_phase"),s["median_target_phase"])

    gates={
        "D1_depth_ordering":med(pooled[2],"error_plain")<med(pooled[1],"error_plain"),
        "D2_per_run_replication":sum(float(smap[(run,2)]["median_error_plain"])<float(smap[(run,1)]["median_error_plain"]) for run in ("double1","double2","double3","double4"))>=3,
        "D3_clean_lower_ridge":sum(float(smap[(run,2)]["median_error_plain"])<.12 for run in ("double1","double2","double3","double4"))>=3,
        "D4_flow_retention":med(pooled[2],"flow_fraction")>med(pooled[1],"flow_fraction"),
        "D5_central_tendency":all(abs(med(pooled[a],"target_phase")-.5)<.05 for a in (1,2)),
    }
    for k,v in gates.items(): checks[f"gate_{k}"]=v==result["gates"][k]
    verdict="SUPPORTED DEPTH-SPLIT EXPLANATION" if all(gates.values()) else "NOT SUPPORTED"
    checks["verdict"]=verdict==result["verdict"]
    validation={"status":"PASS" if all(checks.values()) else "FAIL","checks_passed":sum(checks.values()),"checks_total":len(checks),"checks":checks}
    OUT.write_text(json.dumps(validation,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(validation,indent=2))
    if validation["status"]!="PASS": raise SystemExit(1)


if __name__=="__main__": main()
