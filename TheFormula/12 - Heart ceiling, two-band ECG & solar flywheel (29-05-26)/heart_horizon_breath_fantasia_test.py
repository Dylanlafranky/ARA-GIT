import wfdb, numpy as np
from wfdb import processing
from scipy.signal import hilbert, periodogram

fs=250; N=fs*60*15
recs=['f1y01','f1y02','f1o01','f1o02']

def domper(x):
    f,P=periodogram(x-x.mean())
    f=f[1:];P=P[1:]
    return 1.0/f[np.argmax(P)]

def fc(a,b): 
    return np.corrcoef(a,b)[0,1] if len(a)>2 and a.std()>0 and b.std()>0 else 0.0

H=[1,3,6,12,24]
agg={h:{'pers':[],'self':[],'breath':[]} for h in H}
for rec in recs:
    try:
        sig,_=wfdb.rdsamp(rec, pn_dir='fantasia', sampto=N)
    except Exception as e:
        print(rec,'skip',e); continue
    resp=sig[:,0]; ecg=sig[:,1]; print('proc',rec,flush=True)
    xqrs=processing.XQRS(sig=ecg, fs=fs); xqrs.detect(verbose=False)
    rp=np.array(xqrs.qrs_inds); rp=rp[(rp>0)&(rp<len(ecg))]
    rr=np.diff(rp)/fs*1000.0; bt=rp[1:]
    m=(rr>300)&(rr<2000); rr=rr[m]; bt=bt[m]
    if len(rr)<800: continue
    br=resp[bt]
    n=len(rr); half=n//2
    # breath phase via hilbert on band-limited? use raw zero-mean hilbert
    brz=(br-br.mean())
    bph=np.angle(hilbert(brz))
    bp_per=domper(br[:half])   # breath period in beats from TRAIN only
    rrz=rr-rr[:half].mean()
    for h in H:
        # train on first half, predict second half value rr[t+h] from info at t
        idx=np.arange(half, n-h)
        if len(idx)<50: continue
        y=rr[idx+h]
        # persistence: rr[t]
        pers=rr[idx]
        # self model: lstsq train on first half using rr[t]
        tr=np.arange(0,half-h)
        Xtr=np.c_[np.ones(len(tr)), rr[tr]]
        ytr=rr[tr+h]
        c1=np.linalg.lstsq(Xtr,ytr,rcond=None)[0]
        Xte=np.c_[np.ones(len(idx)), rr[idx]]
        self_pred=Xte@c1
        # breath model: add breath value now + breath phase projected forward
        ph_tr=bph[tr]+2*np.pi*h/bp_per
        Xtr2=np.c_[np.ones(len(tr)), rr[tr], br[tr], np.cos(ph_tr), np.sin(ph_tr)]
        c2=np.linalg.lstsq(Xtr2,ytr,rcond=None)[0]
        ph_te=bph[idx]+2*np.pi*h/bp_per
        Xte2=np.c_[np.ones(len(idx)), rr[idx], br[idx], np.cos(ph_te), np.sin(ph_te)]
        br_pred=Xte2@c2
        agg[h]['pers'].append(fc(pers,y))
        agg[h]['self'].append(fc(self_pred,y))
        agg[h]['breath'].append(fc(br_pred,y))

print(f"{'h':>3} {'persist':>8} {'RR-self':>8} {'+breath':>8} {'breath adds':>11}")
for h in H:
    p=np.mean(agg[h]['pers']); s=np.mean(agg[h]['self']); b=np.mean(agg[h]['breath'])
    print(f"{h:>3} {p:>8.3f} {s:>8.3f} {b:>8.3f} {b-s:>+11.3f}")
print('records used', len(agg[1]['self']))
