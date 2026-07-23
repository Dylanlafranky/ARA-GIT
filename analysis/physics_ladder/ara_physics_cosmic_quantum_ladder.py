"""Build the ARA physics traversal from solar spacetime to quantum hydrogen.

This is a synthesis/reconstruction artifact.  It does not claim that general
relativity literally reduces to quantum mechanics in one derivation.  Every
edge is typed as an exact limit, reformulation, theorem consequence, sibling
mathematical bridge, field consequence, or quantisation/model transition.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent

AU_M = 149_597_870_700.0
SATELLITE_R_M = 7_000_000.0
BOHR_RADIUS_M = 5.291_772_105_44e-11


LAW_ROWS = [
    {
        "order": 1,
        "law": "Einstein field equation and covariant conservation",
        "ara_math": (
            "Directed relation appearance: Phase A/source = T_mu_nu; relation J = "
            "8*pi*G/c^4; Phase B/response = G_mu_nu + Lambda*g_mu_nu. "
            "The exact balance spine is nabla_mu T^{mu nu}=0. No unique 0-2 "
            "opposition coordinate is assigned."
        ),
        "physics_equation": (
            "G_mu_nu + Lambda*g_mu_nu = (8*pi*G/c^4) T_mu_nu; "
            "nabla_mu T^{mu nu}=0."
        ),
        "bridge_role": "Cosmic parent/source geometry",
        "map_type": "established law plus directed ARA relation",
        "status": "E0 equation; E1 continuity skeleton; A1 source/response reading",
    },
    {
        "order": 2,
        "law": "Einstein weak-field limit to Poisson and Newton",
        "ara_math": (
            "Rung compression: metric g_mu_nu -> potential Phi -> field "
            "g=-grad(Phi) -> matter acceleration. On a declared force axis, "
            "x_F=2F_B/(F_A+F_B) and F_net=(F_A+F_B)(x_F-1)."
        ),
        "physics_equation": (
            "g_00 approximately -(1+2Phi/c^2); nabla^2 Phi=4*pi*G*rho; "
            "g=-grad(Phi); m*r_ddot=m*g."
        ),
        "bridge_role": "Exact weak-field rung crossing",
        "map_type": "exact established limit under declared assumptions",
        "status": "E0 limit; E1 exact force-coordinate reparameterisation",
    },
    {
        "order": 3,
        "law": "Newton I, II and III",
        "ara_math": (
            "Newton II reads the signed distance from the force ridge: "
            "m*a_parallel=Sigma_F(x_F-1). Newton III gives an active parent "
            "ridge x_pair=1 for equal nonzero anti-directed internal forces. "
            "Newton I also allows the distinct null case Sigma_F=0."
        ),
        "physics_equation": (
            "F_net=dp/dt; for constant mass F_net=m*a; "
            "F_A<-B=-F_B<-A; F_net=0 implies p=constant."
        ),
        "bridge_role": "Directed pair, residual and enclosing parent",
        "map_type": "exact law and exact bounded force coordinate",
        "status": "E0 laws; E1 exact declared ARA residual identity",
    },
    {
        "order": 4,
        "law": "Hamilton equations and energy allocation",
        "ara_math": (
            "For a two-account Hamiltonian, t_V=2V/H and t_K=2K/H, so "
            "t_V+t_K=2 and x_H=t_K. The harmonic oscillator traverses "
            "0 -> 1 -> 2 -> 1 -> 0 while signed (Q,P) retains four quadrants."
        ),
        "physics_equation": (
            "H(q,p)=K(p)+V(q); q_dot=partial H/partial p; "
            "p_dot=-partial H/partial q. Harmonic case: Q^2+P^2=2H."
        ),
        "bridge_role": "Canonical reformulation and full cycle",
        "map_type": "exact reformulation for the declared Hamiltonian system",
        "status": "E0 Hamilton mechanics; E1 exact oscillator ARA crosswalk",
    },
    {
        "order": 5,
        "law": "Noether theorem",
        "ara_math": (
            "The state/allocation may move while a parent physical invariant "
            "remains fixed. TE-ARA closure sum(t_c)=2 is normalization; "
            "dQ_physical/dt=0 is the separate Noether conservation statement."
        ),
        "physics_equation": (
            "time translation -> dH/dt=0; spatial translation -> dp/dt=0; "
            "rotation -> dL/dt=0."
        ),
        "bridge_role": "Symmetry selects the conserved parent account",
        "map_type": "exact theorem consequence, not a diameter value",
        "status": "E0 theorem; E1 invariant-versus-normalisation distinction",
    },
    {
        "order": 6,
        "law": "Virial theorem",
        "ara_math": (
            "For inverse-distance binding, declare C=|<V>| and R=2<T>. "
            "Then x_vir=2R/(C+R)=1. The raw TE-ARA energy allocation remains "
            "t_T=2/3 and t_C=4/3, totaling 2."
        ),
        "physics_equation": (
            "2<T>=<r dot grad V>; for V proportional to -1/r, "
            "2<T>=|<V>|."
        ),
        "bridge_role": "Completed bound-cycle weighted ridge",
        "map_type": "exact theorem plus exact declared coordinate",
        "status": "E0 theorem; E1 exact 21.45-order cross-scale crosswalk",
    },
    {
        "order": 7,
        "law": "Gauss electric law",
        "ara_math": (
            "With x_Q=2Q_+/(Q_++Q_-) and T_Q=Q_++Q_-, "
            "Q_net=T_Q(x_Q-1). The 1.0 point is equal signed-source "
            "cancellation while T_Q retains activity."
        ),
        "physics_equation": (
            "closed-surface integral E dot dA = Q_inside/epsilon_0; "
            "differential form div E=rho/epsilon_0."
        ),
        "bridge_role": "Enclosed source to boundary flux",
        "map_type": "exact law and exact signed-pair embedding",
        "status": "E0 law; E1 exact ARA source-composition identity",
    },
    {
        "order": 8,
        "law": "Gauss magnetic law",
        "ara_math": (
            "Split nonzero closed-boundary activity into outward and inward "
            "flux magnitudes. x_B=2Phi_out/(Phi_out+Phi_in)=1 because net "
            "magnetic flux is zero. Empty activity leaves x_B undefined."
        ),
        "physics_equation": "closed-surface integral B dot dA=0; differential form div B=0.",
        "bridge_role": "Active closed-boundary ridge",
        "map_type": "exact law and exact active-flux coordinate",
        "status": "E0 law; E1 exact ridge when unsigned flux is nonzero",
    },
    {
        "order": 9,
        "law": "Faraday induction",
        "ara_math": (
            "The useful ARA object is the four-quadrant trajectory "
            "(Phi_B, dPhi_B/dt), not a forced static ridge. Phi_B=0 is the "
            "orientation crossing; dPhi_B/dt=0 is the accumulation/release turn."
        ),
        "physics_equation": (
            "closed-loop integral E dot dl = -dPhi_B/dt; "
            "curl E=-partial B/partial t."
        ),
        "bridge_role": "Changing flux to circulating response",
        "map_type": "exact differential/integral law plus phase-plane reading",
        "status": "E0 law; E1 exact four-quadrant sinusoidal crosswalk",
    },
    {
        "order": 10,
        "law": "Ampere-Maxwell law",
        "ara_math": (
            "Declare conduction C=|J| and displacement D=|epsilon*dE/dt|. "
            "x_D/C=2D/(C+D): 0 conduction-dominant, 1 equal participation, "
            "2 displacement-dominant. Signed vector phase remains required."
        ),
        "physics_equation": (
            "curl B=mu_0 J + mu_0 epsilon_0 partial E/partial t."
        ),
        "bridge_role": "Matter-current and field-change handover",
        "map_type": "exact law plus declared source-participation coordinate",
        "status": "E0 law; E1 bounded composition; vector closure retained",
    },
    {
        "order": 11,
        "law": "Poynting theorem and Maxwell plane-wave relation",
        "ara_math": (
            "Energy account: x_P=2P_out/(P_in+P_out), with x_P=1 an active "
            "equal-throughput ridge. For a vacuum plane wave, "
            "x_E/B=2u_B/(u_E+u_B)=1 and S=(1/mu_0) E cross B is the "
            "oriented relational third."
        ),
        "physics_equation": (
            "partial_t u_EM + div S = -J dot E; "
            "S=(1/mu_0) E cross B; u_E=u_B for a vacuum plane wave."
        ),
        "bridge_role": "Field storage, boundary flow and oriented relation",
        "map_type": "exact conservation law and exact plane-wave crosswalk",
        "status": "E0 laws; E1 exact declared energy/throughput coordinates",
    },
    {
        "order": 12,
        "law": "Lorentz force and electromagnetic momentum balance",
        "ara_math": (
            "Particle channel coordinate x_L=2|q v cross B|/(|qE|+|q v cross B|) "
            "must retain both directions and their angle. At parent scale, "
            "div T = partial_t g_EM + f_matter is a three-term conservation lock."
        ),
        "physics_equation": (
            "F=q(E+v cross B); f_matter=rho E+J cross B; "
            "div T=partial_t(epsilon_0 E cross B)+f_matter."
        ),
        "bridge_role": "Field-to-matter handover",
        "map_type": "exact force decomposition and momentum continuity",
        "status": "E0 laws; E1 exact channel reconstruction; simple rung-up law failed",
    },
    {
        "order": 13,
        "law": "Schrodinger equation and probability continuity",
        "ara_math": (
            "Quantum evolution preserves the same accumulation/release skeleton: "
            "partial_t rho + div j=0. For a declared two-outcome projection, "
            "x_Q=2p_B=1-r dot n spans 0 to 2; 1 means equal outcome probability, "
            "not automatically incoherence or stillness."
        ),
        "physics_equation": (
            "i*hbar partial_t psi=H psi; rho=|psi|^2; "
            "partial_t rho+div j=0; p_B=(1-r dot n)/2."
        ),
        "bridge_role": "Quantum state evolution and conserved probability",
        "map_type": "established quantum law plus exact two-level coordinate",
        "status": "E0 quantum mechanics; E1 exact Bloch-diameter crosswalk",
    },
    {
        "order": 14,
        "law": "Quantum hydrogen and two-level handover",
        "ara_math": (
            "Hydrogen closes the path with H=T+V_Coulomb and the quantum virial "
            "ridge 2<T>=|<V>|. A selected pair of hydrogen levels may then be "
            "represented on a Bloch diameter; driven avoided crossing uses "
            "x_path=1+vt/sqrt((vt)^2+4g^2)."
        ),
        "physics_equation": (
            "H=-(hbar^2/2mu) nabla^2 - k_e e^2/r; H psi=E psi; "
            "2<T>=|<V>|. Two-level model: H_2=(vt/2)sigma_z+g sigma_x."
        ),
        "bridge_role": "Atomic bound identity and optional two-level projection",
        "map_type": "established quantum model plus exact declared coordinates",
        "status": "E0 model; E1 virial/Bloch/Landau-Zener crosswalks",
    },
]


LANDMARK_ROWS = [
    {
        "order": 1,
        "law": "Einstein field equation",
        "pole_0": "stress-energy source T_mu_nu",
        "ridge_1": "coupling/conservation relation",
        "pole_2": "curvature response G_mu_nu",
        "reading_kind": "directed source-response map; no numerical ridge claimed",
    },
    {
        "order": 2,
        "law": "Newton force axis",
        "pole_0": "Phase-A-directed force",
        "ridge_1": "equal nonzero opposing forces",
        "pole_2": "Phase-B-directed force",
        "reading_kind": "bounded signed resultant coordinate",
    },
    {
        "order": 3,
        "law": "Hamilton energy allocation",
        "pole_0": "all potential/configuration",
        "ridge_1": "K=V",
        "pole_2": "all kinetic/traversal",
        "reading_kind": "full 0-2 cycle; quadrant needed for direction",
    },
    {
        "order": 4,
        "law": "Virial theorem",
        "pole_0": "binding/Connection C",
        "ridge_1": "2<T>=|<V>|",
        "pole_2": "weighted Traversal R",
        "reading_kind": "exact weighted ridge for inverse-distance binding",
    },
    {
        "order": 5,
        "law": "Gauss electric",
        "pole_0": "negative charge magnitude",
        "ridge_1": "equal positive/negative source",
        "pole_2": "positive charge magnitude",
        "reading_kind": "signed source composition",
    },
    {
        "order": 6,
        "law": "Gauss magnetic",
        "pole_0": "inward boundary flux",
        "ridge_1": "equal inward/outward flux",
        "pole_2": "outward boundary flux",
        "reading_kind": "active closed-boundary ridge if flux activity is nonzero",
    },
    {
        "order": 7,
        "law": "Faraday induction",
        "pole_0": "one signed magnetic-flux lobe",
        "ridge_1": "axis-dependent crossing/turn",
        "pole_2": "opposite signed flux lobe",
        "reading_kind": "four-quadrant phase-plane cycle, not one static scalar",
    },
    {
        "order": 8,
        "law": "Ampere-Maxwell",
        "pole_0": "conduction current",
        "ridge_1": "equal conduction/displacement magnitude",
        "pole_2": "displacement current",
        "reading_kind": "source participation; retain vector phase",
    },
    {
        "order": 9,
        "law": "Poynting energy account",
        "pole_0": "input/field accumulation",
        "ridge_1": "equal input/output throughput",
        "pole_2": "output/field release",
        "reading_kind": "local energy-flow composition",
    },
    {
        "order": 10,
        "law": "Vacuum Maxwell wave",
        "pole_0": "electric energy",
        "ridge_1": "u_E=u_B; active propagation",
        "pole_2": "magnetic energy",
        "reading_kind": "equal E/B energy with perpendicular relation S",
    },
    {
        "order": 11,
        "law": "Lorentz force",
        "pole_0": "electric force channel",
        "ridge_1": "equal channel magnitudes",
        "pole_2": "magnetic force channel",
        "reading_kind": "composition only; angle/direction remains part of state",
    },
    {
        "order": 12,
        "law": "Quantum Bloch diameter",
        "pole_0": "outcome/state A",
        "ridge_1": "equal A/B probability",
        "pole_2": "outcome/state B",
        "reading_kind": "exact measurement-axis projection",
    },
    {
        "order": 13,
        "law": "Landau-Zener handover",
        "pole_0": "bare state A",
        "ridge_1": "equal instantaneous bare-state mixing",
        "pole_2": "bare state B",
        "reading_kind": "continuous avoided-crossing path",
    },
    {
        "order": 14,
        "law": "Quantum hydrogen virial",
        "pole_0": "Coulomb binding magnitude",
        "ridge_1": "2<T>=|<V>|",
        "pole_2": "weighted kinetic traversal",
        "reading_kind": "expectation-value ridge, not a classical electron orbit",
    },
]


TRAVERSAL_ROWS = [
    {
        "step": 1,
        "stage": "Solar spacetime",
        "ladder_level": 8,
        "physics": "Einstein field equation",
        "transition_in": "starting parent description",
        "edge_class": "established theory",
        "example": "Sun exterior",
    },
    {
        "step": 2,
        "stage": "Weak solar field",
        "ladder_level": 7,
        "physics": "Poisson equation and Newton gravity",
        "transition_in": "weak-field, stationary, slow-motion limit",
        "edge_class": "exact limit",
        "example": "Sun-Earth field",
    },
    {
        "step": 3,
        "stage": "Orbital dynamics",
        "ladder_level": 6,
        "physics": "Newton plus Hamilton",
        "transition_in": "canonical reformulation",
        "edge_class": "exact reformulation",
        "example": "Sun-Earth orbit",
    },
    {
        "step": 4,
        "stage": "Invariant and cycle accounts",
        "ladder_level": 5,
        "physics": "Noether plus virial theorem",
        "transition_in": "symmetry consequence and cycle average",
        "edge_class": "exact theorem consequence",
        "example": "conserved orbital quantities and mean energies",
    },
    {
        "step": 5,
        "stage": "Inverse-square sibling",
        "ladder_level": 4,
        "physics": "gravity 1/r potential compared with Coulomb 1/r potential",
        "transition_in": "same mathematical family, different physical interaction",
        "edge_class": "sibling bridge, not derivation",
        "example": "mass source compared with charge source",
    },
    {
        "step": 6,
        "stage": "Electromagnetic field",
        "ladder_level": 3,
        "physics": "Gauss, Faraday and Ampere-Maxwell",
        "transition_in": "field equations and their differential consequences",
        "edge_class": "established field closure",
        "example": "electron-proton Coulomb field and changing fields",
    },
    {
        "step": 7,
        "stage": "Matter-field handover",
        "ladder_level": 2,
        "physics": "Poynting theorem and Lorentz force",
        "transition_in": "energy-momentum conservation",
        "edge_class": "exact conservation consequence",
        "example": "charged matter interacting with E and B",
    },
    {
        "step": 8,
        "stage": "Quantum dynamics",
        "ladder_level": 1,
        "physics": "Schrodinger equation and probability continuity",
        "transition_in": "quantum Hamiltonian model",
        "edge_class": "quantisation/model transition",
        "example": "electron-proton relative state",
    },
    {
        "step": 9,
        "stage": "Quantum hydrogen",
        "ladder_level": 0,
        "physics": "Coulomb Hamiltonian, quantum virial and optional two-level projection",
        "transition_in": "bound-state solution and selected measurement projection",
        "edge_class": "established quantum solution",
        "example": "hydrogen 1s or a declared two-level subspace",
    },
]


CONTINUITY_ROWS = [
    {
        "order": 1,
        "domain": "General relativity",
        "law": "covariant stress-energy conservation",
        "accumulation": "local stress-energy/momentum account",
        "release_flux": "covariant transport through spacetime",
        "source_or_handover": "geometry and matter-field coupling are already included",
        "equation": "nabla_mu T^{mu nu}=0",
    },
    {
        "order": 2,
        "domain": "Electromagnetic charge",
        "law": "charge continuity",
        "accumulation": "partial_t rho",
        "release_flux": "div J",
        "source_or_handover": "zero for a closed charge account",
        "equation": "partial_t rho+div J=0",
    },
    {
        "order": 3,
        "domain": "Electromagnetic energy",
        "law": "Poynting theorem",
        "accumulation": "partial_t u_EM",
        "release_flux": "div S",
        "source_or_handover": "-J dot E to matter",
        "equation": "partial_t u_EM+div S=-J dot E",
    },
    {
        "order": 4,
        "domain": "Quantum probability",
        "law": "probability continuity",
        "accumulation": "partial_t |psi|^2",
        "release_flux": "div j",
        "source_or_handover": "zero for unitary closed evolution",
        "equation": "partial_t |psi|^2+div j=0",
    },
]


VIRIAL_SCALE_ROWS = [
    {
        "rung": "Earth-Sun orbit",
        "rung_order": 1,
        "log10_scale_m": math.log10(AU_M),
        "ara_coordinate": 1.0,
        "physics_domain": "Newtonian gravitation",
        "bridge_type": "inverse-distance virial",
    },
    {
        "rung": "Earth satellite reference",
        "rung_order": 2,
        "log10_scale_m": math.log10(SATELLITE_R_M),
        "ara_coordinate": 1.0,
        "physics_domain": "Newtonian gravitation",
        "bridge_type": "inverse-distance virial",
    },
    {
        "rung": "Classical Coulomb at a0",
        "rung_order": 3,
        "log10_scale_m": math.log10(BOHR_RADIUS_M),
        "ara_coordinate": 1.0,
        "physics_domain": "Classical electromagnetism",
        "bridge_type": "inverse-distance virial",
    },
    {
        "rung": "Quantum hydrogen 1s",
        "rung_order": 4,
        "log10_scale_m": math.log10(BOHR_RADIUS_M),
        "ara_coordinate": 1.0,
        "physics_domain": "Quantum mechanics",
        "bridge_type": "quantum inverse-distance virial",
    },
]


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_artifact() -> dict:
    source = {
        "id": "src-physics-ladder",
        "label": "ARA physics ladder synthesis",
        "path": "analysis/physics_ladder/ara_physics_cosmic_quantum_ladder.py",
        "query": {
            "engine": "portable-snapshot",
            "language": "sql",
            "description": (
                "A deterministic synthesis of the reviewed gravity, Hamilton/Noether, "
                "virial, Maxwell/Lorentz, and quantum ARA crosswalk reports."
            ),
            "sql": (
                "SELECT * FROM snapshot.law_ladder ORDER BY law_order; "
                "SELECT * FROM snapshot.ara_landmarks ORDER BY landmark_order; "
                "SELECT * FROM snapshot.traversal_path ORDER BY step; "
                "SELECT * FROM snapshot.continuity_spine ORDER BY continuity_order; "
                "SELECT * FROM snapshot.virial_scale ORDER BY rung_order;"
            ),
            "tables_used": [
                "snapshot.law_ladder",
                "snapshot.ara_landmarks",
                "snapshot.traversal_path",
                "snapshot.continuity_spine",
                "snapshot.virial_scale",
            ],
            "filters": [
                "Established laws and previously reviewed ARA crosswalks only",
                "Every transition explicitly typed",
                "No direct GR-to-quantum derivation claimed",
                "Numerical 0-2 coordinates shown only where comparable channels are declared",
            ],
            "metric_definitions": [
                "ARA diameter position runs from 0 to 2 after an ordered pair is declared",
                "A value of 1 means equal declared contributions only for that named coordinate",
                "TE-ARA total 2 is normalized closure, not a universal physical energy amount",
                "Traversal step is narrative order, not physical length or evidential weight",
            ],
        },
    }

    law_rows = [
        {
            "law_order": row["order"],
            "ara_math_and_version": (
                f"{row['order']}. {row['law']} — {row['ara_math']} [{row['status']}]"
            ),
            "established_physics_equation": (
                f"{row['physics_equation']} "
                f"Bridge role: {row['bridge_role']}. "
                f"Transformation type: {row['map_type']}."
            ),
            "law": row["law"],
            "bridge_role": row["bridge_role"],
            "map_type": row["map_type"],
            "status": row["status"],
        }
        for row in LAW_ROWS
    ]

    landmark_rows = [
        {
            "landmark_order": row["order"],
            "law": row["law"],
            "ara_0": row["pole_0"],
            "ara_1": row["ridge_1"],
            "ara_2": row["pole_2"],
            "reading_kind": row["reading_kind"],
        }
        for row in LANDMARK_ROWS
    ]

    traversal_rows = [
        {
            "step": row["step"],
            "stage": row["stage"],
            "ladder_level": row["ladder_level"],
            "physics": row["physics"],
            "transition_in": row["transition_in"],
            "edge_class": row["edge_class"],
            "example": row["example"],
        }
        for row in TRAVERSAL_ROWS
    ]

    continuity_rows = [
        {
            "continuity_order": row["order"],
            "domain": row["domain"],
            "law": row["law"],
            "accumulation": row["accumulation"],
            "release_flux": row["release_flux"],
            "source_or_handover": row["source_or_handover"],
            "equation": row["equation"],
        }
        for row in CONTINUITY_ROWS
    ]

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "ARA physics ladder: solar spacetime to quantum hydrogen",
        "description": (
            "A two-column technical traversal showing where established physics "
            "and declared ARA geometry agree, differ, or require a fence."
        ),
        "generatedAt": "2026-07-23T00:00:00+10:00",
        "sources": [source],
        "charts": [
            {
                "id": "physics-traversal-chart",
                "title": "Ordered physics traversal from solar spacetime to hydrogen",
                "subtitle": (
                    "Schematic rung order; edges include exact limits, reformulations, "
                    "conservation consequences, one sibling bridge, and a quantum model transition"
                ),
                "intent": "trend",
                "question": "How are the reviewed laws connected without pretending they form one direct derivation?",
                "rationale": (
                    "An ordered ladder keeps the path readable while source fields retain "
                    "the scientifically different transition classes."
                ),
                "comparisonContext": {
                    "grain": "one reviewed theory/method stage",
                    "unit": "schematic rung order",
                    "semanticFamily": "typed law traversal",
                },
                "type": "line",
                "dataset": "traversal_path",
                "sourceId": "src-physics-ladder",
                "encodings": {
                    "x": {"field": "stage", "type": "nominal", "label": "Traversal stage"},
                    "y": {
                        "field": "ladder_level",
                        "type": "quantitative",
                        "label": "Schematic parent-to-child rung",
                    },
                    "tooltip": [
                        {"field": "stage", "type": "text", "label": "Stage"},
                        {"field": "physics", "type": "text", "label": "Physics"},
                        {"field": "transition_in", "type": "text", "label": "Incoming bridge"},
                        {"field": "edge_class", "type": "text", "label": "Bridge class"},
                        {"field": "example", "type": "text", "label": "Example"},
                    ],
                },
                "xAxisTitle": "Solar spacetime → classical dynamics → fields → quantum hydrogen",
                "yAxisTitle": "Schematic rung (not physical length)",
                "layout": "full",
                "maxRows": 9,
                "surface": {
                    "surface": "explorer",
                    "viewMode": "both",
                    "interactiveLegend": False,
                    "showControls": False,
                },
            },
            {
                "id": "virial-scale-chart",
                "title": "Virial ARA coordinate versus characteristic scale",
                "subtitle": (
                    "Four declared inverse-distance systems; log10 metres on the scale axis"
                ),
                "intent": "relationship",
                "question": "Which part of the wider ladder already has one exact numerical cross-scale coordinate?",
                "rationale": (
                    "The four deliberately selected points show the validated virial thread "
                    "without implying that every law in the wider atlas is a 1.0 ridge."
                ),
                "comparisonContext": {
                    "grain": "one ideal bound-system rung",
                    "unit": "dimensionless ARA coordinate versus log10 metres",
                    "semanticFamily": "cross-scale invariant coordinate",
                },
                "type": "scatter",
                "dataset": "virial_scale",
                "sourceId": "src-physics-ladder",
                "encodings": {
                    "x": {
                        "field": "log10_scale_m",
                        "type": "quantitative",
                        "label": "log10 characteristic scale (m)",
                    },
                    "y": {
                        "field": "ara_coordinate",
                        "type": "quantitative",
                        "label": "Virial ARA coordinate",
                    },
                    "tooltip": [
                        {"field": "rung", "type": "text", "label": "Rung"},
                        {
                            "field": "physics_domain",
                            "type": "text",
                            "label": "Physics domain",
                        },
                        {
                            "field": "log10_scale_m",
                            "type": "quantitative",
                            "label": "log10 scale (m)",
                        },
                        {
                            "field": "ara_coordinate",
                            "type": "quantitative",
                            "label": "ARA",
                        },
                    ],
                },
                "xAxisTitle": "log10 characteristic length in metres",
                "yAxisTitle": "Weighted virial ARA coordinate",
                "layout": "full",
                "maxRows": 4,
                "referenceLines": [
                    {"value": 1, "label": "1.0 virial ridge", "axis": "y"}
                ],
                "surface": {
                    "surface": "explorer",
                    "viewMode": "both",
                    "interactiveLegend": False,
                    "showControls": False,
                },
            },
        ],
        "tables": [
            {
                "id": "two-column-law-crosswalk",
                "title": "ARA math beside the established physics",
                "subtitle": (
                    "Fourteen reviewed laws or theorem-level stages; ARA is on the left "
                    "and the native physics is on the right"
                ),
                "dataset": "law_ladder",
                "defaultSort": {"field": "ara_math_and_version", "direction": "asc"},
                "density": "spacious",
                "sourceId": "src-physics-ladder",
                "layout": "full",
                "columns": [
                    {
                        "field": "ara_math_and_version",
                        "label": "ARA math and version",
                        "type": "text",
                    },
                    {
                        "field": "established_physics_equation",
                        "label": "Established physics equation and bridge",
                        "type": "text",
                    },
                ],
            },
            {
                "id": "ara-landmark-matrix",
                "title": "Where each law sits on its declared ARA diameter",
                "subtitle": (
                    "The numeral 1 has law-specific meaning; some rows are cycles or "
                    "directed relations rather than measured equilibria"
                ),
                "dataset": "ara_landmarks",
                "defaultSort": {"field": "law", "direction": "asc"},
                "density": "spacious",
                "sourceId": "src-physics-ladder",
                "layout": "full",
                "columns": [
                    {"field": "law", "label": "Law / appearance", "type": "text"},
                    {"field": "ara_0", "label": "ARA 0", "type": "text"},
                    {"field": "ara_1", "label": "ARA 1", "type": "text"},
                    {"field": "ara_2", "label": "ARA 2", "type": "text"},
                    {
                        "field": "reading_kind",
                        "label": "What kind of reading this is",
                        "type": "text",
                    },
                ],
            },
            {
                "id": "continuity-spine-table",
                "title": "The accumulation–release balance skeleton across four theories",
                "subtitle": (
                    "The stored quantity changes with boundary flux and any declared source or handover"
                ),
                "dataset": "continuity_spine",
                "defaultSort": {"field": "domain", "direction": "asc"},
                "density": "spacious",
                "sourceId": "src-physics-ladder",
                "layout": "full",
                "columns": [
                    {"field": "domain", "label": "Domain", "type": "text"},
                    {"field": "equation", "label": "Established equation", "type": "text"},
                    {
                        "field": "accumulation",
                        "label": "Accumulation / stored change",
                        "type": "text",
                    },
                    {
                        "field": "release_flux",
                        "label": "Boundary release / flux",
                        "type": "text",
                    },
                    {
                        "field": "source_or_handover",
                        "label": "Source or handover",
                        "type": "text",
                    },
                ],
            },
        ],
        "blocks": [
            {
                "id": "title",
                "type": "markdown",
                "layout": "full",
                "body": "# ARA physics ladder: solar spacetime to quantum hydrogen",
            },
            {
                "id": "technical-summary",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## One geometry can organise the walk, but the arrows are not all the same kind\n\n"
                    "The wider result is not that every law sits at `1.0`. The repeated ARA object is a "
                    "declared pair plus its retained relation, boundary and direction. Exact limits connect "
                    "Einstein to Newton; canonical mechanics connects Newton to Hamilton; Noether and the "
                    "virial theorem expose different parent invariants; Maxwell closes charge, field, energy "
                    "and momentum accounts; the quantum Hamiltonian then describes hydrogen. The gravity-to-"
                    "Coulomb step is only a **sibling inverse-square bridge**, not a derivation of electromagnetism "
                    "from gravity."
                ),
            },
            {
                "id": "path-heading",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## The Sun-to-hydrogen path is a typed network rather than one collapsing equation\n\n"
                    "Read the descending line as navigation through descriptions. Its vertical coordinate is "
                    "schematic. Each tooltip states whether the incoming step is an exact limit, reformulation, "
                    "theorem consequence, conservation consequence, sibling bridge, or quantum model transition."
                ),
            },
            {
                "id": "path-chart",
                "type": "chart",
                "layout": "full",
                "chartId": "physics-traversal-chart",
            },
            {
                "id": "numeric-thread-heading",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## The virial theorem is the exact numerical thread inside the wider atlas\n\n"
                    "Only the inverse-distance virial sub-ladder has so far been assigned one unchanged numeric "
                    "coordinate across the full planetary-to-quantum span. It remains at `1.0` because the "
                    "theorem supplies the weighting `2<T>=|<V>|`; this should not be transferred to unrelated "
                    "laws without their own measurable pair."
                ),
            },
            {
                "id": "virial-chart",
                "type": "chart",
                "layout": "full",
                "chartId": "virial-scale-chart",
            },
            {
                "id": "landmarks-heading",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## The same 0–2 canvas carries different lawful meanings\n\n"
                    "`0` and `2` name the declared endpoints. `1` names equal contribution only when the two "
                    "channels are comparable in that law. Faraday requires a four-quadrant phase plane; Noether "
                    "describes a parent invariant; Einstein is first a directed source–response relation. These "
                    "differences are transformations of appearance that must be retained, not flattened away."
                ),
            },
            {
                "id": "landmarks-table",
                "type": "table",
                "layout": "full",
                "tableId": "ara-landmark-matrix",
            },
            {
                "id": "crosswalk-heading",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## ARA and physics remain side by side at every step\n\n"
                    "The left column gives the declared ARA object and its evidence tier. The right gives the "
                    "native equation and the type of bridge. Exact reparameterisation is labelled separately "
                    "from interpretation, and failed simple rung rules remain visible."
                ),
            },
            {
                "id": "crosswalk-table",
                "type": "table",
                "layout": "full",
                "tableId": "two-column-law-crosswalk",
            },
            {
                "id": "continuity-heading",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## Continuity is the strongest equation-level Accumulation–Release spine\n\n"
                    "Charge, electromagnetic energy, quantum probability and relativistic stress-energy all "
                    "use a local balance structure. The stored quantity and flux are different physical objects, "
                    "but the grammatical form repeats: local change plus boundary transport equals the named "
                    "source or handover."
                ),
            },
            {
                "id": "continuity-table",
                "type": "table",
                "layout": "full",
                "tableId": "continuity-spine-table",
            },
            {
                "id": "methodology",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## Method: preserve the native law, then declare the ARA appearance\n\n"
                    "For each row the measurement boundary, ordered pair, relation, direction and transformation "
                    "type are stated before assigning a `0–2` coordinate. A numeric ARA position is used only "
                    "when the channels share units or an established theorem supplies the conversion. This is "
                    "a reconstruction atlas assembled from already reviewed work, not a new prospective test."
                ),
            },
            {
                "id": "limitations",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## What survives—and what remains unproved\n\n"
                    "The atlas shows that one relational vocabulary can preserve many established equations "
                    "without obvious contradiction. It does not derive Maxwell from Newton, quantum mechanics "
                    "from relativity, or prove universal fractality. Gravity and Coulomb share an inverse-square "
                    "form but have different sources and theories. Quantisation is not a mere scale zoom. The "
                    "scientific next step is to reuse one frozen boundary/orientation/coarse-graining rule on "
                    "several laws and require it to predict both successes and controlled failures."
                ),
            },
            {
                "id": "next-steps",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## Next step: test the transformation rule, not another resemblance\n\n"
                    "Freeze one operator that moves between child, parent and boundary accounts. Apply it to "
                    "Newtonian momentum, electromagnetic energy/momentum and quantum probability. The useful "
                    "result would be a shared residual rule that identifies an omitted boundary or coupling term "
                    "without being retuned after each law is inspected."
                ),
            },
            {
                "id": "further-questions",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## Further questions\n\n"
                    "Can one frozen ARA coarse-graining operator recover the covariance terms that defeated the "
                    "simple Lorentz rung-up rule? Does the same operator distinguish an active `1.0` ridge from "
                    "a null one using activity, variance and coherence across classical and quantum examples?"
                ),
            },
        ],
    }

    snapshot = {
        "version": 1,
        "generatedAt": "2026-07-23T00:00:00+10:00",
        "status": "ready",
        "datasets": {
            "law_ladder": law_rows,
            "ara_landmarks": landmark_rows,
            "traversal_path": traversal_rows,
            "continuity_spine": continuity_rows,
            "virial_scale": VIRIAL_SCALE_ROWS,
        },
    }

    return {
        "surface": "report",
        "manifest": manifest,
        "snapshot": snapshot,
        "sources": [source],
    }


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)

    write_csv(HERE / "ARA_PHYSICS_LAW_LADDER.csv", LAW_ROWS)
    write_csv(HERE / "ARA_PHYSICS_LANDMARK_MATRIX.csv", LANDMARK_ROWS)
    write_csv(HERE / "ARA_PHYSICS_TRAVERSAL_PATH.csv", TRAVERSAL_ROWS)
    write_csv(HERE / "ARA_PHYSICS_CONTINUITY_SPINE.csv", CONTINUITY_ROWS)
    write_csv(HERE / "ARA_PHYSICS_VIRIAL_SCALE_THREAD.csv", VIRIAL_SCALE_ROWS)

    result = {
        "status": "built",
        "law_rows": len(LAW_ROWS),
        "landmark_rows": len(LANDMARK_ROWS),
        "traversal_steps": len(TRAVERSAL_ROWS),
        "continuity_domains": len(CONTINUITY_ROWS),
        "virial_scale_points": len(VIRIAL_SCALE_ROWS),
        "virial_scale_span_orders": math.log10(AU_M / BOHR_RADIUS_M),
        "interpretation": (
            "Typed reconstruction atlas. It contains exact limits, reformulations, "
            "conservation consequences and declared ARA coordinates, but no direct "
            "GR-to-quantum derivation."
        ),
    }

    (HERE / "ARA_PHYSICS_COSMIC_QUANTUM_LADDER_RESULTS.json").write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )
    (HERE / "ARA_PHYSICS_COSMIC_QUANTUM_REPORT_ARTIFACT.json").write_text(
        json.dumps(build_artifact(), indent=2),
        encoding="utf-8",
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
