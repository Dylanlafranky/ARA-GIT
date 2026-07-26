# Q31 source selection — frozen before outcome inspection

**Frozen:** 2026-07-26 19:52 AEST  
**Parent protocol:** `Q31_LATTICE_TO_TRAVERSAL_PROTOCOL_v1_FROZEN.md`  
**Selection rule:** take the first public source that is experimental, time/order resolved, non-diagonal, and supplies an externally defined traversal coordinate without choosing a crossing from the Q31 result.

## Search audit

The following decisions use repository metadata, paper abstracts, file schemas, row/column extents and published checksums only. No Q31 outcome statistic was calculated before this file was frozen.

| Order | Candidate | Eligibility decision | Reason |
|---:|---|---|---|
| 1 | Vaartjes et al., *Certifying the quantumness of a nuclear spin qudit through its uniform precession*, Dryad DOI `10.5061/dryad.547d7wmj0` | Reject for Q31 v1 | Experimental tomography and off-diagonal density matrices are available, but the metadata does not supply the required predeclared connection-to-traversal handover or clearly identify at least 30 independent crossing units. It remains a useful later precession test. |
| 2 | Jiang et al., *Observation of separated dynamics of charge and spin in the Fermi-Hubbard model*, Dryad DOI `10.5061/dryad.crjdfn32v` | Reject for Q31 v1 | Experimental lattice spreading is available, but the advertised measurements are primarily site densities and processed spreading quantities rather than a native non-diagonal relation vector at each ordered step. |
| 3 | Yen et al., *Observation of non-adiabatic Landau-Zener tunneling among Floquet states*, Zenodo DOI `10.5281/zenodo.18860416` | Reject for Q31 v1 | Experimental and externally driven, but the repository metadata does not establish a reusable three-axis or off-diagonal relation object or at least 30 independent crossing units. The archive is also 549 MB, so it was not opened merely to search for a favourable representation. |
| 4 | Lin et al., *Simulation of a Floquet non-Abelian topological insulator with photonic quantum walks*, Zenodo DOI `10.5281/zenodo.18264638`; Dryad DOI `10.5061/dryad.3ffbg79vk` | **Selected provisionally** | Experimental photon-counting data include reconstructed three-axis eigenstate trajectories on the unit sphere as quasimomentum traverses the Brillouin zone, plus lattice-site/quasienergy/weight tables. This is non-diagonal, ordered, sphere-valued, and exposes both traversal and lattice representations without Ramsey/Hahn filtering. |

## Selected source and frozen interpretation

The three figure workbooks are treated as three externally declared system configurations, not as three chances to select the most favourable result:

- Figure 2: single-gap domain-wall configuration.
- Figure 3: multiple-gap domain-wall configuration.
- Figure 4: anomalous non-Abelian configuration.

For Q31, quasimomentum order is the native traversal coordinate. Signed axis-zero passages are the only permitted local handover anchors. They are determined directly from adjacent measured coordinate signs; no Q31 score may move an anchor.

The unit-sphere trajectory is the non-diagonal relation object. The lattice-site/quasienergy/weight table is a source-side comparison view; it is not used to redefine the ARA metrics.

The selected source remains **provisional** until the schema audit confirms:

1. at least 30 independently identifiable trajectory/crossing units;
2. both development and untouched evaluation groups;
3. enough adjacent ordered samples for the frozen short- and long-memory lags.

Failure of any item makes Q31 v1 **inconclusive by data gate**. It does not authorize a protocol change.

## Acquisition record

Downloaded from the public Zenodo mirror on 2026-07-26 and checked against the published MD5 values:

| File | Bytes | Published and observed MD5 |
|---|---:|---|
| `SourceData_Fig2.xlsx` | 144,854 | `746c65ddccd37e82d0710712ecfec4fb` |
| `SourceData_Fig3.xlsx` | 123,704 | `c24a6ed6475b64d61e08318eeae0c629` |
| `SourceData_Fig4.xlsx` | 153,612 | `7d4dda38985171a5196981ee5a7ed397` |

Local source directory:

`analysis/quantum/q31_data/source/`

## Evidence boundary

Selection of this source does not itself support an ARA singularity flip. It only establishes that Q31 can be attempted on fresh, public, experimental, sphere-resolved data. The physics labels supplied by the authors will be reported beside the ARA labels but will not alter the frozen ARA geometry.
