import sys, numpy as np, wfdb
from wfdb import processing
r=sys.argv[1]
t0,fsn,WIN_MIN=np.load(f'/tmp/meta_{r}.npy')
WIN_MIN=int(WIN_MIN)
fsw=125; sf=int(t0*fsw)
hh=wfdb.rdheader(r, pn_dir=f'mimicdb/{r}'); SL=hh.sig_len
st=min(sf+int(WIN_MIN*60*fsw), SL-1)
# find ECG channel index from header sig_name (segments share layout)
wn=hh.sig_name
if wn is None:
    # multiseg: read a segment header
    for s in hh.seg_name:
        if s=='~': continue
        wn=wfdb.rdheader(s,pn_dir=f'mimicdb/{r}').sig_name; break
ecgnames=['II','III','V','MCL1','I','aVF','aVL','aVR']
ie=None
for en in ecgnames:
    if en in wn: ie=wn.index(en); break
wsig,wf=wfdb.rdsamp(r,pn_dir=f'mimicdb/{r}',sampfrom=sf,sampto=st,channels=[ie])
ecg=wsig[:,0]; ecg=np.nan_to_num(ecg,nan=np.nanmean(ecg))
xq=processing.XQRS(sig=ecg,fs=fsw); xq.detect(verbose=False)
rp=np.array(xq.qrs_inds); rr=np.diff(rp)/fsw*1000.0; bt=rp[1:]/fsw
ok=(rr>300)&(rr<2000); rr=rr[ok]; bt=bt[ok]
spo2=np.load(f'/tmp/spo2full_{r}.npy'); abpm=np.load(f'/tmp/abpfull_{r}.npy')
tabs=t0+bt; ni=(tabs*fsn).astype(int)
def bwin(arr,idx,half):
    out=np.empty(len(idx))
    for k,c in enumerate(idx):
        a=max(0,c-2*half); b=min(len(arr),c+1)
        s=arr[a:b]; s=s[np.isfinite(s)&(s>0)]
        out[k]=s.mean() if len(s) else np.nan
    return out
spo2_b=bwin(spo2,ni,int(round(fsn*4))); abp_b=bwin(abpm,ni,int(round(fsn*4)))
np.save(f'/tmp/m_rr_{r}.npy',rr);np.save(f'/tmp/m_spo2_{r}.npy',spo2_b);np.save(f'/tmp/m_bp_{r}.npy',abp_b)
print(f"{r}: ECG={wn[ie]} beats={len(rr)} RRmean={rr.mean():.0f} spo2span={np.nanmax(spo2_b)-np.nanmin(spo2_b):.0f} bpspan={np.nanmax(abp_b)-np.nanmin(abp_b):.0f} valid spo2={np.isfinite(spo2_b).mean():.2f}")
