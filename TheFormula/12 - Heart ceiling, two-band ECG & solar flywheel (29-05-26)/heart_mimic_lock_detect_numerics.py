import sys, numpy as np, wfdb
r=sys.argv[1]; WIN_MIN=30
nsig,nf = wfdb.rdsamp(f'{r}n', pn_dir=f'mimicdb/{r}')
nn=nf['sig_name']; fsn=nf['fs']
def ncol(k):
    for i,x in enumerate(nn):
        if k.lower()==x.lower(): return i
spo2=nsig[:,ncol('SpO2')].astype(float)
abpm=nsig[:,ncol('ABPmean')].astype(float)
w=int(WIN_MIN*60*fsn)
clean=np.where(np.isfinite(spo2)&(spo2>40)&(spo2<=100),spo2,np.nan)
best=None;bj=0
for j in range(0,len(clean)-w,int(60*fsn)):
    seg=clean[j:j+w]
    if np.isfinite(seg).sum()<0.7*w: continue
    m=np.nanmean(seg)
    if best is None or m<best: best=m;bj=j
t0=bj/fsn
np.save(f'/tmp/spo2full_{r}.npy',spo2); np.save(f'/tmp/abpfull_{r}.npy',abpm)
np.save(f'/tmp/meta_{r}.npy',np.array([t0,fsn,WIN_MIN]))
print(f"{r}: t0={t0/3600:.2f}h meanSpO2={best:.1f} fsn={fsn:.4f} rows={len(spo2)}")
