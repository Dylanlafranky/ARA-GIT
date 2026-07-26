"""Build and execute the durable Q27 analytical notebook.

This notebook is a compact reader-facing companion to the checksum-locked
runner. It reads frozen outputs only; raw extraction and numerical analysis
remain in q27_ara9_network_reconstruction_test.py.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import asyncio


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

RUNTIME = HERE / ".q27_jupyter"
IPYTHON_DIR = RUNTIME / "ipython"
JUPYTER_DATA = RUNTIME / "data"
JUPYTER_CONFIG = RUNTIME / "config"
for directory in (IPYTHON_DIR, JUPYTER_DATA, JUPYTER_CONFIG):
    directory.mkdir(parents=True, exist_ok=True)
os.environ["IPYTHONDIR"] = str(IPYTHON_DIR)
os.environ["JUPYTER_DATA_DIR"] = str(JUPYTER_DATA)
os.environ["JUPYTER_CONFIG_DIR"] = str(JUPYTER_CONFIG)

kernel_dir = JUPYTER_DATA / "kernels" / "python3"
kernel_dir.mkdir(parents=True, exist_ok=True)
(kernel_dir / "kernel.json").write_text(
    json.dumps(
        {
            "argv": [
                sys.executable,
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
            "display_name": "Python 3 (Q27 isolated)",
            "language": "python",
        },
        indent=2,
    ),
    encoding="utf-8",
)

import nbformat
from nbclient import NotebookClient


OUTPUT = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_NOTEBOOK.ipynb"


def code(source: str):
    return nbformat.v4.new_code_cell(source.strip())


def markdown(source: str):
    return nbformat.v4.new_markdown_cell(source.strip())


def main() -> None:
    notebook = nbformat.v4.new_notebook()
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook["metadata"]["language_info"] = {"name": "python", "version": "3"}
    notebook["cells"] = [
        markdown(
            """
# Q27 — ARA⁹ Network Reconstruction

## TL;DR

The registered strict verdict is **INCONCLUSIVE** because one frozen
source-quality gate failed: the largest sampled trace error was
`2.53e-05`, above the runner's `1e-05` threshold.

The two substantive registered branches can still be evaluated
conditionally:

- A local crest → trough → crest pattern was common (88.20%), but the
  registered symmetric return clock failed: only 31.82% met the timing
  tolerance and its mirror forecast was worse than both controls.
- Only 2.58% of non-returning sources produced the registered strong
  direct-neighbour crest.
- A weaker, precisely ordered network-transfer relation survived both
  null controls: exact overlap 0.2768 versus pair-shuffle median 0.2072
  and circular-time median 0.2261.

Therefore this run does **not** establish a simple doubled resonance wave,
a strong Phase-B recipient crest, an orientation flip, or universal
fractal physics. It does show stable ARA-compressed closure geometry and
a non-random adjacency/time-ordered transfer relation in this complete
simulated network dataset.
"""
        ),
        markdown(
            """
## Context & Methods

Q27 was frozen before numerical values were opened. The public source has
two network-connectivity strata, 100 unitary seeds per stratum, 500 time
steps per seed, and all 66 unordered two-qubit density matrices per step.

For each pair, the ARA cut is formed from the connected correlation block
`C = T - a bᵀ`. Its amplitude is `h = |det(C)|^(1/3)`, normalized onto the
0–2 diameter using the exposed half's 95th percentile. Development used
times 0–249; times 250–499 were held out.

The complete raw extraction and analysis are reproducible with
`q27_ara9_network_reconstruction_test.py`. This notebook independently
loads and displays the frozen outputs and validation result.
"""
        ),
        code(
            """
from pathlib import Path
from IPython.display import Image, display
import json

HERE = Path.cwd()
if not (HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_RESULTS.json").exists():
    HERE = Path(r"F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/quantum")

results = json.loads(
    (HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_RESULTS.json").read_text(
        encoding="utf-8"
    )
)
validation = json.loads(
    (HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_VALIDATION.json").read_text(
        encoding="utf-8"
    )
)
assert validation["status"] == "PASS"
assert validation["passed"] == validation["checks"] == 46
assert results["verdict"] == "INCONCLUSIVE"
print("Independent validation:", validation["status"], "46/46")
print("Frozen strict verdict:", results["verdict"])
"""
        ),
        markdown("## Data"),
        code(
            """
source = results["source"]
quality = results["data_quality"]
print("DOI:", source["doi"])
print("Archive MD5:", source["archive_md5"])
print("HDF5 SHA-256:", source["hdf5_sha256"])
print("Matrices used:", 2 * 100 * 500 * 66)
print("QC sample:", quality["sampled_matrices"])
print("Maximum trace error:", quality["maximum_trace_error"])
print("Maximum Hermiticity error:", quality["maximum_hermiticity_error"])
print("Minimum eigenvalue:", quality["minimum_eigenvalue"])
print("PSD failures below -1e-6:", quality["psd_failures_below_minus_1e_6"])
"""
        ),
        markdown("## Results"),
        code(
            """
pooled = next(row for row in results["branches"] if row["stratum"] == "pooled")
controls = results["controls"]
summary = {
    "eligible sources": pooled["eligible_sources"],
    "local reconstruction": pooled["local_reconstruction_fraction"],
    "timing hit": pooled["timing_hit_fraction"],
    "direct-neighbour crest": pooled["direct_neighbour_transfer_fraction"],
    "mirror MAE": pooled["mirror_mae"],
    "persistence MAE": pooled["persistence_mae"],
    "no-return MAE": pooled["no_return_mae"],
    "exact ordered overlap": controls["exact_transfer_overlap"],
    "pair-shuffle median": controls["pair_shuffle_quantiles"]["median"],
    "circular-time median": controls["circular_time_quantiles"]["median"],
    "stable orientation flip": pooled["stable_orientation_flip_fraction"],
}
for label, value in summary.items():
    print(f"{label:28s} {value}")
"""
        ),
        code(
            """
display(Image(filename=str(HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_GEOMETRY.png")))
"""
        ),
        markdown(
            """
### Gate interpretation

The visual recurrence alone is not enough to support the frozen parent-wave
claim. The registered model also required the return timing to be predictable
and the mirrored trajectory to beat simple controls; neither happened.

The network transfer control is narrower but genuine inside this simulator:
the source's release and its actual active neighbours' accumulation overlap
more than after either pair-label shuffling or circular time displacement.
That supports an ordered coupling relation, not the stronger claim that a
single neighbour becomes a crest-level Phase-B recipient.
"""
        ),
        code(
            """
for gate, passed in results["gates"].items():
    print(f"{gate:42s} {'PASS' if passed else 'FAIL'}")
"""
        ),
        markdown(
            """
## Takeaways

### ARA reading

The ARA cut reliably exposes a common local closure sequence and preserves
enough relational information to identify a real source-to-neighbour transfer
structure. But the larger motion is not a simple symmetric x2 resonance clock,
and the registered transfer does not close as one dominant neighbour crest.
The next ARA test should model a distributed, delayed coupling web rather than
promoting this weaker overlap result into the failed stronger branch.

### Established-physics reading

The dataset consists of simulated reduced two-qubit density-matrix trajectories
from larger unitary networks. Correlations can leave one reduced pair and
spread among several adjacent relations without appearing as a single
recipient's large peak. Q27's control result is compatible with that distributed
network behaviour.

### Evidence boundary

This is a checksum-locked test on complete public simulated data. It does not
yet demonstrate a new quantum law, a hardware effect, or universal fractality.
"""
        ),
        markdown(
            """
## Reproduction

From `analysis/quantum`:

```powershell
python q27_ara9_network_reconstruction_test.py all --workers 6
python q27_ara9_network_reconstruction_validate.py
python q27_build_notebook.py
```

If absent, the main runner automatically downloads and verifies the frozen
Zenodo archive before extracting it. The source and derived cache are excluded
from Git because they are large and reproducible.
"""
        ),
    ]

    client = NotebookClient(
        notebook,
        timeout=300,
        startup_timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(HERE)}},
    )
    executed = client.execute()
    nbformat.write(executed, OUTPUT)
    print(f"Executed notebook written: {OUTPUT}")


if __name__ == "__main__":
    main()
