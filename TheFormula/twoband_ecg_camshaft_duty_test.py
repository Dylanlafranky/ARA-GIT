# Does the GOLD (slow) band's phase gate the GREEN (fast) band's amplitude?
# i.e. is green riding gold like a valve on a camshaft?
import numpy as np, wfdb, glob
from scipy.signal import welch, butter, sosfiltfilt, hilbert
PHI=(1+5**0.5)/2
base="/sessions/youthful-charming-wozniak/mnt/SystemFormulaFolder/normal-sinus-rhythm-rr-interval-database-1.0.0/"
def load(rec):
    ann=wfdb.rdann(rec,'ecg'); rr=np.diff(ann.sample)/ann.fs*1000.0
    return rr[(rr>300)&(rr<2000)]
def hp(x,Pc): return sosfiltfilt(butter(2,(1.0/Pc)/0.5,btype='high',output='sos'),x-x.mean())
def loud(x,b):
    f,P=welch(x,fs=1.0,nperseg=4096); per=np.divide(1.,f,out=np.full_like(f,np.inf),where=f>0)
    m=(per>=b[0])&(per<=b[1]); return per[m][np.argmax(P[m])]
def bf(x,P,frac=0.4):
    lo=(1/P)*(1-frac)/0.5; hi=min((1/P)*(1+frac)/0.5,0.99)
    return sosfiltfilt(butter(4,[lo,hi],btype='band',output='sos'),x)
NB=12; binsum=np.zeros(NB); bincnt=np.zeros(NB); cc=[]
recs=sorted(glob.glob(base+"nsr*.hea"))[:20]
for fp in recs:
    try:
        rr=load(fp[:-4]); spb=np.median(rr)/1000.0; x=hp(rr,60)
        g=loud(x,(1/0.40/spb,1/0.15/spb)); b=loud(x,(1/0.15/spb,1/0.04/spb))
        G=bf(x,g); B=bf(x,b)
        genv=np.abs(hilbert(G))               # green loudness
        bph=np.angle(hilbert(B))              # gold phase
        bamp=np.abs(hilbert(B))               # gold loudness
        # correlation of green loudness with gold loudness
        cc.append(np.corrcoef(genv,bamp)[0,1])
        # bin green loudness by gold phase
        idx=((bph+np.pi)/(2*np.pi)*NB).astype(int)%NB
        gz=(genv-genv.mean())/genv.std()
        for k in range(NB):
            m=idx==k; binsum[k]+=gz[m].sum(); bincnt[k]+=m.sum()
    except Exception as e: print("skip",e)
prof=binsum/bincnt
cc=np.array(cc)
print(f"N={len(cc)}")
print(f"corr(green loudness, gold loudness) = {cc.mean():+.3f} ± {cc.std():.3f}")
print(f"\ngreen loudness by gold phase (z-score, 12 bins over one gold cycle):")
for k in range(NB):
    ang=int((k+0.5)/NB*360)
    bar='#'*int((prof[k]+1.5)*10)
    print(f"  {ang:3d}deg  {prof[k]:+.3f} {bar}")
print(f"\nmodulation depth (max-min) = {prof.max()-prof.min():.3f} z   peak at {int((np.argmax(prof)+0.5)/NB*360)}deg, trough at {int((np.argmin(prof)+0.5)/NB*360)}deg")
