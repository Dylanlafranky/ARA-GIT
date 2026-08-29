"""Fine pre-score inspection of the earliest visible coalescence frames."""

from __future__ import annotations

from pathlib import Path

import cv2
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
VIDEO_DIR = HERE / "source_videos"
OUT_DIR = HERE / "source_qa"


def make_sheet(path: Path, indices: list[int], suffix: str) -> None:
    cap = cv2.VideoCapture(str(path))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    fig, axes = plt.subplots(4, 5, figsize=(17, 11), constrained_layout=True)
    for ax, frame_index in zip(axes.flat, indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError(f"Could not decode {path.name} frame {frame_index}")
        ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ax.set_title(f"frame {frame_index} · playback {frame_index / fps:.3f} s")
        ax.axis("off")
    fig.suptitle(f"{path.name} — fine onset inspection (no ARA scoring)", fontsize=16)
    fig.savefig(OUT_DIR / f"{path.stem}_{suffix}.png", dpi=160)
    plt.close(fig)
    cap.release()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in ["Video_S1.mp4", "Video_S2.mp4", "Video_S4.mp4", "Video_S5.mp4", "Video_S6.mp4", "Video_S7.mp4"]:
        make_sheet(VIDEO_DIR / name, list(range(0, 60, 3)), "EARLY_FRAMES")
    make_sheet(VIDEO_DIR / "Video_S3.mp4", list(range(0, 120, 6)), "FIRST_CASCADE_FRAMES")


if __name__ == "__main__":
    main()
