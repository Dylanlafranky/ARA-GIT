#!/usr/bin/env python3
"""Independent artifact validator for T349. Does not import the run script."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
PROTOCOL_HASH = "4F6DF8E7AA0F2726EF3952ED791D3246C6588D2EE0C70F7AEE763D10F6D8075E"
CLAIM_HASH = "3137E226C627F6C6657327D95CC00B4215389D3EC1D2EDDE5B68B0279ADF8CD8"
EXPECTED_SECTOR = {
    "periodic rational": (0, 0), "irrational rotation": (1, 0),
    "deterministic chaos": (1, 0), "finite stochastic": (0, 1),
    "continuous stochastic": (1, 1),
}
RESOLUTIONS = np.array((16, 32, 64, 128, 256), dtype=int)
K = 5
MAX_LAG = 512
G_REF = 0.75


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def circular_mean(values: np.ndarray) -> float:
    v = np.mean(np.exp(2j * np.pi * values))
    return 0.0 if abs(v) < 1e-15 else float((np.angle(v) / (2*np.pi)) % 1.0)


def x_p(u: np.ndarray) -> float:
    occupied = []
    for bins in RESOLUTIONS:
        occupied.append(np.unique(np.minimum((u*bins).astype(int), bins-1)).size)
    return 2 * float(np.clip(np.polyfit(np.log(RESOLUTIONS), np.log(occupied), 1)[0], 0, 1))


def x_r(u: np.ndarray) -> float:
    split = len(u)//2
    tx, ty = u[:split-1], u[1:split]
    qx, qy = u[split:-1], u[split+1:]
    order = np.argsort(tx); sx, sy = tx[order], ty[order]
    insertion = np.searchsorted(sx, qx); offsets = np.arange(-7, 8)
    candidates = (insertion[:,None] + offsets[None,:]) % len(sx)
    d = np.abs(sx[candidates] - qx[:,None]); d = np.minimum(d, 1-d)
    positions = np.argpartition(d, K-1, axis=1)[:,:K]
    neighbours = sy[np.take_along_axis(candidates, positions, axis=1)]
    vectors = np.mean(np.exp(2j*np.pi*neighbours), axis=1)
    prediction = (np.angle(vectors)/(2*np.pi)) % 1.0
    prediction[np.abs(vectors)<1e-12] = circular_mean(ty)
    loss = lambda a,b: 1-np.cos(2*np.pi*(a-b))
    local = float(np.mean(loss(qy,prediction)))
    null = float(np.mean(loss(qy,np.full_like(qy,circular_mean(ty)))))
    return 2*min(1.0,local/max(null,1e-12))


def mean_rho(u: np.ndarray) -> float:
    n=len(u); v=np.exp(2j*np.pi*u); nfft=1 << (2*n-1).bit_length()
    f=np.fft.fft(v,nfft); raw=np.fft.ifft(f*np.conj(f))[:MAX_LAG+1]
    raw=raw/np.arange(n,n-MAX_LAG-1,-1)
    return float(np.median(np.abs(raw[1:])))


def state(radius: np.ndarray, u: np.ndarray) -> tuple[float,float]:
    gain=float(np.log(radius[-1]/radius[0])); xl=1+math.tanh(gain/G_REF)
    delta=np.angle(np.exp(2j*np.pi*(u[1:]-u[:-1]))); den=float(np.sum(np.abs(np.sin(delta))))
    xc=1.0 if den<1e-15 else 1+float(np.sum(np.sin(delta))/den)
    return xl,xc


def check(name: str, passed: bool, detail: str, rows: list[dict]) -> None:
    rows.append({"check": name, "passed": bool(passed), "detail": detail})


def main() -> None:
    metrics=pd.read_csv(HERE/"T349_STATE_HISTORY_DI_ARA_METRICS.csv")
    summary=pd.read_csv(HERE/"T349_STATE_HISTORY_DI_ARA_FACTORIAL_SUMMARY.csv")
    interventions=pd.read_csv(HERE/"T349_STATE_HISTORY_DI_ARA_INTERVENTIONS.csv")
    constants=pd.read_csv(HERE/"T349_STATE_HISTORY_DI_ARA_CONSTANT_SPECIFICITY.csv")
    gates=pd.read_csv(HERE/"T349_STATE_HISTORY_DI_ARA_FROZEN_GATES.csv")
    examples=pd.read_csv(HERE/"T349_STATE_HISTORY_DI_ARA_EXAMPLES.csv")
    result=json.loads((HERE/"T349_STATE_HISTORY_DI_ARA_RESULTS.json").read_text(encoding="utf-8"))
    rows=[]

    check("protocol hash",digest(HERE/"T349_STATE_HISTORY_DI_ARA_INTERFACE_PROTOCOL_v1_FROZEN.md")==PROTOCOL_HASH,digest(HERE/"T349_STATE_HISTORY_DI_ARA_INTERFACE_PROTOCOL_v1_FROZEN.md"),rows)
    check("claim hash",digest(HERE/"T349_STATE_HISTORY_DI_ARA_INTERFACE_CLAIM_PACKET_v1.md")==CLAIM_HASH,digest(HERE/"T349_STATE_HISTORY_DI_ARA_INTERFACE_CLAIM_PACKET_v1.md"),rows)
    check("metric row count",len(metrics)==15120,f"rows={len(metrics)}",rows)
    check("natural key unique",not metrics.duplicated(["trajectory_id","control"]).any(),f"duplicates={metrics.duplicated(['trajectory_id','control']).sum()}",rows)
    check("coordinate ranges",all(metrics[c].between(0,2).all() for c in ["x_l","x_c","x_p","x_r"]),"xL/xC/xP/xR all in [0,2]",rows)
    check("core counts",result["n_core_trajectories"]==3024 and result["n_holdout_core_trajectories"]==1656,str((result["n_core_trajectories"],result["n_holdout_core_trajectories"])),rows)

    hold=metrics[(metrics.split=="holdout")&(metrics.control=="chronological")].copy()
    hold["radial_correct"]=((hold.radial_mode=="contraction")&(hold.x_l<0.75))|((hold.radial_mode=="neutral")&hold.x_l.between(0.75,1.25))|((hold.radial_mode=="expansion")&(hold.x_l>1.25))
    hold["path_correct"]=[((r.x_p>=1)==EXPECTED_SECTOR[r.family][0]) and ((r.x_r>=1)==EXPECTED_SECTOR[r.family][1]) for r in hold.itertuples()]
    radial_acc=float(hold.radial_correct.mean()); path_acc=float(hold.path_correct.mean())
    check("headline radial accuracy",abs(radial_acc-result["radial_accuracy_holdout"])<1e-12,f"{radial_acc:.12f}",rows)
    check("headline history accuracy",abs(path_acc-result["history_sector_accuracy_holdout"])<1e-12,f"{path_acc:.12f}",rows)

    keys=["trajectory_id","split","family","radial_mode","radial_span"]
    base=metrics[(metrics.split=="holdout")&(metrics.control=="chronological")].set_index(keys)
    for control in ["radial_inverted","phase_reflected","shuffled","endpoint_shuffled"]:
        other=metrics[(metrics.split=="holdout")&(metrics.control==control)].set_index(keys)
        joined=base.join(other,lsuffix="_base",rsuffix="_control")
        saved=interventions[interventions.intervention==control].set_index("metric")
        for coordinate in ["x_l","x_c","x_p","x_r","mean_rho"]:
            value=float(np.median(np.abs(joined[f"{coordinate}_control"]-joined[f"{coordinate}_base"])))
            expected=float(saved.loc[f"abs_delta_{coordinate}","median"])
            check(f"{control} {coordinate} intervention",abs(value-expected)<1e-12,f"recomputed={value:.12g}",rows)

    fixed={"plastic":1.324717957244746,"sqrt2":math.sqrt(2),"phi":(1+math.sqrt(5))/2,"octave":2.0,"e":math.e}
    observed=np.abs(hold[hold.radial_mode!="neutral"].radial_log_gain.to_numpy())
    for name,alpha in fixed.items():
        value=float(np.mean(np.abs(observed-math.log(alpha))))
        expected=float(constants.set_index("candidate").loc[name,"mean_abs_log_error"])
        check(f"constant {name}",abs(value-expected)<1e-12,f"mean_log_error={value:.12g}",rows)

    example_failures=[]
    metric_index=metrics[metrics.control=="chronological"].set_index("trajectory_id")
    for trajectory_id,group in examples.groupby("trajectory_id"):
        group=group.sort_values("t"); u=group.u.to_numpy(); radius=group.radius.to_numpy()
        xl,xc=state(radius,u); xp=x_p(u); xr=x_r(u); rho=mean_rho(u)
        saved=metric_index.loc[trajectory_id]
        errors={"x_l":abs(xl-saved.x_l),"x_c":abs(xc-saved.x_c),"x_p":abs(xp-saved.x_p),"x_r":abs(xr-saved.x_r),"mean_rho":abs(rho-saved.mean_rho)}
        if max(errors.values())>1e-10: example_failures.append((trajectory_id,errors))
    check("raw-example formula reconstruction",not example_failures,f"groups={examples.trajectory_id.nunique()} failures={len(example_failures)}",rows)

    image=Image.open(HERE/"T349_STATE_HISTORY_DI_ARA_FIGURE.png")
    check("figure dimensions",image.size==(2400,1500),f"size={image.size}",rows)
    check("all primary gates passed",bool(gates.iloc[:7].passed.all()) and not bool(gates.iloc[7].passed),f"primary={int(gates.iloc[:7].passed.sum())}/7 constant={bool(gates.iloc[7].passed)}",rows)

    passed=all(row["passed"] for row in rows)
    validation={"test":"T349 independent artifact validation","passed":passed,"checks_passed":sum(r["passed"] for r in rows),"checks_total":len(rows),"checks":rows}
    (HERE/"T349_STATE_HISTORY_DI_ARA_VALIDATION.json").write_text(json.dumps(validation,indent=2),encoding="utf-8")
    lines=["# T349 independent validation","",f"**Verdict:** {'PASS' if passed else 'FAIL'} — {validation['checks_passed']}/{validation['checks_total']} checks","","The validator does not import the run script. It independently recomputes headline accuracies, intervention summaries, every fixed-constant score, and all five coordinates from 15 complete raw example trajectories.","","| Check | Result | Detail |","|---|---|---|"]
    for row in rows: lines.append(f"| {row['check']} | {'PASS' if row['passed'] else 'FAIL'} | {row['detail']} |")
    (HERE/"T349_STATE_HISTORY_DI_ARA_VALIDATION.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(validation,indent=2))
    raise SystemExit(0 if passed else 1)


if __name__=="__main__":
    main()

