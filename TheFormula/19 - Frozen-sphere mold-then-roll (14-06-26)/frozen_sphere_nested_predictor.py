#!/usr/bin/env python3
"""
FROZEN-SPHERE MOLD-THEN-ROLL predictor  (Test 1: nested NINO3.4 <- WWV)
=======================================================================
Dylan's epiphany (13 Jun 2026): the WAVE *is* the topography. Mold each
system's sphere ONCE on the first 63% (golden 1/phi split), FREEZE the shape;
the sphere keeps its designed MOTION (spin + wobble). The TARGET's spin is
driven by the rung BELOW feeding energy up (WWV recharge -> NINO).

  - Nested-Blind : the feeder (WWV) is ALSO rolled forward on its own frozen
                   sphere; nothing in the test window is observed.
  - Driver-Fed   : the feeder (WWV) is observed during the test window.

VERDICT (see FROZEN_SPHERE_MOLD_THEN_ROLL_RESULT.md):
  Driver-fed beats AR at h=12/24, BUT a plain linear recharge regression
  (NINO + WWV + WWV[t-6]) matches/beats it -> the long-horizon win is the
  FEEDER, not the sphere geometry. Same value-ceiling as every prior test.

Strict-causal: all stats/normalisation TRAIN-ONLY; no acausal filters
(causal first-difference slope only); NINO future never read; feeder blind in
nested mode. Headline metric = correlation (per Dylan's rule).
Data: NOAA NINO3.4 anomaly + PMEL WWV east/west (1980-2025 overlap).
"""
import numpy as np, re, json
PHI=(1+5**0.5)/2
DATA="Claude4.8"   # nino34_long_anom.csv, wwv_east.dat, wwv_west.dat

def load_nino():
    d={}
    for line in open(f"{DATA}/nino34_long_anom.csv"):
        m=re.match(r'\s*(\d{4})-(\d{2})-\d{2},\s*(-?\d+\.\d+)',line)
        if m and float(m.group(3))>-99: d[(int(m.group(1)),int(m.group(2)))]=float(m.group(3))
    return d
def load_wwv():
    def rd(fn):
        d={}
        for line in open(f"{DATA}/{fn}"):
            m=re.match(r'\s*(\d{4})(\d{2})\s+\S+\s+(\S+)',line)
            if m: d[(int(m.group(1)),int(m.group(2)))]=float(m.group(3).replace('E','e'))
        return d
    e,w=rd("wwv_east.dat"),rd("wwv_west.dat")
    return {k:e[k]+w[k] for k in e if k in w}

nino,wwv=load_nino(),load_wwv()
keys=sorted(set(nino)&set(wwv)); N=np.array([nino[k] for k in keys]); W=np.array([wwv[k] for k in keys])
n=len(keys); split=int(round(n/PHI))
Nz=(N-N[:split].mean())/N[:split].std(); Wz=(W-W[:split].mean())/W[:split].std()
print(f"overlap months={n} ({keys[0]}..{keys[-1]}) train={split} test={n-split}")

def cslope(x): s=np.zeros_like(x); s[1:]=x[1:]-x[:-1]; return s
NB=24
def pick(x,tr): s=cslope(x); return x[:tr].std()/(s[:tr].std()+1e-9)
def mold(x,tr,sc):  # freeze phase-portrait terrain (the molded wave-shape) from train
    s=cslope(x); xt,st=x[:tr],s[:tr]
    th=np.arctan2(st*sc,xt); r=np.sqrt(xt**2+(st*sc)**2); dth=np.diff(np.unwrap(th))
    bv=np.full(NB,np.nan); br=np.full(NB,np.nan); idx=((th+np.pi)/(2*np.pi)*NB).astype(int)%NB
    for b in range(NB):
        if (idx[:-1]==b).sum()>=3: bv[b]=np.median(dth[idx[:-1]==b])
        if (idx==b).sum()>=3: br[b]=np.median(r[idx==b])
    for arr in (bv,br):
        gd=~np.isnan(arr)
        if gd.sum()<2: arr[:]=(np.nanmedian(arr) if gd.any() else 0.0)
        else: arr[~gd]=np.interp(np.where(~gd)[0],np.where(gd)[0],arr[gd],period=NB)
    return dict(bv=bv,br=br,sc=sc)
def step(x,s,t,push=0.0):  # one ARA step on the frozen sphere (spin + ridge/sink + push)
    sc=t['sc']; th=np.arctan2(s*sc,x); b=int(((th+np.pi)/(2*np.pi)*NB))%NB
    t2=th+t['bv'][b]; r=t['br'][b]
    return r*np.cos(t2)+push, r*np.sin(t2)/sc

scN,scW=pick(Nz,split),pick(Wz,split); tN=mold(Nz,split,scN); tW=mold(Wz,split,scW)
sN,sW=cslope(Nz),cslope(Wz)
# WWV->NINO coupling: level-level lead (recharge) + single strength scalar, train only
best=(0,0.0)
for L in range(0,19):
    a=Wz[:split-L] if L>0 else Wz[:split]; b=Nz[L:split] if L>0 else Nz[:split]
    c=np.corrcoef(a,b)[0,1]
    if abs(c)>abs(best[1]): best=(L,c)
LEAD,lc=best
a=Wz[:split-LEAD] if LEAD>0 else Wz[:split]; b=Nz[LEAD:split] if LEAD>0 else Nz[:split]
g,inter=np.polyfit(a,b,1); BETA=abs(lc)   # driver weight = train explanatory corr (not tuned)
print(f"level lead={LEAD}mo corr {lc:+.3f}  g={g:+.3f}  beta={BETA:.3f}")

HOR=[3,6,12,24]
def roll(o,h,mode):  # mode: 'pure'|'blind'|'fed'
    xN,sN_=Nz[o],sN[o]; xW,sW_=Wz[o],sW[o]; wbuf=list(Wz[:o+1])
    for k in range(h):
        if mode=='pure': push=0.0
        else:
            w_lag=wbuf[-1-LEAD] if len(wbuf)>LEAD else wbuf[0]
            tgt=g*w_lag+inter; sph,_=step(xN,sN_,tN); push=BETA*(tgt-sph)
        xN,sN_=step(xN,sN_,tN,push=push)
        if mode in ('pure','blind'): xW,sW_=step(xW,sW_,tW)
        else:
            j=o+k+1
            if j<n: xW,sW_=Wz[j],sW[j]
        wbuf.append(xW)
    return xN
AR_P=6
X=np.column_stack([Nz[AR_P-1-i:split-1-i] for i in range(AR_P)]); y=Nz[AR_P:split]
arb,*_=np.linalg.lstsq(np.column_stack([np.ones(len(y)),X]),y,rcond=None)
def arf(h):
    out=[]
    for o in range(split,n-h):
        hist=list(Nz[o-AR_P+1:o+1])
        for _ in range(h): hist.append(arb[0]+sum(arb[1+i]*hist[-1-i] for i in range(AR_P)))
        out.append(hist[-1])
    return np.array(out)
def C(a,b): return np.corrcoef(a,b)[0,1] if np.std(a)>1e-9 and np.std(b)>1e-9 else 0.0
print(f"\n{'h':>4} {'pure':>7} {'blind':>7} {'fed':>7} {'AR6':>7} {'pers':>7}")
res={}
for h in HOR:
    P=[];B=[];F=[];T=[];Pe=[]
    for o in range(split,n-h):
        P.append(roll(o,h,'pure')); B.append(roll(o,h,'blind')); F.append(roll(o,h,'fed'))
        T.append(Nz[o+h]); Pe.append(Nz[o])
    P,B,F,T,Pe=map(np.array,(P,B,F,T,Pe)); ar=arf(h)
    res[h]=dict(pure=C(P,T),blind=C(B,T),fed=C(F,T),ar=C(ar,T),pers=C(Pe,T),n=len(T))
    print(f"{h:>4} {res[h]['pure']:+7.3f} {res[h]['blind']:+7.3f} {res[h]['fed']:+7.3f} {res[h]['ar']:+7.3f} {res[h]['pers']:+7.3f}")
print("\nLinear recharge baseline [const,NINO,WWV,WWV-6] (the decisive control):")
for h in HOR:
    Xtr=[];Ytr=[];Xte=[];Yte=[]
    for o in range(6,n-h):
        f=[1.0,Nz[o],Wz[o],Wz[o-6]]
        (Xtr,Ytr) if o<split else (Xte,Yte)
        if o<split: Xtr.append(f); Ytr.append(Nz[o+h])
        else: Xte.append(f); Yte.append(Nz[o+h])
    Xtr,Ytr,Xte,Yte=map(np.array,(Xtr,Ytr,Xte,Yte))
    bb,*_=np.linalg.lstsq(Xtr,Ytr,rcond=None)
    print(f"  h={h:2d}  LR {C(Xte@bb,Yte):+.3f}")
