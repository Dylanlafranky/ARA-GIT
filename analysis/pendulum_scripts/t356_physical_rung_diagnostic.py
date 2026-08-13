"""Frozen T356 double-pendulum rung diagnostic."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
from scipy.signal import find_peaks


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROTOCOL = HERE / "T356_PHYSICAL_RUNG_DIAGNOSTIC_ADDENDUM_v1_FROZEN.md"
EXPECTED_SHA = "77C74B1862B236320E0332BCA9C2835B213D52C67B4BAD947457572DD974D53A"
EVENTS = HERE / "T356_PHYSICAL_RUNG_DIAGNOSTIC_EVENTS.csv"
SUMMARY = HERE / "T356_PHYSICAL_RUNG_DIAGNOSTIC_SUMMARY.csv"
RESULTS = HERE / "T356_PHYSICAL_RUNG_DIAGNOSTIC_RESULTS.json"
FIGURE = HERE / "T356_PHYSICAL_RUNG_DIAGNOSTIC_FIGURE.png"
REPORT = HERE / "T356_PHYSICAL_RUNG_DIAGNOSTIC_REPORT_2026-08-11.md"

SOURCES = {
    "double1": HERE / "data" / "pend_double.mat",
    "double2": ROOT / "external_data" / "MultiArm-Pendulum" / "DoublePendulum" / "DoubleDataFreeSwing_2_Dt_0_001.mat",
    "double3": ROOT / "external_data" / "MultiArm-Pendulum" / "DoublePendulum" / "DoubleDataFreeSwing_3_Dt_0_001.mat",
    "double4": ROOT / "external_data" / "MultiArm-Pendulum" / "DoublePendulum" / "DoubleDataFreeSwing_4_Dt_0_001.mat",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def wrap(a):
    return (a + np.pi) % (2*np.pi) - np.pi


def load(path):
    m = sio.loadmat(path)
    dt = float(np.asarray(m["dt"]).ravel()[0])
    t = np.asarray(m["Time"]).ravel()
    angle = {a: np.asarray(m[f"Theta{a}"]).ravel() for a in (1,2)}
    vel = {a: np.asarray(m[f"dTheta{a}"]).ravel() for a in (1,2)}
    centred = {}
    for a in (1,2):
        c = math.atan2(float(np.mean(np.sin(angle[a]))), float(np.mean(np.cos(angle[a]))))
        centred[a] = wrap(angle[a]-c)
    return t, centred, vel, 1/dt


def turns(x, fs):
    distance = max(1, int(round(.4*1.333*fs)))
    hi = find_peaks(x, prominence=.02*math.pi, distance=distance)[0]
    lo = find_peaks(-x, prominence=.02*math.pi, distance=distance)[0]
    return sorted([(int(i),1) for i in hi]+[(int(i),-1) for i in lo])


def events_for(run, path, arm):
    t,xs,vs,fs = load(path)
    x = xs[arm]; speed=np.abs(vs[arm]); tt=turns(x,fs); rows=[]
    for j in range(len(tt)-1):
        (left,lk),(right,rk)=tt[j],tt[j+1]
        if lk==rk or right-left<6: continue
        z=speed[left+1:right]
        if len(z)<5 or not np.all(np.isfinite(z)): continue
        target=left+1+int(np.argmax(z)); pred=.5*(left+right); dur=right-left
        rows.append({
            "run":run,"arm":arm,"event_local":len(rows),"direction":"increasing" if x[right]>x[left] else "decreasing",
            "left_index":left,"right_index":right,"target_index":target,
            "left_time_s":float(t[left]),"right_time_s":float(t[right]),"target_time_s":float(t[target]),
            "pred_time_s":float(np.interp(pred,np.arange(len(t)),t)),"duration_s":float(t[right]-t[left]),
            "target_phase":(target-left)/dur,"signed_phase_offset":(target-left)/dur-.5,
            "error_plain":abs(pred-target)/dur,
            "flow_fraction":float(np.interp(pred,np.arange(len(speed)),speed)/speed[target]),
        })
    return rows


def med(v):
    x=np.asarray(v,float); x=x[np.isfinite(x)]; return float(np.median(x))


def summary(rows):
    out=[]
    for run in SOURCES:
        for arm in (1,2):
            z=[r for r in rows if r["run"]==run and r["arm"]==arm]
            out.append({"run":run,"arm":arm,"n":len(z),"median_error_plain":med([r["error_plain"] for r in z]),"median_flow_fraction":med([r["flow_fraction"] for r in z]),"median_target_phase":med([r["target_phase"] for r in z]),"median_signed_phase_offset":med([r["signed_phase_offset"] for r in z])})
    return out


def write_csv(path,rows):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def plot(rows,summ,result):
    fig,ax=plt.subplots(2,2,figsize=(14,9),constrained_layout=True); fig.patch.set_facecolor("#f4f7fb")
    for a in ax.flat:
        a.set_facecolor("white"); a.grid(color="#dfe5ec",lw=.7); a.spines[["top","right"]].set_visible(False)
    colours={1:"#5c8fc5",2:"#dd8b24"}
    for arm in (1,2):
        z=[r for r in rows if r["arm"]==arm]
        ax[0,0].scatter(np.arange(len(z)),[r["target_phase"] for r in z],s=12,alpha=.5,color=colours[arm],label=f"arm {arm}")
    ax[0,0].axhline(.5,color="#202b38",lw=2,label="plain-ARA ridge")
    ax[0,0].set(xlabel="half-swing occurrence (pooled)",ylabel="recorded peak-flow phase",ylim=(0,1),title="Physical flow can split around the geometric ridge")
    ax[0,0].legend(frameon=False,ncols=3,fontsize=8)
    bins=np.linspace(0,1,41)
    for arm in (1,2):
        z=[r["target_phase"] for r in rows if r["arm"]==arm]
        ax[0,1].hist(z,bins=bins,density=True,histtype="step",lw=2,color=colours[arm],label=f"arm {arm}")
    ax[0,1].axvline(.5,color="#202b38",lw=2)
    ax[0,1].set(xlabel="recorded peak-flow phase",ylabel="density",title="Depth changes the ridge expression")
    ax[0,1].legend(frameon=False)
    x=np.arange(4); width=.36
    for arm,off in ((1,-width/2),(2,width/2)):
        z=[next(s for s in summ if s["run"]==run and s["arm"]==arm)["median_error_plain"] for run in SOURCES]
        ax[1,0].bar(x+off,z,width,color=colours[arm],label=f"arm {arm}")
    ax[1,0].axhline(.12,color="#b64b4b",ls="--",lw=1.3,label="clean-ridge gate")
    ax[1,0].set_xticks(x,list(SOURCES)); ax[1,0].set(ylabel="median normalized error",title="Frozen replication across four double-pendulum runs")
    ax[1,0].legend(frameon=False,ncols=3,fontsize=8)
    for arm,off in ((1,-width/2),(2,width/2)):
        z=[next(s for s in summ if s["run"]==run and s["arm"]==arm)["median_flow_fraction"] for run in SOURCES]
        ax[1,1].bar(x+off,z,width,color=colours[arm],label=f"arm {arm}")
    ax[1,1].set_xticks(x,list(SOURCES)); ax[1,1].set_ylim(0,1.05); ax[1,1].set(ylabel="midpoint speed / interval peak",title="How much peak flow remains at the geometric ridge")
    ax[1,1].legend(frameon=False)
    fig.suptitle(f"T356 physical-rung diagnostic | {result['verdict']} ({result['gates_passed']}/5 gates)",fontsize=16,fontweight="normal")
    fig.savefig(FIGURE,dpi=170); plt.close(fig)


def report(result,summ):
    p=result["pooled"]
    lines=["# T356 physical-rung diagnostic", "", "**Date:** 11 August 2026  ", f"**Frozen verdict:** **{result['verdict']} (`{result['gates_passed']}/5` gates)**  ", f"**Protocol SHA-256:** `{result['protocol_sha256']}`", "", "## Answer first", "", f"Across four public double-pendulum runs, the deeper arm did **{'not ' if not result['gates']['D1_depth_ordering'] else ''}repeat the cleaner central-flow pattern. Pooled median error was **{p['arm1']['median_error_plain']:.6f}** for arm 1 and **{p['arm2']['median_error_plain']:.6f}** for arm 2; midpoint flow retention was **{p['arm1']['median_flow_fraction']:.6f}** versus **{p['arm2']['median_flow_fraction']:.6f}**.", "", "## Frozen gates", ""]
    for k,v in result["gates"].items(): lines.append(f"- `{k}`: **{'PASS' if v else 'FAIL'}**")
    lines += ["", "## Run-level results", "", "| Run | Arm | n | Median error | Midpoint flow | Median target phase |", "|---|---:|---:|---:|---:|---:|"]
    for s in summ: lines.append(f"| {s['run']} | {s['arm']} | {s['n']} | {s['median_error_plain']:.6f} | {s['median_flow_fraction']:.6f} | {s['median_target_phase']:.6f} |")
    lines += ["", "## Interpretation boundary", "", "This addendum tests the post-T356 depth-split explanation and cannot alter T356's frozen `5/7` verdict. A pass supports a repeatable archive-specific pattern: the relational centre stays near phase `0.5`, while coupling redistributes which local flow crest becomes largest. It does not yet identify the complete parent mechanism or establish a universal rung law."]
    REPORT.write_text("\n".join(lines)+"\n",encoding="utf-8")


def main():
    actual=sha(PROTOCOL)
    if actual!=EXPECTED_SHA: raise RuntimeError(f"protocol hash mismatch {actual}")
    rows=[]
    for run,path in SOURCES.items():
        for arm in (1,2): rows.extend(events_for(run,path,arm))
    for i,r in enumerate(rows): r["event_id"]=i
    summ=summary(rows)
    pooled={}
    for arm in (1,2):
        z=[r for r in rows if r["arm"]==arm]
        pooled[f"arm{arm}"]={"n":len(z),"median_error_plain":med([r["error_plain"] for r in z]),"median_flow_fraction":med([r["flow_fraction"] for r in z]),"median_target_phase":med([r["target_phase"] for r in z]),"median_signed_phase_offset":med([r["signed_phase_offset"] for r in z])}
    by={(s["run"],s["arm"]):s for s in summ}
    gates={
        "D1_depth_ordering":pooled["arm2"]["median_error_plain"]<pooled["arm1"]["median_error_plain"],
        "D2_per_run_replication":sum(by[(run,2)]["median_error_plain"]<by[(run,1)]["median_error_plain"] for run in SOURCES)>=3,
        "D3_clean_lower_ridge":sum(by[(run,2)]["median_error_plain"]<.12 for run in SOURCES)>=3,
        "D4_flow_retention":pooled["arm2"]["median_flow_fraction"]>pooled["arm1"]["median_flow_fraction"],
        "D5_central_tendency":all(abs(pooled[f"arm{arm}"]["median_target_phase"]-.5)<.05 for arm in (1,2)),
    }
    result={"protocol_sha256":actual,"verdict":"SUPPORTED DEPTH-SPLIT EXPLANATION" if all(gates.values()) else "NOT SUPPORTED","gates_passed":sum(gates.values()),"gates":gates,"pooled":pooled,"source_sha256":{run:sha(path) for run,path in SOURCES.items()}}
    write_csv(EVENTS,rows); write_csv(SUMMARY,summ); RESULTS.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8"); plot(rows,summ,result); report(result,summ)
    print(json.dumps(result,indent=2))


if __name__=="__main__": main()
