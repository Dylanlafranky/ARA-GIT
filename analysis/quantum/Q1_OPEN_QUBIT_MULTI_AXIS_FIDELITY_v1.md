# Q1 translation-fidelity packet — open-qubit multi-axis ARA

**Claim ID / version:** `Q1-FID-v1`  
**Date frozen:** 23 July 2026  
**Status:** `EXACT ENOUGH TO TEST`  
**Evidence type:** translation contract only; no result

## F0 — frozen source

**USER PRIOR — Dylan:**

> ARA is the condensed triangle lock that gives you the rough idea on a line cut through it. Like seeing an ant
> farm against the glass, you can see where the sphere does and does not pass through. But to see beyond that, we
> need the full sphere.

> I wonder if we could do an ARA for every degree in a sphere to like “properly properly” map it.

After the quantum example was back-translated:

> Ahhh, so just a ARA cut along a different axis. Yes. I was aware of this and trying to do similar here.

**Identity/system being measured:** one open two-level quantum state through time.

**Ordered poles and declared direction:** for each declared measurement axis \(\hat n\), the two mutually exclusive
measurement outcomes are the poles. Use

\[
x_{\hat n}=1-\mathbf r\cdot\hat n,
\]

so Bloch projection \(+1\rightarrow x=0\), zero projection \(\rightarrow x=1\), and Bloch projection
\(-1\rightarrow x=2\). Reversing the axis reverses the reading:

\[
x_{-\hat n}=2-x_{\hat n}.
\]

**Scale/rung origin:** one qubit at one declared physical scale. Changing measurement axis is rotating the line cut,
not changing rung.

**Invariant relational claim:** one ARA diameter is a real but incomplete projection of the same full identity.
Different axis cuts may change while the first cut remains fixed. A multi-axis account plus radius/direction must
retain distinctions that one compressed diameter cannot.

**Permitted decompression:**

- standard density matrix and Bloch-vector representation;
- declared \(X,Y,Z\) measurement axes or an equal-area directional set;
- time-resolved direction and sphere radius/purity;
- standard \(T_1\) relaxation, \(T_2\) dephasing and unitary rotation as known-referee dynamics;
- child/current/parent outputs kept separate.

**Forbidden substitutions/proxies:**

- replacing the full identity with population on the \(Z\) diameter alone;
- treating measurement axes as automatically different rungs;
- inferring missing axes from a scalar trace without independent measurements;
- calling a rendering of repeated scalar values spherical reconstruction;
- identifying a hidden physical Phase B, Information ontology, measurement collapse or entanglement mechanism from
  a coordinate crosswalk;
- claiming derivation of quantum mechanics from ARA.

**Observable needed:** time-resolved two-outcome probabilities along declared independent axes, sufficient to
recover \(\mathbf r(t)\), direction and radius/purity; for controlled validation, the native simulated density
matrix supplies ground truth but is hidden from estimators.

**Known ambiguity / competing reading:** transverse coherence may be described either as hidden cuts through the
same ARA identity or as child identities whose coarse-grained parent is the qubit. Q1 tests the same-rung
multi-axis reading only. It does not adjudicate the later child/parent ontology.

**What would count as wrong object:** scoring only \(x_z\), using additional clean state information for the
multi-axis method but not the control, confusing standard tomography accuracy with a new ARA law, or flattening
coherent and incoherent `1.0` states into the same identity.

## F1 — three-view translation

### Plain restatement

The population reading is one ARA line through the qubit sphere. A state can remain at the `1.0` ridge on that line
while changing on transverse lines. To see whether the identity remains coherent or unravels, measure the coupled
cuts, their direction through time and the sphere radius.

### Mathematical representation

For

\[
\rho(t)=\frac12\left(I+\mathbf r(t)\cdot\boldsymbol\sigma\right),
\qquad
\|\mathbf r(t)\|\le1,
\]

define

\[
\boxed{x_{\hat n}(t)=1-\mathbf r(t)\cdot\hat n}.
\]

A sparse complete three-axis set is

\[
\mathbf x(t)=\left(x_{\hat x}(t),x_{\hat y}(t),x_{\hat z}(t)\right),
\]

from which

\[
\mathbf r(t)=\left(1-x_{\hat x},1-x_{\hat y},1-x_{\hat z}\right)
\]

under the fixed axis convention. The radius

\[
R(t)=\|\mathbf r(t)\|
\]

distinguishes a pure coherent state (`R=1`) from a maximally mixed state (`R=0`) even when one selected diameter
reads `1.0` in both.

Known-referee open dynamics may use

\[
\dot r_x=-r_x/T_2,\qquad
\dot r_y=-r_y/T_2,\qquad
\dot r_z=-(r_z-r_z^{\rm eq})/T_1,
\]

with additional declared Hamiltonian rotation when required.

### Back-translation without the source wording

One two-outcome measurement reports only the component of the state along its chosen direction. Opposite
measurement directions complement one another, while perpendicular measurements expose information hidden from
the first. Relaxation can move the population component; dephasing can remove transverse coherence while leaving
that population component unchanged. The combined directional readings and their radius describe more of the same
state than any one reading.

## Translation audit

**AI assumptions added:**

- the first controlled domain is a standard two-level quantum system;
- three orthogonal axes are sufficient for the sparse complete qubit reconstruction;
- Bloch radius/purity is the operational full-sphere depth variable for Q1;
- \(T_1/T_2\) dynamics are the first known-referee distinction.

**Information discarded:**

- nested rungs below and above the qubit;
- spatial wavefunction structure;
- environment identity and microscopic bath modes;
- ordered Information³ closure beyond the qubit state;
- entanglement and measurement back-action.

**Alternative mathematical objects fitting the wording:**

- full angular quantum tomography with more than three axes;
- quasiprobability representations;
- child/parent channel decompositions of the environment;
- a spatial field sphere rather than the Bloch state sphere.

**First reversal/collapse risk:** confusing the axis reversal
\(x_{-\hat n}=2-x_{\hat n}\) with time reversal, or treating all `x=1` readings as one state without retaining
transverse axes and radius.

## F2 — Dylan fidelity verdict

**Recorded verdict:** `EXACT ENOUGH TO TEST`

**Basis:** Dylan's ordinary-language confirmation on 23 July 2026:

> Ahhh, so just a ARA cut along a different axis. Yes.

The librarian converts that confirmation to the protocol's fixed verdict label. No physical result is implied.

## F3 — critical-field gate

| Field | Match | Record |
|---|---:|---|
| Identity | 1 | one qubit identity |
| Poles | 1 | two outcomes per declared axis |
| Direction | 1 | fixed \(x_{\hat n}=1-\mathbf r\cdot\hat n\) |
| Rung | 1 | axes remain same-rung cuts |
| Observable | 1 | independent directional outcome probabilities |
| Coupling | 1 | coupled cuts belong to the same state |
| Closure | 1 | multi-axis direction plus radius |
| Falsifier | 1 | multi-axis account must retain information absent from one cut under equal-information controls |

**Documentation fidelity:** `1.0` under the declared Q1 scope.

## Test-binding fence

This packet authorizes preparation of a controlled instrument test. A separate ledger registration, protocol,
development/target split, controls and kill thresholds are still required before target outcomes are computed.

