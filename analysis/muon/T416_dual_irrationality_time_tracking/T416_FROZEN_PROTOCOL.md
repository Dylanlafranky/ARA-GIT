# T416 — Dual Irrationality Di-ARA tracking through the muon lifespan

**Frozen before development or validation scoring:** 21 August 2026  
**Status:** ARA-first instrument transfer; public population histograms  
**Source:** ISIS EMU experiment RB1620447, the same resolved archive used by T413–T415

## Relational location

- **Measured identity:** the resolved detector-share spin mode of a muon
  population.
- **Parent:** the detector-summed survival/release envelope.
- **State Irrationality Di-ARA:** the local complex spin state
  \(D_{\rm state}=(x_L,x_C)\), where \(x_L\) is contraction/expansion of the
  measured spin-mode magnitude and \(x_C\) is reverse/forward phase traversal.
- **Path/history Irrationality Di-ARA:** the retained phase path
  \(D_{\rm history}=(x_P,x_R,C(H))\), where \(x_P\) is reused/open address
  potential, \(x_R\) is determined/unresolved continuation, and \(C(H)\)
  retains lagged closure history.

These are two cuts of the same measured trajectory. The test does not assume
in advance that one is the parent of the other. It asks whether they retain
different information while the lifespan parent advances.

## Who / what / when / where / why / how

### Who

The 13 development and 13 interleaved validation runs at 300 K and 50–500 G.
RF-on and RF-off are separate identities until the final comparison. Every
record is a 96-detector ensemble histogram; it is **not** a continuously
observed individual muon.

### What

Recover one measured complex spin-child path from detector shares and apply
both canonical Irrationality Di-ARA instruments to it through time. Keep the
smooth parent release coordinate beside both cuts.

### When

Use native corrected time from 0.25 to 6.00 microseconds in 0.016-microsecond
bins. The detector basis is calibrated from only the first 2.00 microseconds
of each run/period. State coordinates use one field-specific spin cycle. The
history coordinate uses a past-only 128-bin (2.048-microsecond) window and is
read every four native bins.

### Where

All operations stay inside a run and RF period. Magnetic-field frequency uses
the already-frozen T414 development calibration
\(f=0.013549 B\) MHz. Detector labels are not interpreted as physical angles
because the archive does not contain usable detector geometry.

### Why

Test the physical meaning of the two already-calibrated Irrationality Di-ARA
instruments on the same muon identity:

1. does the state cut describe the current observed spin-mode condition;
2. does the history cut preserve chronology and closure information that is
   not reducible to the state cut alone;
3. how do both change as the lifespan parent advances from 0 toward 2?

### How

Detector shares remove the total-count envelope before the spin mode is
estimated. An early, past-bounded harmonic fit supplies a two-dimensional
detector basis. Projection onto that basis gives
\(w(t)=u(t)+iv(t)=M(t)e^{i\theta(t)}\). The magnitude \(M\) feeds the state
radial cut and the phase \(\theta\) feeds both orientation and history.

## Frozen measurements

### Complex observed spin path

For detector share residual \(r_i(t)\), fit the two target-frequency detector
vectors on \(0.25\le t<2.25\) microseconds using intercept, linear drift,
cosine and sine. Project every later residual into their least-squares plane:

\[
w(t)=u(t)+iv(t),\qquad
M(t)=|w(t)|,\qquad
z(t)=\frac{\arg w(t)}{2\pi}\pmod 1.
\]

This per-run early calibration makes T416 a descriptive and causal-in-time
tracking cut after the calibration interval. It is not a fully external
detector-basis transfer.

### State Di-ARA

Let \(p_r\) be one observed spin period in native bins and let
\(\widetilde M\) be a fixed three-bin median of \(M\). Then

\[
s_t=\frac{\widetilde M(t)}{\widetilde M(t-p_r)},
\qquad
x_L(t)=\frac{2s_t}{1+s_t}.
\]

The phase-orientation cut over the same trailing cycle is

\[
x_C(t)=1+
\frac{\sum_j\sin \Delta\theta_j}
     {\sum_j|\sin \Delta\theta_j|}.
\]

Thus \(x_L<1\) is contraction, \(x_L>1\) expansion,
\(x_C<1\) reverse traversal and \(x_C>1\) forward traversal. The poles are
reference identities; observations may occupy gradients.

### Path/history Irrationality Di-ARA

For the past-only phase history \(H_t=(z_{t-127},\ldots,z_t)\):

- \(x_P=2\widehat\beta\), where \(\widehat\beta\) is the clipped log-log
  slope of occupied phase bins at resolutions \(8,16,32,64\);
- \(x_R=2\min(1,L_{\rm local}/L_{\rm null})\), using the frozen T348
  five-neighbour, first-half-to-second-half circular successor prediction;
- \(C(H)\) retains lag coherence \(\rho_h\) and angular miss \(d_h\) for
  \(1\le h\le32\).

The reduced resolutions and lag budget preserve the T348 equations while
matching this archive's 128-bin causal window. They are an explicitly declared
instrument projection, not a claim that 128 bins equal the original 4096-bin
synthetic calibration.

### Lifespan parent

The already-frozen T414 parent coordinate remains

\[
x_{\rm parent}(t)=2\left(1-e^{-t/2.203\,\mu s}\right).
\]

It is shown as context and used in the non-redundancy diagnostic. It does not
enter either Di-ARA coordinate.

## Controls

1. **Within-window chronology shuffle:** preserves visited phase values and
   therefore address support while destroying order.
2. **Wrong-frequency extraction:** repeat the early detector-plane extraction
   at fixed sidebands \(f\pm4/L\) and \(f\pm8/L\), where \(L=5.75\) us;
   compare the median wrong-frequency history.
3. **Reverse path:** reverse each history window. This is descriptive; it tests
   direction but is not required to preserve determinacy.
4. **RF identity:** score RF-on and RF-off separately before pooling.
5. **Parent adjustment:** remove a quadratic function of the lifespan-parent
   coordinate within each run/period before comparing state and history.

## Frozen gates on untouched validation runs

Validation is reported by magnetic field, not by treating time bins as
independent replicates.

1. **Observed state orientation:** median \(x_C>1\) in both RF conditions.
2. **Observed contraction:** the bootstrap upper bound for median \(x_L\) is
   below 1 in at least one RF condition, and the pooled median is below 1.
3. **Chronology determinacy:** shuffled history has larger \(x_R\) than intact
   history with a paired field-bootstrap 95% interval wholly above zero.
4. **Support preservation:** median \(|x_P^{shuffle}-x_P^{intact}|<0.10\).
5. **Closure history:** intact median closure coherence exceeds shuffled
   coherence with a paired field-bootstrap 95% interval wholly above zero.
6. **Frequency specificity:** intact target-frequency \(x_R\) is lower than
   the median wrong-frequency result with a paired field-bootstrap interval
   wholly above zero for \(x_R^{wrong}-x_R^{target}\).
7. **Non-redundancy diagnostic:** after parent adjustment,
   \(|\rho_S(x_L,x_R)|<0.80\). This is a coarse dependence screen, not proof
   of causal independence.

The complete physical dual-instrument transfer is labelled **supported** only
if Gates 1–7 pass. Individual failures remain visible; descriptive trajectories
cannot rescue the complete verdict.

## Claim boundary

T416 can show how two ARA instruments describe one resolved population spin
path and whether chronology/frequency controls preserve their intended roles.
It cannot observe a single muon continuously, time a neutrino, prove a hidden
constituent, establish universal irrational constants, or identify state and
history as a fixed parent/child orientation across all domains.
