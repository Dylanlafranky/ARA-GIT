"""Q53 recorded trapped-qutrit external 1/e <-> Phi return test.

The source is a chronological hardware-measurement record.  This script never
generates a future observation.  It reconstructs each recorded post-measurement
ray, extracts complete projected circuits on three fixed cuts, and applies the
previously frozen Q49 external-centreline heading construction.
"""

from __future__ import annotations

import hashlib
import json
import math
import pathlib
import time
from dataclasses import dataclass, field

import numpy as np

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None


HERE = pathlib.Path(__file__).resolve().parent
SOURCE = (
    pathlib.Path(r"F:\SystemFormulaFolder\external_data\quantum")
    / "eth_single_ion_contextuality_2017"
    / "ExpDataYuOh.csv"
)
PROTOCOL = HERE / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_PROTOCOL_v1_FROZEN.md"
RESULTS = HERE / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_RESULTS.json"
EVENTS = HERE / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_EVENTS.npz"
FIGURE = HERE / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN.png"
EXTRACTION_METADATA = HERE / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_EXTRACTION.json"

SOURCE_SHA256 = "5410775C307EDEA9F68E95133CF0A733B6CD34E7D9D774B6509472FACE74D55D"
TOTAL_VALID_MEASUREMENTS = 53_459_987
PHI = (1.0 + math.sqrt(5.0)) / 2.0
LEFT = 1.0 / math.e
RIGHT = PHI - 1.0
WIDTH = RIGHT - LEFT
ARC_STARTS = np.mod(LEFT + np.arange(4, dtype=np.float64) / 4.0, 1.0)
ARC_NAMES = ("declared", "rotated_1", "rotated_2", "rotated_3")
PLANE_NAMES = ("psi0_psi1", "psi1_psi2", "psi2_psi0")
PLANE_AXES = ((0, 1), (1, 2), (2, 0))
CENTRE_NAMES = ("circle", "centroid", "extrema")
PRIMARY_MOVEMENT = 0.01
MOVEMENT_SENSITIVITIES = (0.0, 0.005, 0.01, 0.02, 0.05)
RESIDUAL_BANDS = (0.25, 0.50, math.inf)
SHUFFLES = 1_000
SHUFFLE_BLOCK = 10_000
SHUFFLE_SEED = 530_053
EPS = 1e-12
INCONSISTENCY_EPS = 1e-10


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


RAYS = np.asarray(
    [
        (0.0, 1.0, -1.0),
        (-1.0, 0.0, 1.0),
        (1.0, -1.0, 0.0),
        (0.0, 1.0, 1.0),
        (1.0, 0.0, 1.0),
        (1.0, 1.0, 0.0),
        (-1.0, 1.0, 1.0),
        (1.0, -1.0, 1.0),
        (1.0, 1.0, -1.0),
        (1.0, 1.0, 1.0),
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
    ],
    dtype=np.float64,
)
RAYS /= np.linalg.norm(RAYS, axis=1, keepdims=True)


def first_nonzero_positive(values: tuple[float, float, float]) -> bool:
    for value in values:
        if abs(value) > EPS:
            return value > 0
    return True


def solve_symmetric_3x3(
    a: float,
    b: float,
    c: float,
    d: float,
    e: float,
    f: float,
    y0: float,
    y1: float,
    y2: float,
) -> tuple[float, float, float] | None:
    det = a * (d * f - e * e) - b * (b * f - c * e) + c * (b * e - c * d)
    scale = max(abs(a), abs(b), abs(c), abs(d), abs(e), abs(f), 1.0)
    if not math.isfinite(det) or abs(det) <= 1e-12 * scale**3:
        return None
    dx = y0 * (d * f - e * e) - b * (y1 * f - e * y2) + c * (y1 * e - d * y2)
    dy = a * (y1 * f - e * y2) - y0 * (b * f - c * e) + c * (b * y2 - y1 * c)
    dz = a * (d * y2 - y1 * e) - b * (b * y2 - y1 * c) + y0 * (b * e - d * c)
    return dx / det, dy / det, dz / det


def median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    if n % 2:
        return ordered[n // 2]
    return 0.5 * (ordered[n // 2 - 1] + ordered[n // 2])


@dataclass
class Circle:
    start: int
    end: int
    circle_u: float
    circle_v: float
    centroid_u: float
    centroid_v: float
    extrema_u: float
    extrema_v: float
    radius: float
    residual: float


@dataclass
class EventStore:
    time: list[int] = field(default_factory=list)
    residual: list[float] = field(default_factory=list)
    circle_heading: list[float] = field(default_factory=list)
    circle_strength: list[float] = field(default_factory=list)
    centroid_heading: list[float] = field(default_factory=list)
    centroid_strength: list[float] = field(default_factory=list)
    extrema_heading: list[float] = field(default_factory=list)
    extrema_strength: list[float] = field(default_factory=list)

    def arrays(self) -> dict[str, np.ndarray]:
        return {
            "time": np.asarray(self.time, dtype=np.int64),
            "residual": np.asarray(self.residual, dtype=np.float64),
            "circle_heading": np.asarray(self.circle_heading, dtype=np.float64),
            "circle_strength": np.asarray(self.circle_strength, dtype=np.float64),
            "centroid_heading": np.asarray(self.centroid_heading, dtype=np.float64),
            "centroid_strength": np.asarray(self.centroid_strength, dtype=np.float64),
            "extrema_heading": np.asarray(self.extrema_heading, dtype=np.float64),
            "extrema_strength": np.asarray(self.extrema_strength, dtype=np.float64),
        }


class PlaneTracker:
    def __init__(self, axes: tuple[int, int]) -> None:
        self.axes = axes
        self.points: list[tuple[float, float]] = []
        self.start_index = -1
        self.start_q: int | None = None
        self.last_q: int | None = None
        self.direction = 0
        self.transitions = 0
        self.last_circles: list[Circle] = []
        self.events = EventStore()
        self.complete_circuits = 0
        self.short_circuits = 0
        self.singular_fits = 0

    def reset(self) -> None:
        self.points.clear()
        self.start_index = -1
        self.start_q = None
        self.last_q = None
        self.direction = 0
        self.transitions = 0
        self.last_circles.clear()

    def _begin(self, q: int, u: float, v: float, index: int) -> None:
        self.points = [(u, v)]
        self.start_index = index
        self.start_q = q
        self.last_q = q
        self.direction = 0
        self.transitions = 0

    def add(self, state: tuple[float, float, float], index: int) -> None:
        u = float(state[self.axes[0]])
        v = float(state[self.axes[1]])
        boundary = abs(u) <= EPS or abs(v) <= EPS
        if self.last_q is None:
            if boundary:
                return
            q = (0 if u >= 0 else 1) if v >= 0 else (3 if u >= 0 else 2)
            self._begin(q, u, v, index)
            return

        self.points.append((u, v))
        if boundary:
            return
        q = (0 if u >= 0 else 1) if v >= 0 else (3 if u >= 0 else 2)
        if q == self.last_q:
            return
        diff = (q - int(self.last_q)) % 4
        step = 1 if diff == 1 else (-1 if diff == 3 else 0)
        if step == 0:
            self._begin(q, u, v, index)
            return
        if self.direction == 0:
            self.direction = step
            self.transitions = 1
            self.last_q = q
            return
        if step != self.direction:
            self._begin(q, u, v, index)
            return
        self.transitions += 1
        self.last_q = q
        if self.transitions >= 4 and q == self.start_q:
            self._finish(index)
            self._begin(q, u, v, index)

    def _finish(self, end_index: int) -> None:
        self.complete_circuits += 1
        if len(self.points) < 6:
            self.short_circuits += 1
            self.last_circles.clear()
            return
        fit = self._fit(end_index)
        if fit is None:
            self.singular_fits += 1
            self.last_circles.clear()
            return
        self.last_circles.append(fit)
        if len(self.last_circles) > 3:
            self.last_circles.pop(0)
        if len(self.last_circles) == 3:
            self._event()

    def _fit(self, end_index: int) -> Circle | None:
        n = len(self.points)
        su = sv = suu = svv = suv = 0.0
        yub = yvb = sb = 0.0
        min_u = min_v = math.inf
        max_u = max_v = -math.inf
        for u, v in self.points:
            rr = u * u + v * v
            su += u
            sv += v
            suu += u * u
            svv += v * v
            suv += u * v
            yub += 2.0 * u * rr
            yvb += 2.0 * v * rr
            sb += rr
            min_u = min(min_u, u)
            max_u = max(max_u, u)
            min_v = min(min_v, v)
            max_v = max(max_v, v)
        solution = solve_symmetric_3x3(
            4.0 * suu,
            4.0 * suv,
            2.0 * su,
            4.0 * svv,
            2.0 * sv,
            float(n),
            yub,
            yvb,
            sb,
        )
        if solution is None:
            return None
        cu, cv, k = solution
        radius2 = k + cu * cu + cv * cv
        if not math.isfinite(radius2) or radius2 <= EPS:
            return None
        radius = math.sqrt(radius2)
        residuals = [
            abs(math.hypot(u - cu, v - cv) - radius) / radius
            for u, v in self.points
        ]
        return Circle(
            start=self.start_index,
            end=end_index,
            circle_u=cu,
            circle_v=cv,
            centroid_u=su / n,
            centroid_v=sv / n,
            extrema_u=0.5 * (min_u + max_u),
            extrema_v=0.5 * (min_v + max_v),
            radius=radius,
            residual=median(residuals),
        )

    def _event(self) -> None:
        previous, current, following = self.last_circles
        mean_radius = (previous.radius + current.radius + following.radius) / 3.0
        if mean_radius <= EPS:
            return
        values: dict[str, tuple[float, float]] = {}
        for name in CENTRE_NAMES:
            left_u = float(getattr(previous, f"{name}_u"))
            left_v = float(getattr(previous, f"{name}_v"))
            right_u = float(getattr(following, f"{name}_u"))
            right_v = float(getattr(following, f"{name}_v"))
            du = right_u - left_u
            dv = right_v - left_v
            strength = math.hypot(du, dv) / mean_radius
            heading = (
                (math.atan2(dv, du) / (2.0 * math.pi)) % 1.0
                if strength > EPS
                else math.nan
            )
            values[name] = (heading, strength)
        self.events.time.append((current.start + current.end) // 2)
        self.events.residual.append(current.residual)
        for name in CENTRE_NAMES:
            getattr(self.events, f"{name}_heading").append(values[name][0])
            getattr(self.events, f"{name}_strength").append(values[name][1])


def reconstruct() -> tuple[list[PlaneTracker], dict[str, int | float]]:
    trackers = [PlaneTracker(axes) for axes in PLANE_AXES]
    valid_rows = omitted_rows = measurements = 0
    inconsistencies = unit_failures = 0
    known = False
    state = (0.0, 0.0, 0.0)
    first_valid_row = True
    started = time.perf_counter()

    with SOURCE.open("r", encoding="utf-8", newline="") as stream:
        for physical_row, line in enumerate(stream, 1):
            text = line.strip()
            if not text:
                continue
            if text.startswith("o"):
                omitted_rows += 1
                continue
            values = list(map(int, text.split(",")))
            valid_rows += 1
            analyze_row = not first_valid_row
            for offset in range(0, len(values), 2):
                ray_label = values[offset]
                photons = values[offset + 1]
                measurements += 1
                ray = RAYS[ray_label - 1]
                rx, ry, rz = float(ray[0]), float(ray[1]), float(ray[2])
                bright = photons >= 6
                if bright:
                    if known:
                        dot = state[0] * rx + state[1] * ry + state[2] * rz
                        if dot < -EPS or (
                            abs(dot) <= EPS
                            and not first_nonzero_positive((rx, ry, rz))
                        ):
                            rx, ry, rz = -rx, -ry, -rz
                    elif not first_nonzero_positive((rx, ry, rz)):
                        rx, ry, rz = -rx, -ry, -rz
                    state = (rx, ry, rz)
                    known = True
                elif known:
                    dot = state[0] * rx + state[1] * ry + state[2] * rz
                    nx = state[0] - dot * rx
                    ny = state[1] - dot * ry
                    nz = state[2] - dot * rz
                    norm = math.sqrt(nx * nx + ny * ny + nz * nz)
                    if norm <= INCONSISTENCY_EPS:
                        inconsistencies += 1
                        known = False
                        for tracker in trackers:
                            tracker.reset()
                        continue
                    state = (nx / norm, ny / norm, nz / norm)
                if analyze_row and known:
                    norm2 = (
                        state[0] * state[0]
                        + state[1] * state[1]
                        + state[2] * state[2]
                    )
                    if abs(norm2 - 1.0) > 1e-9:
                        unit_failures += 1
                    for tracker in trackers:
                        tracker.add(state, measurements)
            first_valid_row = False
            if valid_rows % 5_000 == 0:
                elapsed = time.perf_counter() - started
                print(
                    f"rows={valid_rows:,} measurements={measurements:,} "
                    f"elapsed={elapsed:.1f}s",
                    flush=True,
                )

    return trackers, {
        "physical_rows": physical_row,
        "valid_rows": valid_rows,
        "omitted_rows": omitted_rows,
        "measurements": measurements,
        "reconstruction_inconsistencies": inconsistencies,
        "unit_norm_failures": unit_failures,
        "elapsed_seconds": time.perf_counter() - started,
    }


def in_arc(headings: np.ndarray, start: float) -> np.ndarray:
    return np.mod(headings - start, 1.0) <= WIDTH


def return_count(headings: np.ndarray, start: float) -> int:
    """Vectorized non-overlapping low -> high -> low count."""
    if headings.size == 0:
        return 0
    delta = np.mod(headings - start, 1.0)
    inside = delta <= WIDTH
    extreme = inside & ((delta <= 0.125 * WIDTH) | (delta >= 0.875 * WIDTH))
    indices = np.flatnonzero(extreme)
    if indices.size == 0:
        return 0
    outside_prefix = np.cumsum(~inside, dtype=np.int64)
    segments = outside_prefix[indices]
    labels = (delta[indices] >= 0.875 * WIDTH).astype(np.int8)
    keep = np.ones(indices.size, dtype=bool)
    if indices.size > 1:
        keep[1:] = (segments[1:] != segments[:-1]) | (labels[1:] != labels[:-1])
    segments = segments[keep]
    labels = labels[keep]
    if segments.size == 0:
        return 0
    _, starts, counts = np.unique(segments, return_index=True, return_counts=True)
    first = labels[starts]
    low_first = first == 0
    returns = np.where(low_first, (counts + 1) // 4, counts // 4)
    return int(np.sum(returns))


def shuffled_null(
    headings: np.ndarray, start: float, rng: np.random.Generator
) -> np.ndarray:
    output = np.empty(SHUFFLES, dtype=np.int64)
    working = headings.copy()
    for draw in range(SHUFFLES):
        working[:] = headings
        for left in range(0, working.size, SHUFFLE_BLOCK):
            rng.shuffle(working[left : left + SHUFFLE_BLOCK])
        output[draw] = return_count(working, start)
    return output


def analyse_cut(
    arrays: dict[str, np.ndarray], plane_index: int
) -> dict[str, object]:
    result: dict[str, object] = {}
    for estimator in CENTRE_NAMES:
        heading = arrays[f"{estimator}_heading"]
        strength = arrays[f"{estimator}_strength"]
        finite = np.isfinite(heading) & np.isfinite(strength)
        estimator_result: dict[str, object] = {}
        for threshold in MOVEMENT_SENSITIVITIES:
            active = finite & (strength >= threshold)
            selected = heading[active]
            occupancy = [int(np.sum(in_arc(selected, float(start)))) for start in ARC_STARTS]
            returns = [return_count(selected, float(start)) for start in ARC_STARTS]
            estimator_result[f"{threshold:.3f}"] = {
                "active_events": int(selected.size),
                "arc_occupancy": dict(zip(ARC_NAMES, occupancy)),
                "return_counts": dict(zip(ARC_NAMES, returns)),
                "return_rate_per_million_active": {
                    name: (count * 1_000_000.0 / selected.size if selected.size else math.nan)
                    for name, count in zip(ARC_NAMES, returns)
                },
            }
        result[estimator] = estimator_result

    heading = arrays["circle_heading"]
    strength = arrays["circle_strength"]
    time_index = arrays["time"]
    residual = arrays["residual"]
    active = (
        np.isfinite(heading)
        & np.isfinite(strength)
        & (strength >= PRIMARY_MOVEMENT)
    )
    primary_heading = heading[active]
    primary_time = time_index[active]
    primary_residual = residual[active]
    chronological: dict[str, object] = {}
    rng = np.random.default_rng(SHUFFLE_SEED + plane_index)
    null_passes = []
    chronological_returns = []
    for third in range(3):
        lo = third * TOTAL_VALID_MEASUREMENTS / 3.0
        hi = (third + 1) * TOTAL_VALID_MEASUREMENTS / 3.0
        mask = (primary_time >= lo) & (
            primary_time < hi if third < 2 else primary_time <= hi
        )
        selected = primary_heading[mask]
        observed = return_count(selected, LEFT)
        null = shuffled_null(selected, LEFT, rng)
        p99 = float(np.quantile(null, 0.99)) if null.size else math.nan
        chronological[f"third_{third + 1}"] = {
            "active_events": int(selected.size),
            "observed_declared_returns": observed,
            "shuffle_mean": float(np.mean(null)) if null.size else math.nan,
            "shuffle_p99": p99,
            "shuffle_max": int(np.max(null)) if null.size else 0,
            "empirical_p_greater_equal": float(
                (1 + np.sum(null >= observed)) / (1 + null.size)
            ),
        }
        chronological_returns.append(observed)
        null_passes.append(bool(observed > p99))
    result["chronological_thirds"] = chronological
    result["all_thirds_have_return"] = all(value > 0 for value in chronological_returns)
    result["all_thirds_beat_shuffle_p99"] = all(null_passes)
    result["primary_active_events"] = int(primary_heading.size)
    result["primary_residual"] = {
        "median": float(np.median(primary_residual)) if primary_residual.size else math.nan,
        "p90": float(np.quantile(primary_residual, 0.90)) if primary_residual.size else math.nan,
        "band_counts": {
            ("all" if math.isinf(band) else f"le_{band:.2f}"): int(
                np.sum(primary_residual <= band)
            )
            for band in RESIDUAL_BANDS
        },
    }
    return result


def make_figure(
    stores: list[dict[str, np.ndarray]], results: dict[str, object]
) -> None:
    if plt is None:
        return
    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    fig.suptitle(
        "Q53 — recorded qutrit whole-direction test: 1/e ↔ Phi ↔ 1/e",
        fontsize=18,
        weight="bold",
    )
    for plane, arrays in enumerate(stores):
        heading = arrays["circle_heading"]
        strength = arrays["circle_strength"]
        times = arrays["time"]
        active = (
            np.isfinite(heading)
            & np.isfinite(strength)
            & (strength >= PRIMARY_MOVEMENT)
        )
        h = heading[active]
        t = times[active]
        if h.size > 150_000:
            take = np.linspace(0, h.size - 1, 150_000, dtype=np.int64)
            hp = h[take]
            tp = t[take]
        else:
            hp, tp = h, t
        ax = axes[plane, 0]
        ax.scatter(tp, hp, s=2, alpha=0.25, color="#496f9b", rasterized=True)
        ax.axhspan(LEFT, RIGHT, color="#e0a33a", alpha=0.16)
        ax.axhline(LEFT, color="#333333", lw=1.2, label="1/e")
        ax.axhline(RIGHT, color="#b65f0a", lw=1.2, label="Phi mod 1")
        ax.set(
            ylabel="whole-centre heading (turns)",
            title=f"{PLANE_NAMES[plane]}: recorded external heading",
            ylim=(0, 1),
        )
        if plane == 2:
            ax.set_xlabel("valid measurement order")
        if plane == 0:
            ax.legend(loc="upper right")

        ax = axes[plane, 1]
        inside = in_arc(h, LEFT)
        x = 2.0 * np.mod(h[inside] - LEFT, 1.0) / WIDTH
        tx = t[inside]
        if x.size > 150_000:
            take = np.linspace(0, x.size - 1, 150_000, dtype=np.int64)
            x, tx = x[take], tx[take]
        ax.scatter(tx, x, s=2, alpha=0.28, color="#7b4d99", rasterized=True)
        ax.axhline(0, color="#333333", lw=1)
        ax.axhline(2, color="#b65f0a", lw=1)
        ax.set(
            ylabel="ARA direction (1/e = 0, Phi = 2)",
            title="Declared carrier only",
            ylim=(-0.05, 2.05),
        )
        if plane == 2:
            ax.set_xlabel("valid measurement order")

        ax = axes[plane, 2]
        primary = results["planes"][PLANE_NAMES[plane]]["circle"]["0.010"]
        returns = list(primary["return_counts"].values())
        occupancy = list(primary["arc_occupancy"].values())
        rates = [
            count * 1_000_000.0 / primary["active_events"]
            if primary["active_events"]
            else 0.0
            for count in returns
        ]
        bars = ax.bar(ARC_NAMES, rates, color=["#df9f2d", "#9eabb8", "#9eabb8", "#9eabb8"])
        ax.set(
            ylabel="0→2→0 returns / million active events",
            title="Declared arc versus matched rotations",
        )
        ax.tick_params(axis="x", rotation=18)
        for bar, value, occ in zip(bars, returns, occupancy):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{value:,}\n({occ:,} in arc)",
                ha="center",
                va="bottom",
                fontsize=8,
            )
    fig.text(
        0.01,
        0.01,
        "Source: ETH Zürich ExpDataYuOh.csv. Directions reconstructed only "
        "from recorded ray + photon response; no future generated.",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.025, 1, 0.965))
    fig.savefig(FIGURE, dpi=180)
    plt.close(fig)


def load_streamed_extraction() -> tuple[list[dict[str, np.ndarray]], dict[str, object], dict[str, object]]:
    dtype = np.dtype(
        [
            ("time", "<i8"),
            ("residual", "<f8"),
            ("circle_heading", "<f8"),
            ("circle_strength", "<f8"),
            ("centroid_heading", "<f8"),
            ("centroid_strength", "<f8"),
            ("extrema_heading", "<f8"),
            ("extrema_strength", "<f8"),
        ]
    )
    metadata = json.loads(EXTRACTION_METADATA.read_text(encoding="utf-8"))
    stores: list[dict[str, np.ndarray]] = []
    for name in PLANE_NAMES:
        path = HERE / f"Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_{name}.bin"
        records = np.fromfile(path, dtype=dtype)
        expected = int(metadata["extraction"][name]["external_events"])
        if records.size != expected:
            raise RuntimeError(
                f"{name} record count mismatch: {records.size} != {expected}"
            )
        stores.append({field: np.asarray(records[field]) for field in records.dtype.names})
    integrity = {
        key: metadata[key]
        for key in (
            "physical_rows",
            "valid_rows",
            "omitted_rows",
            "measurements",
            "reconstruction_inconsistencies",
            "unit_norm_failures",
            "elapsed_seconds",
        )
    }
    return stores, integrity, metadata["extraction"]


def main() -> None:
    source_hash = sha256(SOURCE)
    if source_hash.upper() != SOURCE_SHA256:
        raise RuntimeError(f"source hash mismatch: {source_hash}")
    protocol_hash = sha256(PROTOCOL)
    binary_paths = [
        HERE / f"Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_{name}.bin"
        for name in PLANE_NAMES
    ]
    if EXTRACTION_METADATA.exists() and all(path.exists() for path in binary_paths):
        print("loading frozen streamed extraction", flush=True)
        stores, integrity, extraction = load_streamed_extraction()
    else:
        trackers, integrity = reconstruct()
        stores = [tracker.events.arrays() for tracker in trackers]
        extraction = {
            name: {
                "complete_circuits": tracker.complete_circuits,
                "short_circuits": tracker.short_circuits,
                "singular_fits": tracker.singular_fits,
                "external_events": len(tracker.events.time),
            }
            for name, tracker in zip(PLANE_NAMES, trackers)
        }

    np.savez_compressed(
        EVENTS,
        **{
            f"{PLANE_NAMES[p]}_{key}": value
            for p, arrays in enumerate(stores)
            for key, value in arrays.items()
        },
    )

    plane_results: dict[str, object] = {}
    for plane, arrays in enumerate(stores):
        print(
            f"analysing {PLANE_NAMES[plane]} with "
            f"{arrays['time'].size:,} external events",
            flush=True,
        )
        plane_results[PLANE_NAMES[plane]] = analyse_cut(arrays, plane)

    g0 = bool(
        source_hash.upper() == SOURCE_SHA256
        and int(integrity["measurements"]) == TOTAL_VALID_MEASUREMENTS
        and int(integrity["valid_rows"]) == 53_301
        and int(integrity["omitted_rows"]) == 1_062
        and int(integrity["unit_norm_failures"]) == 0
    )
    g1_cut = []
    g2_cut = []
    g3_cut = []
    g4_cut = []
    for name in PLANE_NAMES:
        plane = plane_results[name]
        primary = plane["circle"]["0.010"]
        occupancy = primary["arc_occupancy"]
        returns = primary["return_counts"]
        g1_cut.append(
            occupancy["declared"]
            > max(occupancy["rotated_1"], occupancy["rotated_2"], occupancy["rotated_3"])
        )
        g2_cut.append(bool(plane["all_thirds_have_return"]))
        g3_cut.append(bool(plane["all_thirds_beat_shuffle_p99"]))
        g4_cut.append(
            returns["declared"]
            > max(returns["rotated_1"], returns["rotated_2"], returns["rotated_3"])
        )
    g1 = sum(g1_cut) >= 2
    g2 = sum(g2_cut) >= 2
    g3 = sum(g3_cut) >= 2
    g4 = sum(g4_cut) >= 2
    substantive = sum((g1, g2, g3, g4))
    if not g0:
        verdict = "INVALID / NOT TESTABLE"
    elif substantive == 4:
        verdict = "SUPPORTED"
    elif substantive >= 2:
        verdict = "MIXED"
    else:
        verdict = "NOT SUPPORTED"

    results: dict[str, object] = {
        "test": "Q53 recorded qutrit external 1/e-Phi return",
        "question": (
            "Does the recorded whole-direction vector repeatedly complete "
            "1/e -> Phi -> 1/e, mapped as ARA 0 -> 2 -> 0?"
        ),
        "verdict": verdict,
        "source": {
            "path": str(SOURCE),
            "sha256": source_hash,
            "protocol_path": str(PROTOCOL),
            "protocol_sha256": protocol_hash,
            **integrity,
        },
        "geometry": {
            "one_over_e": LEFT,
            "phi_mod_one": RIGHT,
            "arc_width_turns": WIDTH,
            "arc_width_degrees": WIDTH * 360.0,
            "plane_cuts": dict(zip(PLANE_NAMES, PLANE_AXES)),
            "movement_gate": PRIMARY_MOVEMENT,
        },
        "extraction": extraction,
        "planes": plane_results,
        "gates": {
            "G0_source_and_reconstruction_integrity": g0,
            "G1_declared_directional_location": g1,
            "G2_complete_ordered_return": g2,
            "G3_time_order": g3,
            "G4_landmark_specificity": g4,
            "cut_passes": {
                "G1": dict(zip(PLANE_NAMES, g1_cut)),
                "G2": dict(zip(PLANE_NAMES, g2_cut)),
                "G3": dict(zip(PLANE_NAMES, g3_cut)),
                "G4": dict(zip(PLANE_NAMES, g4_cut)),
            },
            "substantive_passes": substantive,
        },
        "boundaries": [
            "The record is hardware data, but the post-measurement direction is reconstructed from the source's projective-measurement rule.",
            "The measurement ray is an external coupling choice selected by a QRNG; it is not by itself the qutrit state.",
            "The three fixed basis-plane cuts are reported without fitting a preferred rotation.",
            "A pass is specific to this experiment and coordinate construction.",
            "No parent-ridge or child-cancellation claim is scored.",
        ],
    }
    RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(stores, results)
    print(
        json.dumps(
            {
                "verdict": verdict,
                "gates": results["gates"],
                "integrity": integrity,
                "extraction": results["extraction"],
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
