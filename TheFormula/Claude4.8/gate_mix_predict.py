#!/usr/bin/env python3
"""STRICT-CAUSAL: mix ocean(WWV)+atmosphere(SOI) at the spring gate to predict NINO3.4.
Framework: the two endpoints blended (mixing term) + seasonal gate beat single systems.
Rules: train-only fit + train-only standardization; no overlap; corr-led; walk-forward.
Predictors use ONLY data at time t to predict NINO(t+h).
"""
import re, numpy as np
from pathlib import Path
import enso_endpoints_test as M
ROOT=Path("/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder")

def load_wwv_anom():
    v=[]
    for ln in (ROOT/"GIT/ARA-GIT/TheFormula/Claude4.8/wwv_west.dat").read_text().splitlines():
        mt=re.match(r"\s*(\d{6})\s+\S+\s+(\S+)",ln)
        if mt:
            try: v.append(float(mt.group(2)))
            except: pass
    return np.array(v)

# Align all three to the WWV window: 1980-01 .. (WWV end). Monthly, all start Jan.
wwv=load_wwv_anom()                       # 1980-01 ..
nino=M.clean(M.load_nino())               # 1870-01
soi =M.clean(M.load_soi())                # 1948-01
nino=nino[(1980-1870)*12:]
soi =soi[(1948-1980)*12:] if 1980>=1948 else soi
soi =M.load_soi(); soi=M.clean(soi)[(1980-1948)*12:]
n=min(len(wwv),len(nino),len(soi)); wwv,nino,soi=wwv[:n],nino[:n],soi[:n]
month=np.array([i%12 for i in range(n)])  # 0=Jan
print(f"aligned N={n} months (1980-01 .. ), ~{n/12:.0f}yr")

def zfit(a,mu,sd): return (a-mu)/sd
def corr(a,b): 
    a=a-a.mean(); b=b-b.mean(); d=np.sqrt((a*a).sum()*(b*b).sum())
    return float((a*b).sum()/d) if d>0 else 0.0

def build_design(t_idx,h,which):
    # features at time t (causal), target NINO(t+h)
    w=wwv[t_idx]; s=soi[t_idx]; mo=month[t_idx]
    # spring gate: bump centered on Mar-Apr-May (boreal spring), smooth
    gate=np.exp(-((((mo-3)+6)%12-6)**2)/(2*1.5**2))  # peak at month index 3 (Apr)
    cols=[np.ones_like(w)]
    if "W" in which: cols.append(w)
    if "S" in which: cols.append(s)
    if "MIX" in which: cols.append(w*s)                 # the blend / mixing term
    if "GMIX" in which: cols.append(gate*(w*s))         # spring-gated mixing
    if "G" in which: cols.append(gate*w); cols.append(gate*s)
    return np.column_stack(cols)

def run(h, which, train_frac=0.6):
    # valid t: need t+h < n
    tt=np.arange(0, n-h)
    cut=int(len(tt)*train_frac)
    tr,te=tt[:cut],tt[cut:]
    y=nino[tt+h]
    # standardize predictors using TRAIN rows only
    Xtr_raw=build_design(tr,h,which); Xte_raw=build_design(te,h,which)
    mu=Xtr_raw.mean(0); sd=Xtr_raw.std(0); sd[sd==0]=1; mu[0]=0; sd[0]=1
    Xtr=(Xtr_raw-mu)/sd; Xte=(Xte_raw-mu)/sd
    ytr=y[:cut]; yte=y[cut:]
    ymu=ytr.mean()
    beta,*_=np.linalg.lstsq(Xtr, ytr-ymu, rcond=None)
    pred=Xte@beta + ymu
    return corr(pred,yte)

def persistence(h, train_frac=0.6):
    tt=np.arange(0,n-h); cut=int(len(tt)*train_frac); te=tt[cut:]
    return corr(nino[te], nino[te+h])

print("\nSTRICT-CAUSAL walk-forward (fit+standardize on train 60%, score corr on test 40%)")
print("corr-led. NINO(t+h) from data at t only.\n")
for h in (6,12):
    p=persistence(h)
    mW=run(h,["W"]); mS=run(h,["S"]); mWS=run(h,["W","S"])
    mMIX=run(h,["W","S","MIX"]); mGMIX=run(h,["W","S","MIX","GMIX"])
    print(f"h={h:2d}mo  persist={p:+.3f} | WWV={mW:+.3f}  SOI={mS:+.3f}  "
          f"WWV+SOI={mWS:+.3f} | +MIX={mMIX:+.3f}  +GATED-MIX={mGMIX:+.3f}")
