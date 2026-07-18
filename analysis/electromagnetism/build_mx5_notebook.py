"""Build the reproducible MX5 child-ARA / TE-ARA closure notebook."""

from pathlib import Path

import nbformat as nbf


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "MX5_CHILD_ARA_TEARA_CLOSURE_NOTEBOOK.ipynb"
SOURCE = Path(
    r"F:\SystemFormulaFolder\work_tmp\ara_mx4\legacy_datasets\picongpu-0.5.0-hdf5-plugin\simData_200.h5"
)

notebook = nbf.v4.new_notebook()
notebook["metadata"] = {
    "kernelspec": {
        "display_name": "ARA verification Python",
        "language": "python",
        "name": "python3",
    },
    "language_info": {"name": "python", "version": "3.14"},
}
notebook["cells"] = [
    nbf.v4.new_markdown_cell(
        """# MX5 child-ARA / TE-ARA closure notebook

## TL;DR

- Exact child-ARA reassembly passed at `3.99e-15` relative grid error.
- Flat parent plus exact Other passed at `9.44e-17`; this is an identity, not a prediction.
- The unfitted first child-moment closure achieved **partial recovery**: correlation `0.477 -> 0.605`, NRMSE `0.888 -> 0.802`, and median angle `61.68 deg -> 48.47 deg`.
- A post-freeze descriptive TE-ARA species drill separated active child identities from their quiet aggregate: electron and ion internal medians were `1.218/2` and `1.145/2`, but the species pair had nearly equal magnitude (`x=1.0002`), a `177.55 deg` median angle and only `0.0718/2` surviving coherence. It was not an outcome gate.
- Interpretation: useful multiscale bookkeeping and an incomplete compact closure; not new plasma physics or a universal ARA confirmation.
"""
    ),
    nbf.v4.new_markdown_cell(
        r"""## Context & Methods

### Key assumptions

- The public PIConGPU/openPMD source is hash locked.
- The same CIC parent operator and active-cell mask as MX4 are retained for comparability.
- Versions A and B are identity checks. Only Version C tests compression.
- TE-ARA is a dimensionless force/activity diagnostic here, not joules.

The compact closure is

\[
\widehat{\mathbf F}^{(1)}
=\bar\rho\bar{\mathbf E}+\bar{\mathbf J}\times\bar{\mathbf B}
+\sum_a P_{\rho,a}\partial_a\bar{\mathbf E}
+\sum_a \mathbf M_{J,a}\times\partial_a\bar{\mathbf B}.
\]

See `MX5_CHILD_ARA_TEARA_CLOSURE_PROTOCOL_v1_FROZEN.md` for the frozen gates and claim boundaries.
"""
    ),
    nbf.v4.new_code_cell(
        f"""from pathlib import Path
import json
import subprocess
import sys
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(r"{HERE}")
SOURCE = Path(r"{SOURCE}")
assert SOURCE.exists(), f"Missing public source file: {{SOURCE}}"
print('Python:', sys.executable)
print('Source:', SOURCE)
print('Working folder:', HERE)
"""
    ),
    nbf.v4.new_markdown_cell(
        """## Data

The next cell reruns the primary analysis and then independently recalculates the exported headline metrics from the cell-level CSV.
"""
    ),
    nbf.v4.new_code_cell(
        """commands = [
    [sys.executable, str(HERE / 'mx5_child_ara_teara_closure.py'), '--source', str(SOURCE), '--output-dir', str(HERE)],
    [sys.executable, str(HERE / 'mx5_validate_outputs.py'), '--source', str(SOURCE), '--results-dir', str(HERE)],
]
for command in commands:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    print(Path(command[1]).name, 'completed')
"""
    ),
    nbf.v4.new_markdown_cell("## Results"),
    nbf.v4.new_code_cell(
        """results = json.loads((HERE / 'MX5_CHILD_ARA_TEARA_CLOSURE_RESULTS.json').read_text(encoding='utf-8'))
validation = json.loads((HERE / 'MX5_CHILD_ARA_TEARA_VALIDATION.json').read_text(encoding='utf-8'))
print('Independent validation:', validation['validation_pass'])
print('Version A pass:', results['version_a_exact_child_ara']['gate_le_1e-12'])
print('Version B pass:', results['version_b_parent_plus_exact_other']['gate_le_1e-12'])
print('Version C classification:', results['version_c_first_moment_gradient']['classification'])
"""
    ),
    nbf.v4.new_code_cell(
        """flat = results['flat_parent_recalculation']['channels']['total']
first = results['version_c_first_moment_gradient']['channels']['total']
pd.DataFrame([
    {'version': 'flat parent', 'correlation': flat['vector_correlation'], 'NRMSE': flat['nrmse_by_target_std'], 'median_angle_deg': flat['median_angular_error_deg']},
    {'version': 'first child moment', 'correlation': first['vector_correlation'], 'NRMSE': first['nrmse_by_target_std'], 'median_angle_deg': first['median_angular_error_deg']},
])
"""
    ),
    nbf.v4.new_code_cell(
        """diagnostics = results['version_b_parent_plus_exact_other']['diagnostics']
pd.DataFrame([
    {'identity': 'all particles', 'median_TE_force': diagnostics['te_force_coherence']['p50']},
    {'identity': 'electrons internally', 'median_TE_force': diagnostics['species_internal_te_force_coherence']['e']['p50']},
    {'identity': 'ions internally', 'median_TE_force': diagnostics['species_internal_te_force_coherence']['i']['p50']},
    {'identity': 'electron/ion pair', 'median_TE_force': diagnostics['species_pair_te_force_coherence']['p50']},
])
"""
    ),
    nbf.v4.new_code_cell(
        """print('Species magnitude coordinate median:', diagnostics['species_pair_ion_coordinate']['p50'])
print('Species force angle median:', diagnostics['species_pair_angle_deg']['p50'])
print('Other-dominant cell fraction:', diagnostics['fraction_other_dominant_x_gt_1'])
print('Median Parent/Other coordinate:', diagnostics['x_other']['p50'])
"""
    ),
    nbf.v4.new_code_cell(
        """image = plt.imread(HERE / 'MX5_CHILD_ARA_TEARA_CLOSURE.png')
plt.figure(figsize=(15, 11))
plt.imshow(image)
plt.axis('off')
plt.show()
"""
    ),
    nbf.v4.new_markdown_cell(
        """## Takeaways

1. ARA reassembly is lossless only when the channel envelope and vector directions are retained with the A/B coordinate.
2. TE-ARA-style force participation resolves a child/parent hierarchy that the aggregate force obscures.
3. The exact Other is large on this snapshot, but defining it is not predicting it.
4. One unfitted positional moment improves every headline metric and both spatial halves, but misses the strong recovery gate.
5. The next clean extension is a separately frozen second-moment/resolution-transfer test, not retrospective tuning of MX5.
"""
    ),
]

nbf.validate(notebook)
nbf.write(notebook, OUTPUT)
print(OUTPUT)
