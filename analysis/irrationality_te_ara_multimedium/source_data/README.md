# T342 ignored public source cache

The large/public numerical files used by T342 are downloaded here and are not
committed. Reproduction downloads the immutable or publicly listed sources,
then verifies the hashes recorded in `T342_MULTIMEDIUM_IRRATIONALITY_TE_ARA_SOURCE_MANIFEST.json`.

Expected layout after acquisition:

```text
source_data/
  cold_room/Raw.zip
  cold_room/experiment_actions.csv
  cold_room/raw/*.csv
  acoustics/*.wav
```

The other five domain sources reuse checksum-recorded local archives already
documented in their originating analysis folders.
