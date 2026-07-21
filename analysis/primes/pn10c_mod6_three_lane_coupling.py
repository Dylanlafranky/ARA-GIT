"""PN10C post-hoc mod-6 three-lane coupling diagnostic.

The protocol was frozen before this script was executed.  This is a structural
diagnostic on the already-open PN10B interval and cannot alter PN10B's NULL
registered verdict.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from pn10b_child_phase_prime_ranking import segmented_least_prime_factor


ROOT = Path(__file__).resolve().parent
LOW, HIGH = 4_000_000_000, 4_001_000_000
WINDOW = 150
SEED = 20260720
BOOT_DRAWS = 2_000
BOOT_BLOCKS = 100

RESULTS = ROOT / "PN10C_MOD6_THREE_LANE_RESULTS.json"
OFFSET_CSV = ROOT / "PN10C_MOD6_OFFSET_PROFILE.csv"
LANE_CSV = ROOT / "PN10C_MOD6_LANE_SUMMARY.csv"
MATRIX_CSV = ROOT / "PN10C_MOD30_BLACK_CHILD_MATRIX.csv"
EXAMPLES_CSV = ROOT / "PN10C_MOD6_WORKED_EXAMPLES.csv"
FIGURE = ROOT / "PN10C_MOD6_THREE_LANE_FIGURE.png"


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def ci(values: np.ndarray) -> dict[str, float]:
    return {
        "estimate": float(values[0]),
        "bootstrap_mean": float(np.mean(values[1:])),
        "ci95_low": float(np.quantile(values[1:], 0.025)),
        "ci95_high": float(np.quantile(values[1:], 0.975)),
    }


def block_draws(per_center: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Observed mean followed by contiguous-block bootstrap means."""
    chunks = [chunk for chunk in np.array_split(per_center, min(BOOT_BLOCKS, len(per_center))) if len(chunk)]
    means = np.array([float(np.mean(chunk)) for chunk in chunks])
    sizes = np.array([len(chunk) for chunk in chunks], dtype=np.float64)
    observed = float(np.mean(per_center))
    picks = rng.integers(0, len(chunks), size=(BOOT_DRAWS, len(chunks)))
    draw_means = np.sum(means[picks] * sizes[picks], axis=1) / np.sum(sizes[picks], axis=1)
    return np.concatenate([[observed], draw_means])


def paired_block_draws(per_center_arrays: list[np.ndarray], rng: np.random.Generator) -> list[np.ndarray]:
    """Observed means plus shared-block draws for paired lane contrasts."""
    count = len(per_center_arrays[0])
    if any(len(values) != count for values in per_center_arrays):
        raise ValueError("paired arrays must share a centre population")
    chunks = [chunk for chunk in np.array_split(np.arange(count), min(BOOT_BLOCKS, count)) if len(chunk)]
    sizes = np.array([len(chunk) for chunk in chunks], dtype=np.float64)
    block_means = np.array([[float(np.mean(values[chunk])) for chunk in chunks] for values in per_center_arrays])
    picks = rng.integers(0, len(chunks), size=(BOOT_DRAWS, len(chunks)))
    denominators = np.sum(sizes[picks], axis=1)
    outputs = []
    for values, means in zip(per_center_arrays, block_means):
        sampled = np.sum(means[picks] * sizes[picks], axis=1) / denominators
        outputs.append(np.concatenate([[float(np.mean(values))], sampled]))
    return outputs


def lane_offsets(lane: int, direction: str = "all") -> np.ndarray:
    offsets = np.arange(-WINDOW, WINDOW + 1, dtype=np.int64)
    mask = (offsets % 6 == lane) & (offsets != 0)
    if direction == "positive":
        mask &= offsets > 0
    elif direction == "negative":
        mask &= offsets < 0
    return offsets[mask]


def per_center_mean(values: np.ndarray, centers_idx: np.ndarray, offsets: np.ndarray) -> np.ndarray:
    return np.mean(values[centers_idx[:, None] + offsets[None, :]], axis=1)


def summarise_lane(
    group: str,
    residue: int,
    lane: int,
    direction: str,
    center_idx: np.ndarray,
    parent: np.ndarray,
    is_prime: np.ndarray,
    survivors: np.ndarray,
) -> tuple[dict, np.ndarray]:
    offsets = lane_offsets(lane, direction)
    idx = center_idx[:, None] + offsets[None, :]
    p = parent[idx]
    per_center = np.mean(p, axis=1)
    return {
        "center_group": group,
        "center_mod6": residue,
        "offset_lane_mod6": lane,
        "direction": direction,
        "center_count": int(len(center_idx)),
        "offset_count_per_center": int(len(offsets)),
        "observation_count": int(p.size),
        "parent_progress_mean": float(np.mean(p)),
        "parent_progress_sd": float(np.std(p)),
        "parent_progress_median": float(np.median(p)),
        "prime_rate": float(np.mean(is_prime[idx])),
        "survivor_rate": float(np.mean(survivors[idx])),
        "divisible_by_3_rate": float(np.mean(((LOW + idx) % 3) == 0)),
        "divisible_by_5_rate": float(np.mean(((LOW + idx) % 5) == 0)),
    }, per_center


def offset_profiles(
    groups: dict[tuple[str, int], np.ndarray],
    parent: np.ndarray,
    is_prime: np.ndarray,
    survivors: np.ndarray,
) -> list[dict]:
    rows: list[dict] = []
    for (group, residue), center_idx in groups.items():
        for offset in range(-WINDOW, WINDOW + 1):
            idx = center_idx + offset
            n = LOW + idx
            lane = offset % 6 if offset % 2 == 0 else "odd"
            rows.append({
                "center_group": group,
                "center_mod6": residue,
                "offset": offset,
                "offset_lane_mod6": lane,
                "center_count": int(len(center_idx)),
                "parent_progress_mean": float(np.mean(parent[idx])),
                "parent_progress_median": float(np.median(parent[idx])),
                "prime_rate": float(np.mean(is_prime[idx])),
                "survivor_rate": float(np.mean(survivors[idx])),
                "divisible_by_3_rate": float(np.mean(n % 3 == 0)),
                "divisible_by_5_rate": float(np.mean(n % 5 == 0)),
            })
    return rows


def mod30_matrix(
    group: str,
    center_idx: np.ndarray,
    parent: np.ndarray,
    is_prime: np.ndarray,
    survivors: np.ndarray,
) -> list[dict]:
    rows: list[dict] = []
    center_numbers = LOW + center_idx
    all_offsets = np.arange(-WINDOW, WINDOW + 1, dtype=np.int64)
    for center_mod5 in (1, 2, 3, 4):
        chosen = center_idx[center_numbers % 5 == center_mod5]
        for m_mod5 in range(5):
            offsets = all_offsets[(all_offsets % 6 == 0) & (all_offsets != 0) & (((all_offsets // 6) % 5) == m_mod5)]
            idx = chosen[:, None] + offsets[None, :]
            n = LOW + idx
            rows.append({
                "center_group": group,
                "center_mod5": center_mod5,
                "black_child_m_mod5": m_mod5,
                "offset_mod30": (6 * m_mod5) % 30,
                "predicted_factor5_collision": int((center_mod5 + m_mod5) % 5 == 0),
                "center_count": int(len(chosen)),
                "offset_count_per_center": int(len(offsets)),
                "observation_count": int(idx.size),
                "parent_progress_mean": float(np.mean(parent[idx])),
                "parent_progress_median": float(np.median(parent[idx])),
                "prime_rate": float(np.mean(is_prime[idx])),
                "survivor_rate": float(np.mean(survivors[idx])),
                "divisible_by_5_rate": float(np.mean(n % 5 == 0)),
            })
    return rows


def plot_line_panel(draw, box, title, subtitle, xs, series, bounds=(0.0, 1.02)):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=14, fill=(249, 250, 252), outline=(208, 215, 224), width=2)
    draw.text((x0 + 20, y0 + 14), title, fill=(24, 32, 44), font=font(20, True))
    draw.text((x0 + 20, y0 + 43), subtitle, fill=(76, 87, 102), font=font(13))
    left, top, right, bottom = x0 + 66, y0 + 82, x1 - 26, y1 - 48
    ymin, ymax = bounds
    def px(x): return left + (x - xs[0]) * (right - left) / (xs[-1] - xs[0])
    def py(y): return bottom - (y - ymin) * (bottom - top) / (ymax - ymin)
    for frac in (0, .25, .5, .75, 1):
        yy = top + frac * (bottom - top)
        val = ymax - frac * (ymax - ymin)
        draw.line((left, yy, right, yy), fill=(225, 230, 236), width=1)
        draw.text((x0 + 8, yy - 7), f"{val:.2f}", fill=(89, 99, 112), font=font(11))
    draw.line((px(0), top, px(0), bottom), fill=(44, 49, 57), width=2)
    lx = left
    for label, ys, color, width in series:
        points = [(px(float(x)), py(float(y))) for x, y in zip(xs, ys)]
        draw.line(points, fill=color, width=width, joint="curve")
        draw.line((lx, y1 - 23, lx + 22, y1 - 23), fill=color, width=width)
        draw.text((lx + 28, y1 - 32), label, fill=(48, 58, 70), font=font(12))
        lx += 42 + int(draw.textlength(label, font=font(12)))


def plot_bar_panel(draw, box, title, subtitle, rows):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=14, fill=(249, 250, 252), outline=(208, 215, 224), width=2)
    draw.text((x0 + 20, y0 + 14), title, fill=(24, 32, 44), font=font(20, True))
    draw.text((x0 + 20, y0 + 43), subtitle, fill=(76, 87, 102), font=font(13))
    left, top, right, bottom = x0 + 150, y0 + 84, x1 - 34, y1 - 28
    vmax = max(value for _, value, _ in rows) * 1.08
    height = (bottom - top) / len(rows)
    for i, (label, value, color) in enumerate(rows):
        yy = top + i * height + 5
        draw.text((x0 + 18, yy + 3), label, fill=(48, 58, 70), font=font(13))
        draw.rectangle((left, yy, left + value / vmax * (right-left), yy + height - 11), fill=color)
        draw.text((left + value / vmax * (right-left) + 7, yy + 3), f"{value:.4f}", fill=(48, 58, 70), font=font(12))


def plot_heatmap(draw, box, title, subtitle, matrix_rows):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=14, fill=(249, 250, 252), outline=(208, 215, 224), width=2)
    draw.text((x0 + 20, y0 + 14), title, fill=(24, 32, 44), font=font(20, True))
    draw.text((x0 + 20, y0 + 43), subtitle, fill=(76, 87, 102), font=font(13))
    left, top = x0 + 95, y0 + 95
    cell_w, cell_h = (x1 - left - 30) / 5, (y1 - top - 48) / 4
    lookup = {(int(r["center_mod5"]), int(r["black_child_m_mod5"])): r for r in matrix_rows}
    for m in range(5):
        draw.text((left + m*cell_w + cell_w/2 - 9, top - 28), f"m{m}", fill=(55,65,77), font=font(12, True))
    for row_i, p5 in enumerate((1,2,3,4)):
        draw.text((x0 + 22, top + row_i*cell_h + cell_h/2 - 8), f"p mod5={p5}", fill=(55,65,77), font=font(12))
        for m in range(5):
            r = lookup[(p5,m)]
            val = float(r["parent_progress_mean"])
            suppressed = int(r["predicted_factor5_collision"]) == 1
            color = (207, 132, 76) if suppressed else (88, 137, 191)
            xx, yy = left + m*cell_w, top + row_i*cell_h
            draw.rectangle((xx+2, yy+2, xx+cell_w-2, yy+cell_h-2), fill=color)
            draw.text((xx+cell_w/2-24, yy+cell_h/2-9), f"{val:.3f}", fill=(255,255,255), font=font(13, True))


def build_figure(offset_rows, lane_rows, matrix_rows, results):
    image = Image.new("RGB", (1680, 1220), (239, 243, 247))
    draw = ImageDraw.Draw(image)
    draw.text((42, 25), "PN10C mod-6 three-lane coupling", fill=(22,31,43), font=font(30, True))
    draw.text((42, 67), "Post-hoc diagnostic; PN10B registered verdict remains NULL", fill=(75,86,101), font=font(16))

    small = [r for r in offset_rows if r["center_group"] == "prime" and -30 <= int(r["offset"]) <= 30]
    xs = np.arange(-30,31,dtype=float)
    series=[]
    for residue, color in ((1,(55,112,179)),(5,(204,135,60))):
        ys=np.array([float(r["parent_progress_mean"]) for r in small if int(r["center_mod6"])==residue])
        series.append((f"centre {residue} mod 6",ys,color,3))
    plot_line_panel(draw,(38,105,820,585),"Orientation-conditioned event traces","The two traces should reflect under k -> -k",xs,series)

    all_lanes=[r for r in lane_rows if r["center_group"]=="prime" and r["direction"]=="all"]
    colors={0:(60,67,76),2:(68,124,190),4:(205,137,61)}
    bars=[]
    for res in (1,5):
        for lane in (0,2,4):
            row=next(r for r in all_lanes if int(r["center_mod6"])==res and int(r["offset_lane_mod6"])==lane)
            bars.append((f"centre {res}, lane {lane}",float(row["parent_progress_mean"]),colors[lane]))
    plot_bar_panel(draw,(850,105,1642,585),"Three lane means after conditioning","Black is compared with the currently admissible coloured branch",bars)

    prime_matrix=[r for r in matrix_rows if r["center_group"]=="prime"]
    plot_heatmap(draw,(38,615,820,1148),"Black lane decompressed from 6 to 30","Orange is the rotating child that collides with factor 5",prime_matrix)

    x0,y0,x1,y1=850,615,1642,1148
    draw.rounded_rectangle((x0,y0,x1,y1),radius=14,fill=(249,250,252),outline=(208,215,224),width=2)
    draw.text((x0+20,y0+14),"Diagnostic readout",fill=(24,32,44),font=font(20,True))
    items=[
        ("Red/blue swap",results["headline_contrasts"]["red_blue_swap"]),
        ("Black orientation difference",results["headline_contrasts"]["black_orientation_difference"]),
        ("Black minus admissible colour",results["headline_contrasts"]["black_minus_admissible_colour"]),
        ("Eligible minus factor-5 child",results["headline_contrasts"]["mod30_eligible_minus_suppressed"]),
    ]
    yy=y0+78
    for label,d in items:
        draw.text((x0+24,yy),label,fill=(45,55,68),font=font(15,True))
        draw.text((x0+390,yy),f"{d['estimate']:+.6f}",fill=(45,55,68),font=font(15,True))
        draw.text((x0+24,yy+26),f"95% block CI [{d['ci95_low']:+.6f}, {d['ci95_high']:+.6f}]",fill=(83,94,108),font=font(13))
        yy+=80
    draw.text((x0+24,yy+3),"Arithmetic finding",fill=(45,55,68),font=font(15,True))
    wrap=[
        "Red and blue are a conditional anti-phase pair.",
        "Black is the common mod-6-admissible route; its", 
        "apparent third-wave height is largely aggregation.",
        "Black then splits into a rotating mod-5 child trough.",
    ]
    for line in wrap:
        yy+=22
        draw.text((x0+24,yy),line,fill=(67,78,92),font=font(14))
    image.save(FIGURE)


def main() -> None:
    numbers, lpf = segmented_least_prime_factor(LOW, HIGH)
    is_prime = lpf == 0
    threshold = numbers.astype(np.float64) ** 0.45
    survivors = is_prime | (lpf.astype(np.float64) > threshold)
    parent = np.empty(len(numbers), dtype=np.float64)
    parent[is_prime] = 1.0
    composite = ~is_prime
    parent[composite] = 2.0 * np.log(lpf[composite].astype(np.float64)) / np.log(numbers[composite].astype(np.float64))

    interior = np.arange(WINDOW, len(numbers)-WINDOW, dtype=np.int64)
    prime_idx = interior[is_prime[interior]]
    rng = np.random.default_rng(SEED)
    groups: dict[tuple[str,int],np.ndarray] = {}
    for residue in (1,5):
        p = prime_idx[numbers[prime_idx] % 6 == residue]
        groups[("prime",residue)] = p
        pool = interior[composite[interior] & (numbers[interior] % 6 == residue)]
        groups[("matched_coprime_composite",residue)] = np.sort(rng.choice(pool,size=len(p),replace=False))

    offset_rows = offset_profiles(groups,parent,is_prime,survivors)
    lane_rows: list[dict] = []
    per_center: dict[tuple[str,int,int],np.ndarray] = {}
    for (group,residue), centers in groups.items():
        for direction in ("all","negative","positive"):
            for lane in (0,2,4):
                row, values = summarise_lane(group,residue,lane,direction,centers,parent,is_prime,survivors)
                lane_rows.append(row)
                if direction == "all": per_center[(group,residue,lane)] = values

    matrix_rows=[]
    for group in ("prime","matched_coprime_composite"):
        both=np.sort(np.concatenate([groups[(group,1)],groups[(group,5)]]))
        matrix_rows.extend(mod30_matrix(group,both,parent,is_prime,survivors))

    rng_boot=np.random.default_rng(SEED+1)
    draws={}
    for residue in (1,5):
        paired=paired_block_draws([per_center[("prime",residue,lane)] for lane in (0,2,4)],rng_boot)
        for lane,values in zip((0,2,4),paired): draws[("prime",residue,lane)]=values
    swap=.5*((draws[("prime",1,4)]-draws[("prime",1,2)])+(draws[("prime",5,2)]-draws[("prime",5,4)]))
    black_diff=draws[("prime",1,0)]-draws[("prime",5,0)]
    black_admissible=.5*((draws[("prime",1,0)]-draws[("prime",1,4)])+(draws[("prime",5,0)]-draws[("prime",5,2)]))
    black_pooled=.5*(draws[("prime",1,0)]+draws[("prime",5,0)])-.25*(draws[("prime",1,2)]+draws[("prime",1,4)]+draws[("prime",5,2)]+draws[("prime",5,4)])

    all_prime=np.sort(np.concatenate([groups[("prime",1)],groups[("prime",5)]]))
    offs=np.arange(-WINDOW,WINDOW+1,dtype=np.int64)
    black=offs[(offs%6==0)&(offs!=0)]
    pmod5=numbers[all_prime]%5
    suppressed=np.empty(len(all_prime)); eligible=np.empty(len(all_prime))
    for i,(idx,p5) in enumerate(zip(all_prime,pmod5)):
        m=(black//6)%5
        hit=(p5+m)%5==0
        vals=parent[idx+black]
        suppressed[i]=float(np.mean(vals[hit])); eligible[i]=float(np.mean(vals[~hit]))
    mod30_contrast=block_draws(eligible-suppressed,rng_boot)

    prof={(r["center_mod6"],r["offset"]):float(r["parent_progress_mean"]) for r in offset_rows if r["center_group"]=="prime"}
    reflected=np.array([prof[(1,k)]-prof[(5,-k)] for k in range(-WINDOW,WINDOW+1)])
    direct=np.array([prof[(1,k)]-prof[(5,k)] for k in range(-WINDOW,WINDOW+1)])

    eligible_vals=np.concatenate([per_center[("prime",1,4)],per_center[("prime",5,2)]])
    black_vals=np.concatenate([per_center[("prime",1,0)],per_center[("prime",5,0)]])
    pooled_sd=math.sqrt((float(np.var(black_vals))+float(np.var(eligible_vals)))/2)
    expected_q5=float(np.mean(2*math.log(5)/np.log(numbers[all_prime].astype(float))))

    control_means={key:float(np.mean(values)) for key,values in per_center.items() if key[0]=="matched_coprime_composite"}
    control_swap=.5*((control_means[("matched_coprime_composite",1,4)]-control_means[("matched_coprime_composite",1,2)])+
                      (control_means[("matched_coprime_composite",5,2)]-control_means[("matched_coprime_composite",5,4)]))
    control_black_admissible=.5*((control_means[("matched_coprime_composite",1,0)]-control_means[("matched_coprime_composite",1,4)])+
                                  (control_means[("matched_coprime_composite",5,0)]-control_means[("matched_coprime_composite",5,2)]))

    # Exact modular controls.
    mod3_failures=0
    for res in (1,5):
        centers=groups[("prime",res)]
        for lane in (2,4):
            expected=((res+lane)%6)==3
            sample_offsets=lane_offsets(lane)
            observed=(numbers[centers[:,None]+sample_offsets[None,:]]%3)==0
            mod3_failures+=int(np.count_nonzero(observed != expected))
    mod5_failures=0
    for idx,p5 in zip(all_prime,pmod5):
        observed=(numbers[idx+black]%5)==0
        expected=(p5+(black//6)%5)%5==0
        mod5_failures+=int(np.count_nonzero(observed!=expected))

    results={
        "status":"post_hoc_structural_diagnostic",
        "registered_pn10b_verdict_unchanged":"NULL",
        "scope":{
            "low_inclusive":LOW,"high_exclusive":HIGH,"window_each_side":WINDOW,
            "raw_integer_count":int(len(numbers)),"interior_prime_count":int(len(prime_idx)),
            "prime_centers_mod6_1":int(len(groups[("prime",1)])),
            "prime_centers_mod6_5":int(len(groups[("prime",5)])),
            "matched_composite_centers":int(len(groups[("matched_coprime_composite",1)])+len(groups[("matched_coprime_composite",5)])),
            "bootstrap_draws":BOOT_DRAWS,"bootstrap_blocks":BOOT_BLOCKS,"seed":SEED,
        },
        "definitions":{
            "parent_progress":"1 for primes; 2*log(least_prime_factor)/log(n) for composites",
            "red_blue_swap":"0.5*((M_1,4-M_1,2)+(M_5,2-M_5,4))",
            "black_lane":"nonzero offsets k=0 mod 6",
            "admissible_colour":"lane 4 for centre 1 mod6; lane 2 for centre 5 mod6",
            "black_child":"m=(k/6) mod5 within black lane",
        },
        "headline_contrasts":{
            "red_blue_swap":ci(swap),
            "black_orientation_difference":ci(black_diff),
            "black_minus_admissible_colour":{**ci(black_admissible),"standardized_difference":float(black_admissible[0]/pooled_sd)},
            "black_minus_pooled_red_blue":ci(black_pooled),
            "mod30_eligible_minus_suppressed":ci(mod30_contrast),
        },
        "reflection_test":{
            "mean_absolute_error_reflected":float(np.mean(np.abs(reflected))),
            "mean_absolute_error_direct":float(np.mean(np.abs(direct))),
            "reflected_to_direct_ratio":float(np.mean(np.abs(reflected))/np.mean(np.abs(direct))),
            "reflected_is_better":bool(np.mean(np.abs(reflected))<np.mean(np.abs(direct))),
        },
        "mechanism_checks":{
            "mod3_identity_failures":mod3_failures,
            "mod5_identity_failures":mod5_failures,
            "expected_factor5_parent_progress":expected_q5,
            "observed_suppressed_parent_progress":float(np.mean(suppressed)),
            "observed_eligible_parent_progress":float(np.mean(eligible)),
        },
        "matched_composite_control":{
            "red_blue_swap":float(control_swap),
            "black_minus_admissible_colour":float(control_black_admissible),
            "interpretation":"The same lane exchange occurs around non-prime centres coprime to 6, so the surrounding three-lane pattern is modular rather than prime-specific. The exact centre ridge remains prime-specific by definition.",
        },
        "interpretation":{
            "red_blue":"conditional anti-phase pair supported if swap CI excludes zero and reflection improves",
            "black":"independent third lane only if it remains materially above the admissible coloured branch after conditioning",
            "mod30":"black common lane contains a rotating factor-5 child trough",
            "boundary":"mechanism is established modular arithmetic; ARA supplies a relational multiscale description, not a new prime law here",
        },
    }

    # Worked examples preserve the event-level geometry.
    example_rows=[]
    for residue in (1,5):
        for center_idx in groups[("prime",residue)][:3]:
            for offset in range(-18,19):
                idx=center_idx+offset
                example_rows.append({
                    "center_prime":int(numbers[center_idx]),"center_mod6":residue,"offset":offset,
                    "n":int(numbers[idx]),"offset_mod6":offset%6,"offset_mod30":offset%30,
                    "least_prime_factor":int(lpf[idx]),"is_prime":int(is_prime[idx]),
                    "parent_progress":float(parent[idx]),"divisible_by_3":int(numbers[idx]%3==0),
                    "divisible_by_5":int(numbers[idx]%5==0),
                })

    write_csv(OFFSET_CSV,offset_rows)
    write_csv(LANE_CSV,lane_rows)
    write_csv(MATRIX_CSV,matrix_rows)
    write_csv(EXAMPLES_CSV,example_rows)
    RESULTS.write_text(json.dumps(results,indent=2),encoding="utf-8")
    build_figure(offset_rows,lane_rows,matrix_rows,results)
    print(json.dumps(results["headline_contrasts"],indent=2))
    print(json.dumps(results["reflection_test"],indent=2))
    print(json.dumps(results["mechanism_checks"],indent=2))


if __name__ == "__main__":
    main()
