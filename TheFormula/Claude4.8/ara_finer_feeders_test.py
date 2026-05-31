"""
ARA finer-feeders test  --  does the 6-month wall (corr ~0.725) move toward 0.764?
==================================================================================
Dylan's hypothesis (2026-05-30): the slow recharge signal is the LARGEST information
packet; finer/faster data rides on top of it. The 6-month skill ceiling ~0.725 should
creep toward 0.764 (= 1 - 1/phi^3) as we pour in finer feeders -- but not past ~0.8
without atom-scale data. Test it by adding real intraseasonal/stratospheric drivers to
the spring regime-switch model and watching h=6 held-out correlation.

Finer feeders (real public data):
  * MJO  -- Bureau of Meteorology RMM index (daily; aggregated to monthly MEAN AMPLITUDE
            = the intraseasonal activity envelope that survives monthly sampling).
  * QBO  -- NOAA CPC 30 hPa & 50 hPa equatorial stratospheric zonal wind (monthly).

Base model = the spring regime-switch (two seasonal maps, ocean*atmosphere mix drives
only in the spring map). Feeders are added as extra standardized state columns. Strictly
causal: every feeder standardized train-only; both maps refit past-only at every origin;
regime label = calendar. Correlation leads.

Compared at every lead:
  switch        = base (T, zW, zE, zSOI)                        [prior champion, ~0.725 @ h6]
  +QBO          = base + QBO30 + QBO50
  +MJO          = base + monthly MJO amplitude
  +QBO+MJO      = all finer feeders (fill the gaps)

Usage: python3 ara_finer_feeders_test.py
"""
import re
import numpy as np

WALK_START=2005.0; MIN_TRAIN=270; CAL_SPLIT_YEAR=2016.0; HMAX=30
SPRING={3,4,5}

# ---------- loaders ----------
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
        for mo,val in enumerate(ln.split()[1:13],1):
            try: v=float(val)
            except: continue
            if v>miss+0.001: d[f"{yr}{mo:02d}"]=v
    return d
def load_qbo(p,miss=-99.0):
    """NOAA CPC monthly: YEAR then 12 monthly values."""
    d={}
    for ln in open(p):
        s=ln.split()
        if len(s)>=13 and s[0].isdigit() and len(s[0])==4:
            yr=int(s[0])
            for mo in range(1,13):
                try: v=float(s[mo])
                except: continue
                if v>miss: d[f"{yr}{mo:02d}"]=v
    return d
def load_mjo_amp(p):
    """BoM RMM daily -> monthly mean amplitude (intraseasonal activity envelope)."""
    acc={}
    for ln in open(p):
        s=ln.split()
        if len(s)<7 or not s[0].isdigit(): continue
        yr,mo=s[0],int(s[1]); amp=float(s[6])
        if amp>900: continue            # missing 999 / 1e36
        k=f"{yr}{mo:02d}"
        acc.setdefault(k,[]).append(amp)
    return {k:float(np.mean(v)) for k,v in acc.items()}

# ---------- model ----------
def base_feats(X,m):
    th=2*np.pi*(m-1)/12; c,s=np.cos(th),np.sin(th)
    return np.column_stack([X, X*c[:,None], X*s[:,None], c, s, np.ones(len(X))])
def spring_feats(X,m):
    F=base_feats(X,m); mix=(X[:,1]*X[:,3])[:,None]   # zWWV * zSOI
    return np.column_stack([F, mix])

def walk_switch(cols_raw, mean_idx_cols, yr, mon, T):
    """cols_raw: list of full-length arrays forming the state (T first, zW second, zSOI fourth).
       Columns are standardized train-only each origin. Returns per-lead records."""
    rec={h:{"pred":[],"truth":[],"clim":[],"oy":[]} for h in range(1,HMAX+1)}
    A=np.column_stack(cols_raw)
    for i in range(len(T)):
        if yr[i]<WALK_START: continue
        idx=np.arange(0,i)
        if len(idx)<MIN_TRAIN: continue
        X=A.copy().astype(float)
        for j in mean_idx_cols:                       # standardize these cols train-only
            mu=A[idx,j].mean(); sd=A[idx,j].std()
            X[:,j]=(A[:,j]-mu)/(sd if sd>0 else 1.0)
        clim=T[idx].mean()
        mtr=mon[idx][:-1]; Xa=X[idx][:-1]; Xb=X[idx][1:]
        sp=np.array([int(v) in SPRING for v in mtr])
        if sp.sum()<12 or (~sp).sum()<12: continue
        Bs=np.linalg.lstsq(spring_feats(Xa[sp],mtr[sp]), Xb[sp], rcond=None)[0]
        Br=np.linalg.lstsq(base_feats(Xa[~sp],mtr[~sp]), Xb[~sp], rcond=None)[0]
        for h in range(1,HMAX+1):
            if i+h>=len(T): break
            x=X[i].copy()
            for kk in range(h):
                mm=((mon[i]-1+kk)%12)+1
                x=(spring_feats(x[None,:],np.array([mm]))[0]@Bs) if mm in SPRING \
                  else (base_feats(x[None,:],np.array([mm]))[0]@Br)
            rec[h]["pred"].append(x[0]); rec[h]["truth"].append(T[i+h])
            rec[h]["clim"].append(clim); rec[h]["oy"].append(yr[i])
    return rec

def corr(pred,truth):
    pred=np.asarray(pred); truth=np.asarray(truth); m=~np.isnan(pred)
    a=pred[m]-pred[m].mean(); b=truth[m]-truth[m].mean()
    d=np.sqrt((a*a).sum()*(b*b).sum()); return float((a*b).sum()/d) if d>0 else 0.0
def skill(pred,truth,clim):
    pred=np.asarray(pred); m=~np.isnan(pred)
    return 1-np.mean((pred[m]-truth[m])**2)/np.mean((clim[m]-truth[m])**2)
def evalrec(rec):
    out={}
    for h in range(1,HMAX+1):
        oy=np.array(rec[h]["oy"]); pr=np.array(rec[h]["pred"])
        tr=np.array(rec[h]["truth"]); cl=np.array(rec[h]["clim"])
        if len(oy)==0: continue
        tst=oy>=CAL_SPLIT_YEAR
        if tst.sum()<20: continue
        out[h]=dict(corr=corr(pr[tst],tr[tst]), skill=skill(pr[tst],tr[tst],cl[tst]), n=int(tst.sum()))
    return out

def main():
    W=load_wwv("wwv_west.dat"); E=load_wwv("wwv_east.dat")
    nino=load_nino("nino34_long_anom.csv"); SOI=load_soi("soi.data")
    Q30=load_qbo("qbo_u30.txt"); Q50=load_qbo("qbo_u50.txt"); MJO=load_mjo_amp("mjo_rmm.txt")

    base_keys=sorted(set(W)&set(E)&set(nino)&set(SOI))
    print(f"base aligned (T,WWV,SOI): {len(base_keys)}  {base_keys[0]}..{base_keys[-1]}")
    print(f"QBO30 {len(Q30)}  QBO50 {len(Q50)}  MJO(mo) {len(MJO)}\n")

    def build(extra):
        keys=[k for k in base_keys if all(k in d for d in extra)]
        T=np.array([nino[k] for k in keys]); Wv=np.array([W[k] for k in keys])
        Ev=np.array([E[k] for k in keys]); Sv=np.array([SOI[k] for k in keys])
        yr=np.array([int(k[:4])+(int(k[4:6])-1)/12 for k in keys])
        mon=np.array([int(k[4:6]) for k in keys])
        cols=[T,Wv,Ev,Sv]; stdz=[1,2,3]                 # standardize WWV,WWVe,SOI (T raw)
        for d in extra:
            cols.append(np.array([d[k] for k in keys])); stdz.append(len(cols)-1)
        return cols,stdz,yr,mon,T,len(keys)

    configs={
        "switch (base)":      [],
        "+QBO":               [Q30,Q50],
        "+MJO":               [MJO],
        "+QBO+MJO":           [Q30,Q50,MJO],
    }
    res={}; ns={}
    for name,extra in configs.items():
        cols,stdz,yr,mon,T,n=build(extra)
        res[name]=evalrec(walk_switch(cols,stdz,yr,mon,T)); ns[name]=n

    print("HELD-OUT CORRELATION (leads)   [N aligned months in brackets]\n")
    names=list(configs)
    print(f"{'lead':>4}  " + "".join(f"{nm:>16}" for nm in names))
    print(f"{'':>4}  " + "".join(f"{'[N='+str(ns[nm])+']':>16}" for nm in names))
    for h in (1,3,6,9,12,15,18,24):
        row=f"{h:>4} "
        for nm in names:
            d=res[nm].get(h)
            row+=f"   {d['corr']:>+6.3f}      " if d else f"   {'--':>10}   "
        print(row)
    print(f"\nDylan's wall: 0.764 = 1 - 1/phi^3.  Watch h=6 (physical horizon).")
    print("If finer feeders lift h=6 toward 0.764 -> the wall is porous (small data fills it).")
    print("If h=6 stays pinned -> 0.725 is this system's true singularity edge.")
if __name__=="__main__": main()
