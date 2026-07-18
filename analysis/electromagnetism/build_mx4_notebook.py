"""Build the reproducible MX4 Lorentz/ARA audit notebook."""

from pathlib import Path

import nbformat as nbf


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "MX4_LORENTZ_ARA_AUDIT_NOTEBOOK.ipynb"
SOURCE = Path(
    r"F:\SystemFormulaFolder\work_tmp\ara_mx4\legacy_datasets\picongpu-0.5.0-hdf5-plugin\simData_200.h5"
)

notebook = nbf.v4.new_notebook()
notebook["metadata"] = {
    "kernelspec": {"display_name": "ARA verification Python", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.14"},
}
notebook["cells"] = [
    nbf.v4.new_markdown_cell(
        """# MX4 Lorentz-force ↔ ARA audit notebook

## TL;DR

- Public PIConGPU snapshot: 225,449 electrons, 225,280 ions, full **E** and **B** fields.
- Particle-rung ARA reconstruction passed at about `1.3e-16` relative error.
- Magnetic work and total-power identities passed at floating-point precision.
- The frozen CIC particle-to-grid bridge failed: correlation `0.477`, NRMSE `0.888`, median angle error `61.7°`.
- A quadratic-deposition sensitivity recovered stored charge density almost exactly but did not repair the force bridge (`r=0.405`).
- Interpretation: separate parent averages omit within-cell covariance/subgrid relations. No independent acceleration test is possible from one snapshot.
"""
    ),
    nbf.v4.new_markdown_cell(
        r"""## Context & Methods

The particle force is split into the established channels

\[
\mathbf f_E=q\mathbf E,\qquad
\mathbf f_B=q(\mathbf v\times\mathbf B),\qquad
\mathbf f=\mathbf f_E+\mathbf f_B.
\]

The frozen ARA coordinate is

\[
x_F=\frac{2|\mathbf f_B|}{|\mathbf f_E|+|\mathbf f_B|},
\]

with a separate envelope and channel angle. The coarse-graining test compares particle-first force deposition with field-first `rho*E + J×B`. The protocol and interpretation ceilings are recorded in `MX4_LORENTZ_ARA_CROSSWALK_PROTOCOL_v1_FROZEN.md`.
"""
    ),
    nbf.v4.new_code_cell(
        f"""from pathlib import Path
import json
import subprocess
import sys
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(r\"{HERE}\")
SOURCE = Path(r\"{SOURCE}\")
assert SOURCE.exists(), f\"Missing public source file: {{SOURCE}}\"
print('Python:', sys.executable)
print('Source:', SOURCE)
print('Working folder:', HERE)
"""
    ),
    nbf.v4.new_markdown_cell(
        """## Data and full rerun

The next cell executes the frozen primary analysis, the independent output validator and the post-freeze quadratic-deposition sensitivity. Source hashes are checked by the scripts before calculation.
"""
    ),
    nbf.v4.new_code_cell(
        """commands = [
    [sys.executable, str(HERE / 'mx4_lorentz_ara_crosswalk.py'), '--source', str(SOURCE), '--output-dir', str(HERE)],
    [sys.executable, str(HERE / 'mx4_validate_outputs.py'), '--source', str(SOURCE), '--results-dir', str(HERE)],
    [sys.executable, str(HERE / 'mx4_quadratic_deposition_sensitivity.py'), '--source', str(SOURCE), '--results-dir', str(HERE)],
]
for command in commands:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    print(Path(command[1]).name, 'completed')
"""
    ),
    nbf.v4.new_markdown_cell("## Results"),
    nbf.v4.new_code_cell(
        """results = json.loads((HERE / 'MX4_LORENTZ_ARA_RESULTS.json').read_text(encoding='utf-8'))
rows = []
for species, values in results['mx4_l1_particle_rung'].items():
    rows.append({
        'level': 'particle',
        'item': species,
        'n': values['n_particles'],
        'reconstruction_error': values['reconstruction_relative_l2'],
        'magnetic_work_leakage': values['magnetic_work_normalised_rms'],
        'median_x_F': values['x_force']['p50'],
    })
pd.DataFrame(rows)
"""
    ),
    nbf.v4.new_code_cell(
        """grid = results['mx4_l2_grid_rung']
grid_rows = []
for channel, values in grid['channels'].items():
    grid_rows.append({
        'channel': channel,
        'vector_correlation': values['vector_correlation'],
        'NRMSE': values['nrmse_by_target_std'],
        'magnitude_ratio': values['l2_magnitude_ratio'],
        'median_angle_deg': values['median_angular_error_deg'],
    })
print('Frozen classification:', grid['classification'])
pd.DataFrame(grid_rows)
"""
    ),
    nbf.v4.new_code_cell(
        """validation = json.loads((HERE / 'MX4_LORENTZ_ARA_VALIDATION.json').read_text(encoding='utf-8'))
sensitivity = json.loads((HERE / 'MX4_QUADRATIC_DEPOSITION_SENSITIVITY_RESULTS.json').read_text(encoding='utf-8'))
print('Independent validation pass:', validation['validation_pass'])
print('Quadratic charge-density total correlation:', sensitivity['charge_density_validation']['total']['pearson'])
print('Quadratic force bridge correlation:', sensitivity['channels']['total']['vector_correlation'])
print('Quadratic classification:', sensitivity['classification'])
"""
    ),
    nbf.v4.new_code_cell(
        """image = plt.imread(HERE / 'MX4_LORENTZ_ARA_CROSSWALK.png')
plt.figure(figsize=(15, 11))
plt.imshow(image)
plt.axis('off')
plt.show()
"""
    ),
    nbf.v4.new_markdown_cell(
        """## Takeaways

1. The local ARA coordinate is a lossless reparameterisation only when the force envelope and channel direction are retained.
2. The magnetic cross channel bends motion but does no work; energy handover remains the electric dot-product channel.
3. A naïve rung transition that carries only separately averaged parent quantities fails on this dataset.
4. The missing subgrid covariance is established closure mathematics and a concrete candidate for ARA `Other`.
5. A new-physics claim requires a frozen compressed rule that predicts that term on held-out data, plus a multi-time dataset for direct momentum-change confirmation.
"""
    ),
]

nbf.validate(notebook)
nbf.write(notebook, OUTPUT)
print(OUTPUT)
