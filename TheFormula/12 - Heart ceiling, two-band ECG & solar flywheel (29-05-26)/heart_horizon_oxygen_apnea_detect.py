import wfdb, numpy as np, sys
from wfdb import processing
rec=sys.argv[1]; fs=100; N=fs*60*40
sig,f=wfdb.rdsamp(rec, pn_dir='apnea-ecg', sampto=N)
names=[n.strip() for n in f['sig_name']]
ecg=sig[:,names.index('ECG')]; spo2=sig[:,names.index('SpO2')]
xqrs=processing.XQRS(sig=ecg, fs=fs); xqrs.detect(verbose=False)
rp=np.array(xqrs.qrs_inds); rp=rp[(rp>0)&(rp<N)]
rr=np.diff(rp)/fs*1000.0; bt=rp[1:]
m=(rr>300)&(rr<2000); rr=rr[m]; bt=bt[m]
o2=spo2[bt]; ok=(o2>40)&(o2<=100); rr=rr[ok]; o2=o2[ok]
np.save(f'/tmp/rr_{rec}.npy',rr); np.save(f'/tmp/o2_{rec}.npy',o2)
print(rec,'beats',len(rr),'O2 std',round(o2.std(),1),'range',round(o2.min()),'-',round(o2.max()))
