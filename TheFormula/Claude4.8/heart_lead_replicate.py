"""
Does the brain's 8-beat lead on the heart replicate across people?  (Dylan, 2026-05-30)
=======================================================================================
slp01a showed: brain (EEG slow tonic, tanked) leads the heart by ~8 beats -- both by
cross-correlation AND by where its standalone forecast of RR[t+h] peaks. Is "8" this one
sleeper, or a body constant? Re-run on several slpdb records (ECG+BP+EEG+Resp).

For each record, strict-causal:
  brain_slow = leaky-tank(z(EEG slow band)), z + tank on TRAIN half only.
  (1) cross-correlation lead of brain_slow to RR (beats).
  (2) horizon where brain_slow ALONE best forecasts RR[t+h] (no heart data fed in).
If both cluster near the same lead across people, the relay handoff is a real constant.

Data: PhysioNet slpdb, fetched live via wfdb. Real. Descriptive.
"""
import numpy as np, json, sys
import wfdb
from scipy.signal import find_peaks

PHI=(1+5**0.5)/2; LEAK=1/PHI; FS=250.0; TRAIN=0.60
HS=(1,2,3,5,8,13,21); SLOW_WIN=8
RECS=['slp01a','slp01b','slp02a','slp03','slp04','slp32','slp37','slp45']

def trailing_slow(x,w):
    out=np.empty_like(x,float)
    for i in range(len(x)): out[i]=x[max(0,i-w+1):i+1].mean()
    return out
def leaky(x):
    h=np.zeros_like(x,float)
    for t in range(1,len(x)): h[t]=LEAK*h[t-1]+(1-LEAK)*x[t]
    return h
def per_beat(rec, max_beats=4000):
    sig,fields=wfdb.rdsamp(rec, pn_dir='slpdb')
    sn=fields['sig_name']; ci={n:i for i,n in enumerate(sn)}
    ecg=sig[:,ci['ECG']]
    eegname=[n for n in sn if 'eeg' in n.lower()][0]
    eeg=sig[:,ci[eegname]]
    pks,_=find_peaks(ecg, distance=int(0.4*FS), prominence=0.4*np.nanstd(ecg))
    pks=pks[(pks>1)&(pks<len(ecg)-1)]
    rr=np.diff(pks)/FS*1000.0
    eeg_b=np.array([np.nanmean(eeg[pks[i]:pks[i+1]]) for i in range(len(pks)-1)])
    med=np.median(rr); good=(rr>0.4*med)&(rr<1.8*med)
    rr=rr[good]; eeg_b=eeg_b[good]
    ok=np.isfinite(rr)&np.isfinite(eeg_b); rr=rr[ok]; eeg_b=eeg_b[ok]
    return rr[:max_beats], eeg_b[:max_beats]
def lead_beats(f,rr,maxlag=20):
    a=(f-f.mean())/(f.std() or 1); b=(rr-rr.mean())/(rr.std() or 1)
    best,bl=-1,0
    for L in range(0,maxlag+1):
        c=abs(np.corrcoef(a,b)[0,1]) if L==0 else abs(np.corrcoef(a[:-L],b[L:])[0,1])
        if c>best: best,bl=c,L
    return bl,best
def fcorr(rr,feat,h):
    n=len(rr); lo=1; hi=n-h; split=lo+int((hi-lo)*TRAIN)
    Xtr=np.array([[feat[t],1.0] for t in range(lo,split)])
    Xte=np.array([[feat[t],1.0] for t in range(split,hi)])
    ytr=np.array([rr[t+h] for t in range(lo,split)]); yte=np.array([rr[t+h] for t in range(split,hi)])
    m=Xtr[:,0].mean(); s=Xtr[:,0].std() or 1; Xtr[:,0]=(Xtr[:,0]-m)/s; Xte[:,0]=(Xte[:,0]-m)/s
    beta,*_=np.linalg.lstsq(Xtr,ytr,rcond=None); pred=Xte@beta
    return np.nan if pred.std()==0 else float(np.corrcoef(pred,yte)[0,1])

def main():
    print("Brain-slow lead on the heart across sleepers (slpdb, strict-causal)\n")
    print("%-8s %6s  %-8s   %s" % ("record","beats","xcorr","forecast-peak horizon (brain alone)"))
    leads=[]; peaks=[]
    for r in RECS:
        try: rr,eeg=per_beat(r)
        except Exception as e:
            print("%-8s ERR %s"%(r,str(e)[:40])); continue
        n=len(rr); split=int(n*TRAIN)
        zt=lambda x:(x-x[:split].mean())/(x[:split].std() or 1)
        brain=leaky(zt(eeg-trailing_slow(eeg,SLOW_WIN)*0+trailing_slow(eeg,SLOW_WIN)))  # slow band, tanked
        # NOTE: brain slow band = trailing_slow(eeg); tank it
        brain=leaky(zt(trailing_slow(eeg,SLOW_WIN)))
        L,c=lead_beats(brain,rr)
        cur=[(h,fcorr(rr,brain,h)) for h in HS]
        ph=max([x for x in cur if x[1]==x[1]], key=lambda z:z[1])[0]
        leads.append(L); peaks.append(ph)
        curstr=" ".join("h%d=%+.2f"%(h,v) for h,v in cur)
        print("%-8s %6d  lead=%2d   peak@%2d  | %s"%(r,n,L,ph,curstr))
    if leads:
        print("\nxcorr leads: %s  median %.1f"%(leads, np.median(leads)))
        print("forecast peaks: %s  median %.1f"%(peaks, np.median(peaks)))
        print("If both cluster ~same beats => relay handoff is a body constant, not one sleeper.")

if __name__=="__main__": main()
