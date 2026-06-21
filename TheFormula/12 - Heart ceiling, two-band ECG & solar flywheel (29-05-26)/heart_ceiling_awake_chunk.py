import sys, numpy as np, wfdb
from wfdb import processing
r=sys.argv[1]; ci=int(sys.argv[2]); CMIN=40; fs=250
sf=ci*CMIN*60*fs; st=sf+CMIN*60*fs
h=wfdb.rdheader(r,pn_dir='fantasia'); SL=h.sig_len
if sf>=SL-fs:
    print(f"{r} chunk {ci}: past end (SL={SL})"); sys.exit()
st=min(st,SL-1)
sig,f=wfdb.rdsamp(r,pn_dir='fantasia',sampfrom=sf,sampto=st)
names=f['sig_name']; print("sigs:",names)
def col(k):
    for i,n in enumerate(names):
        if k.lower() in n.lower(): return i
iecg=col('ECG'); iresp=col('Resp')
ecg=np.nan_to_num(sig[:,iecg])
rp=processing.gqrs_detect(sig=ecg,fs=fs); rr=np.diff(rp)/fs*1000.0; btl=rp[1:]
ok=(rr>300)&(rr<2000); rr=rr[ok]; btl=btl[ok]
def bwin(x,c,half,fn):
    a=max(0,c-2*half); b=c+1; s=x[a:b]; s=s[np.isfinite(s)]
    return fn(s) if len(s) else np.nan
resp=sig[:,iresp] if iresp is not None else None
respv=np.array([bwin(resp,c,fs,np.std) for c in btl]) if resp is not None else np.full(len(btl),np.nan)
np.savez(f'/tmp/FA_{r}_{ci}.npz',rr=rr,resp=respv,bt=btl+sf)
print(f"{r} ch{ci}: {len(rr)} beats, SL={SL}")
