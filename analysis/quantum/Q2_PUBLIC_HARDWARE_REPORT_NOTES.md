# Q2 report source and chart notes

**Audience:** technical  
**Delivery mode:** MCP app report  
**Question:** does a real public hardware output preserve added class information in two ARA cuts compared with
one training-selected native cut?

## Report structure mapping

| Technical-report role | Reader-facing section |
|---|---|
| Technical summary | `Technical Summary` |
| Key findings | `One aligned I axis carried nearly all separation` and replication section |
| Scope/data/definitions | `What was measured` |
| Methodology/model specification | `How the frozen test worked` |
| Limitations/robustness | `What passed, what failed, and what it means` |
| Recommended next steps | `Test real tomography next` |
| Further questions | `Open questions` |

## Chart map

| Section | Question | Family/type | Fields | Supported claim | Palette |
|---|---|---|---|---|---|
| Primary evidence | how do I, Q and coupled I/Q vary across held-out conditions? | grouped bar | condition, arm, balanced accuracy | I carries nearly all separation | hard two-root cap plus neutral |
| Replications | does the gain recur in other registered arms? | signed bar | arm, ARA-minus-one-cut gain | every registered arm is slightly negative | single-root plus zero reference |
| Dynamics | do T1 and Ramsey have different ridge-crossing structure? | grouped bar | mode, family, crossings | monotonic T1 and oscillatory Ramsey remain distinct | hard two-root cap |

The condition chart uses six discrete experimental settings, so grouped bars are more honest than a trend line.
The dynamics chart uses three modes per family and reports exact crossing counts; no continuous trend is implied.

## Source inventory

- Zenodo DOI `10.5281/zenodo.14033026`;
- Nature Physics DOI `10.1038/s41567-024-02741-4`;
- `Q2_PUBLIC_HARDWARE_IQ_FOLDS.csv`;
- `Q2_PUBLIC_HARDWARE_IQ_BLOCKS.csv`;
- `Q2_PUBLIC_HARDWARE_IQ_SUMMARY.csv`;
- `Q2_PUBLIC_HARDWARE_IQ_RESULTS.json`;
- `Q2_PUBLIC_HARDWARE_IQ_VALIDATION.json`;
- `Q2_PUBLIC_HARDWARE_DYNAMICS_CROSSWALK.csv`.

## Omitted evidence

Raw 600,000-shot target rows are not copied into the report artifact. The report uses audited condition-level
aggregates and bounded dynamics rows. The raw immutable archive remains available from the DOI and is checksum
verified by the reproduction script.
