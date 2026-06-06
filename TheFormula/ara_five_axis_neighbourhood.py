#!/usr/bin/env python3
"""
ARA five-axis neighbourhood scaffold.

This module defines the local contact environment described by the ARA coordinate
sphere:

    5 axes x 2 directions x 3 depths = 30 contacts around the home sphere.

It is intentionally a scaffold, not a scored predictor. The goal is to keep the
next formula honest to the full five-axis surroundings instead of collapsing back
to one lower feeder and one upper pressure term.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Dict, Iterable, List, Optional, Tuple


PHI = (1.0 + sqrt(5.0)) / 2.0


AXES: Dict[str, Tuple[float, float, float, float, float]] = {
    # Coordinates are abstract five-axis basis vectors:
    # X mapping/ARA, Y rung, Z coupling, phi-line, anti-phi line.
    "x_mapping_ara": (1.0, 0.0, 0.0, 0.0, 0.0),
    "y_rung": (0.0, 1.0, 0.0, 0.0, 0.0),
    "z_coupling": (0.0, 0.0, 1.0, 0.0, 0.0),
    "phi_line": (0.0, 0.0, 0.0, 1.0, 0.0),
    "anti_phi_line": (0.0, 0.0, 0.0, 0.0, 1.0),
}


@dataclass(frozen=True)
class ContactAddress:
    axis: str
    direction: int
    depth: int

    @property
    def key(self) -> str:
        sign = "plus" if self.direction > 0 else "minus"
        return f"{self.axis}:{sign}:{self.depth}"


@dataclass
class ContactState:
    address: ContactAddress
    ara: float = 1.0
    sub_ara: float = 1.0
    coupling_ara: float = 1.0
    spin: float = 0.0
    pressure: float = 0.0
    terrain_slope: float = 0.0
    ridge_pressure: float = 0.0
    observed: bool = False
    label: str = ""


@dataclass
class HomeSphereState:
    ara: float
    rung: float
    coupling_ara: float
    phi_coord: float
    anti_phi_coord: float
    carried_energy: float
    own_spin: float

    def vector(self) -> Tuple[float, float, float, float, float]:
        return (
            self.ara,
            self.rung,
            self.coupling_ara,
            self.phi_coord,
            self.anti_phi_coord,
        )


def build_contact_addresses(depth: int = 3) -> List[ContactAddress]:
    """Return the 30 direct five-axis contacts for depth=3."""
    if depth < 1:
        raise ValueError("depth must be at least 1")
    out: List[ContactAddress] = []
    for axis in AXES:
        for direction in (-1, 1):
            for d in range(1, depth + 1):
                out.append(ContactAddress(axis=axis, direction=direction, depth=d))
    return out


def depth_weight(depth: int) -> float:
    """Logarithmic depth decay. Depth 1 matters most; depth 3 is background terrain."""
    return PHI ** (-depth)


def parity(depth: int) -> float:
    """Layered contact flips orientation at each depth."""
    return -1.0 if depth % 2 else 1.0


def _add(a: Tuple[float, ...], b: Tuple[float, ...]) -> Tuple[float, ...]:
    return tuple(x + y for x, y in zip(a, b))


def _scale(v: Tuple[float, ...], s: float) -> Tuple[float, ...]:
    return tuple(x * s for x in v)


def local_phi_points(lo: float, hi: float) -> Tuple[float, float]:
    width = hi - lo
    return lo + width / PHI, hi - width / PHI


def recursive_ara_terrain(x: float, depth: int = 5) -> Dict[str, float]:
    """
    Read a one-dimensional recursive ARA terrain address.

    This is the terrain-reader ingredient: every coordinate has local phi valleys,
    anti-phi mirrors, and ridge pressure inside its current bounds.
    """
    x = max(0.0, min(2.0, float(x)))
    slope = 0.0
    ridge = 0.0
    lo = 0.0
    hi = 2.0
    address = 0.0
    for lvl in range(depth):
        mid = (lo + hi) / 2.0
        bit = 0.0 if x < mid else 1.0
        address += bit * (PHI ** (-(lvl + 1)))
        if x < mid:
            hi = mid
        else:
            lo = mid
        left_phi, right_phi = local_phi_points(lo, hi)
        target = left_phi if abs(x - left_phi) <= abs(x - right_phi) else right_phi
        width = max(hi - lo, 1e-12)
        w = PHI ** (-(lvl + 1))
        slope += w * (target - x) / width
        edge_distance = min(x - lo, hi - x) / width
        ridge += w * max(0.0, 1.0 - 2.0 * edge_distance)
    return {
        "terrain_slope": slope,
        "ridge_pressure": ridge,
        "address": address,
        "bounds_lo": lo,
        "bounds_hi": hi,
    }


def default_contact_state(address: ContactAddress) -> ContactState:
    """
    Create a terrain-derived placeholder contact when no observed feeder exists.

    This avoids treating missing surrounding systems as empty space.
    """
    base = 1.0 + address.direction * 0.12 * depth_weight(address.depth)
    terrain = recursive_ara_terrain(base)
    return ContactState(
        address=address,
        ara=base,
        sub_ara=(base * PHI) % 2.0,
        coupling_ara=1.0,
        spin=address.direction * parity(address.depth) * depth_weight(address.depth),
        pressure=abs(terrain["terrain_slope"]) * depth_weight(address.depth),
        terrain_slope=terrain["terrain_slope"],
        ridge_pressure=terrain["ridge_pressure"],
        observed=False,
        label="terrain-default",
    )


def complete_neighbourhood(
    observed: Optional[Dict[str, ContactState]] = None,
    depth: int = 3,
) -> List[ContactState]:
    """Return all required contacts, filling missing entries from terrain defaults."""
    observed = observed or {}
    out: List[ContactState] = []
    for address in build_contact_addresses(depth):
        out.append(observed.get(address.key, default_contact_state(address)))
    return out


def contact_force(contact: ContactState) -> Tuple[float, float, float, float, float]:
    """
    Contact force along the relevant five-axis basis vector.

    Pressure and spin act through depth weighting and parity. Ridge pressure brakes
    the force, rather than deleting it.
    """
    axis_vec = AXES[contact.address.axis]
    brake = 1.0 + max(0.0, contact.ridge_pressure)
    magnitude = (
        contact.address.direction
        * depth_weight(contact.address.depth)
        * parity(contact.address.depth)
        * (contact.pressure + abs(contact.spin) + abs(contact.terrain_slope))
        / brake
    )
    return _scale(axis_vec, magnitude)


def roll_vector(
    home: HomeSphereState,
    contacts: Iterable[ContactState],
    floor_motion: float = 0.0,
    upper_brake: float = 0.0,
) -> Tuple[float, float, float, float, float]:
    """
    Sum the five-axis roll vector induced by the local contact environment.
    """
    vec = (floor_motion, 0.0, 0.0, 0.0, 0.0)
    for contact in contacts:
        vec = _add(vec, contact_force(contact))
    brake = 1.0 + max(0.0, upper_brake)
    return tuple(v / brake for v in vec)


def advance_pose(
    home: HomeSphereState,
    vec: Tuple[float, float, float, float, float],
    horizon: float,
) -> Tuple[float, float, float, float, float]:
    """Advance the home coordinate by the contact-induced roll vector."""
    current = home.vector()
    return tuple(c + horizon * v for c, v in zip(current, vec))


def neighbourhood_summary(depth: int = 3) -> Dict[str, object]:
    addresses = build_contact_addresses(depth)
    return {
        "axes": list(AXES.keys()),
        "depth": depth,
        "contact_count": len(addresses),
        "home_plus_contacts": len(addresses) + 1,
        "addresses": [a.key for a in addresses],
    }


if __name__ == "__main__":
    summary = neighbourhood_summary(3)
    print(f"axes: {', '.join(summary['axes'])}")
    print(f"contacts: {summary['contact_count']} plus home sphere = {summary['home_plus_contacts']}")
    for key in summary["addresses"]:
        print(key)
