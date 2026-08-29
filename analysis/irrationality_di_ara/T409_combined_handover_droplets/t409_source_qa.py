"""Pre-score source inspection for T409 combined handover Di-ARA.

This script only decodes the seven public supplementary videos and builds
uniform contact sheets.  It does not calculate ARA coordinates, detect bridge
times, select landmarks, or score the frozen hypothesis.
"""

from __future__ import annotations

import csv
from pathlib import Path

import cv2
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
VIDEO_DIR = HERE / "source_videos"
OUT_DIR = HERE / "source_qa"
META_CSV = OUT_DIR / "T409_SOURCE_METADATA.csv"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []

    for path in sorted(VIDEO_DIR.glob("Video_S*.mp4")):
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            raise RuntimeError(f"Could not open {path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_s = frame_count / fps if fps else float("nan")

        rows.append(
            {
                "video": path.name,
                "width_px": width,
                "height_px": height,
                "encoded_fps": fps,
                "frame_count": frame_count,
                "encoded_duration_s": duration_s,
            }
        )

        indices = [round(i * (frame_count - 1) / 11) for i in range(12)]
        fig, axes = plt.subplots(3, 4, figsize=(16, 9), constrained_layout=True)
        for ax, frame_index in zip(axes.flat, indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError(f"Could not decode {path.name} frame {frame_index}")
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ax.imshow(frame_rgb)
            ax.set_title(f"frame {frame_index} · playback {frame_index / fps:.2f} s")
            ax.axis("off")

        fig.suptitle(
            f"{path.name} — uniform pre-score source inspection\n"
            f"{width}×{height} px · {frame_count} frames · encoded {fps:.3f} fps",
            fontsize=15,
        )
        fig.savefig(OUT_DIR / f"{path.stem}_CONTACT_SHEET.png", dpi=150)
        plt.close(fig)
        cap.release()

    with META_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
