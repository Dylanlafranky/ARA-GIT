"""Multi-record replication: does the heart's sub-beat morphology lift the h=3 dip across people?
Strict-causal. slpdb records fetched via wfdb. ECG morphology (causal, per beat) + RR AR lags.
For each record and horizon: persistence vs AR(RR lags) vs AR+morph. We ask whether AR+morph
(a) beats persistence and (b) beats AR-alone, at each horizon, focusing on h=3."""
import numpy as np, json, sys, time
import wfdb
from scipy.signal import find_peaks
FS=250.0; TRAIN=0.60; LAGS=[0,1,2,3,4,5,8,13]; HS=[1,3,5,8,13]
RECS=['slp01a','slp01b','slp02a','slp02b','slp03','slp04','slp14','slp16','slp32',
      'slp37','slp41','slp45','slp48','slp59','slp60','slp61','slp66','slp67']

def ridge(Xtr,ytr,Xte,pen=1.0):
    mu=np.nanmean(Xtr,0); sd=np.nanstd(Xtr,0); sd[sd<1e-9]=1
    A=np.nan_to_num((Xtr-mu)/sd); B=np.nan_to_num((Xte-mu)/sd)
    A=np.column_stack([np.ones(len(A)),A]); B=np.column_stack([np.ones(len(B)),B])
    R=np.eye(A.shape[1])*pen; R[0,0]=0
    beta=np.linalg.solve(A.T@A+R,A.T@ytr); return B@beta
def cc(a,b):
    a=np.asarray(a);b=np.asarray(b);v=np.isfinite(a)&np.isfinite(b)
    if v.sum()<5: return np.nan
    return float(np.corrcoef(a[v],b[v])[0,1])
def fillc(x):
    x=np.asarray(x,float); med=np.nanmedian(x); out=x.copy(); last=med if np.isfinite(med) else 0.0
    for i in range(len(out)):
        if np.isfinite(out[i]): last=out[i]
        else: out[i]=last
    return out

def features(rec, sampto=450000, max_beats=3500):
    sig,fields=wfdb.rdsamp(rec, pn_dir='slpdb', sampto=sampto)
    sn=fields['sig_name']; ci={n:i for i,n in enumerate(sn)}
    ename=[n for n in sn if n.lower()=='ecg'] or [n for n in sn if 'ecg' in n.lower()]
    if not ename: raise ValueError('no ECG')
    ecg=sig[:,ci[ename[0]]]
    bpn=[n for n in sn if 'bp' in n.lower() or 'blood' in n.lower()]
    bp=sig[:,ci[bpn[0]]] if bpn else None
    pks,_=find_peaks(ecg, distance=int(0.4*FS), prominence=0.4*np.nanstd(ecg))
    pks=pks[(pks>1)&(pks<len(ecg)-1)]
    if len(pks)<200: raise ValueError('too few beats')
    rr=np.diff(pks)/FS*1000.0; nb=len(pks)-1
    qt=np.full(nb,np.nan); cen=np.full(nb,np.nan); amp=np.full(nb,np.nan)
    bps=np.full(nb,np.nan); bpp=np.full(nb,np.nan)
    for i in range(nb):
        w=ecg[pks[i]:pks[i+1]]; L=len(w)
        if L<10: continue
        a,b=int(0.10*L),max(int(0.55*L),int(0.10*L)+2); seg=w[a:b]
        if len(seg)>1: qt[i]=(a+int(np.argmax(np.abs(seg-np.median(w)))))/L
        e=(w-np.mean(w))**2; s=e.sum()
        if s>0: cen[i]=float(np.dot(np.arange(L),e)/s)/L
        amp[i]=float(w.max()-w.min())
        if bp is not None:
            wb=bp[pks[i]:pks[i+1]]
            if len(wb)>2: bps[i]=float(np.argmax(wb))/len(wb); bpp[i]=float(wb.max()-wb.min())
    med=np.median(rr); good=(rr>0.4*med)&(rr<1.8*med)
    cols=[qt,cen,amp]+([bps,bpp] if bp is not None else [])
    rr=rr[good]; cols=[fillc(c[good]) for c in cols]
    morph=np.column_stack(cols)
    return rr[:max_beats], morph[:max_beats]

def run_record(rec):
    rr,morph=features(rec); n=len(rr); cut=int(n*TRAIN); start=14
    out={}
    for h in HS:
        idx=np.arange(start,n-h); tr=idx[idx<cut-h]; te=idx[idx>=cut]
        if len(tr)<50 or len(te)<50: out[h]=None; continue
        ytr=rr[tr+h]; yte=rr[te+h]; cur=rr[te]
        AR_tr=np.column_stack([rr[tr-l] for l in LAGS]); AR_te=np.column_stack([rr[te-l] for l in LAGS])
        M_tr=morph[tr]; M_te=morph[te]
        pers=cc(yte,cur)
        car=cc(yte,ridge(AR_tr,ytr,AR_te))
        cam=cc(yte,ridge(np.column_stack([AR_tr,M_tr]),ytr,np.column_stack([AR_te,M_te])))
        out[h]={'pers':pers,'ar':car,'ar_morph':cam,'beats':int(n)}
    return out

def main():
    import os
    RES='heart_subsystem_replication_result.json'
    results=json.load(open(RES)) if os.path.exists(RES) else {}
    budget=time.time()+18
    for r in RECS:
        if r in results: continue
        if time.time()>budget:
            print('TIME BUDGET hit, exiting to resume next call', flush=True); break
        t0=time.time()
        try:
            results[r]=run_record(r)
            json.dump(results, open('heart_subsystem_replication_result.json','w'), indent=1, default=float)
            h3=results[r].get(3)
            msg=f"{r}: ok ({time.time()-t0:.0f}s)"
            if h3: msg+=f"  h3 pers {h3['pers']:+.3f} AR {h3['ar']:+.3f} AR+morph {h3['ar_morph']:+.3f}"
            print(msg, flush=True)
        except Exception as e:
            results[r]={'error':str(e)[:60]}; print(f"{r}: ERR {str(e)[:50]}", flush=True)
            json.dump(results, open('heart_subsystem_replication_result.json','w'), indent=1, default=float)
    # summary
    print("\n=== SUMMARY: AR+morph vs persistence and vs AR-alone, per horizon ===")
    for h in HS:
        rows=[v[h] for v in results.values() if isinstance(v,dict) and v.get(h)]
        if not rows: continue
        nbeat=sum(1 for x in rows if x['ar_morph']>x['pers'])
        nlift=sum(1 for x in rows if x['ar_morph']>x['ar']+0.005)
        dmorph=np.mean([x['ar_morph']-x['ar'] for x in rows])
        dpers=np.mean([x['ar_morph']-x['pers'] for x in rows])
        print(f"h={h:>2}: n={len(rows)}  beats_persist {nbeat}/{len(rows)}  morph_lifts_AR {nlift}/{len(rows)}  "
              f"mean(morph-AR) {dmorph:+.3f}  mean(morph-pers) {dpers:+.3f}")
    json.dump(results, open('heart_subsystem_replication_result.json','w'), indent=1, default=float)
    print("\nDONE -> heart_subsystem_replication_result.json")

if __name__=='__main__': main()
