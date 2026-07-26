# H1 public-data reproduction

Source:

<https://doi.org/10.24432/C5CW21>

Expected archive:

- `condition_monitoring_of_hydraulic_systems.zip`

The downloaded archive and extracted source files are ignored by Git. The committed runner verifies the archive
hash recorded after the first frozen download and regenerates all derived CSV, JSON and report artifacts.

Run from `analysis/hydraulics`:

```powershell
python -m pip install -r h1_public_hydraulic_requirements.txt
python h1_public_hydraulic_two_cut_test.py --download
python h1_public_hydraulic_two_cut_validate.py
```

Expected archive SHA-256:

`24128aad2ee45eea7e6b63ebbd9992cdf25d0483a2cebefbfc13bc69079af1f2`

The source numerical files are never rewritten. The runner regenerates the derived CSV and JSON results; the
validator independently reconstructs the sample accounting, fold isolation, metrics, controls, gates and verdict.
