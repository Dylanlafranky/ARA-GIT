"""Fairest shot: do sub-beat morphology features DIRECTLY (not aggregated) help predict
RR[t+h] beyond (a) persistence and (b) an RR autoregressive model? Strict causal, train 60%."""
import json, numpy as np
from heart_subsystem_dip_test import load_beats, fill

def ridge_fit(Xtr,ytr,Xte,pen=1.0):
    mu=np.nanmean(Xtr,0); sd=np.nanstd(Xtr,0); sd[sd<1e-9]=1
    A=np.nan_to_num((Xtr-mu)/sd); B=np.nan_to_num((Xte-mu)/sd)
    A=np.column_stack([np.ones(len(A)),A]); B=np.column_stack([np.ones(len(B)),B])
    R=np.eye(A.shape[1])*pen; R[0,0]=0
    beta=np.linalg.solve(A.T@A+R, A.T@ytr); return B@beta

def corr(a,b):
    a=np.asarray(a); b=np.asarray(b); v=np.isfinite(a)&np.isfinite(b)
    return float(np.corrcoef(a[v],b[v])[0,1])

d=load_beats()
for k in d: d[k]=fill(d[k])
rr=d["rr"]; n=len(rr); cut=int(n*0.6)
lags=[0,1,2,3,4,5,8,13]
morph=np.column_stack([d["ecg_qt"],d["ecg_cen"],d["ecg_amp"],d["bp_sys"],d["bp_pp"]])
start=14
print(f"beats {n}, train {cut}\n")
print(f"{'h':>3} | {'persist':>8} {'AR(rr lags)':>12} {'AR+morph':>10} {'morph-only':>11}  verdict")
for h in (1,3,5,8,13):
    idx=np.arange(start, n-h)
    tr=idx[idx<cut-h]; te=idx[idx>=cut]
    y=lambda i: rr[i+h]
    ytr=rr[tr+h]; yte=rr[te+h]; cur=rr[te]
    Lar=np.column_stack([rr[(np.add.outer(tr,[-l for l in lags]))] for _ in [0]][0]) if False else None
    def lagmat(ix): return np.column_stack([rr[ix-l] for l in lags])
    AR_tr,AR_te=lagmat(tr),lagmat(te)
    M_tr,M_te=morph[tr],morph[te]
    pers=corr(yte,cur)
    car=corr(yte, ridge_fit(AR_tr,ytr,AR_te))
    cam=corr(yte, ridge_fit(np.column_stack([AR_tr,M_tr]),ytr,np.column_stack([AR_te,M_te])))
    cm =corr(yte, ridge_fit(M_tr,ytr,M_te))
    best=max(car,cam,cm)
    verdict = "morph HELPS" if cam>car+0.005 else ("nothing beats persist" if best<pers else "AR~best")
    print(f"{h:>3} | {pers:+.3f}   {car:+.3f}      {cam:+.3f}    {cm:+.3f}    {verdict}")
