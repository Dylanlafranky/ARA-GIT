"""Render a fixed contact sheet for the T360 public Plinko source video."""

from pathlib import Path

import cv2
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
VIDEO = HERE / "T360_SOURCE_GEORGIA_TECH_MAGNETIC_PLINKO_EXPERIMENT.mp4"
OUT = HERE / "T360_SOURCE_CONTACT_SHEET.png"
BOARD_OUT = HERE / "T360_SOURCE_BOARD_FRAME0.png"


def main() -> None:
    cap = cv2.VideoCapture(str(VIDEO))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {VIDEO}")
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    indices = [round(i * (count - 1) / 14) for i in range(15)]

    fig, axes = plt.subplots(3, 5, figsize=(15, 8.5), constrained_layout=True)
    for ax, frame_index in zip(axes.flat, indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError(f"Could not read frame {frame_index}")
        ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ax.set_title(f"frame {frame_index} · {frame_index / fps:.2f} s", fontsize=9)
        ax.set_axis_off()
    cap.release()
    fig.suptitle(
        "T360 source inspection — Georgia Tech magnetic Plinko experiment",
        fontsize=15,
        fontweight="bold",
    )
    fig.savefig(OUT, dpi=170, facecolor="white")
    plt.close(fig)

    cap = cv2.VideoCapture(str(VIDEO))
    ok, first = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError("Could not read source frame 0")
    board = first[88:342, 120:316]
    board = cv2.resize(board, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(str(BOARD_OUT), board)


if __name__ == "__main__":
    main()
