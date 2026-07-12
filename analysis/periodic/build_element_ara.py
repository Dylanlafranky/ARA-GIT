"""Per-element multi-wave ARA breakdown. Real data (mendeleev). NO min-max/clamping:
each magnitude wave uses a smooth ANCHORED map ARA = 1 +/- tanh((x-ridge)/width) that
asymptotes toward but never reaches the 0/2 singularities (real systems approach, don't
sit on, the pole). Geometric/cycle waves keep their real endpoints. Math shown per wave."""
import json, math
from mendeleev.fetch import fetch_table, fetch_ionization_energies
df=fetch_table('elements').set_index('atomic_number')
ie=fetch_ionization_energies(degree=1)
ser={r['id']:(r['name'],r['color']) for r in fetch_table('series').to_dict('records')}
try: oxc=fetch_table('oxidationstates').groupby('atomic_number').size().to_dict()
except Exception: oxc={}
PSTART={1:1,2:3,3:11,4:19,5:37,6:55,7:87}; PLEN={1:2,2:8,3:8,4:18,5:18,6:32,7:32}
ANG={1:180,2:180,13:120,14:109.5,15:107,16:104.5,17:180,18:180}
HYB={180:"sp/linear",120:"sp2",109.5:"sp3",107:"pyramidal",104.5:"bent",90:"octahedral"}
def num(x):
    try:
        x=float(x); return x if math.isfinite(x) else None
    except: return None
def th(x,ridge,width,sign=+1):  # 1 +/- tanh; asymptotes (0,2), never reaches
    return round(1+sign*math.tanh((x-ridge)/width),3)
OUT=[]
for z in range(1,119):
    r=df.loc[z]
    en=num(r.get('en_pauling')); ar=num(r.get('atomic_radius')); eva=num(r.get('evaporation_heat'))
    IE1=num(ie['IE1'].get(z)); blk=r.get('block'); grp=r.get('group_id'); sid=r.get('series_id')
    cat,colr=ser.get(int(sid),("?","#888")) if sid==sid else ("?","#888")
    per=int(r.get('period')); rad=bool(r.get('is_radioactive')); nox=oxc.get(z,0)
    W={}
    # W1 give<->take : ridge = metalloid EN 2.0 (PHYSICAL), high EN -> acceptor(->2)
    if en is not None:
        a=th(en,2.0,1.2,+1); W["give_take"]={"ara":a,"raw":en,"unit":"EN","lo":"donor","hi":"acceptor",
          "arch":"donor" if a<0.85 else("acceptor" if a>1.15 else "balanced"),
          "math":"1+tanh((EN-2.0)/1.2)","anchor":"physical ridge: metalloid EN 2.0"}
    # W2 hold<->release : ridge = H IE 13.6 eV (reference atom), high IE -> hold(->0)
    if IE1 is not None:
        a=th(IE1,13.6,8.0,-1); W["hold_release"]={"ara":a,"raw":round(IE1,2),"unit":"eV","lo":"holds e-","hi":"releases e-",
          "arch":"holder" if a<0.85 else("releaser" if a>1.15 else "mid"),
          "math":"1-tanh((IE1-13.6)/8)","anchor":"reference ridge: H IE 13.6 eV (adjustable)"}
    # W3 bind<->free : ridge = 250 kJ/mol vaporise (reference), high -> bind(->0)
    if eva is not None:
        a=th(eva,250,180,-1); W["bind_free"]={"ara":a,"raw":round(eva,0),"unit":"kJ/mol","lo":"cohesive","hi":"volatile",
          "arch":"binder" if a<0.85 else("free" if a>1.15 else "mid"),
          "math":"1-tanh((Hvap-250)/180)","anchor":"reference ridge: 250 kJ/mol (adjustable)"}
    # W4 compress<->expand : ridge = 150 pm (reference), large -> expand(->2)
    if ar is not None:
        a=th(ar,150,55,+1); W["compress_expand"]={"ara":a,"raw":round(ar,0),"unit":"pm","lo":"compressed","hi":"expanded",
          "arch":"compressed" if a<0.85 else("expanded" if a>1.15 else "mid"),
          "math":"1+tanh((r-150)/55)","anchor":"reference ridge: 150 pm (adjustable)"}
    # W5 couple<->isolate : 0 oxistates = genuine isolation pole (noble); tanh(n/3)
    a=round(2*math.tanh(nox/3.0),3) if nox>0 else 0.0
    W["couple_isolate"]={"ara":a,"raw":nox,"unit":"oxi-states","lo":"isolate/noble","hi":"versatile",
      "arch":"isolate" if a<0.6 else("versatile" if a>1.2 else "mid"),
      "math":"2*tanh(n/3)  (n=0 -> genuine 0: no coupling)","anchor":"geometric (0 = real isolation pole)"}
    # W6 nuclear : binary for now (half-life grading TBD)
    W["nuclear"]={"ara":1.8 if rad else 0.2,"raw":"radioactive" if rad else "stable","lo":"stable","hi":"decays",
      "arch":"decayer" if rad else "stable","math":"binary 0.2/1.8","anchor":"binary (half-life refinement TBD)"}
    # W7 shell-fill phase : real cycle endpoints (start=release 0, noble=full 2)
    ps=PSTART[per]; pl=PLEN[per]; frac=(z-ps)/(pl-1) if pl>1 else 0; a=round(2*frac,3)
    W["shell_phase"]={"ara":a,"raw":round(frac,2),"lo":"period start","hi":"noble (full)",
      "arch":"early/released" if a<0.7 else("late/full" if a>1.3 else "mid-period"),
      "math":"2*(Z-Zstart)/(period_len-1)","anchor":"geometric (real cycle endpoints)"}
    # W8 bond geometry : Dylan's rule -> angle IS the ARA: 180deg=1.0 ridge, 360=2.0
    ang=ANG.get(int(grp),90) if grp==grp else 90
    a=round(ang/180.0,3)
    W["bond_geometry"]={"ara":a,"raw":ang,"unit":"deg","lo":"0deg","hi":"360deg (2.0)",
      "arch":HYB.get(ang,"octahedral"),"math":"angle/180  (180deg = 1.0 ridge)","anchor":"geometric (angle = ARA on the circle)"}
    OUT.append({"z":z,"sym":r.get('symbol'),"name":r.get('name'),"weight":num(r.get('atomic_weight')),"period":per,
      "group":(int(grp) if grp==grp else None),"block":blk,"category":cat,"color":colr,
      "econf":r.get('electronic_configuration'),"n_oxi":nox,"radioactive":rad,"rung":per,"waves":W})
json.dump(OUT,open("_elements_ara.json","w"))
n0=sum(1 for e in OUT for w in e['waves'].values() if w.get('ara') in (0,2,0.0,2.0))
print(f"built {len(OUT)} elements. exact-0-or-2 readings now: {n0} (only the geometric/genuine poles)")
for sym in ["Na","C","F","He","W","Au","U"]:
    e=next(x for x in OUT if x['sym']==sym)
    print(f"\n{e['sym']} {e['name']} (p{e['period']}, {e['category']})")
    for k,w in e['waves'].items():
        if 'ara' in w: print(f"   {k:16s} {w['ara']:>5}  [{w['arch']}]  {w['math']}")
