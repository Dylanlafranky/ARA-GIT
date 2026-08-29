"""Pre-score visual QA for the separate flat-substrate S1 transfer control."""

from __future__ import annotations

from pathlib import Path

import cv2
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
VIDEO = HERE / "source_videos" / "Video_S1.mp4"
OUTPUT = HERE / "source_qa" / "Video_S1_CENTRAL_TRANSFER_QA.png"


def main() -> None:
    cap = cv2.VideoCapture(str(VIDEO))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    indices = list(range(0, 121, 5))
    fig, axes = plt.subplots(5, 5, figsize=(15, 13), constrained_layout=True)
    for ax, frame_index in zip(axes.flat, indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError(f"Could not decode frame {frame_index}")
        crop = frame[160:500, 120:760]
        ax.imshow(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
        ax.set_title(f"frame {frame_index} | encoded {frame_index / fps:.3f} s")
        ax.axis("off")
    fig.suptitle(
        "T409 S1 flat-substrate transfer control - visual target registration only",
        fontsize=17,
    )
    fig.savefig(OUTPUT, dpi=180)
    plt.close(fig)
    cap.release()


if __name__ == "__main__":
    main()
