import wfdb, numpy as np
rec='a01er'; fs=100; N=fs*60*45
sig,f=wfdb.rdsamp(rec, pn_dir='apnea-ecg', sampto=N)
names=[n.strip() for n in f['sig_name']]
print('channels',names)
airflow=sig[:,names.index('Resp N')]   # nasal airflow
bt=np.load('/tmp/apn_bt.npy')
rr=np.load('/tmp/rr_a01er.npy'); o2=np.load('/tmp/o2_a01er.npy')
# ventilation envelope per beat: RMS of airflow in +-1s window
w=fs
vent=np.zeros(len(bt))
for i,b in enumerate(bt):
    a=max(0,b-w); z=min(len(airflow),b+w)
    seg=airflow[a:z]; vent[i]=np.sqrt(np.mean((seg-seg.mean())**2))
# align lengths to rr/o2 (apn1 filtered o2 ok mask AFTER bt; rr/o2 already filtered, bt was pre-filter)
# rebuild: apn1 saved bt BEFORE the o2 ok-mask trim. trim vent same way:
spo2_at_bt=None
# Safer: recompute o2-at-bt and ok mask exactly like apn1
m=len(rr)
print('len rr',len(rr),'len o2',len(o2),'len bt',len(bt),'len vent',len(vent))

# CO2 proxy = leaky integral of ventilation deficit
base=np.percentile(vent,75)
deficit=np.maximum(0, base-vent)
co2=np.zeros(len(vent)); leak=0.97
for i in range(1,len(co2)): co2[i]=leak*co2[i-1]+deficit[i]
co2=(co2-co2.mean())/co2.std()
print('corr(O2, CO2-proxy) =', round(np.corrcoef(o2,co2)[0,1],3),'(want negative = anti-wave)')

# forecast test: RR self vs +O2 vs +O2+CO2 pair
n=len(rr); half=n//2; ww=15
slope=np.zeros(n)
for i in range(ww,n): slope[i]=o2[i]-o2[i-ww]
cslope=np.zeros(n)
for i in range(ww,n): cslope[i]=co2[i]-co2[i-ww]
def fc(a,b): return np.corrcoef(a,b)[0,1]
print(f"{'h':>4}{'~min':>6}{'self':>8}{'+O2':>8}{'+O2+CO2':>9}{'pair adds':>10}")
for h in [12,20,40,60,90,120]:
    tr=np.arange(ww,half-h); ytr=rr[tr+h]; idx=np.arange(half,n-h); y=rr[idx+h]
    def fit(cols):
        Xt=np.c_[tuple([np.ones(len(tr))]+[c[tr] for c in cols])]
        cc=np.linalg.lstsq(Xt,ytr,rcond=None)[0]
        Xe=np.c_[tuple([np.ones(len(idx))]+[c[idx] for c in cols])]
        return fc(Xe@cc,y)
    s=fit([rr]); o=fit([rr,o2,slope]); p=fit([rr,o2,slope,co2,cslope])
    print(f"{h:>4}{h/67:>6.1f}{s:>8.3f}{o:>8.3f}{p:>9.3f}{p-o:>+10.3f}")
