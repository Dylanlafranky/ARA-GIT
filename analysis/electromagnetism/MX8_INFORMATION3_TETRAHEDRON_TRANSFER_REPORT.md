# MX8 — Information³ tetrahedron mathematics and held-out transfer

## Result first

The mathematics confirms a precise core of Dylan's proposed construction:

- two binary phase axes have exactly four joint routes;
- adjoining their interaction coordinate produces a regular tetrahedron, not merely a loose pyramid analogy;
- the interaction is the closing third, not a third independent wave;
- a four-route strength table decomposes exactly into a common term, two single-axis asymmetries and one relational
  asymmetry;
- three named identities have six possible directed pair relations, or nine state-and-relation slots when their three
  self-state slots are included.

The new held-out plasma test did **not**, however, confirm that one constant relation coefficient predicts route
strength across later time slices. The relation model improved relative L2 error over the two-axis additive model by
only `0.00736%`; its 95% snapshot-block-bootstrap interval was `-0.00140%` to `+0.01550%`, crossing zero. Vector
correlation and median angular error were also microscopically worse. The frozen gate therefore failed.

This is a constructive split result: the Information³ closure has exact mathematics, while its reusable local
dynamics remain unresolved and require contextual geometry rather than a universal multiplier.

## 1. Exact four-route closure

Let

\[
\underbrace{x}_{\substack{\text{first signed axis}\\\text{ARA Phase A/B}}},
\underbrace{y}_{\substack{\text{second signed axis}\\\text{angled ARA Phase A/B}}}
\in\{-1,+1\},
\qquad
\underbrace{r=xy}_{\substack{\text{interaction sign}\\\text{ARA informative third}}}.
\]

There are exactly four joint possibilities:

\[
(x,y,r)\in
\{(+,+,+),(+,-,-),(-,+,-),(-,-,+)\}.
\]

They obey

\[
\underbrace{xyr}_{\substack{\text{three-coordinate closure}\\\text{relational lock}}}
=
\underbrace{(xy)^2}_{\substack{\text{same relation twice}\\\text{binary parity}}}
=1.
\]

Plainly: two signed readings create four routes. The third symbol records how those two readings relate. Any two of
`x`, `y`, and `r` recover the third. It closes the identity, but it does not add a third freely moving wave.

## 2. Why the lifted shape is a regular tetrahedron

Call the four vectors above \(v_1,\ldots,v_4\). Every vector has

\[
\|v_i\|^2=1^2+1^2+1^2=3.
\]

For any distinct pair, either one or two input signs change. In both cases,

\[
v_i\cdot v_j=-1.
\]

Therefore every pair has the same separation:

\[
\|v_i-v_j\|^2
=\|v_i\|^2+\|v_j\|^2-2v_i\cdot v_j
=3+3-2(-1)=8,
\]

so

\[
\underbrace{\|v_i-v_j\|}_{\substack{\text{all six equal edges}\\\text{closure geometry}}}
=2\sqrt2.
\]

Their centroid is zero. Four equidistant points in three coordinates form a regular tetrahedron.

Plainly: once the two phase readings and their interaction are held simultaneously, the four possible routes occupy
the corners of a perfectly balanced triangular pyramid. This is the exact mathematical version of the “extra axis
locks the information” intuition.

One qualification matters. A **square pyramid** has four base vertices plus a separate fifth apex. The parity lift
itself produces four tetrahedral vertices. If the aggregate parent is drawn as an additional apex, that is a useful
ARA visualisation, but its position is not fixed by this proof. In the exact weighted construction below, the parent
is naturally a barycentre and projection of the tetrahedron.

## 3. The parent as a weighted whole-state reading

For each route \(i\), let \(p_i\) be its occupancy, \(m_i\) its strength, and \(r_i=x_i y_i\) its output orientation.
Define

\[
\underbrace{M=\sum_i p_i m_i}_{\substack{\text{total participating magnitude}\\\text{TE-ARA-like envelope}}}
\]

and the strength-weighted point

\[
\underbrace{\bar v}_{\substack{\text{whole-state location}\\\text{parent reading}}}
=
\frac{1}{M}\sum_i p_i m_i
\underbrace{(x_i,y_i,x_i y_i)}_{\substack{\text{child route}\\\text{tetrahedron vertex}}}.
\]

Its third coordinate is

\[
\bar v_3=\frac{\sum_i p_i m_i r_i}{M}.
\]

Therefore the resolved parent output is exactly

\[
\underbrace{F}_{\substack{\text{resolved parent output}\\\text{observed identity}}}
=
\underbrace{Q}_{\substack{\text{participating activity}\\\text{coupling amount}}}
\underbrace{M}_{\substack{\text{total route strength}\\\text{identity envelope}}}
\underbrace{\bar v_3}_{\substack{\text{relation-axis projection}\\\text{phase balance}}}
=Q\sum_i p_i m_i r_i.
\]

Plainly: the parent is not obtained by throwing the children away. It is the weighted location of all four routes,
read along the interaction axis. Equal opposing contributions place it at the quiet centre; asymmetric strengths
move it toward the corresponding route.

## 4. Exact Information³ / Hadamard decomposition

Any four route strengths can be written uniquely as

\[
\underbrace{h_{xy}}_{\substack{\text{strength on route }(x,y)\\\text{local expression}}}
=
\underbrace{\mu}_{\substack{\text{common level}\\\text{shared envelope}}}
+
\underbrace{\alpha x}_{\substack{\text{first-axis asymmetry}\\\text{first ARA contribution}}}
+
\underbrace{\beta y}_{\substack{\text{second-axis asymmetry}\\\text{second ARA contribution}}}
+
\underbrace{\gamma xy}_{\substack{\text{joint interaction}\\\text{informative third}}}.
\]

The coefficients are

\[
\mu=\tfrac14(h_{++}+h_{+-}+h_{-+}+h_{--}),
\]

\[
\alpha=\tfrac14(h_{++}+h_{+-}-h_{-+}-h_{--}),
\]

\[
\beta=\tfrac14(h_{++}-h_{+-}+h_{-+}-h_{--}),
\]

\[
\underbrace{\gamma}_{\substack{\text{non-additive closure}\\\text{relation-specific strength}}}
=\tfrac14(h_{++}-h_{+-}-h_{-+}+h_{--}).
\]

This is the two-bit Walsh–Hadamard decomposition. It is exact for every four-number table.

Plainly: `μ` says how strong the whole local table is; `α` says how it leans on the first ARA; `β` says how it leans
on the second; and `γ` says whether knowing the two separately still misses something specific to their combination.
If `γ=0`, the two axes add independently. A nonzero `γ` is the clean mathematical version of the extra interaction
information Dylan was pointing to.

## 5. Where 3 → 6 → 9 is exact

If the first identity, second identity and their promoted relation are named \(A,B,C\), the possible directed
relations are

\[
AB,BA,AC,CA,BC,CB.
\]

The count is

\[
\underbrace{3(3-1)=6}_{\substack{\text{ordered pair relations}\\\text{direction retained}}}.
\]

Putting node states and directed relations in one matrix gives

\[
\underbrace{
\begin{pmatrix}
A & AB & AC\\
BA & B & BC\\
CA & CB & C
\end{pmatrix}}_{\substack{\text{three self-states + six directed relations}\\\text{nine-slot state/relation map}}}.
\]

Plainly: three identities provide three “what is it?” readings and six “how does it act toward the other?” readings.
That is exactly nine addressable slots. It does not mean the nine are statistically independent, and it does not by
itself prove ARA⁹ or fractal recursion. Recursion needs the additional ARA rule that a sufficiently closed relation
may be promoted to a new node and mapped again.

## 6. Frozen held-out plasma test

The protocol was written before fitting or scoring. The source was a different public simulator from MX7: the Warp
`example-2d` openPMD series. Fourteen early snapshots (`255–320`) fitted the models, six middle snapshots (`325–350`)
were quarantined, and ten later snapshots (`355–400`) formed the untouched test set. The test contained `97,510`
active vector cells.

For positive route magnitude, MX8 used a multiplicative height

\[
h_{xy}=\log(m_{xy}/\bar m)
\]

and compared

\[
h=\mu+\alpha x+\beta y
\]

against

\[
h=\mu+\alpha x+\beta y+\gamma xy.
\]

The held-out results were:

| Model | Relative L2 | Vector correlation | Median angle |
|---|---:|---:|---:|
| independent phase marginals | `0.123651` | `0.992359` | `0.00000085°` |
| joint sign only | `0.125689` | `0.992088` | `0.00000085°` |
| route-blind learned height | `0.139860` | `0.992088` | `0.021816°` |
| two separate axes | `0.131528` | `0.992175` | `0.019053°` |
| two axes + relation | `0.131518` | `0.992173` | `0.019065°` |
| exact conditioned identity | `0.0` | `1.0` | `0.0°` |

The relation term's relative-L2 change was only `+0.00736%` in the favourable direction, far below the frozen `5%`
gate. Its bootstrap interval crossed zero, and the two directional metrics were slightly worse. The simpler
independent-marginal baseline also beat all three learned height models.

Plainly: the extra interaction coordinate exists, but one average `γ` learned earlier did not tell us how strong that
interaction would be later. It added essentially no transferable predictive power in this form.

## 7. Why the transfer failed — exploratory diagnostic

After the frozen gate was scored, local `γ` values were inspected in cells containing all four routes. They were broad
and centred near zero. On the final test set:

- x: median approximately `0`, standard deviation `0.345`, positive fraction `0.490`;
- y: median `-0.00437`, standard deviation `0.279`, positive fraction `0.481`;
- z: median `0.000543`, standard deviation `0.324`, positive fraction `0.501`.

The development fits consequently produced very small global relation coefficients: x `-0.000400`, y `-0.004144`,
z `-0.005291`.

Plainly: strong positive and negative local interactions exist, but they mostly cancel when compressed to one global
number. This is compatible with ARA's insistence that the observer must declare location, scale and coupling context.
It is **not** evidence by itself that fractality causes the variation; ordinary plasma heterogeneity also predicts
context-dependent local interactions.

## 8. What this implies for ARA

### Confirmed mathematical scaffold

1. `two binary phase axes → four routes` is exact;
2. `two readings + their relation` is an exact parity closure;
3. the four lifted routes form a regular tetrahedron;
4. the relation coordinate is recoverable as the fourth Hadamard term after common, first-axis and second-axis terms;
5. `three identities → six directed relations → nine state/relation slots` is exact bookkeeping.

### Strengthened framework interpretation

Information³ can now be stated without invoking a literal Shannon cube:

> Two identities determine a relation; retaining the two identities and that relation closes the minimal joint state.

The tetrahedron also explains why flattening to positive/negative loses information. Positive collapses `AA` and `BB`
onto one relation sign; negative collapses `AB` and `BA`. These are opposite tetrahedron edges, not identical routes.

### Not confirmed

- a universal relation-strength coefficient;
- automatic square-pyramid apex geometry;
- physical independence of all nine matrix slots;
- recursive promotion at every scale;
- universal ARA fractality or replacement of Maxwell's equations.

### Best next mathematical/empirical move

Do not add more free route constants. Predict the **local** relation coefficient from predeclared parent geometry:
field gradients, local phase occupancy, positional moments and scale coordinates, with the final time block held out.
The discriminating question is no longer “does `xy` exist?”—that is algebraically settled. It is:

> Which independently measured local coordinates determine the sign and magnitude of `γ`, and does the same rule
> transfer across time, simulator and rung?

That is a much sharper aggregation-and-coupling problem for ARA.

## Reproduction packet

- `MX8_INFORMATION3_TETRAHEDRON_TRANSFER_PROTOCOL_v1_FROZEN.md`
- `mx8_information3_tetrahedron_transfer.py`
- `MX8_INFORMATION3_TETRAHEDRON_TRANSFER_RESULTS.json`
- `MX8_INFORMATION3_TETRAHEDRON_TRANSFER.png`
- `mx8_validate_outputs.py`
- `MX8_INFORMATION3_TETRAHEDRON_TRANSFER_VALIDATION.json`

All validation checks passed, including the tetrahedron Gram matrix, equal-edge calculation, parity closure,
Hadamard reconstruction, disjoint split, all 30 source hashes, saved metrics and deterministic bootstrap interval.
