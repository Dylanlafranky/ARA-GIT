import sys, numpy as np, wfdb
from wfdb import processing
from scipy.signal import welch

rec = sys.argv[1]
MIN = 40
fs = 250
N = MIN*60*fs

sig, fields = wfdb.rdsamp(rec, pn_dir='slpdb', sampto=N)
names = fields['sig_name']
def col(key):
    for i,n in enumerate(names):
        if key.lower() in n.lower(): return i
    return None
iecg = col('ECG'); ibp = col('BP'); ieeg = col('EEG'); iresp = col('Resp')
ecg = sig[:,iecg]
xqrs = processing.XQRS(sig=ecg, fs=fs)
xqrs.detect(verbose=False)
rp = np.array(xqrs.qrs_inds)
rr = np.diff(rp)/fs*1000.0
ok = (rr>300)&(rr<2000)
# per-beat samples at the beat's R-peak (use rp[1:] aligned with rr)
bt = rp[1:]
def winval(x, center, half):  # BACKWARD-only window (causal)
    a=max(0,center-2*half); b=center+1
    return x[a:b]
bp = sig[:,ibp]; eeg = sig[:,ieeg]; resp = sig[:,iresp]
bpv = np.array([winval(bp,c,fs//2).mean() for c in bt])
respv = np.array([winval(resp,c,fs).std() for c in bt])  # ventilation amplitude
# EEG band power per beat in +-2s window: delta(0.5-4) and beta(13-30)
delta=np.zeros(len(bt)); beta=np.zeros(len(bt))
half=2*fs
for j,c in enumerate(bt):
    seg=winval(eeg,c,half)
    if len(seg)<fs:
        delta[j]=np.nan; beta[j]=np.nan; continue
    f,P=welch(seg,fs=fs,nperseg=min(256,len(seg)))
    delta[j]=P[(f>=0.5)&(f<4)].sum()
    beta[j]=P[(f>=13)&(f<30)].sum()
m = ok & np.isfinite(delta) & np.isfinite(bpv)
np.save(f'/tmp/s_rr_{rec}.npy', rr[m])
np.save(f'/tmp/s_bp_{rec}.npy', bpv[m])
np.save(f'/tmp/s_resp_{rec}.npy', respv[m])
np.save(f'/tmp/s_delta_{rec}.npy', delta[m])
np.save(f'/tmp/s_beta_{rec}.npy', beta[m])
print(rec,'beats',m.sum(),'rr mean',round(rr[m].mean()),'bp range',round(bpv[m].min()),round(bpv[m].max()),'bp std',round(bpv[m].std(),1))
