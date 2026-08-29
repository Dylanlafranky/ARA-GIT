"""Source-only QA for T424 hourglass videos.

This script intentionally does not construct or score any ARA coordinate. It
records video metadata and evenly spaced frame contact sheets so apparatus
geometry can be registered under the frozen protocol's source-QA exception.
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_data"
OUT = ROOT / "source_qa"
VERIFIED_CONDITION_BOUNDARIES = {
    "SN101_Alumina_060.mp4": [200, 400, 600, 800, 1000, 1200, 1400],
    "SN101_Alumina_120.mp4": [200, 400, 600, 800, 1000, 1200, 1400],
    "SN102_SilicaSandNo5_060.mp4": [200, 400, 600, 800, 1000, 1200, 1400],
    "SN102_SilicaSandNo5_120.mp4": [200, 400, 600, 800, 1000, 1200, 1400],
    "SN103_ToyouraSand_060.mp4": [271, 551, 823, 1117, 1396, 1691, 1974],
    "SN103_ToyouraSand_120.mp4": [304, 576, 859, 1130, 1409, 1689, 1967],
}


def read_frame(cap: cv2.VideoCapture, index: int) -> np.ndarray:
    cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    ok, frame = cap.read()
    if not ok:
        raise RuntimeError(f"Could not decode frame {index}")
    return frame


def contact_sheet(path: Path, samples: int = 12) -> dict[str, object]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {path}")
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    indices = np.linspace(0, max(frames - 1, 0), samples, dtype=int)

    # Detect the seven published AG-condition changes from the on-screen
    # "AG = ... G" label alone. The sand and both ARA measurement regions are
    # deliberately outside this crop, keeping segmentation source-only.
    label_frames: list[np.ndarray] = []
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    for index in range(frames):
        ok, frame = cap.read()
        if not ok:
            break
        label_gray = cv2.cvtColor(
            frame[
                int(0.075 * height) : int(0.15 * height),
                int(0.14 * width) : int(0.38 * width),
            ],
            cv2.COLOR_BGR2GRAY,
        )
        # Keep the bright numeric overlay glyphs and suppress the apparatus.
        label_frames.append(label_gray >= 205)
    label_stack = np.asarray(label_frames, dtype=bool)
    reference_centres = [int(round((k + 0.5) * frames / 8)) for k in range(8)]
    references = []
    for centre in reference_centres:
        lo = max(0, centre - 2)
        hi = min(frames, centre + 3)
        references.append(np.mean(label_stack[lo:hi], axis=0) >= 0.5)
    distances = np.asarray(
        [np.mean(label_stack != reference, axis=(1, 2)) for reference in references],
        dtype=float,
    )
    detected_boundaries: list[int] = []
    boundary_margins: list[float] = []
    for state in range(7):
        lo = reference_centres[state]
        hi = reference_centres[state + 1]
        delta = distances[state + 1, lo:hi] - distances[state, lo:hi]
        kernel = np.ones(7, dtype=float) / 7.0
        smooth = np.convolve(delta, kernel, mode="same")
        crossings = np.flatnonzero(smooth < 0)
        if len(crossings):
            local = int(crossings[0])
        else:
            local = int(np.argmin(np.abs(smooth)))
        boundary = lo + local
        detected_boundaries.append(boundary)
        boundary_margins.append(float(abs(smooth[local])))

    thumbs: list[np.ndarray] = []
    for index in indices:
        frame = read_frame(cap, int(index))
        scale = min(300 / frame.shape[1], 240 / frame.shape[0])
        thumb = cv2.resize(frame, None, fx=scale, fy=scale)
        cv2.putText(
            thumb,
            f"f={index}  t={index / fps:.2f}s",
            (8, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            thumb,
            f"f={index}  t={index / fps:.2f}s",
            (8, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )
        thumbs.append(thumb)
    # Source-layout QA: show the last frame before and first frame after each
    # nominal one-eighth boundary. This checks editorial segmentation only;
    # it does not inspect or score either ARA coordinate.
    boundary_pairs: list[tuple[np.ndarray, np.ndarray]] = []
    boundary_label_pairs: list[tuple[np.ndarray, np.ndarray]] = []
    nominal = frames / 8
    nominal_boundaries = [int(round(k * nominal)) for k in range(1, 8)]
    boundaries = VERIFIED_CONDITION_BOUNDARIES[path.name]
    for boundary in boundaries:
        pair: list[np.ndarray] = []
        label_pair: list[np.ndarray] = []
        for index, tag in ((boundary - 1, "before"), (boundary, "after")):
            frame = read_frame(cap, index)
            label_crop = frame[: max(90, int(0.16 * frame.shape[0])), : int(0.72 * frame.shape[1])]
            label_crop = cv2.resize(label_crop, None, fx=1.8, fy=1.8)
            cv2.putText(label_crop, f"{tag} f={index}", (8, label_crop.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(label_crop, f"{tag} f={index}", (8, label_crop.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
            label_pair.append(label_crop)
            scale = min(270 / frame.shape[1], 220 / frame.shape[0])
            thumb = cv2.resize(frame, None, fx=scale, fy=scale)
            label = f"{tag} f={index}"
            cv2.putText(thumb, label, (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(thumb, label, (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 0), 1, cv2.LINE_AA)
            pair.append(thumb)
        boundary_pairs.append((pair[0], pair[1]))
        boundary_label_pairs.append((label_pair[0], label_pair[1]))
    rows = []
    for start in range(0, len(thumbs), 4):
        row = thumbs[start : start + 4]
        while len(row) < 4:
            row.append(np.zeros_like(thumbs[0]))
        rows.append(cv2.hconcat(row))
    sheet = cv2.vconcat(rows)
    out_path = OUT / f"{path.stem}_contact_sheet.jpg"
    cv2.imwrite(str(out_path), sheet, [cv2.IMWRITE_JPEG_QUALITY, 92])
    boundary_rows = [cv2.hconcat([before, after]) for before, after in boundary_pairs]
    boundary_sheet = cv2.vconcat(boundary_rows)
    boundary_path = OUT / f"{path.stem}_montage_boundaries.jpg"
    cv2.imwrite(str(boundary_path), boundary_sheet, [cv2.IMWRITE_JPEG_QUALITY, 92])
    label_rows = [cv2.hconcat([before, after]) for before, after in boundary_label_pairs]
    label_sheet = cv2.vconcat(label_rows)
    label_path = OUT / f"{path.stem}_boundary_labels.jpg"
    cv2.imwrite(str(label_path), label_sheet, [cv2.IMWRITE_JPEG_QUALITY, 95])

    # Coarse label-only timeline for human verification of unequal-duration
    # condition blocks in the public montage.
    timeline_thumbs: list[np.ndarray] = []
    timeline_step = max(40, int(round(frames / 28)))
    for index in range(0, frames, timeline_step):
        frame = read_frame(cap, index)
        crop = frame[: int(0.19 * frame.shape[0]), : int(0.58 * frame.shape[1])]
        crop = cv2.resize(crop, None, fx=0.72, fy=0.72)
        cv2.putText(crop, f"f={index}", (8, crop.shape[0] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(crop, f"f={index}", (8, crop.shape[0] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        timeline_thumbs.append(crop)
    timeline_rows: list[np.ndarray] = []
    for start in range(0, len(timeline_thumbs), 4):
        row = timeline_thumbs[start : start + 4]
        while len(row) < 4:
            row.append(np.zeros_like(timeline_thumbs[0]))
        timeline_rows.append(cv2.hconcat(row))
    timeline_path = OUT / f"{path.stem}_label_timeline.jpg"
    cv2.imwrite(str(timeline_path), cv2.vconcat(timeline_rows), [cv2.IMWRITE_JPEG_QUALITY, 95])
    cap.release()
    return {
        "name": path.name,
        "frames": frames,
        "fps": fps,
        "width": width,
        "height": height,
        "duration_s": frames / fps,
        "sample_indices": indices.tolist(),
        "nominal_boundaries": nominal_boundaries,
        "detected_label_boundaries": detected_boundaries,
        "verified_condition_boundaries": boundaries,
        "label_reference_centres": reference_centres,
        "detected_label_margin": boundary_margins,
        "contact_sheet": str(out_path.relative_to(ROOT)),
        "montage_boundaries": str(boundary_path.relative_to(ROOT)),
        "boundary_labels": str(label_path.relative_to(ROOT)),
        "label_timeline": str(timeline_path.relative_to(ROOT)),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = [contact_sheet(path) for path in sorted(SOURCE.glob("*.mp4"))]
    (OUT / "video_metadata.json").write_text(
        json.dumps(records, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
