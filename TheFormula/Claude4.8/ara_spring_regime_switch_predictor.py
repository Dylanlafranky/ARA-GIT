"""
ARA SPRING REGIME-SWITCH predictor
==================================
Dylan's idea, built honestly: the spring ocean<->atmosphere handoff is the system's
CLOCK / contact point. So instead of adding the mix as one more always-on feature
(which the seasonal propagator just absorbs -- see ara_seasonal_heartbeat_predictor.py),
make it a true REGIME SWITCH:

  * SPRING step (the month being stepped through is Mar/Apr/May): the propagator that
    carries the state forward is the one fit ONLY on spring->next transitions, and it
    CARRIES the ocean*atmosphere mixing term (zWWV*zSOI). The mix drives here.
  * REST step (any other month): the propagator is fit on the non-spring transitions,
    plain state, no mix. The surface coasts on its own memory.

Multi-step forecasts walk through the calendar and switch map at each step by the
month they are stepping out of. Two maps, picked by the clock.

Compared head to head with:
  ocean      = baseline single seasonal map (T, zW, zE)            [capstone]
  atmos      = single seasonal map + zSOI                          (two systems, no switch)
  heartbeat  = single map + always-on spring-gated mix feature     (absorbed version)
  SWITCH     = this file: separate spring vs rest maps, mix only in the spring map

Strictly causal: regime label is the calendar (known a priori, no leakage); SOI/WWV
standardized train-only; both maps refit past-only at every origin. Correlation leads;
MSE-skill vs climatology reported in brackets. Per-lead shrinkage calibration as before.

Usage: python3 ara_spring_regime_switch_predictor.py nino34_long_anom.csv soi.data
"""
import os, sys, urllib.request, re
import numpy as np

WALK_START=2005.0; MIN_TRAIN=270; CAL_SPLIT_YEAR=2016.0; HMAX=30
SPRING={3,4,5}  # Mar Apr May

def load_wwv(p):
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)==3 and s[0].isdigit() and len(s[0])==6: d[s[0]]=float(s[2])/1e14
    return d
def load_nino(p,miss=-99.99):
    d={}
    for ln in open(p):
        s=[x.strip() for x in ln.split(",")]
        if len(s)==2 and s[0][:4].isdigit():
            v=float(s[1])
            if v>miss+0.001: d[s[0][:7].replace("-","")]=v
    return d
def load_soi(p,miss=-99.99):
    d={}
    for ln in open(p):
        m=re.match(r"\s*(\d{4})\s+(.*)",ln)
        if not m: continue
        yr=int(m.group(1))
        if yr<1900 or yr>2100: continue
        nums=ln.split()[1:]
        for mo,val in enumerate(nums[:12],1):
            try: v=float(val)
            except: continue
            if v>miss+0.001: d[f"{yr}{mo:02d}"]=v
    return d

def base_feats(X,m):
    """Single shared seasonal feature block (first-harmonic annual modulation)."""
    th=2*np.pi*(m-1)/12; c,s=np.cos(th),np.sin(th)
    return np.column_stack([X, X*c[:,None], X*s[:,None], c, s, np.ones(len(X))])

def spring_feats(X,m):
    """Spring map carries the ocean*atmosphere mix term (zW * zSOI)."""
    F=base_feats(X,m)
    mix=(X[:,1]*X[:,3])[:,None]      # zWWV * zSOI
    return np.column_stack([F, mix])

def walk_single(T,W,E,SOI,yr,mon,mode):
    """ocean / atmos / heartbeat -- one seasonal map (as in heartbeat predictor)."""
    rec={h:{"pred":[],"truth":[],"clim":[],"oy":[]} for h in range(1,HMAX+1)}
    for i in range(len(T)):
        if yr[i]<WALK_START: continue
        idx=np.arange(0,i)
        if len(idx)<MIN_TRAIN: continue
        zW=(W-W[idx].mean())/W[idx].std(); zE=(E-E[idx].mean())/E[idx].std()
        if mode=="ocean": X=np.column_stack([T,zW,zE])
        else:
            zS=(SOI-SOI[idx].mean())/SOI[idx].std(); X=np.column_stack([T,zW,zE,zS])
        clim=T[idx].mean()
        def ff(x,mm):
            F=base_feats(x,mm)
            if mode=="heartbeat":
                g=np.array([1.0 if int(v) in SPRING else 0.0 for v in mm])
                F=np.column_stack([F,(g*(x[:,1]*x[:,3]))[:,None]])
            return F
        B=np.linalg.lstsq(ff(X[idx][:-1],mon[idx][:-1]), X[idx][1:], rcond=None)[0]
        for h in range(1,HMAX+1):
            if i+h>=len(T): break
            x=X[i].copy()
            for kk in range(h):
                mm=((mon[i]-1+kk)%12)+1
                x=ff(x[None,:],np.array([mm]))[0]@B
            rec[h]["pred"].append(x[0]); rec[h]["truth"].append(T[i+h])
            rec[h]["clim"].append(clim); rec[h]["oy"].append(yr[i])
    return rec

def walk_switch(T,W,E,SOI,yr,mon):
    """Two maps: spring (with mix) and rest. Pick by the month being stepped out of."""
    rec={h:{"pred":[],"truth":[],"clim":[],"oy":[]} for h in range(1,HMAX+1)}
    for i in range(len(T)):
        if yr[i]<WALK_START: continue
        idx=np.arange(0,i)
        if len(idx)<MIN_TRAIN: continue
        zW=(W-W[idx].mean())/W[idx].std(); zE=(E-E[idx].mean())/E[idx].std()
        zS=(SOI-SOI[idx].mean())/SOI[idx].std()
        X=np.column_stack([T,zW,zE,zS]); clim=T[idx].mean()
        mtr=mon[idx][:-1]; Xa=X[idx][:-1]; Xb=X[idx][1:]
        sp=np.array([int(v) in SPRING for v in mtr])
        # spring map (with mix) on spring-origin transitions; rest map on the others
        Bs=Br=None
        if sp.sum()>=12:
            Bs=np.linalg.lstsq(spring_feats(Xa[sp],mtr[sp]), Xb[sp], rcond=None)[0]
        if (~sp).sum()>=12:
            Br=np.linalg.lstsq(base_feats(Xa[~sp],mtr[~sp]), Xb[~sp], rcond=None)[0]
        if Bs is None or Br is None: continue
        for h in range(1,HMAX+1):
            if i+h>=len(T): break
            x=X[i].copy()
            for kk in range(h):
                mm=((mon[i]-1+kk)%12)+1
                if mm in SPRING: x=spring_feats(x[None,:],np.array([mm]))[0]@Bs
                else:            x=base_feats(x[None,:],np.array([mm]))[0]@Br
            rec[h]["pred"].append(x[0]); rec[h]["truth"].append(T[i+h])
            rec[h]["clim"].append(clim); rec[h]["oy"].append(yr[i])
    return rec

def skill(pred,truth,clim):
    pred=np.asarray(pred); m=~np.isnan(pred)
    return 1-np.mean((pred[m]-truth[m])**2)/np.mean((clim[m]-truth[m])**2)
def corr(pred,truth):
    pred=np.asarray(pred); truth=np.asarray(truth); m=~np.isnan(pred)
    a=pred[m]-pred[m].mean(); b=truth[m]-truth[m].mean()
    d=np.sqrt((a*a).sum()*(b*b).sum()); return float((a*b).sum()/d) if d>0 else 0.0

def calib(rec):
    out={}
    for h in range(1,HMAX+1):
        oy=np.array(rec[h]["oy"]); pr=np.array(rec[h]["pred"])
        tr=np.array(rec[h]["truth"]); cl=np.array(rec[h]["clim"])
        if len(oy)==0: continue
        trn=oy<CAL_SPLIT_YEAR; tst=oy>=CAL_SPLIT_YEAR
        if tst.sum()<20 or trn.sum()<20: continue
        x=pr[trn]-cl[trn]; y=tr[trn]-cl[trn]
        beta=np.dot(x,y)/np.dot(x,x) if np.dot(x,x)>0 else 0.0
        beta=max(0.0,min(1.0,beta))
        cal=cl[tst]+beta*(pr[tst]-cl[tst])
        out[h]=dict(corr=corr(pr[tst],tr[tst]), skill=skill(pr[tst],tr[tst],cl[tst]),
                    skill_cal=skill(cal,tr[tst],cl[tst]), beta=beta)
    return out

def main():
    nino_csv=sys.argv[1] if len(sys.argv)>1 else "nino34_long_anom.csv"
    soi_path=sys.argv[2] if len(sys.argv)>2 else "soi.data"
    W=load_wwv("wwv_west.dat"); E=load_wwv("wwv_east.dat")
    nino=load_nino(nino_csv); SOI=load_soi(soi_path)
    keys=sorted(set(W)&set(E)&set(nino)&set(SOI))
    T=np.array([nino[k] for k in keys]); Wv=np.array([W[k] for k in keys])
    Ev=np.array([E[k] for k in keys]); Sv=np.array([SOI[k] for k in keys])
    yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in keys])
    mon=np.array([int(k[4:6]) for k in keys])
    print(f"aligned N={len(keys)} months  {keys[0]}..{keys[-1]}\n")
    res={}
    for m in ("ocean","atmos","heartbeat"):
        res[m]=calib(walk_single(T,Wv,Ev,Sv,yr,mon,m))
    res["switch"]=calib(walk_switch(T,Wv,Ev,Sv,yr,mon))
    print("HELD-OUT CORRELATION (leads) | MSE-skill in [brackets]\n")
    cols=("ocean","atmos","heartbeat","switch")
    hdr=("ocean(base)","+atmos","+heartbeat(absorbed)","SPRING SWITCH")
    print(f"{'lead':>4}  " + "".join(f"{h:>21}" for h in hdr))
    for h in (1,3,6,9,12,15,18,21,24,27):
        row=f"{h:>4} "
        for m in cols:
            d=res[m].get(h)
            row+=f"  {d['corr']:>+6.3f}[{d['skill']:>+5.2f}]   " if d else f"  {'--':>14}   "
        print(row)
    print("\ncorr LEADS. SWITCH = separate spring/rest maps; mix drives only in the spring map.")
if __name__=="__main__": main()
