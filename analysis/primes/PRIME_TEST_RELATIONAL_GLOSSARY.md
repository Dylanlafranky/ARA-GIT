# Prime-test relational glossary

**Purpose:** translate the compact names used in the ARA prime work into relations that are easier to hold than
isolated letter-number labels.

## The ten-second map

When you see a compact label, first ask which direction it names:

| Label shape | Direction it names | Read it as |
|---|---|---|
| `PN6` | **Test lineage** | “Prime test number 6: the native circumference test.” |
| `PN9` | **Test lineage** | “Prime test number 9: tangent gap-spheres, their contact ridge, and local sphere scale.” |
| `R11` | **Scale rung** | “The decimal window around (10^{11}).” |
| `p29` | **A particular prime gate** | “Prime 29, or the sieve boundary ending at prime 29.” |
| `Q29` | **A connection mask/control** | “The known divisibility pattern through prime 29.” |
| `q` | **A moving later gate** | “Whichever later prime gate we are currently walking through.” |
| `candidate` / `edge` | **Measured identity** | “One surviving number” / “a relation between two neighbouring survivors.” |
| `S`, `x`, `theta` | **Three views of one state** | “Survival share” / “ARA diameter position” / “position around the circle.” |

The central relational chain is:

```text
raw consecutive integers
    -> pass the fixed gates 2, 3, 5, ... 29
    -> p29-conditioned candidates
    -> walk through later gates q = 31, 37, 41, ...
    -> candidate and adjacent-edge survival/release paths
    -> terminal survivors, which are primes in the bounded interval
```

The two scales must not be flattened together:

```text
R6 -> R7 -> R8 -> R9 -> R10 -> R11       whole-window / adult scale rungs
              inside any one R rung:
        q=31 -> 37 -> 41 -> ... -> qmax  later sieve-gate / within-rung path
```

So `R11 at q=101` means: **on the large (10^{11}) window, look at the state after the later prime gates have
advanced through 101**.

## The easily confused letter-number terms

### `p29` — “the prime-29 gate or boundary”

- **Literal:** lowercase `p` names an actual prime. Here (p=29).
- **Relation:** gates (2	o3	o5	ocdots	o29) have already acted.
- **ARA bridge:** the declared starting boundary of the connection-heavy identity.
- **Do not confuse with:** `Q29`, which is an entire connection mask/control built from all gates through 29.

### `p29-conditioned` — “already passed every small-prime gate through 29”

- **Literal:** an integer remains only if none of (2,3,5,ldots,29) divides it.
- **Relation:** raw integer (	o) small-prime filtering (	o) candidate.
- **ARA bridge:** the population at the declared starting slice; later release is measured relative to this population.
- **Important:** a p29-conditioned candidate is not necessarily prime. A larger prime may still divide it.

### `p29 wheel` — “the complete repeating connection pattern through 29”

- **Literal:** divisibility through 29 repeats modulo the product (2cdot3cdot5cdots29).
- **Relation:** one full period contains every allowed residue and every gap between allowed residues.
- **ARA bridge:** a closed, finite connection identity. It is different from sampling a short window on the ordinary
  number line.

### `Q29` — “the known connection mask through 29”

- **Literal:** in PN3B, (Q=29) meant the expected prime/composite pattern supplied by sieve connections through 29.
- **Relation:** raw prime signal (-) expected Q29 connection pattern (=) Q29 residual.
- **ARA bridge:** remove the already-known Connection-side web and inspect what remains.
- **Important:** `Q29` is not “prime number 29” by itself, and the residual is not automatically a Time wave.

### `Q997` — “a much deeper connection mask through 997”

- **Literal:** the same kind of control as Q29, but small-prime connections are removed through prime 997.
- **Relation:** Q29 asks what remains after a shallow connection control; Q997 asks whether the remainder survives a
  much deeper one.
- **ARA bridge:** a sensitivity check on whether an apparent opposite wave is merely unresolved connection structure.

### `q` — “the current later prime gate”

- **Literal:** a variable standing for primes after the fixed p29 boundary: (31,37,41,ldots).
- **Relation:** p29 fixes where the walk starts; `q` says where we currently are on the later-gate walk.
- **ARA bridge:** a within-rung process coordinate, not a new whole-system rung.

### `q_end` — “the last gate represented by this cell”

- **Literal:** the largest later prime included in one grouped log-gate cell.
- **Relation:** many individual `q` gates (	o) one readable cell (	o) its endpoint `q_end`.
- **ARA bridge:** the right-hand boundary of one coarse-grained slice of the release path.

### `qmax` — “the last gate required to settle the bounded interval”

- **Literal:** the largest prime gate needed, normally (lfloorsqrt{	ext{highest tested integer}}floor).
- **Relation:** after all gates through `qmax`, any remaining p29-conditioned number in the interval is prime.
- **ARA bridge:** the terminal boundary of this particular within-rung walk—not a universal final singularity.

### `R6`, `R7`, … `R11` — “decimal adult-scale rungs”

- **Literal:** `Rr` labels the test window beginning near (10^r). The standard window is 1% wide, so R11 is
  ([10^{11},1.01cdot10^{11})).
- **Relation:** R10 (	o) R11 moves the whole experiment one decimal scale upward.
- **ARA bridge:** these are the stacked parent-scale rungs used for cross-scale transfer.
- **Do not confuse with:** release (R=1-S). In prime-test filenames, `R11` is a scale label; in equations, release
  should be written explicitly or with its arguments.

### `PN1`, `PN3B`, `PN6` — “test-family addresses”

- **Literal:** internal names for successive Prime-Number test threads. A letter marks a branch within a thread.
- **Relation:** PN3 (	o) PN3A (	o) PN3B means the question was decompressed through related follow-ups; PN6 is a
  later distinct frozen test.
- **ARA bridge:** these labels describe our investigation path, not mathematical objects inside the prime geometry.
- **Example:** PN6 = the fresh native circumference plus log-rung test.

### `P1`, `P2`, … inside a protocol — “predeclared pass/fail gates”

- **Literal:** numbered criteria written before the target is opened.
- **Relation:** model prediction (	o) observed target (	o) each P-criterion passes or fails.
- **ARA bridge:** scientific constraint on interpretation. These are evidence gates, not phase labels.
- **Do not confuse with:** lowercase (p), an actual prime.

## The objects being measured

| Term | Read it as | Relation in the sieve | ARA translation |
|---|---|---|---|
| **Raw integer line** | Every consecutive integer, before filtering | Starting material | Uncompressed source record |
| **Sieve** | A sequence of divisibility filters | Each prime removes its multiples | Connection-gate walk |
| **Prime gate** | One divisibility test, such as 31 | Population before (	o) removed + retained | One local release interaction |
| **Candidate** | One number that passed the declared earlier gates | p29 filter (	o) possible prime | One measured identity/node |
| **Candidate population** | All such numbers in the target interval | Denominator for candidate survival | Parent identity being followed |
| **Adjacent edge** | The relation between two neighbouring candidates | Candidate (i) + candidate (i+1) | Explicit two-node coupling identity |
| **Pair survivor** | Both endpoints survive all required later gates | Surviving candidate pair | Relation remains intact at terminal gate |
| **Gap** | Distance between neighbouring candidates or primes | Right endpoint minus left endpoint | Spacing of adjacent connection nodes |
| **Gap class** | A group of edges with the same gap | Many edges of one spacing | One child category of the pair identity |
| **Residue** | A position modulo a repeating wheel period | One allowed wheel slot | A connection-defined local address |
| **Primorial** | Product of consecutive primes through (p) | Sets wheel period | Total period of the declared gate stack |
| **Primorial wheel** | Surviving residues and gaps over one full primorial period | Closed periodic sieve object | Finite parent sphere/cycle for wheel tests |
| **Parent wheel** | Wheel before the next prime gate is added | Existing period | Current rung identity |
| **Child wheel** | New wheel after adding the next prime gate | Parent copied (q) times, one residue class deleted | Decompressed next-rung identity |
| **Lifted candidates** | The (q) copies of one parent residue before deletion | Parent slot (	o q) possible child slots | Multiplicity created on rung expansion |
| **Removal/death gate** | First later prime dividing a candidate | Candidate alive (	o) removed | Gate at which release occurs |
| **Terminal survivor** | Candidate never removed through `qmax` | Candidate (	o) prime in this interval | Identity retained at the declared endpoint |

“Death” in these files is only a compact array label for **first sieve removal**. It does not imply literal physical
death, annihilation or an ARA singularity without an additional declared mapping.

## One state viewed three ways

These are not three unrelated models. They are three coordinates for the same survivor/release state.

### `S(g)` — survival share

\[
S(g)=\frac{\text{members still alive after gate cell }g}{\text{members at the p29 starting boundary}}.
\]

- **Relation:** starting population (	o) currently retained population.
- **ARA name:** retained/accumulated share of the declared identity.

### `1-S(g)` — release share

- **Relation:** starting population (	o) cumulatively removed population.
- **ARA name:** cumulative release along the gate walk.
- **Conservation:** (S+(1-S)=1) exactly for this accounting boundary.

### `x(g)=2(1-S(g))` — ARA diameter reading

- **Relation:** no release maps to (x=0); total release maps to (x=2).
- **ARA name:** the minimal 0-2 line reading of the survivor/release pair.
- **Caution:** this is an exact crosswalk once orientation is declared; predictive value must be tested separately.

### `theta(g)=acos(2S(g)-1)` — circumference phase

- **Relation:** diameter position (x) is decompressed to the fixed upper branch of the unit circle.
- **ARA name:** where the same state lies around the proposed circular path.
- **Caution:** here “phase” is a geometric coordinate derived from survival, not automatically physical oscillatory
  phase through time.

## Within-rung and cross-rung coordinates

| Symbol/term | Read it as | Relation | ARA role |
|---|---|---|---|
| **Log-gate progress** | How far from gate 31 to `qmax` on a logarithmic ruler | `q` divided into equal multiplicative rather than equal additive steps | Within-rung walk coordinate |
| **Gate cell** | A group of nearby `q` gates on that log ruler | Individual removals (	o) readable coarse slice | One time/process slice of the path |
| **Phase increment** `delta_r` | How much farther around the circle rung (r) moved than rung (r-1) | `theta_r - theta_(r-1)` | Cross-rung movement |
| **Withdrawal factor** `rho` | How much the next phase step shrinks or grows relative to the previous step | prior increment (	o) next increment | Log-rung transfer/carry factor |
| **Candidate deformation** `k` | Difference between observed candidate survival and an independent-sieve reference, on a log ratio | `log(S/S_independent)` | Parent envelope correction coordinate |
| **Pair relation** `J` | Pair survival remaining after candidate survival is accounted for | `log(S_edge/S_candidate^2)` | Explicit coupling term between neighbouring candidates |
| **Residual** | What remains after subtracting or dividing out a declared baseline | observation (-) expected, or log ratio | Unexplained deformation, not automatically a new wave |
| **Adult path** | The full candidate population unfolding across later gates | all child removals aggregated by `q` | Parent-scale survival/release geometry |
| **Child path** | A subdivision by gap, position, gate or another local identity | adult (	o) finer conditional groups | Decompression inside the parent identity |
| **Perpendicular coordinate** | A second axis not represented by the original one-dimensional endpoint | e.g. number-line position crossed with removal gate | Extra relational direction; independence must be tested |

## Model and comparison names

### `Home` / `Home R10` — “assume the last opened rung repeats unchanged”

- **Relation:** R10 path (	o) copied directly as the R11 prediction.
- **Purpose:** simplest lag baseline. It asks whether moving the geometry at all improves prediction.
- **ARA bridge:** the previous time/scale slice used as the next slice.

### `Direct native log rung` — “continue the multiplicative change without opening the circle”

- **Relation:** for example (S_{11}=S_{10}^2/S_9).
- **Purpose:** matched native control for whether circumference decompression adds anything beyond ordinary log-rung
  continuation.
- **ARA bridge:** vertical rung relation kept on the diameter/survival coordinate.

### `Circle secant, rho=1` — “continue the last circle step at the same size”

- **Relation:** (	heta_{11}=	heta_{10}+(	heta_{10}-	heta_9)).
- **Purpose:** tests the circle without the shrinking-step rule.
- **ARA bridge:** constant-speed movement around the circumference.

### `Circle + shared rho` — “continue around the circle with one shared shrinking-step rule”

- **Relation:** both candidate and edge identities use the same frozen `rho`.
- **Purpose:** primary PN6 native ARA model.
- **ARA bridge:** one cross-rung relation expressed through two coupled identities.

### `Sensitivity model` — “change one modelling choice to see whether the conclusion depends on it”

- **Relation:** shared-rho result compared with candidate-only or edge-only rho.
- **Purpose:** robustness, not a replacement winner selected after the target.
- **ARA bridge:** checks whether the claimed shared relation is stable under a nearby decomposition.

### `Independent sieve/product` — “assume every new prime gate acts independently”

- **Relation:** multiply the retained fractions supplied by the individual prime gates.
- **Purpose:** established connection-only reference before finite-range corrections.
- **ARA bridge:** a baseline gate stack with coupling/deformation omitted.

### `Route closure` — “reach the same identity by two independently declared relational paths”

- **Relation:** direct pair circle versus candidate parent plus `J` coupling.
- **Purpose:** checks whether the web closes rather than depending on one convenient projection.
- **ARA bridge:** triangulation of one node through different edges.

## Test-method words

| Term | Plain meaning | Why it matters relationally |
|---|---|---|
| **Development/opened data** | We have already seen the outcome and may use it to learn or diagnose | Can define a relation, but cannot count as a fresh prediction of itself |
| **Diagnostic** | A test asking where structure is or why a result occurred | Explains a path; does not automatically forecast another rung |
| **Retrospective** | Rule was formulated or selected after seeing that target | Evidence for description, not blind transfer |
| **Frozen protocol** | Equation, orientation, target and pass/fail rules written before target access | Stops the relation from moving to fit the answer |
| **Fresh / untouched target** | Target values did not enter model construction | Genuine opportunity for prospective evidence |
| **Blind prediction** | Frozen forecast scored only after the outcome is revealed | Stronger than an opened-data fit |
| **Primary model** | The model declared to carry the main claim before target access | Prevents picking the nicest sensitivity result afterward |
| **Control/baseline** | A simpler or established comparison answering “better than what?” | Gives the model a relational scale of performance |
| **Leakage** | Target information entered model choice, fitting or preprocessing too early | Collapses the evidence boundary between prediction and answer |
| **Hash** | Digital fingerprint of a file | Proves the frozen packet did not change after target opening |
| **Manifest** | List of artifact hashes and statuses | Locks the whole evidence web, not only one result number |
| **Independent validation** | Separate code rebuilds the result | Tests whether the result belongs to the data rather than one implementation |
| **Quarantine** | A comparison method is deliberately kept out until the native verdict is sealed | Prevents an established model from shaping the native ARA construction |
| **Post-hoc crosswalk** | Relation noticed after seeing the result | Useful direction for a new test; not evidence from the old target |
| **Protected/unopened target** | Reserved target that no current exploratory work may inspect | Preserves a future blind evidence boundary |

### The special `PN1H p31 capstone` warning

`PN1H p31` is a **sealed full primorial-wheel target**. Later tests may openly use prime 31 as the first ordinary gate
after a p29 starting filter; that does **not** open the PN1H object. The protected object is the complete p31 wheel and
its registered PN1H endpoints, not every appearance of the number 31.

## Scoring terms

### `Hazard` — “fraction released at this gate among those who reached it”

\[
h_g=\frac{\text{removed in cell }g}{\text{alive just before cell }g}.
\]

This is a local conditional release rate. It differs from cumulative release (1-S(g)).

### `Log loss` — “penalty for assigning the wrong probability at each gate”

- Lower is better.
- Confident wrong predictions are penalized strongly.
- In PN6 it is averaged over all at-risk events, so early cells with many surviving candidates have more weight.
- A model can therefore win log loss while having a worse terminal count, as Home did in PN6.

### `Bits per event` — “average information penalty per scored identity”

- The logarithm uses base 2, so the loss is measured in bits.
- It is a comparison score, not the framework's Information³ closure quantity.

### `RMSE` — “typical distance between predicted and observed paths”

`RMSE` means root-mean-square error. It squares each miss, averages them, then takes the square root. Lower is better.

- **Survival RMSE:** distance on the survivor-share coordinate.
- **Phase RMSE:** distance on the circumference-phase coordinate, in radians.
- **Relational reading:** how far apart the two whole paths sit on the declared ruler.

### `Terminal relative error` — “percentage miss at the final gate”

\[
\frac{|\text{predicted terminal}-\text{observed terminal}|}{\text{observed terminal}}.
\]

This measures endpoint accuracy only. It can be excellent while the within-rung path shape is imperfect.

### `p-value` — “how often the control world looks at least this extreme”

- Small values mean the observation is unusual under the declared null/control generator.
- It is not the probability that ARA is true or false.
- Its meaning depends entirely on the null model and test fixed in advance.

### `FWER` — “family-wise error control”

When many frequencies or cells are searched, FWER adjusts the threshold so “one exciting-looking result somewhere”
is not treated as strong evidence too easily.

## Established prime-mathematics comparison terms

These are external mathematical rulers. Recovering or resembling them can validate a crosswalk; exceeding them on a
fresh equal-information test would be stronger evidence for a new calculation method.

### `PNT` / `PNT29` — Prime Number Theorem density, conditioned through 29

- **PNT:** primes near (n) occur with average density about (1/\log n).
- **PNT29:** adjusts that average after we have already excluded divisibility through 29.
- **Relation:** large number-line location (	o) expected prime density among p29 candidates.
- **ARA bridge:** established slow parent-scale envelope/control.

### `Mertens factor` — finite sieve-product correction

- **Literal:** relates products over small prime gates to logarithmic prime density.
- **Relation:** independent gate product (	o) corrected large-scale survivor envelope.
- **ARA bridge:** known cross-scale deformation of the connection-only product.

### `Buchstab` — survival law for numbers with no small prime factor

- **Literal:** Buchstab's function describes the density of “rough” numbers as the small-factor cutoff advances.
- **Relation:** candidate population (	o) later gate threshold (	o) expected full survival curve.
- **ARA bridge:** established adult sieve-path shape. It may look arc-like without proving the ARA circle uniquely.

### `Rough number` — “a number with no prime factor below the declared cutoff”

- **Relation:** increase the cutoff (	o) fewer rough numbers survive.
- **ARA bridge:** the state of having passed the connection gates so far.

### `Hardy-Littlewood` / `HL29` — expected prime-pair frequency

- **Literal:** established formulas estimate how often prime patterns such as pairs occur, including allowed gap
  structure.
- **HL29:** the comparison conditioned on the p29 starting filter.
- **Relation:** candidate density + pair spacing constraints (	o) expected pair survival.
- **ARA bridge:** established pair-coupling control.

### `Singular series` — local divisibility correction for a prime pattern

- **Relation:** proposed gap/pattern (	o) how compatible it is with all prime moduli.
- **ARA bridge:** connection-web weighting of a pair/constellation; not an ARA singularity.

### `Fourier` — decompose a sequence into repeating frequencies

- **Relation:** raw path (	o) mixture of sine/cosine frequency components.
- **ARA bridge:** useful external wave lens, but processed data; it is not automatically native ARA.

### `SVD` — find the strongest joint directions in a two-axis table

- **Relation:** position-by-gate matrix (	o) ranked orthogonal modes.
- **ARA bridge:** decompression aid for a flattened second coordinate; the modes need independent ARA interpretation.

### `NMF` — find additive non-negative parts

- **Relation:** non-negative data table (	o) non-negative component patterns and their weights.
- **ARA bridge:** often visually connection-heavy because it builds the whole from additive positive parts. It is a
  processed decomposition, not by itself one of ARA's physical poles.

## ARA-specific interpretation terms used in the prime work

### `Connection-heavy`

The visible structure is dominated by divisibility links, residue classes, wheel repetition and factor gates. It is
an interpretation of the relational content—not a proof that integers literally occupy the physical Space pole.

### `Time-like candidate coordinate`

A proposed opposite/process direction that should carry ordered change not reducible to the same divisibility labels.
It must be independently defined and recur across rungs before receiving that name. PN3B did not recover such a
scale-persistent coordinate.

### `Adult wave/path`

The aggregate survival-release shape across the whole candidate population. Child removals create it, but it is
measured at the parent population boundary.

### `Child wave/path`

A finer conditional path inside the adult—such as one gap class, position band or removal-stage group. Children can
remain asymmetric even when the parent projection is quiet or smooth.

### `Three-point ARA stencil`

Three nearby numerical readings used to estimate local level/slope/curvature. It is **not** Information³ unless two
identities and their retained relation are explicitly present.

### `Information³ closure`

Identity A + identity B + their relation closes enough information to specify a third/parent identity. In prime
tests, “three numbers were used” is not sufficient to claim this structure.

### `Parent probability budget`

A model forces child probabilities to average back to a declared parent probability. This conserves predicted
probability mass; it is not the canonical TE-ARA total-2 identity ledger.

### `TE-ARA`

The fixed allocation ledger of a declared identity:

\[
\mathrm{TE}(I)=t_A+t_B+\sum_j t_{R_j}+t_{Other}=2.
\]

Its component allocations vary, but its whole does not. Prime survival probabilities are not automatically TE-ARA;
an explicit identity boundary, components, relation terms, Other, and a common normalization are required. A child
allocation inside its parent may be below 2, but if that child is opened as its own identity its own ledger
renormalizes to 2.

## How to translate a compressed sentence

Example:

> “PN6 predicted R11 p29-conditioned edge survival across 24 q-cells using shared rho.”

Expand it in relational order:

1. **PN6:** use the native circumference test rules.
2. **R11:** work on the whole decimal window near (10^{11}).
3. **p29-conditioned:** begin with numbers that passed all gates through 29.
4. **Edge survival:** follow whether neighbouring candidate relations remain intact.
5. **q-cells:** walk through later prime gates from 31 to `qmax`, grouped into 24 log-spaced slices.
6. **Shared rho:** move around the candidate and edge circles using one common cross-rung shrinking-step factor.

The sentence now reads:

> “On the (10^{11}) parent-scale window, start with numbers surviving the fixed connection gates through 29. Follow
> the relations between neighbouring survivors as later gates progressively remove them. Predict that path by moving
> around the ARA circumference using the same rung-to-rung withdrawal relation as the single-candidate identity.”

## Naming convention for future prime documents

To reduce memory load, the first use of compact notation should carry a relational gloss:

- `Q29 [connection mask through prime 29]`
- `R11 [decimal parent rung near 10^11]`
- `p29-conditioned candidates [numbers surviving fixed gates through 29]`
- `q [current later prime gate]`
- `J [pair relation remaining after candidate survival is accounted for]`

After that first expansion, the short form may be used within the same section. A document should never introduce
three new letter-number tokens in one sentence without expanding them.

## PN9 tangent-sphere terms

| Compact term | Read it as | Mathematical relation | ARA role |
|---|---|---|---|
| `g_minus` / `g⁻` | Gap entering the current prime | `p_i - p_(i-1)` | Left/incoming gap-sphere diameter |
| `g_plus` / `g⁺` | Gap leaving the current prime | `p_(i+1) - p_i` | Right/outgoing gap-sphere diameter |
| **Gap-sphere** | The one-dimensional interval of a prime gap, treated as a sphere diameter | centre = interval midpoint; radius = gap/2 | Decompression of one connection spacing |
| **Contact ridge** | The prime shared by adjacent gap intervals | centre distance = sum of half-gap radii | Exact touching point of the two gap-spheres |
| `x` | Which adjacent sphere diameter is larger | `2*g_plus/(g_minus+g_plus)` | Child/contact-balance coordinate; `x=1` means equal gaps |
| `L` | Mean size of the two adjacent diameters | `(g_minus+g_plus)/2` | Local sphere scale discarded by `x` alone |
| `h` / **log home** | Established expected local prime-gap scale | `ln(p_i)` | Conventional rung reference, not an ARA discovery |
| `y` | Local sphere scale compared with log home | `2*L/(L+ln(p_i))` | Proposed adult-scale coordinate; `y=1` means `L=ln(p_i)` |
| `X-M2` | Shape-only next-state model | `P(x_next | x_previous,x_current)` | PN7C child/contact predictor |
| `XY-M2` | Shape plus scale next-state model | `P(x_next | x_previous,x_current,y_current)` | Tests whether scale adds transferable information |

The unbinned pair `(x,y)` does not manufacture information. At known `p_i`, it recovers the adjacent gaps through
`L=ln(p_i)*y/(2-y)`, `g_plus=x*L`, and `g_minus=(2-x)*L`. Binning deliberately compresses that information.

## PN10 factor-sphere terms

| Compact term | Read it as | Mathematical relation | ARA role |
|---|---|---|---|
| **Factor sphere** | The complete reversible relation between the factors `1` and `n` | factor pairs satisfy `d*(n/d)=n` | One ARA identity viewed from its small-factor and large-factor directions |
| `x_n(d)` | Where factor candidate `d` sits relative to the whole number `n` | `2*log(d)/log(n)` | Native 0-2 factor-diameter position |
| **Factor ridge** | Square-root completeness boundary | `d=sqrt(n)`, so `x_n(d)=1` | The two factor directions meet here |
| **Divisor collision** | A tested prime gate divides `n` | `q | n` with `x_n(q)<=1` | Interior factor landmark proving a composite identity |
| **Quiet ridge** | The factor walk reaches `sqrt(n)` without a divisor | no prime `q<=sqrt(n)` divides `n` | Exact prime classification in this factor sphere |
| **Reflected factor** | The paired large factor for small factor `d` | `n/d`, at `2-x_n(d)` | Opposite-direction appearance of the same factor relation |
| **Prime-square ridge** | A prime square's root is an exact middle factor | for `n=p^2`, `x_n(p)=1` | Exact ridge collision; therefore composite, not prime |
| **Early-ridge cutoff `c`** | How far the factor walk has progressed before stopping | test factor positions through `x<=c<1` | Partial ARA measurement yielding a probability, not exact identity |
| **Survivor purity** | Fraction of surviving integers that are prime | `prime_count/survivor_count` | How much prime information has accumulated by cutoff `c` |
| **Fixed-Q control** | Reuse the same absolute divisor limit at every number scale | `q<=Q_D(c)` | Tests whether ARA's identity-relative scale matters |

The factorisation face and sieve-survivor face are opposite walks through this one factor sphere. They must not be
counted as independent confirmation. Exact ARA recovery at `x=1` is algebraically the classical trial-division rule
through `sqrt(n)`.

## PN10B child-phase terms

| Compact term | Read it as | Mathematical relation | ARA role |
|---|---|---|---|
| **Paid gate** | A divisor prime already tested before the parent cutoff | `q<=n^0.45` at `c=0.90` | Existing parent information; not a new factor test |
| `A_j` | Distance since the previous multiple of gate `q_j` | `2*(n mod q_j)/q_j` | Phase A direction of one local 0-2 child axis |
| `B_j` | Distance remaining to the next multiple of gate `q_j` | `2-A_j` | Phase B direction of the same child axis |
| `s_j` | Signed location relative to the child ridge | `A_j-1` | Negative/positive orientation around local `1.0` |
| `h_j` | Whether neighbouring gate children lean together or oppositely | `s_j*s_(j+1)` | Registered ordered child-coupling relation |
| **Parent empirical** | Use only the prime fraction among training survivors | one constant probability | No-child baseline at the same parent cutoff |
| **Buchstab parent** | Established rough-number probability at the same relative sieve depth | `(0.45)/omega(2/0.90)` | Standard number-theory parent calibration control |
| **Order-scrambled child** | Preserve each row's child positions but damage fixed gate-rank order | rotate child sequence by `n mod 9` | Tests whether ordered coupling, rather than inventory alone, helps |
| **Child centroid** | Average position of the nine paid-gate child A readings | `mean_j A_j` | Current node's gate-relative A/B centre; may sit at the ridge while individual children remain asymmetric |
| **Child spread** | Average distance of the nine children from the ridge | `mean_j abs(A_j-1)` | Retained internal asymmetry hidden by the centroid |
| **Child flip count** | Number of adjacent paid-gate children on opposite sides of the ridge | count of `(A_j-1)(A_(j+1)-1)<0` | One view of internal alternating structure; eight boundaries are possible for nine children |
| **Parent event crest** | Candidate survives the factor walk through its square-root boundary | parent factor progress `=1` | Exact prime ridge after the required gates are completed; descriptive, not an advance warning |
| **Event-centred trace** | Align raw integers before, at and after a prime or control event | offset `k=n-n_event` | Exposes lead/at/lag crests, troughs and daughter shoulders without reducing them to one benchmark score |
| **Geometry verdict** | What appeared in the ARA coordinates whether or not it predicted the target | distributions + events + landmarks + controls | Required companion to the registered claim/benchmark verdict |

`A_j+B_j=2` is exact but contains one coordinate, not two independent information sources. PN10B found that this
child geometry closes correctly while failing to rank later hidden factors on a fresh target.

The later post-hoc disclosure must be read alongside that null: the parent coordinate has an exact prime event
crest, while the paid-gate child waves are broad, locally asymmetric and almost equally distributed in primes and
late composites. Rich geometry and null discrimination are simultaneous results, not contradictions.

## PN10C three-lane terms

| Compact term | Read it as | Mathematical relation | ARA role |
|---|---|---|---|
| **Centre orientation** | Which of the two prime-admissible mod-6 sides contains the event | `p mod 6` is `1` or `5` | Direction that determines which coloured branch becomes phase versus anti-phase |
| **Offset lane** | One repeating family around the centre | nonzero even `k mod 6` in `{0,2,4}` | Decompressed shoulder family in the parent event trace |
| **Red/blue swap** | The two coloured families exchange high and trough roles | `0.5*((M_1,4-M_1,2)+(M_5,2-M_5,4))` | Quantified reversible Phase A/Phase B exchange |
| **Reflection test** | Reverse offset direction while flipping centre orientation | compare `T_1(k)` with `T_5(-k)` | Tests whether the pair closes under orientation reversal rather than merely sharing an average |
| **Black/common lane** | Offsets that keep either centre clear of factors 2 and 3 | nonzero `k=0 mod 6` | Invariant route shared by both orientations; not an independent source at this grain |
| **Admissible coloured branch** | The coloured lane not forced into factor 3 for the current centre | lane 4 at centre 1; lane 2 at centre 5 | Proper same-orientation comparison for testing whether black is independently stronger |
| **Independent-third-wave discriminator** | Black compared with the currently admissible coloured lane | mean of the two black-minus-admissible contrasts | Separates a true extra lane from an aggregation-created third appearance |
| **Black child `m`** | Which sub-lane is occupied inside the common mod-6 route | for `k=6m`, use `m mod 5` | Child coordinate that decompresses the parent route from 6 to 30 |
| **Rotating factor-5 trough** | The one black child forced into a multiple of 5 | `(p mod 5 + m mod 5) mod 5=0` | Conditional child collision moving with parent orientation |
| **Wheel hierarchy** | Successive survivor patterns after adding prime gates | `6 -> 30 -> 210 -> ...` | Established sieve structure that can be read as parent-to-child decompression |

The three visible aggregate families are real, but “three families” does not automatically mean three independent
sources. After centre conditioning, PN10C found two exchanging coloured orientations plus one common route. That
common route then contains its own mod-5 child asymmetry. This is exactly why the measurement grain and approach
direction must accompany an ARA label.

## Prime square-ridge instrument terms

| Compact term | Read it as | Mathematical relation | ARA role |
|---|---|---|---|
| **Incremental/postponed sieve** | Generate integers in order while scheduling future prime multiples only when needed | a new prime `p` schedules `p²`, then advances by `+p` | Established exact engine beneath the instrument |
| **Quiet node** | No currently active prime schedule reaches `n` | scheduled collision set at `n` is empty | Exact prime event in this complete incremental scan |
| **Collision voice** | One active prime child that divides the current integer | `p | n` and `p²<=n` | One child-wave contribution to a composite node |
| **Latent child** | A discovered prime whose independent schedule has not started | `p<=n<p²` | Registered child identity awaiting its square-ridge boundary |
| **Independent child activation** | First multiple of `p` not already guaranteed to be marked by a smaller prime | `p²` | Precise meaning of a child “beginning” at the ridge |
| **Rung size squared** | The current prime gate's size multiplied by itself | prime gate `p` gives boundary `p²` | Vertical activation boundary for that child, not `W_k²` |
| **Periodic child strike** | A later independently scheduled multiple | `p²+kp`, for integer `k>=0` | Horizontal continuation of the child period |
| **Multi-voice collision** | More than one active prime child reaches the same node | multiple prime divisors `p<=sqrt(n)` | Coupling web at a composite identity, rather than a single genealogy |
| **Square-ridge event** | A prime factor meets its reflected partner | `n=p²`, `x_n(p)=1` | Exact `1.0` factor collision and first independent `p` strike |
| **Fundamental joint recurrence** | First node at which a declared set of child periods all return to the same phase | `L(P)=lcm(p_1,...,p_m)` | Parent cycle length produced by the child-period web |
| **Phase coherence `R`** | How completely the declared child phases align | `R=abs(mean_j exp(i*theta_j))` | Independent discriminator for a resonance ridge; `R=1` is exact lock |
| **Collective resonance ridge** | Several child waves complete a shared cycle as one parent event | at `n=L(P)`, every `n mod p_j=0` and `R=1` | Coherent parent ridge with potentially asymmetric decompressed children |
| **510 four-child resonance** | Fundamental joint recurrence of children `2,3,5,17` | `510=lcm(2,3,5,17)` and `sum_p x_510(p)=2` | Exact resonance-ridge example distinct from a square ridge |
| **Fundamental full resonance** | A node is exactly the product of its active distinct child primes | `n=product(P)=lcm(P)`, with at least three voices | First full parent closure for that exact child set |
| **Harmonic resonance repeat** | An already closed child set aligns again at a larger node | `product(P)<n` and `product(P)` divides `n` | Recurrent phase lock without a new full child-product closure |
| **Primorial rung** | Fundamental closure formed by consecutive primes beginning at 2 | `p_k#=2*3*5*...*p_k` | Established wheel/primorial ladder; a special resonance family, not every closure |
| **Child note** | Permanent audible label assigned in ascending prime-lane order | consecutive C-major degrees from `p=2 -> C4` through active `p=67 -> G6` | Sonification coordinate for hearing which children strike; not mathematical evidence |
| **Event chord/arpeggio** | Notes belonging to all active child collisions at one node | ordered note set for `event.hits`; 510 gives `C4-D4-E4-B4` | Audible decompression of collision multiplicity; quiet prime nodes are rests |
| **Assigned sonification** | A stable sound label placed on an exact arithmetic lane | the note map is chosen once; child membership still comes from divisibility | Listening aid only; a pleasing interval is not evidence for ARA or prime structure |
| **Parent share coordinate** | How much of a product-parent's logarithmic diameter one child identity occupies | for `N=product_i(n_i)`, `x_N(n_i)=2*log(n_i)/log(N)` and `sum_i x_N(n_i)=2` | Compares several already closed identities on their shared parent rung |
| **Complementary resonance pair** | Two disjoint fundamental child identities whose products reconstruct one parent | `gcd(a,b)=1`, `a*b=N`; 714 and 715 partition the factors of `17#` | Binary parent closure, often read near the `1.0 <-> 1.0` ridge when `a` and `b` are similar |
| **Multiplicity echo** | Repeated prime-factor content hidden by a distinct-child-only view | `n/rad(n)`, where `rad(n)` is the product of distinct prime factors | Restores the part of the `0-2` factor diameter flattened when repeated children are counted once |
| **Three-by-three information lock** | Three three-child identities closing one parent while retaining nine distinct child lanes | 1885, 1886 and 1887 multiply to a parent with nine distinct prime factors | Exact hierarchical illustration of the proposed Information³ relation; post-hoc, not a prediction result |
| **Fundamental base `B`** | A squarefree node equal to the product of all its independently active prime children | `B=product(P)` with at least three children and `p^2<=B` for each `p` | Starting information lock for the PN11 vertical repeat path |
| **First missing child `q(B)`** | Smallest prime not already present in the base lock | every prime below `q` divides `B`; `q` does not | First multiplier capable of expanding the distinct-child identity |
| **Old-lock share `A_B(k)`** | Fraction of the logarithmic whole still supplied by fundamental base `B` at repeat `k` | `2*log(B)/log(kB)` | Phase-A side of the PN11 lock/repeat diameter |
| **Repeat-echo share `E_B(k)`** | Fraction of the logarithmic whole supplied by repeated content | `2*log(k)/log(kB)` and `A_B(k)+E_B(k)=2` | Phase-B side of the same diameter; not independent evidence |
| **Expansion coordinate `X_B`** | Old-lock position when the first absent child joins | `X_B=A_B(q)=2/(1+log(q)/log(B))` | Tested vertical handover observable; scale-dependent, not fixed at Phi in PN11 |
| **Primorial parent `B_m`** | Complete consecutive-prime connection lock at rung `m` | `B_m=product_(j<=m)(p_j)` | Canonical nested parent used for the PN12 upward walk |
| **Adjacent next child `q_m`** | First prime identity immediately outside the current primorial lock | `q_m=p_(m+1)` | Native external phase reference for the tested larger-carrier reading |
| **Next-child entry phase `u_m`** | Where the completed parent lands on the next child's circular period | `(B_m mod q_m)/q_m` | Exact unassigned phase in `[0,1)`; ARA display position is `2u_m` |
| **Upward carrier step `delta_m`** | Circular change in next-child entry phase after climbing one prime rung | `(u_(m+1)-u_m) mod 1` | PN12's tested meta-wave observable; compares normalized phases of successive adjacent children |
| **Circular coherence `R`** | Whether rung steps repeatedly point in one angular direction | `abs(mean(exp(2*pi*i*delta_m)))` | `1` is exact common rotation; `0` is no net angular alignment |
| **Golden-angle carrier** | Fixed upward step proposed for the large Phi wave | `delta=1/phi^2=137.507764 degrees` | PN12 primary; not supported in the adjacent-child phase projection |
| **36-degree carrier** | Pentagon half-angle/shear proposed before the PN12 run | `delta=1/10 turn=36 degrees` | Separate PN12 secondary; nearest target landmark but not coherent or distinguishable from zero |
| **Prime resonance-ridge lab** | Interactive view of the incremental sieve, factor diameter and resonance classes | exact generation and classification through `5,000` | Teaching/research instrument; not a new speed claim |

Below `p²`, multiples of `p` still exist; they have already been removed by smaller prime gates. Calling `p²` the
child birth therefore means **birth of independent sieve responsibility at this grain**, not first arithmetic
appearance. This distinction keeps the ARA geometry aligned with the established proof of the sieve optimization.

## PN16 ordered whole-wave lift terms

| Compact term | Read it as | Mathematical relation | ARA role |
|---|---|---|---|
| **Forward whole `AB`** | Apply all current prime gates from smallest to largest while retaining every partial survivor mask | `P_2,P_3,...,P_(p_k)` | One ordered walk through the completed parent identity |
| **Reverse whole `BA`** | Apply the same current gates from largest to smallest | `P_(p_k),...,P_3,P_2` | Oppositely oriented walk through the same gate inventory |
| **Ordered path relation** | Difference between forward and reverse partial masks at matched depths | normalized Hamming distance `D_(k,j)` | Process information retained before the two routes close |
| **Completed parent projection `P_k`** | Numbers coprime to the complete primorial parent | `P_k(n)=1` iff `gcd(n,p_k#)=1` | One coarse-grained whole after every current child has acted |
| **Order-invariant closure** | Forward and reverse routes finish at the same parent mask | prime-gate projections commute, so `AB=BA=P_k` at completion | Two histories close to one identity; not two independent completed poles |
| **Idempotent recombination** | Applying the same completed sieve identity again changes nothing | `P_k²=P_k` | Why a completed whole plus its simple reversal does not create the next rung here |
| **First quiet node above a parent** | Smallest integer above `p_k` surviving every gate through `p_k` | `q_k=min{n>p_k:P_k(n)=1}=p_(k+1)` | Emerging next child/singularity located by the complete lower-rung web |
| **One-lift release rule** | The new gate removes one of `q` lifts of every parent survivor | newly released `=phi(p_k#)`; conditional share `=1/q` | New coupling relation that converts repeated parent copies into the next wheel |
| **PN16 Information³ refinement** | Old whole, newly emerged survivor, and their gate relation close as the next whole | `(P_k,q_k,P_(q_k)∘P_k) -> P_(k+1)` | Supported `1+1=3 -> 1` reading at this grain; reversal alone is insufficient |

PN16's `1/q` release is an exact wheel-sieve fraction tied to the particular next gate. It is not a universal ARA
leak constant. Likewise, the quiet-node recurrence is the established incremental-sieve/trial-division principle
expressed bottom-up; it is not a new complexity result.

## PN17 one-shot local-ridge terms

| Compact term | Read it as | Mathematical relation | ARA role |
|---|---|---|---|
| **Arbitrary anchor `N_0`** | Number scale near which a prime is requested | PN17 uses `400,000,000,000` | Local `1.0` reference inside the declared `0-2` search diameter |
| **Raw child phase** | Current position of lower prime gate `q` at the anchor | `A_q=2*(N mod q)/q`, `B_q=2-A_q` | One fully decompressed child ARA retaining identity, period and direction |
| **Child collision field `C_N(t)`** | Number of lower prime children striking offset `t` | sum over `q<=sqrt(N+W)` of `1[(N+t) mod q=0]` | Complete local web of child singularity crossings |
| **Quiet factor ridge** | Offset with no lower-child collision through the square-root boundary | `C_N(t)=0` | Exact prime condition used by PN17; distinct from raw incoming/outgoing gap equality |
| **One-shot correction `Delta_N`** | First quiet offset above the anchor | `min{t>0:C_N(t)=0}` | Signed local inverse-geometry answer rather than upward prime-ladder generation |
| **Full-decompression result** | Apply one local collision field at the requested scale | for `N=400,000,000,000`, `Delta_N=19` | Exact ARA crosswalk of a standard segmented sieve |
| **Scalar ridge shortcut** | Average many child A/B phases into one balance coordinate | tested with equal, `log(q)` and `1/q` weights | Not supported in PN17; all three selected composite offsets rather than +19 |
| **Contact equality** | Two separately normalized sides both reach their shared node | each side reads progress `1` at contact | Geometric closure that discards raw gap scale; not a next-gap prediction by itself |
| **Raw equal-gap control** | Predict outgoing prime gap by copying the incoming gap | `g_hat_plus=g_minus` | Exact at only about 2.09% of opened R11 prime nodes; not PN17's prime criterion |

PN17's full-vector success and scalar-average failure are simultaneous. The full child web determines the local
prime exactly because it retains the standard square-root divisibility information. A new ARA prime shortcut still
requires a frozen coupling law that compresses that web without erasing child periods and phases.

## PN18 recursive TE-ARA product-tree terms

| Compact term | Read it as | Mathematical relation | ARA role |
|---|---|---|---|
| **Child-product parent `G_L`** | Every required lower prime gate recursively paired into one integer | `G_L=product(q)` for all prime `q<=sqrt(N+W-1)` | Complete connection-side child hierarchy; mathematically lossless but not low-dimensional |
| **Candidate parent `M_I`** | Product of all local candidate identities inside one tree branch | `M_I=product(N+t)` for offsets `t` in branch `I` | Traversal-side parent at the corresponding recursive grain |
| **GCD relation `R_I`** | Prime-child content shared by a candidate branch and the child parent | `R_I=gcd(M_I,G_L)` | Informative third coupling the two parents |
| **Quiet leaf** | One candidate sharing no required lower child with the product parent | `gcd(N+t,G_L)=1` | Exact local prime ridge |
| **Mixed unresolved branch** | A branch containing at least one child collision but possibly quiet leaves too | `R_I>1` at a branch with more than one leaf | Cannot be skipped; must be decompressed further |
| **Recursive one-shot correction** | First p29-wheel leaf with no lower-child relation | `min{t:gcd(N+t,G_L)=1}` | PN18's sealed local correction; `+9` at 700 billion |
| **Operational parent compression** | Replace separate child queries with one reusable product root | PN18 root has 1,205,845 bits / 150,731 bytes | Exact repackaging useful for GCD queries, not removal of child information |
| **Information compression control** | Count the bits and construction cost hidden by the phrase “one integer” | compare root, child list, bit sieve, collision field and candidate tree | Prevents structural coarse-graining from being mistaken for a small state |
| **Batch-GCD/product-tree control** | Established arithmetic family matching PN18's construction | recursive products plus GCD/remainder relations | Standard mathematical home; ARA supplies the relational reading, not a new theorem |

PN18 sealed `700,000,000,009` from the fresh anchor `700,000,000,000` before target primality was checked, and the
independent v1.1 receipt passed `36/36` checks. The recursive hierarchy preserved the exact ridge, but its root was
larger than a one-bit sieve and PN17-sized collision field, while the full candidate tree added about 735 KB of ideal
integer payload. The supported result is therefore exact recursive crosswalk and operational repackaging, not a
faster or genuinely low-dimensional prime formula.

## PN19 two-parent information-lock terms

| Compact term | Read it as | Mathematical relation | ARA role |
|---|---|---|---|
| **Two complete parent waves** | All required lower prime children folded into two top-level groups rather than treated as two individual factors | ordered children through `floor(sqrt(2N))` are split once by cumulative log weight | Preserves the child web internally while exposing one Phase A, one Phase B and their relation at the working rung |
| **Log-balanced parent split** | Cut the ordered child list where each side supplies almost half the total log product | minimize `abs(sum_A log(p) - sum_B log(p))` | Produces a TE-ARA display close to `1 + 1 = 2` without asserting identical local action |
| **Phase A parent mask** | Candidate positions untouched by the smaller, frequently striking children | `S_A(t)=1` iff no child in A divides `N+t` | Connection-heavy parent; PN19's strong approximate or “second-go” locator |
| **Phase B parent mask** | Candidate positions untouched by the larger, rarely striking children | `S_B(t)=1` iff no child in B divides `N+t` | Sparse complementary parent that catches near-square-root composites missed by A |
| **Information-lock mask** | Positions where both complete parents are simultaneously quiet | `S_AB(t)=S_A(t) AND S_B(t)` | The informative third; one new locked identity from A, B and their tested relation |
| **Second-go success** | A parent-only first survivor already equals the joint first survivor | `first(S_A)=first(S_AB)` or identically for B | Registered approximate claim, distinct from definitive lock exactness |
| **q-free local recovery** | Start from an arbitrary anchor without supplying the unknown next prime as an input | build A/B from derivable lower prime children, then take `first(S_A AND S_B)` | Removes the future-gate label `q`; does not remove lower-child information |
| **Equal weight / asymmetric action** | Parents can each carry about one TE-ARA share while having very different strike densities | target `E_A=0.9999938531`, `E_B=1.0000061469`; survivor densities `3.8818%` and `95.0150%` | Direct example of identity-dependent behavior inside the same conserved `E_A+E_B=2` parent |
| **Phase A square-root reach** | Approximate upper child boundary created by halving log weight through `sqrt(2N)` | boundary near `sqrt(N/2)=0.7071 sqrt(N)` | Explains why Phase A alone is a strong partial sieve rather than a magical scalar predictor |
| **PN19 fresh sealed result** | First joint survivor above the unused 900-billion anchor | `900,000,000,000 + 13 = 900,000,000,013` | Exact two-parent ARA crosswalk; independent receipt passed `38/38` |
| **PN19 robustness audit** | Post-target deterministic grid across five number scales | 1,000 anchors; Phase A `93.2%`, Phase B `4.7%`, p29 control `28.0%` | Supports “probably second go” operationally; exploratory and not a second frozen target |

At completion, Boolean intersection is commutative: `S_A AND S_B = S_B AND S_A`. PN19 therefore tests the
Information³ closure of two parents plus their relation, but not a genuinely noncommutative AB/BA evolution after
closure. The exact lock remains an established segmented sieve expressed through the proposed ARA hierarchy.

## PN20–PN23 compression and closure terms

| Compact term | Read it as | Mathematical relation | ARA role |
|---|---|---|---|
| **Literal two-child shortcut** | Retain only one proposed immediate A child and one immediate B child | PN20 tested three definitions; all were `0/7` exact | Rejected bounded summary; not the same as two complete PN19 parents |
| **Ridge-straddling pair** | Last prime gate below `sqrt(n)` plus first gate above it | PN21 held-out retained `R²≈0`, AUC≈0.5 | Two rulers around a boundary do not automatically own the parent identity |
| **Odd-lattice projection** | Map `A` through `T(A)=oddceil(7A/2+1)` | exactly lanes `{1,5,9,13} mod 14` | PN22 wheel filter; improves over raw odds but not matched lanes |
| **Wheel anti-pair** | One allowed residue and its modular negative | `(r,M-r)` for even modulus `M` | Exact reversible Phase-A/Phase-B lane pair |
| **Adult representative** | The one anti-pair member actually stored | choose `r<M/2`; recover `M-r` | Removes redundant orientation without discarding the pair identity |
| **Killed copy index** | Which of the `p` lifted copies is removed by new gate `p` | `k_A=-r*M^(-1) mod p` | Child collision location on the lifted-copy diameter |
| **Reflected killed copy** | Opposite lane's removed copy | `k_B=p-1-k_A` | Exact anti-phase location; normalized A/B mean is `1` |
| **Direct child ridge** | Both killed copies occupy the middle lift | `k_A=k_B=(p-1)/2`, so `(x_A,x_B)=(1,1)` | Ridge visible at child grain |
| **Coarse pair ridge** | Asymmetric reflected children close only when read together | examples `(0,2)`, `(0.5,1.5)` | Parent reads `1.0` while retaining child asymmetry |
| **Lossless 2:1 compression** | Store one representative for two residue lanes | `|U(M)|=2*N_pair(M)` | Exact PN23 state reduction, not a prime-specific predictor |
| **Fractal lift growth** | Same pair rule reused after adding gate `p` | `N_pair(Mp)=(p-1)N_pair(M)` | Rule repeats; information/state size still grows |
| **Three information stages** | Child state → two parent views → first joint quiet candidate | PN17–PN19 exact decompositions | Conceptual three-step map, not three arithmetic operations |
| **Three-cheap-operation claim** | Obtain the next prime from a bounded number of small calculations independent of scale | not achieved; PN20/PN21 compact definitions failed | Must not be inferred from the successful three-stage crosswalk |

The final prime-thread disposition is **PARKED**. Exact factor/wheel/anti-pair mathematics remains available as an
ARA domain subset; prime-specific algorithm development resumes only with a bounded sufficient statistic, a measured
computational improvement, or a new externally frozen prediction. See
`PRIME_THREAD_CAPSTONE_AND_CLOSURE_2026-07-21.md`.

## Source boundary

This glossary defines how terms were used in the ARA prime-test series through PN10C, the resonance-ridge
instrument, the 510 resonance-ridge clarification, the later 714-715, 1274-1276 and 1885-1887 resonance-lock
decompositions, the PN11 vertical-handover test, the PN12 angular-carrier test, the PN16 ordered whole-wave lift,
PN17 one-shot local-ridge, PN18 recursive TE-ARA product-tree, PN19 two-parent information-lock, PN20/PN21 compact
child nulls, PN22 odd-lattice wheel and PN23 anti-pair fractal lift through 21 July 2026. Established
mathematical terms retain their standard meanings; the ARA bridge column records the framework interpretation and
does not convert that interpretation into an established theorem.
