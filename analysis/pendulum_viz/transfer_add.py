import os,sys,json,numpy as np,scipy.io as sio
from scipy.signal import welch,csd,coherence
HERE=os.path.dirname(os.path.abspath(__file__)); SCR=os.path.join(HERE,"..","pendulum_scripts")
sys.path.insert(0,SCR); from pendulum_common import rest_centered
DATA=os.path.join(SCR,"data")
def r(a,p=4): a=np.asarray(a,float); return [round(float(x),p) for x in a]

GRID=np.linspace(0.4,4.0,80)   # f / f0
def step(x,y,fs):
    NP=int(fs*16)
    f,Pxx=welch(x,fs,nperseg=NP); _,Pxy=csd(x,y,fs,nperseg=NP); _,coh=coherence(y,x,fs,nperseg=NP)
    H=Pxy/Pxx
    fp,Pp=welch(x,fs,nperseg=len(x)//8); fp,Pp=fp[1:],Pp[1:]; f0=fp[np.argmax(Pp)]
    xn=f/f0
    re=np.interp(GRID,xn,H.real); im=np.interp(GRID,xn,H.imag); co=np.interp(GRID,xn,coh)
    g=np.abs(re+1j*im); ph=np.degrees(np.angle(re+1j*im))
    def at(mult):
        i=np.argmin(np.abs(GRID-mult)); return g[i],ph[i],co[i]
    return dict(gain=r(g,4),phase=r(ph,1),coh=r(co,3),f0=round(float(f0),3),
                h1=[round(float(v),3) for v in at(1)],h2=[round(float(v),3) for v in at(2)],h3=[round(float(v),3) for v in at(3)])

# cart->arm1 from single (ground truth)
m=sio.loadmat(os.path.join(DATA,"SingleDataWithControl_1_Dt_0_0001.mat"),struct_as_record=False,squeeze_me=True)
def sig(n): return np.asarray(m[n].signals.values,float).ravel()
q=100; fss=10000/q
cart=sig("Distance")[::q]; a1=sig("Theta1")[::q]; cart=cart-cart.mean(); a1=a1-np.mean(a1)
T_cart=step(cart,a1,fss)
# triple chain steps
mt=sio.loadmat(os.path.join(DATA,"TripleDataWithControl_1_Dt_0_0001.mat"))
qt=100; fst=(1/float(np.asarray(mt['dt']).ravel()[0]))/qt
th={i:mt[f'Theta{i}'].ravel()[::qt] for i in (1,2,3)}; th=rest_centered(th)
for i in (1,2,3): th[i]=th[i]-th[i].mean()
T12=step(th[1],th[2],fst); T23=step(th[2],th[3],fst)

D=json.load(open(os.path.join(HERE,"_driven_data.json")))
D["transfer"]={"grid":r(GRID,3),"cart_arm1":T_cart,"arm1_arm2":T12,"arm2_arm3":T23}
json.dump(D,open(os.path.join(HERE,"_driven_data.json"),"w"))
print("transfer added. fundamentals:",T_cart["f0"],T12["f0"],T23["f0"])
print("gain@f0:",T_cart["h1"][0],T12["h1"][0],T23["h1"][0])
print("phase@f0:",T_cart["h1"][1],T12["h1"][1],T23["h1"][1])
print("phase@2f0:",T_cart["h2"][1],T12["h2"][1],T23["h2"][1])
