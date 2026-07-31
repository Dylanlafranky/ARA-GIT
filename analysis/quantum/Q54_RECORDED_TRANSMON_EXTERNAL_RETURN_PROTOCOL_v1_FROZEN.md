# Q54 — recorded transmon external-return protocol v1

**Frozen:** 30 July 2026, after source-field profiling and before any
whole-circle centre, external heading, arc occupancy, traversal count, or
return verdict was calculated  
**Ledger:** T314  
**Status:** confirmatory test on public recorded quantum hardware  
**Primary population:** Devices B and C  
**Development/profile-only population:** Device A

## Registered question

For an experimentally recorded quantum \(I/Q\) trajectory, treat each
complete internal rotation as one ARA circle. Follow the centre of that whole
circle through successive rotations.

The frozen questions are:

1. does that external whole-circle vector actively traverse the declared
   \(1/e\rightarrow\phi\) ARA diameter, \(0\rightarrow2\), in either direction;
2. does it subsequently return, producing a complete active
   \(0\rightarrow2\rightarrow0\) or \(2\rightarrow0\rightarrow2\) cycle?

The half-traversal and full-return claims receive separate verdicts. A
half-traversal cannot rescue a failed full return.

## Public source

Zenodo DOI:
[`10.5281/zenodo.8004359`](https://doi.org/10.5281/zenodo.8004359),
source data for *Inductively shunted transmons exhibit noise insensitive
plasmon states and a fluxon decay exceeding 3 hours*.

Q54 uses the recorded `Fig6/**/T2 Vs Flux/T2_*.txt` Ramsey files:

- raw delay coordinate;
- raw repeated \(I\)-quadrature rows;
- raw repeated \(Q\)-quadrature rows;
- 101 recorded delay points per complete file;
- 11 repeats per primary Device B/C file.

The full Zenodo ZIP is not required. `q54_extract_zenodo_subset.py` reads its
central directory by HTTP range, extracts only declared recorded files, checks
every ZIP CRC, and saves per-file SHA-256 hashes in
`Q54_ZENODO_SUBSET_MANIFEST.json`.

### Source separation

Device A was opened to identify the file grammar and inspect example values.
It is excluded from the primary verdict and retained only as a sensitivity
population.

Device B and Device C values have not been inspected before this freeze. All
complete non-duplicate Device B/C `T2_*.txt` files with:

- exactly 101 ordered delay points;
- at least 9 paired \(I/Q\) repeats;
- finite data;
- strictly increasing delay;

enter the primary population. These are schema exclusions, not outcome
exclusions.

## ARA object and physics object

| ARA reading | Recorded-hardware reading |
|---|---|
| internal ARA circle | one complete Ramsey \(I/Q\) rotation |
| circle centre | algebraic least-squares centre fitted to all samples in that rotation |
| external/meta vector | centre of later circle minus centre of earlier circle |
| external direction | heading of that centre displacement |
| \(1/e\) pole, ARA \(0\) | declared local-heading endpoint \(1/e\) turn |
| \(\phi\) pole, ARA \(2\) | declared local-heading endpoint \(\phi-1\) turn |
| active half-cycle | ordered endpoint-to-endpoint traversal |
| full active return | ordered endpoint-to-opposite-endpoint-to-start traversal |

This is a hardware replication of Q49's whole-circle-centre construction. It
does not score the amount of internal Ramsey rotation as the external vector.

## Parsing and fixed intrinsic orientation

For each file, pair the \(j\)-th \(I\) row with the \(j\)-th \(Q\) row:

\[
z_j(t)=I_j(t)+iQ_j(t).
\]

The primary trace is the raw repeat mean:

\[
\bar z(t)=\frac1{n_{\rm rep}}\sum_j z_j(t).
\]

The repeat median is a fixed sensitivity estimator.

The late-time origin is the mean of the final 20 recorded points:

\[
c_\infty=\frac1{20}\sum_{t=82}^{101}\bar z(t).
\]

To remove the arbitrary detector-phase rotation without fitting the target,
rotate the trace so that the mean of the first five centred phasors lies on
the positive real axis. If the median unwrapped phase slope is negative,
complex-conjugate the trace so forward experimental time has positive
orientation. The same one-time transformation is applied to every point and
every repeat in that file.

This fixes an intrinsic source pole and time direction. No result-dependent
rotation is permitted.

## Complete internal-circle extraction

From the intrinsically oriented mean trace:

1. compute unwrapped phase of \(\bar z(t)-c_\infty\);
2. partition it at successive integer \(2\pi\) crossings;
3. retain a candidate internal circle only when it:
   - contains at least 6 recorded points;
   - spans at least \(1.8\pi\);
   - has mean radius at least 20% of the first retained circle's radius;
4. fit its algebraic least-squares centre using every point;
5. require relative median radial residual at most 0.25.

The thresholds are frozen before circle extraction. Rejected late-time
noise cannot be reintroduced to improve a verdict.

For retained circle \(r\), save centre \(\mathbf c_r\), radius \(R_r\), time
midpoint, phase span, point count, and radial residual.

## External vector and declared ARA diameter

For every interior retained circle:

\[
\mathbf d_r=\mathbf c_{r+1}-\mathbf c_{r-1},
\qquad
m_r=
\frac{\|\mathbf d_r\|}
{\operatorname{mean}(R_{r-1},R_r,R_{r+1})}.
\]

The primary population requires \(m_r\ge0.01\), matching Q49. Headings are:

\[
h_r=
\operatorname{frac}
\left[
\frac{\operatorname{atan2}(d_{r,Q},d_{r,I})}{2\pi}
\right].
\]

The declared local arc is:

\[
L=\frac1e,
\qquad
R=\phi-1,
\qquad
W=R-L.
\]

Inside that oriented arc:

\[
x_r=2\,\frac{h_r-L}{W},
\]

so \(1/e\mapsto0\) and \(\phi-1\mapsto2\).

Three matched controls have the same width and begin at
\(L+1/4\), \(L+1/2\), and \(L+3/4\) turns, modulo one.

## Frozen events

Within one file, eligible headings must come from consecutive retained circle
indices. A missing or ineligible circle ends the run.

An endpoint hit is:

- low: \(x\le0.25\);
- high: \(x\ge1.75\).

### Active half-traversal

A low-to-high or high-to-low event within a contiguous run, with at least one
intermediate heading satisfying \(0.5\le x\le1.5\).

### Full active return

A low-high-low or high-low-high endpoint sequence within a contiguous run,
with at least one intermediate heading in \(0.5\le x\le1.5\) on each leg.

Overlapping returns share endpoints but are counted once by earliest
completion.

## Controls

### C0 — construct and invariance

- translating every \(I/Q\) point leaves headings unchanged;
- rotating every raw trace before intrinsic orientation leaves headings
  unchanged;
- uniform positive rescaling leaves headings and eligibility unchanged;
- the internal phase-turn amount is never substituted for centre movement;
- all finite headings lie in `[0,1)`.

C0 earns no evidence.

### C1 — matched rotated locations

Apply the identical endpoint and traversal rules to the three matched
quarter-turn control arcs.

### C2 — destroyed time order

Within every file, independently permute eligible external headings 5,000
times while preserving:

- heading values;
- movement strengths;
- file sizes;
- the count of eligible events.

Recalculate half-traversals and full returns after every permutation.

### C3 — estimator sensitivity

Repeat the primary analysis with the point median across repeats instead of
the repeat mean. No other threshold or coordinate may change.

## Frozen gates and verdicts

### G0 — valid hardware object

C0 passes and at least five primary Device B/C files yield at least three
eligible external headings each.

### G1 — declared directional location

In the pooled primary Device B/C population:

- the declared arc has greater occupancy than every matched rotated arc;
- in 5,000 file-cluster bootstrap draws, it exceeds the strongest control in
  at least 95% of draws.

### G2 — active half-traversal

- at least five half-traversals occur across at least five files;
- both directions occur;
- the declared arc exceeds every rotated control;
- its count exceeds the 99th percentile of C2.

### G3 — full active return

- at least three full returns occur across at least three files;
- both low-high-low and high-low-high occur;
- the declared arc exceeds every rotated control;
- its count exceeds the 99th percentile of C2.

### G4 — device and estimator replication

For the relevant verdict:

- the declared arc must beat each matched arc separately in Device B and
  Device C;
- the repeat-median sensitivity must preserve the same declared-arc winner
  and a non-zero event count of the relevant type.

### Verdicts

- **Directional path:** supported if G0, G1 and directional parts of G4 pass;
  mixed if G0 and only one of G1/G4 passes; otherwise not supported.
- **Active half-reversal:** supported if G0, G2 and half-traversal parts of G4
  pass; otherwise not supported.
- **Full \(0\to2\to0\) return:** supported if G0, G3 and return parts of G4
  pass; otherwise not supported.

No parent-ridge average, T1 curve, flux-jump reset, fitted decay model,
rotated post-hoc axis, or Device A result may rescue a failed primary gate.

## Interpretation boundary

A pass would show that Q49's ARA whole-circle construction recovers a
directionally specific ordered external path in a new, public, recorded
transmon dataset. It would not prove a universal time vector, universal Phi,
literal travel through physical space, or all quantum systems.

A failure would reject this exact recorded-hardware realization. It would not
erase earlier simulator reversals, nor would measurement backaction or an
alternative detector angle be used as an after-the-fact rescue.
