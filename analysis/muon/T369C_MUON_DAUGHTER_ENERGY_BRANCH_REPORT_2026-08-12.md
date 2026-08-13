# T369C - prompt-energy / neutron-connection branch

**Verdict:** **ANTI-DIRECTED ENERGY/CONNECTION BRANCH SUPPORTED**  
**Evidence class:** post-result diagnostic

## Result

- Prompt-child holdout rows: **20,040**
- Signed rank correlation: **-0.314980**
- Bootstrap 95% interval: **[-0.326753, -0.303274]**
- Descending adjacent bins: **7/7**
- Neutron rate, lowest energy bin: **39.183%**
- Neutron rate, highest energy bin: **3.225%**
- Low/high rate ratio: **12.15x**
- Time-bin-preserving shuffle exceedances: **0/1,000**
- Strict `5-15 MeV` correlation: **-0.302886**
- Hash-half correlations: **-0.312792**, **-0.317226**

## Plain-language ARA reading

The strong opposite-looking child branch is in prompt energy versus observed
neutron connection, not in prompt time versus neutron detection time. As the
prompt-energy coordinate rises, the observed neutron branch falls smoothly.
This survives timing-preserving shuffles and internal replications.

That establishes an **anti-directed relation in the released detector
record**. It does not establish exact pure anti-phase closure: the dataset has
no neutron-emission energy coordinate, and neutron detection is incomplete.

A likely established-physics contribution must remain explicit: the
`p <= 15 MeV` sample is capture-enriched rather than capture-pure. Increasing
prompt momentum may shift the mixture toward residual muon-decay-electron
events, which naturally carry fewer capture-neutron tags. The relation is
therefore a strong detector-record result, not yet a new mechanism claim.

Independent raw-source validation: **PASS**. The validator reparsed the
checksum-locked CSV without importing the primary analysis or its derived
arrays and reproduced every headline value.
