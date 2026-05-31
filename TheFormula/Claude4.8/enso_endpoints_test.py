#!/usr/bin/env python3
"""TRUE exchange-channel test on REAL, independently-defined ENSO channels.
Endpoints (predict PASS, build own phi-tower):
  ocean = WWV anomaly (PMEL/NOAA warm water volume, monthly)
  air   = SOI (CPC/NOAA Southern Oscillation pressure index, monthly)
Exchange/tether (predict FAIL, inherited): NINO3.4 SST anomaly (the surface swap).
None of these signals is constructed by my filtering -> not the rigged-to-fail trap.
"""
import re, json, warnings
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfiltfilt, correlate, correlation_lags, welch
warnings.filterwarnings("ignore")
PHI=(1+5**0.5)/2
ROOT=Path("/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder")
rng=np.random.default_rng(7)

def norm(a):
    a=np.asarray(a,float); a=a-a.mean(); s=a.std(); return a/s if s>0 else a
def bp(x,period,ratio=1.3):
    lo=1.0/(period*ratio); hi=min(1.0/(period/ratio),0.49)
    sos=butter(3,[lo,hi],btype="band",fs=1.0,output="sos"); return sosfiltfilt(sos,x)
def phase_rand(x):
    X=np.fft.rfft(x); mag=np.abs(X); ph=np.angle(X)
    rp=rng.uniform(-np.pi,np.pi,len(ph)); rp[0]=ph[0]
    if len(x)%2==0: rp[-1]=ph[-1]
    return np.fft.irfft(mag*np.exp(1j*rp),n=len(x))
def gen_slow(s,r1,r2,r3): return bp(bp(s,r1)*bp(s,r2),r3)
def pcl(a,b,maxlag):
    a=norm(a); b=norm(b); c=correlate(b,a,mode="full")/len(a)
    lg=correlation_lags(len(b),len(a),mode="full"); m=np.abs(lg)<=maxlag
    cc=c[m]; ll=lg[m]; i=int(np.argmax(cc)); return float(cc[i]),int(ll[i])
def dom_period(x,lo,hi):
    x=norm(x); f,P=welch(x,fs=1.0,nperseg=min(len(x),512))
    m=(f>=1/hi)&(f<=1/lo)&(f>0)
    if not m.any(): return (lo+hi)/2
    return float(1.0/f[m][np.argmax(P[m])])
def dot(x,P,nn=40):
    x=norm(x); r1,r2,r3=P,P*PHI,P*PHI**2
    if len(x)<6*r3 or r1<4: return None
    g=gen_slow(x,r1,r2,r3); ac=bp(x,r3); ml=int(round(r3))
    co,lag=pcl(g,ac,ml)
    nl=[pcl(gen_slow(phase_rand(x),r1,r2,r3),bp(phase_rand(x),r3),ml)[0] for _ in range(nn)]
    nl=np.array(nl); z=float((co-nl.mean())/(nl.std()+1e-9))
    return {"P":P,"recon":co,"lag_frac":float(lag/r3),"z":z,"n":len(x)}

def load_soi():
    vals=[]
    for ln in (ROOT/"SOI_NOAA/soi.data").read_text().splitlines():
        m=re.match(r"\s*(\d{4})\s+(.*)",ln)
        if not m: continue
        yr=int(m.group(1))
        if yr<1900 or yr>2100: continue
        nums=[float(t) for t in m.group(2).split()]
        if len(nums)<12: continue
        vals+=nums[:12]
    a=np.array(vals); a[a<=-99]=np.nan
    return a
def load_wwv():
    vals=[]
    for ln in (ROOT/"GIT/ARA-GIT/TheFormula/Claude4.8/wwv_west.dat").read_text().splitlines():
        m=re.match(r"\s*(\d{6})\s+\S+\s+(\S+)",ln)
        if not m: continue
        try: vals.append(float(m.group(2)))
        except: pass
    return np.array(vals)
def load_nino():
    vals=[]
    for ln in (ROOT/"Nino34/nino34.long.anom.csv").read_text().splitlines()[1:]:
        p=ln.split(",")
        if len(p)<2: continue
        try: v=float(p[1])
        except: continue
        vals.append(v)
    a=np.array(vals); a[a<=-99]=np.nan
    return a
def clean(a):
    a=np.asarray(a,float); idx=np.arange(len(a)); good=np.isfinite(a)
    return np.interp(idx,idx[good],a[good])

def run(name,a,lo=24,hi=96):
    a=clean(a); P=dom_period(a,lo,hi); d=dot(a,P)
    if d is None:
        print(f"  {name:22s} N={len(a):4d}  dot=None (too short for P={P:.0f}mo)"); return None
    tag="PASS" if d["z"]>=2 else "FAIL"
    print(f"  {name:22s} N={d['n']:4d}  P={d['P']:4.0f}mo  recon={d['recon']:+.3f}  "
          f"z={d['z']:+6.1f}  -> {tag}")
    d["name"]=name; return d
def main():
    print("="*74); print("TRUE EXCHANGE TEST  REAL ENSO channels (ocean / air / swap)"); print("="*74)
    soi=load_soi(); wwv=load_wwv(); nino=load_nino()
    print(f"loaded: SOI {len(soi)}mo  WWV {len(wwv)}mo  NINO {len(nino)}mo\n")
    print("FULL SPAN each:")
    out={}
    out["WWV_ocean"]=run("WWV ocean (endpoint)",wwv)
    out["SOI_air"]  =run("SOI air (endpoint)",soi)
    out["NINO_swap"]=run("NINO3.4 (exchange)",nino)
    # common window 1982-2023 (limited by WWV cache overlap); align by month index
    print("\nCOMMON WINDOW 1980-2023 (WWV-limited, all three same months):")
    # WWV starts 1980-01; SOI starts 1948-01; NINO starts 1870-01
    soi_c=soi[(1980-1948)*12:]; nino_c=nino[(1980-1870)*12:]
    n=min(len(wwv),len(soi_c),len(nino_c))
    out["WWV_c"]=run("WWV ocean (endpoint)",wwv[:n])
    out["SOI_c"]=run("SOI air (endpoint)",soi_c[:n])
    out["NINO_c"]=run("NINO3.4 (exchange)",nino_c[:n])
    res={k:({kk:v[kk] for kk in('name','P','recon','lag_frac','z','n')} if v else None)
         for k,v in out.items()}
    Path("/tmp/p2/enso_endpoints_result.json").write_text(json.dumps(res,indent=2))
    print("\nPrediction: both endpoints PASS (z>=2), exchange FAILS (z<2, recon can be high).")
if __name__=="__main__": main()

def sweep():
    print("\n"+"="*74); print("FIXED-ANCHOR SWEEP (same rung for all 3, fair compare)"); print("="*74)
    soi=clean(load_soi()); wwv=clean(load_wwv()); nino=clean(load_nino())
    chans=[("WWV ocean (endpoint)",wwv),("SOI air (endpoint)",soi),("NINO3.4 (exchange)",nino)]
    for P in (24,28,33):
        print(f"\n  anchor P={P}mo  (r3={P*PHI**2:.0f}mo, need {6*P*PHI**2:.0f}mo data):")
        for nm,a in chans:
            d=dot(a,float(P),nn=40)
            if d is None: print(f"    {nm:22s} too short (N={len(a)})"); continue
            tag="PASS" if d["z"]>=2 else "FAIL"
            print(f"    {nm:22s} recon={d['recon']:+.3f}  z={d['z']:+6.1f}  -> {tag}")
sweep()
