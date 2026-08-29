"""Build the executed, reader-facing T435 notebook companion."""

from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T435_ANALYSIS.ipynb"

nb = nbf.v4.new_notebook()
nb["metadata"]["kernelspec"] = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}
nb["metadata"]["language_info"] = {"name": "python", "version": "3.12"}

nb["cells"] = [
    nbf.v4.new_markdown_cell(
        "# T435 — blind ARA binary-identity inversion\n\n"
        "**TL;DR:** the sealed waveform-only inversion recovered the two-hole axis, "
        "the common closing relation, and correlated child radial histories, but its "
        "three-landmark common-horizon clock was 37.54 M late. The frozen verdict is "
        "**PARTIAL**, and the individual child-share magnitudes remain unresolved."
    ),
    nbf.v4.new_markdown_cell(
        "## Context & methods\n\n"
        "The prediction stage read only the combined SXS strain modes. It used "
        "`phase(h22)/2` for the antipodal child axis, odd/even modal imbalance for "
        "the unordered child split, and reverse cadence rank for the remaining relation. "
        "The prediction NPZ was hashed before the individual A/B and common C horizons "
        "were revealed. See `T435_FROZEN_PROTOCOL.md` for the complete predeclared rules."
    ),
    nbf.v4.new_markdown_cell(
        "## Data\n\n"
        "Source: SXS:BBH:0305 Lev6, Zenodo record 13182440. Inference used "
        "`Strain_N4`; scoring used horizon coordinate centers and masses. Time is in "
        "simulation units M. This is a numerical-relativity crosswalk, not independent "
        "observational evidence."
    ),
    nbf.v4.new_code_cell(
        "import hashlib, json\n"
        "from pathlib import Path\n"
        "import pandas as pd\n"
        "from IPython.display import display, Image\n\n"
        "ROOT = Path.cwd()\n"
        "RESULTS = ROOT / 'results'\n"
        "scored = json.loads((RESULTS / 'T435_SCORED_RESULT.json').read_text())\n"
        "sealed = (RESULTS / 'T435_PREDICTION_SHA256.txt').read_text().splitlines()[0].split()[-1]\n"
        "current = hashlib.sha256((RESULTS / 'T435_WAVEFORM_ONLY_PREDICTION.npz').read_bytes()).hexdigest()\n"
        "assert sealed == current\n"
        "print('prediction seal verified:', current)\n"
        "print('frozen result:', scored['result'])"
    ),
    nbf.v4.new_markdown_cell("## Results"),
    nbf.v4.new_code_cell(
        "m = scored['metrics']\n"
        "rows = [\n"
        "    ('Orientation coherence', m['orientation_axis_coherence'], 0.80, scored['gates']['orientation']),\n"
        "    ('Unhalved control', m['unhalved_phase_control_coherence'], None, None),\n"
        "    ('Relation Spearman', m['relation_spearman'], 0.70, scored['gates']['relation']),\n"
        "    ('Shift control', m['circular_shift_control_spearman'], None, None),\n"
        "    ('Child-radius median Spearman', m['child_radius_median_spearman'], 0.50, scored['gates']['child_radii']),\n"
        "    ('Child-share MAE', m['child_share_mean_absolute_error'], None, None),\n"
        "    ('Handover error / M', m['handover_absolute_error'], m['parent_waveform_cycle_at_prediction'], scored['gates']['handover_timing']),\n"
        "]\n"
        "display(pd.DataFrame(rows, columns=['metric', 'value', 'frozen threshold', 'pass']))"
    ),
    nbf.v4.new_code_cell(
        "display(Image(filename=str(RESULTS / 'T435_BLIND_BINARY_INVERSION_AUDIT.png'), width=1200))"
    ),
    nbf.v4.new_markdown_cell(
        "## Takeaways\n\n"
        "1. The ARA half-phase/octave operation selected the correct two-child axis; the "
        "unhalved control nearly erased coherence.\n"
        "2. Cadence ordering recovered the A–B closing relation, but its near-perfect rank "
        "score does not establish absolute distance.\n"
        "3. The two radial histories share that closing trend. The 0.0858 child-share error "
        "means the full identities are not yet separated.\n"
        "4. The frozen median handover clock failed even though the total-power peak alone "
        "was close; that post-result observation cannot rescue the gate.\n"
        "5. The next decisive test is a multi-simulation holdout that predicts hidden mass "
        "contrast from one fixed waveform-only child-split mapping."
    ),
]

nbf.write(nb, OUT)
client = NotebookClient(nb, timeout=300, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}})
executed = client.execute(cwd=str(ROOT))
nbf.write(executed, OUT)
print(OUT)
