# T361 independent validation

**Validation:** **PASS**

| check | result | detail |
|---|---|---|
| source MD5 | PASS | abe81a3631481b58977925daf453ede5 |
| frozen hash T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_CLAIM_PACKET_v1.md | PASS | 180f60856b6a7ee45c3d1330f00c6396a380061b2f35f75d1950fda660c41dae |
| frozen hash T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_PROTOCOL_v1_FROZEN.md | PASS | 3d94fca5959a100d4e8b2824f6f8fa95c4ab4d7b8d0b42c6418c47ac8156bcbb |
| frozen hash T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_PROTOCOL_v2_FROZEN.md | PASS | 28cdbc84e614f97b0988fc46a62035ead253a8ad0caf8bb2c21ce15bdd75e44c |
| frozen hash T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_PROTOCOL_v3_FROZEN.md | PASS | 63e815b6d674bf2b377ffde52da7060461f5dac9cecbd17e5d990f2e86cda438 |
| cycle schema | PASS | columns=14 |
| nine records | PASS | [np.int64(0), np.int64(50), np.int64(100), np.int64(150), np.int64(170), np.int64(190), np.int64(240), np.int64(290), np.int64(340)] |
| forty pairs per record | PASS | {0: 40, 50: 40, 100: 40, 150: 40, 170: 40, 190: 40, 240: 40, 290: 40, 340: 40} |
| four methods per cycle | PASS | all cycle groups have four methods |
| coordinate ranges | PASS | agreement and turn metrics bounded |
| record medians | PASS | recomputed from complete cycle table |
| frozen gate hits | PASS | recomputed=[3, 3, 3, 0, 3, 1] |
| frozen gate verdicts | PASS | recomputed=[False, False, False, False, False, False] |
| overall verdict | PASS | recomputed=False |
| example path arithmetic | PASS | rows=64; RMSE=0.776224 |
| figure present | PASS | bytes=620202 |
