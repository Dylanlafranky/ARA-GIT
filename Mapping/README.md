# Mapping

This folder is for geometry-first diagnostic workbenches and map-building assets.

The files here are not the forward formula itself. They are for locating systems, rungs, ARA positions, orientations, boundaries, and relation candidates before deciding whether a prediction test makes sense.

Current contents:

- `ara_mapping_atlas_3d.html` - interactive 3D mapping atlas.
- `ara_mapping_atlas_build.py` - rebuilds the atlas data from the old temporal-coordinate visualiser and current `TheFormula` data exports.
- `ara_mapping_atlas_data.json` - structured atlas data.
- `ara_mapping_atlas_data.js` - browser-loadable atlas data.

To rebuild:

```powershell
python Mapping\ara_mapping_atlas_build.py
```
