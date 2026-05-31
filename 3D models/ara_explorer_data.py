"""Build the system table for the ARA Explorer 3D viewer.
Radius = scale (log10 period, seconds) mapped to a viewable shell; latitude = ARA (z=ARA-1);
node size scales with the system's scale (bigger/slower = larger). Writes ara_explorer_data.json."""
import numpy as np, json
LMIN,LMAX=-10.0,18.0; RMIN,RMAX=0.65,2.8
def R(logp): return round(RMIN+(logp-LMIN)/(LMAX-LMIN)*(RMAX-RMIN),3)
def size(logp): return round(0.045+0.075*(logp-LMIN)/(LMAX-LMIN),3)
def node(name,P,ara,dom,src,lon,note=""):
    lp=np.log10(P); r=R(lp); z=ara-1.0; th=np.arccos(max(-1,min(1,z))); rr=r*np.sin(th); lo=np.radians(lon)
    return {"name":name,"period_s":P,"log10P":round(lp,2),"ara":ara,"domain":dom,"source":src,
            "radius":r,"size":size(lp),"xyz":[round(rr*np.cos(lo),3),round(rr*np.sin(lo),3),round(r*z,3)],"note":note}
S=[
 node("Myocyte action potential",0.28,0.27,"heart","measured (HOW_TO)",10,"snap/consumer"),
 node("Heartbeat (ventricular pump)",0.83,1.60,"heart","measured (HOW_TO)",40,"engine, near phi"),
 node("Respiratory sinus arrhythmia",5.0,1.50,"heart","measured",70,"breath modulation"),
 node("Circadian HRV",86400,0.50,"heart","measured",100,"day/night consumer"),
 node("ENSO NINO 3.4",1.26e8,0.82,"climate","measured (mean)",200,"surface; matched pair w/ SOI"),
 node("ENSO SOI (Walker)",1.26e8,0.82,"climate","measured",210,"anti-phase partner of NINO"),
 node("WWV warm-water volume",1.26e8,1.00,"climate","measured",230,"subsurface recharge feeder"),
 node("PDO decadal",6.3e8,0.90,"climate","measured-ish",250,"slow modulation"),
 node("Solar Schwabe cycle",3.5e8,1.73,"solar","measured (flywheel)",300,"exothermic donor"),
 node("Golden star pulsation (RRc)",2.3e4,2.00,"stellar","ARA illustrative",330,"leanest recyclers; ARA approx"),
 node("Classical Cepheid pulsation",4.3e5,2.40,"stellar","ARA from Script98",345,"relaxation snap >2"),
]
shells=[{"log10P":l,"radius":R(l),"label":lab} for l,lab in
        [(-9,"ns"),(-6,"µs"),(-3,"ms"),(0,"s"),(3,"ks (~17min)"),(6,"Ms (~12d)"),(9,"Gs (~32yr)"),(12,"Ts (~32kyr)"),(15,"Ps"),(18,"Es")]]
out={"axis":"radius=log10 period (scale); latitude z=ARA-1 (0..2); longitude=spread; node size ~ scale",
     "ara_markers":{"balance":1.0,"phi":round((1+5**0.5)/2,4),"space_pole":2.0,"time_pole":0.0},
     "reference_shells_decade":shells,"systems":S,
     "note":"Octave rungs are x2 sub-steps between the decade reference shells (1 decade ~ 3.32 octaves). ARA values flagged by source; some illustrative."}
json.dump(out,open("ara_explorer_data.json","w"),indent=2)
print("systems:",len(S))
for s in S: print("  %-32s logP=%5.1f R=%.2f ara=%.2f size=%.3f  [%s]"%(s["name"],s["log10P"],s["radius"],s["ara"],s["size"],s["source"]))
print("wrote ara_explorer_data.json")
