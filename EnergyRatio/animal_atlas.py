import numpy as np, json
# Representative published values (compiled, REAL allometry — not synthetic).
# mass_kg, heart_rate_bpm (resting; pace proxy for animals), lifespan_yr,
# cycle_s (fundamental clock: heartbeat for animals, division for cells, replication for virus),
# evo_rate (substitutions/site/year, order-of-magnitude literature), class, strategy
# evo_rate sources: RNA virus ~1e-3..1e-2; DNA virus ~1e-6; bacteria ~1e-8..1e-9/site/yr (fast gen);
# mammals/birds ~2e-9..5e-9; reptiles slower ~1e-9. (Order-of-magnitude; Duffy 2008, Bromham, Gillooly.)
R=[
# name, mass_kg, HR_bpm, lifespan_yr, cycle_s, evo_rate, klass, strategy
("Influenza(RNA virus)", 1e-19, None, None, 6*3600, 4e-3, "virus","burst"),
("HIV(RNA virus)",       1e-19, None, None, 24*3600, 5e-3, "virus","sustained"),
("Bacteriophage",        1e-19, None, None, 30*60,  2e-3, "virus","burst"),
("E.coli(bacterium)",    1e-15, None, None, 20*60,  5e-9, "microbe","sustained"),
("Yeast(cell)",          5e-14, None, None, 90*60,  3e-9, "microbe","sustained"),
("Human somatic cell",   3e-12, None, None, 24*3600,1e-9, "microbe","sustained"),
("Etruscan shrew",       0.002, 1000, 2.0,  60/1000, 4e-9,"mammal","sustained"),
("Hummingbird",          0.004, 1200, 4.0,  60/1200, 4e-9,"bird","burst"),
("Mouse",                0.02,  600,  3.0,  60/600,  4e-9,"mammal","sustained"),
("Rat",                  0.3,   350,  3.5,  60/350,  3.5e-9,"mammal","sustained"),
("Rabbit",               2.0,   200,  9.0,  60/200,  3e-9,"mammal","sustained"),
("Cat",                  4.0,   150,  15.0, 60/150,  3e-9,"mammal","burst"),
("Dog",                  20.0,  100,  13.0, 60/100,  3e-9,"mammal","sustained"),
("Human",                70.0,  60,   75.0, 60/60,   2e-9,"mammal","sustained"),
("Horse",                500.0, 40,   28.0, 60/40,   2e-9,"mammal","sustained"),
("Elephant",             5000.0,28,   65.0, 60/28,   1.5e-9,"mammal","sustained"),
("Blue whale",           1.2e5, 8,    85.0, 60/8,    1.2e-9,"mammal","sustained"),
("Green lizard",         0.05,  50,   8.0,  60/50,   1.2e-9,"reptile","burst"),
("Galapagos tortoise",   200.0, 12,   150.0,60/12,   1.0e-9,"reptile","sustained"),
("Crocodile",            400.0, 30,   70.0, 60/30,   1.0e-9,"reptile","burst"),
("Saltwater fish(tuna)", 200.0, 70,   15.0, 60/70,   1.5e-9,"fish","burst"),
]
names=[r[0] for r in R]; mass=np.array([r[1] for r in R]); cyc=np.array([r[4] for r in R])
evo=np.array([r[5] for r in R]); klass=[r[6] for r in R]; strat=[r[7] for r in R]
gen_yr_per=np.array([r[2] for r in R],dtype=object)  # lifespan, may be None

pace=1.0/cyc                      # TIME knob proxy: cycles per second (intrinsic clock speed)
lmass=np.log10(mass); lpace=np.log10(pace); levo=np.log10(evo)

print("=== cross-rung atlas (space-knob = log mass, time-knob = log pace) ===")
for r in R:
    print(f"{r[0]:22s} m={r[1]:.2e}kg  cycle={r[4]:8.1f}s  pace={1/r[4]:.3e}/s  evo={r[5]:.1e}  [{r[6]:7s}/{r[7]}]")

# --- correlations across the WHOLE span (virus->whale) ---
print("\n=== scaling (log-log, whole span) ===")
print(f"corr(log mass, log pace)      = {np.corrcoef(lmass,lpace)[0,1]:+.3f}   (expect strong NEG: big=slow)")
print(f"corr(log pace, log evo-rate)  = {np.corrcoef(lpace,levo)[0,1]:+.3f}   (Dylan: faster pace=faster adapt)")
print(f"corr(log mass, log evo-rate)  = {np.corrcoef(lmass,levo)[0,1]:+.3f}")
# slope mass->pace (animals only, where heartbeat is the clock)
am=[i for i,k in enumerate(klass) if k in ('mammal','bird')]
sm,b=np.polyfit(lmass[am],lpace[am],1)
print(f"\nMammal/bird heartbeat allometry: pace ~ mass^{sm:.3f}  (classic Kleiber = -0.25; framework wall=0.25)")
se,_=np.polyfit(lpace,levo,1)
print(f"adaptation slope: log evo ~ {se:.3f}*log pace")

# --- ecto vs endo separation on the pace axis (same mass band) ---
print("\n=== endotherm vs ectotherm (pace at given size) ===")
endo=[i for i,k in enumerate(klass) if k in('mammal','bird')]
ecto=[i for i,k in enumerate(klass) if k in('reptile','fish')]
# compare residual pace after removing mass trend
allan=endo+ecto
sl,ic=np.polyfit(lmass[allan],lpace[allan],1)
resid={i:lpace[i]-(sl*lmass[i]+ic) for i in allan}
print(f"  endo mean pace-residual = {np.mean([resid[i] for i in endo]):+.3f} (faster than size predicts?)")
print(f"  ecto mean pace-residual = {np.mean([resid[i] for i in ecto]):+.3f}")

json.dump([{"name":r[0],"mass":r[1],"cycle_s":r[4],"pace":1/r[4],"evo":r[5],"class":r[6],"strategy":r[7],
            "log_mass":float(np.log10(r[1])),"log_pace":float(np.log10(1/r[4])),"log_evo":float(np.log10(r[5]))}
           for r in R], open("/tmp/animal_atlas.json","w"),indent=1)
print("\n-> /tmp/animal_atlas.json")
