# T350 independent validation

**Verdict:** **PASS — 28/28 checks**

The validator does not import the T350 run script. It recomputes frozen hashes, row integrity, all headline metrics and gates, tick reconstruction from every raw example, and all seven complete raw-example history vectors.

| Check | Result | Detail |
|---|---|---|
| claim hash | PASS | `C4C5CE519F1F596172D1209AF033C88915004E6B04002EFF16F3B606B15241A5` |
| protocol hash | PASS | `C68DD4A2EB60A18034CF8A7B504F5FAE8D3ADBE7AC7ABC2E14BD32E3132EB35E` |
| path row count | PASS | `rows=672` |
| prefix row count | PASS | `rows=6048` |
| matched-pair count | PASS | `rows=588` |
| cadence-pair count | PASS | `rows=192` |
| path natural key unique | PASS | `duplicates=0` |
| all common suffixes exact | PASS | `suffix=8.88e-16; recent=0` |
| parent metric max_reconstruction_error | PASS | `8.881784197e-16` |
| parent metric retained_share | PASS | `1` |
| parent metric median_retention | PASS | `0.871961128883` |
| parent metric median_emergence | PASS | `0.25` |
| parent metric median_closure_jump | PASS | `0.0162126123922` |
| parent metric cadence_median | PASS | `0.000339545727873` |
| parent metric cadence_share | PASS | `1` |
| front metric final_small_share | PASS | `0` |
| front metric median_final_distance | PASS | `0.415835987665` |
| front metric median_emergence | PASS | `0.25` |
| front metric median_closure_jump | PASS | `0.0162126123922` |
| front metric local_median_error | PASS | `1.23350218928e-11` |
| front metric local_p95_error | PASS | `7.92510945757e-11` |
| gate rows | PASS | `[True, True, True, True, False, False, True]` |
| parent verdict | PASS | `True` |
| pure-front verdict | PASS | `False` |
| local-front verdict | PASS | `True` |
| raw-example tick reconstruction | PASS | `max=8.882e-16` |
| raw-example history vectors | PASS | `failures=0` |
| figure dimensions | PASS | `size=(2400, 1500)` |
