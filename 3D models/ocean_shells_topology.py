"""
Ocean layer on the base ARA topology — rungs as nested octave shells.
Closed resonant pairs share a shell (anti-phase, 180 deg apart); open feeders link across shells.
Illustrative ENSO wiring from systems we know: NINO<->SOI matched-rung anti-phase (confirmed),
WWV subsurface recharge feeder (confirmed driver-below), PDO slow modulation (overflow).
Writes ocean_shells_topology.json for the 3D viewer.  ARA on z: ARA = z+1 (0..2), equator=1.0.
"""
import numpy as np, json
phi=(1+5**0.5)/2
def xyz(R, ara, lon_deg):
    z=ara-1.0; th=np.arccos(max(-1,min(1,z))); r2=R*np.sin(th); lon=np.radians(lon_deg)
    return [round(r2*np.cos(lon),4), round(r2*np.sin(lon),4), round(R*z,4)]
# shells: rung index -> visual radius (linear in rung = octave in reality). pump = rung 0.
shells=[
 {"rung":-1,"radius":0.80,"label":"WWV subsurface (faster recharge battery)"},
 {"rung": 0,"radius":1.20,"label":"ENSO pump shell (NINO / SOI)"},
 {"rung":+1,"radius":1.70,"label":"PDO slow modulation"},
]
Rp={s["rung"]:s["radius"] for s in shells}
nodes=[
 {"id":"NINO","label":"NINO 3.4 (surface temp)","rung":0,"ara":0.82,"lon":0,  "xyz":xyz(Rp[0],0.82,0)},
 {"id":"SOI", "label":"SOI (Walker / atmosphere)","rung":0,"ara":0.82,"lon":180,"xyz":xyz(Rp[0],0.82,180)},
 {"id":"WWV", "label":"WWV (subsurface warm water)","rung":-1,"ara":1.00,"lon":90,"xyz":xyz(Rp[-1],1.00,90)},
 {"id":"PDO", "label":"PDO (decadal modulation)","rung":1,"ara":0.90,"lon":45, "xyz":xyz(Rp[1],0.90,45)},
]
couplings=[
 {"from":"NINO","to":"SOI","kind":"closed-resonant","type":"matched-rung anti-phase","note":"same shell, 180 deg apart; Walker circulation; CONFIRMED |corr|~0.72"},
 {"from":"WWV","to":"NINO","kind":"open-feeder","type":"handoff (driver-below)","note":"subsurface recharge leads surface ~quarter cycle; CONFIRMED lift"},
 {"from":"PDO","to":"NINO","kind":"open-feeder","type":"overflow (slow modulation)","note":"decadal background sets the rate; matched-rung at phi^10"},
]
out={"ara_axis":"z; ARA=z+1; equator(z=0)=1.0 balance; phi at z=0.618; span 0..2",
     "shell_spacing":"linear in rung index = octave (x2) in real period",
     "shells":shells,"nodes":nodes,"couplings":couplings,
     "legend":{"closed-resonant":"two nodes, same shell, anti-phase (matched-rung pair)",
               "open-feeder":"node linked across shells (handoff / overflow / driver-below)"},
     "notes":"Illustrative ENSO wiring on the nested-shell ocean layer; structure (closed pairs on a shell, open feeders across shells) is the framework claim; ARA values approximate. Sits around the base two-octave-sphere core (base_ara_topology.json)."}
json.dump(out,open("ocean_shells_topology.json","w"),indent=2)
print("shells:");[print("  rung %+d  R=%.2f  %s"%(s["rung"],s["radius"],s["label"])) for s in shells]
print("nodes:");[print("  %-5s ara=%.2f lon=%3d  xyz=%s"%(n["id"],n["ara"],n["lon"],n["xyz"])) for n in nodes]
print("couplings:");[print("  %-5s -> %-5s  %-15s %s"%(c["from"],c["to"],c["kind"],c["type"])) for c in couplings]
print("\nwrote ocean_shells_topology.json")
