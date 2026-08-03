from __future__ import annotations

import csv
import itertools
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Bubble:
    frame: int
    time: float
    ident: int
    x: float
    y: float
    area: float
    perimeter: float
    vx: float
    vy: float

    @property
    def radius(self) -> float:
        return math.sqrt(max(self.area, 0.0) / math.pi)

    @property
    def circularity(self) -> float:
        if self.perimeter <= 0:
            return float("nan")
        return 4.0 * math.pi * self.area / (self.perimeter * self.perimeter)


@dataclass
class RunData:
    path: Path
    video: str
    amplitude: float
    umf: float
    frames: dict[int, list[Bubble]]
    tracks: dict[int, dict[int, Bubble]]


@dataclass
class Candidate:
    run: RunData
    frame: int
    child_a: Bubble
    child_b: Bubble
    parent: Bubble
    closure: float
    separation_norm: float
    center_norm: float
    separation_change: float
    score: float
    ambiguity_ratio: float = float("inf")


NAME_RE = re.compile(r"V(?P<video>\d+)_Amp(?P<amp>[0-9.]+)_umf(?P<umf>[0-9.]+)\.csv$")


def load_run(path: Path) -> RunData:
    match = NAME_RE.match(path.name)
    if not match:
        raise ValueError(f"Unexpected filename: {path.name}")
    frames: dict[int, list[Bubble]] = defaultdict(list)
    tracks: dict[int, dict[int, Bubble]] = defaultdict(dict)
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            bubble = Bubble(
                frame=int(row["frame_number"]),
                time=float(row["time [sec]"]),
                ident=int(row["ID"]),
                x=float(row["cx_pos [m]"]),
                y=float(row["cy_pos [m]"]),
                area=float(row["size [m^2]"]),
                perimeter=float(row["perimeter [m]"]),
                vx=float(row["x_velocity [m/s]"]),
                vy=float(row["y_velocity [m/s]"]),
            )
            frames[bubble.frame].append(bubble)
            tracks[bubble.ident][bubble.frame] = bubble
    return RunData(
        path=path,
        video=f"V{match.group('video')}",
        amplitude=float(match.group("amp")),
        umf=float(match.group("umf")),
        frames=dict(frames),
        tracks=dict(tracks),
    )


def contiguous_back(track: dict[int, Bubble], end: int) -> int:
    count = 0
    frame = end
    while frame in track:
        count += 1
        frame -= 1
    return count


def contiguous_forward(track: dict[int, Bubble], start: int, limit: int | None = None) -> list[Bubble]:
    rows: list[Bubble] = []
    frame = start
    while frame in track and (limit is None or len(rows) < limit):
        rows.append(track[frame])
        frame += 1
    return rows


def distance(a: Bubble, b: Bubble) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def detect_candidates(
    run: RunData,
    *,
    min_child_age: int = 3,
    min_parent_life: int = 6,
    closure_min: float = 0.70,
    closure_max: float = 1.30,
    separation_min: float = 0.65,
    separation_max: float = 2.00,
    center_max: float = 1.00,
    isolation_radius: float = 1.25,
    ambiguity_min: float = 1.10,
    max_separation_growth: float = 0.10,
) -> list[Candidate]:
    accepted: list[Candidate] = []
    for frame in sorted(run.frames):
        if frame + 1 not in run.frames:
            continue
        current = run.frames[frame]
        following = run.frames[frame + 1]
        if len(current) < 2 or not following:
            continue

        next_ids = {bubble.ident for bubble in following}
        raw: list[Candidate] = []
        for child_a, child_b in itertools.combinations(current, 2):
            if contiguous_back(run.tracks[child_a.ident], frame) < min_child_age:
                continue
            if contiguous_back(run.tracks[child_b.ident], frame) < min_child_age:
                continue
            # A two-to-one merger cannot leave both child tracks separately visible.
            if child_a.ident in next_ids and child_b.ident in next_ids:
                continue
            radius_sum = child_a.radius + child_b.radius
            if radius_sum <= 0:
                continue
            separation_norm = distance(child_a, child_b) / radius_sum
            if not (separation_min <= separation_norm <= separation_max):
                continue
            prev_a = run.tracks[child_a.ident].get(frame - 1)
            prev_b = run.tracks[child_b.ident].get(frame - 1)
            if prev_a is None or prev_b is None:
                continue
            previous_separation = distance(prev_a, prev_b)
            if previous_separation <= 0:
                continue
            separation_change = (distance(child_a, child_b) - previous_separation) / previous_separation
            if separation_change > max_separation_growth:
                continue

            total_area = child_a.area + child_b.area
            weighted_x = (child_a.x * child_a.area + child_b.x * child_b.area) / total_area
            weighted_y = (child_a.y * child_a.area + child_b.y * child_b.area) / total_area
            for parent in following:
                life = contiguous_forward(run.tracks[parent.ident], frame + 1)
                if len(life) < min_parent_life:
                    continue
                closure = parent.area / total_area
                if not (closure_min <= closure <= closure_max):
                    continue
                if parent.area < 0.90 * max(child_a.area, child_b.area):
                    continue
                center_delta = math.hypot(parent.x - weighted_x, parent.y - weighted_y)
                center_norm = center_delta / max(parent.radius, 1e-12)
                if center_norm > center_max:
                    continue

                # Reject crowded transitions in which an unassigned third contour
                # lies inside the proposed parent's immediate capture region.
                third_is_close = False
                for other in current:
                    if other.ident in (child_a.ident, child_b.ident):
                        continue
                    if math.hypot(other.x - weighted_x, other.y - weighted_y) <= isolation_radius * parent.radius:
                        third_is_close = True
                        break
                if third_is_close:
                    continue

                closure_term = abs(math.log(closure)) / abs(math.log(closure_max))
                separation_term = abs(separation_norm - 1.0)
                score = closure_term + center_norm + 0.25 * separation_term
                raw.append(Candidate(
                    run=run,
                    frame=frame,
                    child_a=child_a,
                    child_b=child_b,
                    parent=parent,
                    closure=closure,
                    separation_norm=separation_norm,
                    center_norm=center_norm,
                    separation_change=separation_change,
                    score=score,
                ))

        if not raw:
            continue

        # A family must be the mutual best local explanation. This prevents the
        # same parent or child from being assigned to two simultaneous families.
        raw.sort(key=lambda item: item.score)
        best_for_parent: dict[int, Candidate] = {}
        best_for_pair: dict[tuple[int, int], Candidate] = {}
        alternatives: dict[tuple[int, int, int], list[float]] = defaultdict(list)
        for item in raw:
            pair = tuple(sorted((item.child_a.ident, item.child_b.ident)))
            best_for_parent.setdefault(item.parent.ident, item)
            best_for_pair.setdefault(pair, item)
            alternatives[(pair[0], pair[1], item.parent.ident)].append(item.score)

        used_children: set[int] = set()
        used_parents: set[int] = set()
        for item in raw:
            pair = tuple(sorted((item.child_a.ident, item.child_b.ident)))
            if best_for_parent[item.parent.ident] is not item or best_for_pair[pair] is not item:
                continue
            if item.parent.ident in used_parents or any(c in used_children for c in pair):
                continue
            competing = [x.score for x in raw if x is not item and (
                x.parent.ident == item.parent.ident or
                tuple(sorted((x.child_a.ident, x.child_b.ident))) == pair
            )]
            item.ambiguity_ratio = min(competing) / max(item.score, 1e-12) if competing else float("inf")
            if item.ambiguity_ratio < ambiguity_min:
                continue
            accepted.append(item)
            used_children.update(pair)
            used_parents.add(item.parent.ident)
    return accepted
