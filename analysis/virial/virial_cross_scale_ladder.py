"""Build the classical-to-quantum virial/ARA cross-scale ladder.

The calculation deliberately keeps three quantities separate:

1. Native physics:
      2 <T> = |<V>|                    for a bound inverse-distance potential.
2. Raw TE-ARA allocation:
      t_T = 2<T>/(<T>+|<V>|)
      t_C = 2|<V>|/(<T>+|<V>|)
      t_T + t_C = 2.
3. Virial-comparison ARA:
      R = 2<T>, C = |<V>|
      x_vir = 2R/(R+C).

At virial balance x_vir=1 while the raw energy allocation remains asymmetric:
t_T=2/3 and t_C=4/3.

Sources for numerical constants:
- NASA Sun Fact Sheet:
  https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html
- NASA Earth-orbit eccentricity teaching table:
  https://pumas.nasa.gov/sites/default/files/examples/01_25_11_1.pdf
- NIST 2022 CODATA wall chart:
  https://physics.nist.gov/cuu/pdf/wall_2022.pdf
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent

# Source-backed numerical inputs. The normalized ARA results do not depend on
# their absolute magnitudes, but retaining them makes the cross-scale ladder
# independently auditable.
G = 6.67430e-11  # m^3 kg^-1 s^-2, 2019 SI/CODATA value
M_SUN = 1.9884e30  # kg, NASA Sun Fact Sheet
M_EARTH = 5.9722e24  # kg, NASA Sun Fact Sheet
AU = 149_597_870_700.0  # m, exact IAU definition
EARTH_ORBIT_ECCENTRICITY = 0.01671123  # NASA PUMAS table
MU_EARTH = 3.986004418e14  # m^3 s^-2, standard Earth gravitational parameter
SATELLITE_REFERENCE_RADIUS = 7_000_000.0  # m, declared circular reference
BOHR_RADIUS = 5.291_772_105_44e-11  # m, NIST 2022 CODATA
HARTREE_EV = 27.211_386_245_981  # eV, NIST 2022 CODATA


@dataclass(frozen=True)
class LadderRow:
    rung_order: int
    system: str
    domain: str
    characteristic_scale_m: float
    energy_unit: str
    mean_kinetic: float
    mean_potential: float
    connection_channel: float
    traversal_channel: float
    raw_traversal_allocation: float
    virial_ara_coordinate: float
    raw_connection_allocation: float
    te_ara_total: float
    virial_residual: float
    physics_equation: str
    ara_equation: str
    interpretation: str


def ara_virial_coordinate(mean_kinetic: float, mean_potential: float) -> float:
    """Return the Traversal-oriented ARA position for virial-weighted channels."""
    traversal = 2.0 * mean_kinetic
    connection = abs(mean_potential)
    return 2.0 * traversal / (traversal + connection)


def raw_te_allocations(mean_kinetic: float, mean_potential: float) -> tuple[float, float]:
    """Return Traversal and Connection shares on the normalized total-2 account."""
    connection = abs(mean_potential)
    total_magnitude = mean_kinetic + connection
    return (
        2.0 * mean_kinetic / total_magnitude,
        2.0 * connection / total_magnitude,
    )


def make_row(
    *,
    rung_order: int,
    system: str,
    domain: str,
    characteristic_scale_m: float,
    energy_unit: str,
    mean_kinetic: float,
    mean_potential: float,
    physics_equation: str,
    ara_equation: str,
    interpretation: str,
) -> LadderRow:
    traversal = 2.0 * mean_kinetic
    connection = abs(mean_potential)
    raw_t, raw_c = raw_te_allocations(mean_kinetic, mean_potential)
    return LadderRow(
        rung_order=rung_order,
        system=system,
        domain=domain,
        characteristic_scale_m=characteristic_scale_m,
        energy_unit=energy_unit,
        mean_kinetic=mean_kinetic,
        mean_potential=mean_potential,
        connection_channel=connection,
        traversal_channel=traversal,
        raw_traversal_allocation=raw_t,
        virial_ara_coordinate=ara_virial_coordinate(mean_kinetic, mean_potential),
        raw_connection_allocation=raw_c,
        te_ara_total=raw_t + raw_c,
        virial_residual=traversal - connection,
        physics_equation=physics_equation,
        ara_equation=ara_equation,
        interpretation=interpretation,
    )


def build_ladder() -> list[LadderRow]:
    earth_sun_t = G * M_SUN * M_EARTH / (2.0 * AU)
    earth_sun_v = -2.0 * earth_sun_t

    satellite_t_specific = MU_EARTH / (2.0 * SATELLITE_REFERENCE_RADIUS)
    satellite_v_specific = -2.0 * satellite_t_specific

    classical_coulomb_t = HARTREE_EV / 2.0
    classical_coulomb_v = -HARTREE_EV

    quantum_hydrogen_t = HARTREE_EV / 2.0
    quantum_hydrogen_v = -HARTREE_EV

    return [
        make_row(
            rung_order=1,
            system="1. Planetary — Earth–Sun",
            domain="Classical gravitation",
            characteristic_scale_m=AU,
            energy_unit="J",
            mean_kinetic=earth_sun_t,
            mean_potential=earth_sun_v,
            physics_equation="<T>=G M_sun M_earth/(2a); <V>=-G M_sun M_earth/a",
            ara_equation="C=|<V>|; R=2<T>; x_vir=2R/(C+R)=1",
            interpretation="The instantaneous orbital children move around the ridge; the full-cycle parent balances.",
        ),
        make_row(
            rung_order=2,
            system="2. Satellite — circular 7000 km reference",
            domain="Classical gravitation",
            characteristic_scale_m=SATELLITE_REFERENCE_RADIUS,
            energy_unit="J/kg",
            mean_kinetic=satellite_t_specific,
            mean_potential=satellite_v_specific,
            physics_equation="T/mu=GM_earth/(2r); V/mu=-GM_earth/r",
            ara_equation="C=|V|; R=2T; x_vir=1 at every point of the ideal circle",
            interpretation="A circular orbit is already locally on the virial ridge rather than only averaging to it.",
        ),
        make_row(
            rung_order=3,
            system="3. Classical Coulomb — electron/proton at a0",
            domain="Classical electromagnetism",
            characteristic_scale_m=BOHR_RADIUS,
            energy_unit="eV",
            mean_kinetic=classical_coulomb_t,
            mean_potential=classical_coulomb_v,
            physics_equation="T=k_e e^2/(2a0)=E_h/2; V=-k_e e^2/a0=-E_h",
            ara_equation="The force law changes identity, but C:R and x_vir remain the same",
            interpretation="This is a classical comparison model, not a claim that hydrogen contains a classical orbit.",
        ),
        make_row(
            rung_order=4,
            system="4. Quantum — ideal hydrogen 1s",
            domain="Nonrelativistic quantum mechanics",
            characteristic_scale_m=BOHR_RADIUS,
            energy_unit="eV expectation value",
            mean_kinetic=quantum_hydrogen_t,
            mean_potential=quantum_hydrogen_v,
            physics_equation="<T>=E_h/2; <V>=-E_h from the quantum virial theorem",
            ara_equation="Expectation-value channels C=|<V>| and R=2<T> give x_vir=1",
            interpretation="The ridge is an expectation-value relation; it is not an electron completing a classical orbit.",
        ),
    ]


def solve_kepler(mean_anomaly: float, eccentricity: float) -> float:
    """Solve M=E-e sin(E) by Newton iteration."""
    eccentric_anomaly = mean_anomaly
    for _ in range(16):
        f = eccentric_anomaly - eccentricity * math.sin(eccentric_anomaly) - mean_anomaly
        fp = 1.0 - eccentricity * math.cos(eccentric_anomaly)
        update = f / fp
        eccentric_anomaly -= update
        if abs(update) < 1e-15:
            break
    return eccentric_anomaly


def build_earth_orbit_curve(sample_count: int = 180) -> tuple[list[dict], list[dict]]:
    """Return wide and tidy equal-time samples through one Earth orbit.

    Channels are normalized by G M_sun M_earth / a, which cancels from x_vir.
    The cumulative coordinate is formed from cumulative channels, not from the
    arithmetic mean of already-normalized instantaneous coordinates.
    """
    wide: list[dict] = []
    tidy: list[dict] = []
    cumulative_connection = 0.0
    cumulative_traversal = 0.0

    for index in range(sample_count):
        phase = index / sample_count
        mean_anomaly = 2.0 * math.pi * phase
        eccentric_anomaly = solve_kepler(mean_anomaly, EARTH_ORBIT_ECCENTRICITY)
        radius_over_a = 1.0 - EARTH_ORBIT_ECCENTRICITY * math.cos(eccentric_anomaly)

        # C=|V|/(GMm/a)=a/r.  R=2T/(GMm/a)=2a/r-1 from vis-viva.
        connection = 1.0 / radius_over_a
        traversal = 2.0 / radius_over_a - 1.0
        instantaneous_x = 2.0 * traversal / (connection + traversal)

        cumulative_connection += connection
        cumulative_traversal += traversal
        cumulative_x = (
            2.0
            * cumulative_traversal
            / (cumulative_connection + cumulative_traversal)
        )

        row = {
            "phase_fraction": phase,
            "radius_au": radius_over_a,
            "connection_channel": connection,
            "traversal_channel": traversal,
            "instantaneous_ara": instantaneous_x,
            "cumulative_channel_ara": cumulative_x,
        }
        wide.append(row)
        for series, value in (
            ("Instantaneous child reading", instantaneous_x),
            ("Cumulative parent reading", cumulative_x),
        ):
            tidy.append(
                {
                    "phase_fraction": phase,
                    "ara_coordinate": value,
                    "series": series,
                    "radius_au": radius_over_a,
                    "connection_channel": connection,
                    "traversal_channel": traversal,
                }
            )

    # Close the displayed curve at one complete cycle. Use the completed
    # full-cycle channel account for the cumulative point.
    final_parent_x = (
        2.0
        * cumulative_traversal
        / (cumulative_connection + cumulative_traversal)
    )
    final_instantaneous = wide[0]["instantaneous_ara"]
    final_radius = wide[0]["radius_au"]
    final_connection = wide[0]["connection_channel"]
    final_traversal = wide[0]["traversal_channel"]
    wide.append(
        {
            "phase_fraction": 1.0,
            "radius_au": final_radius,
            "connection_channel": final_connection,
            "traversal_channel": final_traversal,
            "instantaneous_ara": final_instantaneous,
            "cumulative_channel_ara": final_parent_x,
        }
    )
    for series, value in (
        ("Instantaneous child reading", final_instantaneous),
        ("Cumulative parent reading", final_parent_x),
    ):
        tidy.append(
            {
                "phase_fraction": 1.0,
                "ara_coordinate": value,
                "series": series,
                "radius_au": final_radius,
                "connection_channel": final_connection,
                "traversal_channel": final_traversal,
            }
        )
    return wide, tidy


def marker_rows(ladder: Iterable[LadderRow]) -> list[dict]:
    rows: list[dict] = []
    for row in ladder:
        log_scale = math.log10(row.characteristic_scale_m)
        for reading_type, coordinate in (
            ("Raw Traversal allocation", row.raw_traversal_allocation),
            ("Virial comparison ridge", row.virial_ara_coordinate),
            ("Raw Connection allocation", row.raw_connection_allocation),
        ):
            rows.append(
                {
                    "rung": row.system,
                    "rung_order": row.rung_order,
                    "domain": row.domain,
                    "reading_type": reading_type,
                    "ara_coordinate": coordinate,
                    "characteristic_scale_m": row.characteristic_scale_m,
                    "log10_scale_m": log_scale,
                    "mean_kinetic": row.mean_kinetic,
                    "mean_potential": row.mean_potential,
                    "energy_unit": row.energy_unit,
                    "te_ara_total": row.te_ara_total,
                }
            )
    return rows


def ridge_rows(ladder: Iterable[LadderRow]) -> list[dict]:
    """One plain-ARA virial coordinate per physical rung."""
    return [
        {
            "rung": row.system,
            "rung_order": row.rung_order,
            "domain": row.domain,
            "ara_coordinate": row.virial_ara_coordinate,
            "characteristic_scale_m": row.characteristic_scale_m,
            "log10_scale_m": math.log10(row.characteristic_scale_m),
            "raw_traversal_allocation": row.raw_traversal_allocation,
            "raw_connection_allocation": row.raw_connection_allocation,
            "te_ara_total": row.te_ara_total,
        }
        for row in ladder
    ]


def table_rows(ladder: Iterable[LadderRow]) -> list[dict]:
    return [
        {
            "physics_equation": f"{row.system}: {row.physics_equation}",
            "ara_equation": f"{row.ara_equation}. {row.interpretation}",
        }
        for row in ladder
    ]


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_artifact(
    ladder: list[LadderRow],
    markers: list[dict],
    orbit_tidy: list[dict],
) -> dict:
    ridges = ridge_rows(ladder)
    generated_at = "2026-07-23T00:00:00+10:00"
    source = {
        "id": "src-virial-ladder",
        "label": "Deterministic virial cross-scale ladder",
        "path": "analysis/virial/virial_cross_scale_ladder.py",
        "query": {
            "engine": "portable-snapshot",
            "language": "sql",
            "description": (
                "Deterministic calculations from the inverse-distance virial "
                "theorem using NASA orbital inputs and NIST 2022 CODATA constants."
            ),
            "sql": (
                "SELECT * FROM snapshot.virial_ladder ORDER BY physics_equation; "
                "SELECT * FROM snapshot.virial_markers ORDER BY rung_order, ara_coordinate; "
                "SELECT * FROM snapshot.virial_ridge ORDER BY rung_order; "
                "SELECT * FROM snapshot.earth_orbit_curve ORDER BY phase_fraction, series;"
            ),
            "tables_used": [
                "snapshot.virial_ladder",
                "snapshot.virial_markers",
                "snapshot.virial_ridge",
                "snapshot.earth_orbit_curve",
            ],
            "filters": [
                "Bound inverse-distance systems only",
                "Ideal Newtonian gravity, ideal classical Coulomb, and ideal nonrelativistic hydrogen",
                "Audit Earth orbit sampled at 180 equal-time mean-anomaly positions",
                "Report visual deterministically downsampled to 18 equal-time positions plus closure",
            ],
            "metric_definitions": [
                "Connection channel C = absolute mean potential energy |<V>|",
                "Traversal channel R = twice mean kinetic energy 2<T>",
                "Virial ARA x_vir = 2R/(C+R)",
                "Raw TE-ARA allocations t_T=2<T>/(<T>+|<V>|), t_C=2|<V>|/(<T>+|<V>|)",
            ],
        },
    }

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "The virial ARA ladder: planetary motion to quantum hydrogen",
        "description": (
            "An exact cross-scale comparison of inverse-distance bound systems "
            "using established virial physics and declared ARA coordinates."
        ),
        "generatedAt": generated_at,
        "sources": [source],
        "charts": [
            {
                "id": "cross-scale-ara-position",
                "title": "Virial ARA coordinate across four bound-system rungs",
                "subtitle": (
                    "The physical scale changes by more than 21 orders of magnitude; "
                    "every declared virial comparison remains at the 1.0 ridge"
                ),
                "intent": "comparison",
                "question": "Where does each inverse-distance bound system sit on the 0–2 virial ARA diameter?",
                "rationale": (
                    "A single-series rung line shows the same declared coordinate "
                    "without flattening TE-ARA component allocations into positions."
                ),
                "comparisonContext": {
                    "grain": "one ARA reading per physical rung",
                    "unit": "dimensionless ARA coordinate",
                    "semanticFamily": "cross-scale normalized position",
                },
                "type": "line",
                "dataset": "virial_ridge",
                "sourceId": "src-virial-ladder",
                "encodings": {
                    "x": {"field": "rung", "type": "nominal", "label": "Scale rung"},
                    "y": {
                        "field": "ara_coordinate",
                        "type": "quantitative",
                        "label": "ARA coordinate",
                    },
                    "tooltip": [
                        {"field": "rung", "type": "text", "label": "Rung"},
                        {
                            "field": "ara_coordinate",
                            "type": "quantitative",
                            "label": "ARA",
                        },
                        {
                            "field": "log10_scale_m",
                            "type": "quantitative",
                            "label": "log10 scale (m)",
                        },
                        {"field": "domain", "type": "text", "label": "Physics"},
                    ],
                },
                "xAxisTitle": "Planetary → satellite → classical Coulomb → quantum",
                "yAxisTitle": "ARA coordinate on 0–2",
                "layout": "full",
                "maxRows": len(ridges),
                "referenceLines": [
                    {"value": 1.0, "label": "1.0 virial ridge", "axis": "y"}
                ],
                "surface": {
                    "surface": "explorer",
                    "viewMode": "both",
                    "interactiveLegend": True,
                    "showControls": False,
                },
            },
            {
                "id": "earth-orbit-approach",
                "title": "Earth–Sun virial ARA over one orbit",
                "subtitle": (
                    "The instantaneous child reading moves around the ridge; "
                    "the completed channel account returns to 1.0"
                ),
                "intent": "trend",
                "question": "How does a time-resolved Kepler orbit produce a stable parent virial ridge?",
                "rationale": (
                    "An ordered line chart separates the instantaneous child reading "
                    "from the cumulative channel account over one complete cycle."
                ),
                "comparisonContext": {
                    "grain": "equal-time orbital phase sample",
                    "unit": "dimensionless ARA coordinate",
                    "semanticFamily": "instantaneous versus accumulated relation",
                },
                "type": "line",
                "dataset": "earth_orbit_curve",
                "sourceId": "src-virial-ladder",
                "encodings": {
                    "x": {
                        "field": "phase_fraction",
                        "type": "quantitative",
                        "label": "Fraction of orbit",
                    },
                    "y": {
                        "field": "ara_coordinate",
                        "type": "quantitative",
                        "label": "ARA coordinate",
                    },
                    "color": {
                        "field": "series",
                        "type": "nominal",
                        "label": "Measurement",
                    },
                    "tooltip": [
                        {
                            "field": "phase_fraction",
                            "type": "quantitative",
                            "label": "Orbit fraction",
                        },
                        {"field": "series", "type": "text", "label": "Measurement"},
                        {
                            "field": "ara_coordinate",
                            "type": "quantitative",
                            "label": "ARA",
                        },
                        {
                            "field": "radius_au",
                            "type": "quantitative",
                            "label": "Radius / a",
                        },
                    ],
                },
                "xAxisTitle": "Fraction of one Earth orbit",
                "yAxisTitle": "Virial ARA coordinate",
                "layout": "full",
                "maxRows": len(orbit_tidy),
                "palette": {"kind": "categorical", "name": "identity"},
                "referenceLines": [
                    {"value": 1.0, "label": "1.0 parent ridge", "axis": "y"}
                ],
                "surface": {
                    "surface": "explorer",
                    "viewMode": "both",
                    "interactiveLegend": True,
                    "showControls": False,
                },
            },
        ],
        "tables": [
            {
                "id": "two-column-ladder",
                "title": "Established physics and its ARA reading",
                "subtitle": "The force identity changes; the declared normalized relation remains fixed",
                "dataset": "virial_ladder",
                "defaultSort": {"field": "physics_equation", "direction": "asc"},
                "density": "spacious",
                "sourceId": "src-virial-ladder",
                "layout": "full",
                "columns": [
                    {
                        "field": "physics_equation",
                        "label": "Established physics equation",
                        "type": "text",
                    },
                    {
                        "field": "ara_equation",
                        "label": "ARA math and plain-language version",
                        "type": "text",
                    },
                ],
            }
        ],
        "blocks": [
            {
                "id": "title",
                "type": "markdown",
                "layout": "full",
                "body": "# The virial ARA ladder: planetary motion to quantum hydrogen",
            },
            {
                "id": "technical-summary",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## One inverse-distance relation survives the entire ladder\n\n"
                    "For four ideal bound systems, established physics gives "
                    "`2<T> = |<V>|`. After declaring **Connection** as "
                    "`C=|<V>|` and **Traversal** as `R=2<T>`, the exact ARA coordinate "
                    "`x_vir=2R/(C+R)` is `1.0` on every rung. This is substantial "
                    "evidence that the same *declared coordinate* can remain scale-consistent. "
                    "It is not a new virial theorem and does not prove that all systems share "
                    "one universal physical sphere."
                ),
            },
            {
                "id": "visual-reading",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## The same ridge appears without flattening the raw asymmetry\n\n"
                    "Read the chart vertically on the plain-ARA `0–2` scale: every rung "
                    "lands at the virial `1.0` ridge. Separately, the raw energy account "
                    "remains asymmetric at `2/3` Traversal and `4/3` Connection, summing "
                    "to TE-ARA `2`; those are component amounts, not extra positions on "
                    "the plotted diameter. The virial comparison weights "
                    "kinetic energy by the theorem's physical factor of two, placing "
                    "`R` and `C` at their `1.0` relational ridge."
                ),
            },
            {
                "id": "cross-scale-chart-block",
                "type": "chart",
                "layout": "full",
                "chartId": "cross-scale-ara-position",
            },
            {
                "id": "two-column-heading",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## The two-column crosswalk keeps physics and interpretation side by side\n\n"
                    "The left column states the established equation. The right column "
                    "shows the declared ARA transformation and its plain-language meaning. "
                    "The quantum row uses expectation values and must not be read as a "
                    "classical electron orbit."
                ),
            },
            {
                "id": "two-column-table-block",
                "type": "table",
                "layout": "full",
                "tableId": "two-column-ladder",
            },
            {
                "id": "scope-definitions",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## The ridge belongs to a weighted relation and a declared boundary\n\n"
                    "**Physics scope:** bound systems governed by an ideal inverse-distance "
                    "potential `V∝-1/r`. **Connection channel:** `C=|<V>|`. "
                    "**Traversal channel:** `R=2<T>`. **Virial ARA:** "
                    "`x_vir=2R/(C+R)`. **Raw TE-ARA:** "
                    "`t_T=2<T>/(<T>+|<V>|)` and "
                    "`t_C=2|<V>|/(<T>+|<V>|)`. These are different observables "
                    "on the same normalized geometry."
                ),
            },
            {
                "id": "approach-heading",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## A moving child can produce a stable parent ridge\n\n"
                    "Earth's slightly elliptical orbit supplies the visual version of the "
                    "original rock insight. Its instantaneous relation moves slightly to "
                    "either side of `1.0`, while the account formed from increasingly "
                    "complete orbital channels converges on the parent ridge. In a "
                    "conservative orbit the planet does not settle or stop; the measurement "
                    "settles as it covers the cycle."
                ),
            },
            {
                "id": "earth-orbit-chart-block",
                "type": "chart",
                "layout": "full",
                "chartId": "earth-orbit-approach",
            },
            {
                "id": "method-validation",
                "type": "markdown",
                "layout": "full",
                "sourceId": "src-virial-ladder",
                "body": (
                    "## Calculation and validation\n\n"
                    "The planetary row uses the Newtonian two-body mean-energy relation at "
                    "one astronomical unit. The satellite row uses a declared circular "
                    "`7000 km` geocentric reference. The classical Coulomb row is a "
                    "comparison model at the Bohr radius. The quantum row uses ideal "
                    "nonrelativistic hydrogen expectation values. All four rows are "
                    "recomputed from saved inputs; no ARA landmark was fitted to the result."
                ),
            },
            {
                "id": "limitations",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## What this establishes—and what it does not\n\n"
                    "This establishes an exact, scale-invariant **crosswalk** for a family "
                    "already unified by the inverse-distance potential and virial theorem. "
                    "The common result is therefore expected in established physics. It "
                    "does not prove universal ARA fractality, quantum gravity, or a new "
                    "planetary-to-quantum force. Driven, dissipative, unbound, relativistic, "
                    "many-body and non-homogeneous systems require boundary terms or a "
                    "different virial relation and are essential controls."
                ),
            },
            {
                "id": "next-step",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## The next discriminating test is controlled failure and recovery\n\n"
                    "Apply the frozen coordinate to potentials `V∝r^k`, where established "
                    "physics predicts `2<T>=k<V>`, and to an open or driven system where "
                    "the simple ridge should fail. A useful ARA contribution would be to "
                    "classify the residual from independently measured boundary terms "
                    "without retuning the coordinate after seeing the outcome."
                ),
            },
            {
                "id": "further-questions",
                "type": "markdown",
                "layout": "full",
                "body": (
                    "## Further questions\n\n"
                    "Does the same ARA residual decomposition identify the missing pressure, "
                    "surface or driving term in a generalized virial theorem? Can a frozen "
                    "measurement-window rule distinguish a genuinely equilibrating system "
                    "from a conservative system whose running average merely approaches "
                    "the ridge?"
                ),
            },
        ],
    }

    snapshot = {
        "version": 1,
        "generatedAt": generated_at,
        "status": "ready",
        "datasets": {
            "virial_ladder": table_rows(ladder),
            "virial_markers": markers,
            "virial_ridge": ridges,
            "earth_orbit_curve": orbit_tidy,
        },
    }
    return {
        "surface": "report",
        "manifest": manifest,
        "snapshot": snapshot,
        "sources": [source],
    }


def main() -> None:
    ladder = build_ladder()
    markers = marker_rows(ladder)
    orbit_wide, orbit_tidy = build_earth_orbit_curve()
    _, orbit_tidy_report = build_earth_orbit_curve(sample_count=18)

    write_csv(HERE / "VIRIAL_CROSS_SCALE_LADDER.csv", [asdict(row) for row in ladder])
    write_csv(HERE / "VIRIAL_ARA_MARKERS.csv", markers)
    write_csv(HERE / "EARTH_ORBIT_VIRIAL_ARA.csv", orbit_wide)

    results = {
        "inputs": {
            "G_m3_kg_s2": G,
            "sun_mass_kg": M_SUN,
            "earth_mass_kg": M_EARTH,
            "astronomical_unit_m": AU,
            "earth_orbit_eccentricity": EARTH_ORBIT_ECCENTRICITY,
            "earth_mu_m3_s2": MU_EARTH,
            "satellite_reference_radius_m": SATELLITE_REFERENCE_RADIUS,
            "bohr_radius_m": BOHR_RADIUS,
            "hartree_energy_eV": HARTREE_EV,
        },
        "ladder": [asdict(row) for row in ladder],
        "scale_span_orders_of_magnitude": math.log10(AU / BOHR_RADIUS),
        "earth_orbit": {
            "sample_count": len(orbit_wide) - 1,
            "instantaneous_ara_min": min(row["instantaneous_ara"] for row in orbit_wide),
            "instantaneous_ara_max": max(row["instantaneous_ara"] for row in orbit_wide),
            "completed_channel_ara": orbit_wide[-1]["cumulative_channel_ara"],
        },
    }
    (HERE / "VIRIAL_CROSS_SCALE_RESULTS.json").write_text(
        json.dumps(results, indent=2) + "\n",
        encoding="utf-8",
    )

    # The audit CSV keeps 180 equal-time samples. The report snapshot uses a
    # deterministic 18-sample view so the visual remains compact and portable.
    artifact = build_artifact(ladder, markers, orbit_tidy_report)
    (HERE / "VIRIAL_CROSS_SCALE_REPORT_ARTIFACT.json").write_text(
        json.dumps(artifact, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "rows": len(ladder),
                "marker_rows": len(markers),
                "orbit_rows": len(orbit_tidy),
                "scale_span_orders": results["scale_span_orders_of_magnitude"],
                "earth_instantaneous_range": [
                    results["earth_orbit"]["instantaneous_ara_min"],
                    results["earth_orbit"]["instantaneous_ara_max"],
                ],
                "earth_completed_channel_ara": results["earth_orbit"][
                    "completed_channel_ara"
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
