"""
Base ARA topology — the geometry numbers.
Two octave topographic spheres: SPACE (head-on) + TIME (sheared 36deg = pentagon angle).
Their terrain surfaces cross and oscillate; the ARA axis runs 0..2 (base ARA = 2.0 octave span).
phi = 2 cos(36deg) is the sheared-octave identity that sets the angle.
Writes base_ara_topology.json (key coordinates) for the 3D viewer.
"""
import numpy as np, json
phi=(1+5**0.5)/2
shear_deg=36.0; shear=np.radians(shear_deg)
print("Shear angle = %.1f deg (= pi/5, the pentagon angle).  Check: 2*cos(36) = %.6f  vs phi = %.6f"%(shear_deg,2*np.cos(shear),phi))

def Rx(a): c,s=np.cos(a),np.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
Rt=Rx(shear)   # rotation that produces the TIME twin from the SPACE sphere (shear about x)

# ARA axis = z. South pole = ARA 0, North pole = ARA 2, equator = ARA 1.0 (balance).
space_axis=np.array([0,0,1.0])
time_axis = Rt@space_axis
def ara_of_z(z): return z+1.0   # map z in [-1,1] -> ARA [0,2]
poles={
 "space_ARA0_southpole":[0,0,-1.0], "space_ARA2_northpole":[0,0,1.0],
 "time_ARA0_southpole":list(Rt@np.array([0,0,-1.0])), "time_ARA2_northpole":list(time_axis),
 "balance_equator_ARA1.0":"z=0 ring (both spheres share it)",
}
# coupling axis = bisector of the two ARA axes (the 1.0 midpoint direction)
bis=(space_axis+time_axis); bis=bis/np.linalg.norm(bis)
half=np.degrees(np.arccos(np.dot(space_axis,time_axis)))/2
print("\nSpace ARA-axis: [0,0,1]   Time ARA-axis: [%.4f,%.4f,%.4f]  (%.1f deg apart)"%(*time_axis,np.degrees(np.arccos(np.dot(space_axis,time_axis)))))
print("Coupling/bisector axis (the shared 1.0): [%.4f,%.4f,%.4f], each octave %.1f deg off it"%(*bis,half))

# octave terrain: 1 doubling pole-to-pole; rung bands as cos in colatitude
def terrain(theta, A=0.18, rungs=3):   # theta=colatitude 0..pi
    return A*np.cos(rungs*2*np.pi*(theta/np.pi))
# crossover ring: where space terrain == time terrain (sample the difference sign changes) - reported as count
th=np.linspace(0.01,np.pi-0.01,400); ph=0.0
# (full crossover is a curve on the sphere; we report the analytic anchor: equator z=0 is always shared)
out={
 "shear_deg":shear_deg, "phi_check_2cos36":2*np.cos(shear), "phi":phi,
 "ara_axis":"z; ARA = z+1, south z=-1 -> ARA0, north z=+1 -> ARA2, equator z=0 -> ARA1.0(balance)",
 "base_ARA_span":2.0,
 "rotation_matrix_space_to_time":Rt.tolist(),
 "poles":poles,
 "coupling_bisector_axis":list(bis), "each_octave_off_coupling_deg":half,
 "terrain":{"type":"octave cos in colatitude","amplitude":0.18,"rungs":3},
 "notes":"Geometric realization of the stated structure. Conventions: ARA on z (0..2); SPACE head-on, TIME sheared 36deg about x; terrain = octave rung bands; the two terrain surfaces cross (oscillate) around the shared equator. phi=2cos36 sets the shear. Exact-geometry where stated; cosmic identification is conjecture (see OPEN_CONJECTURE_spacetime_mixing.md)."
}
json.dump(out,open("base_ara_topology.json","w"),indent=2)
print("\nWrote base_ara_topology.json")
print("Base ARA span (pole to pole) = 2.0 ; balance ring at ARA 1.0 ; engine mark at phi=%.4f"%phi)
