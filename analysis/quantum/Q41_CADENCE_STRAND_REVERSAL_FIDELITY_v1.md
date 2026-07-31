# Q41 ARA fidelity packet — cadence-defined strand reversal

Date: 2026-07-27 (Australia/Brisbane)

Status: pre-target frozen design

## ARA statement being tested

Q40C recovered two visibly different closure cadences from the same ARA
relation plane:

- a one-turn family whose visible orbit closes after about 15 samples; and
- a two-turn family whose apparent turn is about 7.5 samples but whose
  coordinate returns only after 15 samples.

In ARA language, the second family contains two interleaved strands. A
completed seam changes which strand is locally visible. Q40 then showed that
most of its missed relation reversals were not spread uniformly: 543 of 646
false negatives occurred in the Ba target quadrant, and 576 of 646 occurred
inside the two-turn family.

Q41 therefore tests this fixed translation:

> Preserve the original visible reversal flag. In addition, reverse the local
> relation when the visible closure path belongs to the recovered two-turn
> family and the next quadrant is Ba.

This is not a new fitted classifier. The only added inputs are the Q40C cadence
windows and the already named Ba quadrant.

## ARA objects and established quantities

| ARA reading | Calculation used in this test |
|---|---|
| Parent closure cut | \(u(t)\), the development-normalised closure magnitude |
| Parent movement cut | \(v(t)=\Delta u(t)\) |
| Complete visible path | \((u(t),v(t),t)\) |
| One-turn family | fitted angular period 14.8–15.2 samples and lag-15 coordinate correlation at least 0.95 |
| Two-turn family | fitted angular period 7.35–7.65 samples and lag-15 coordinate correlation at least 0.95 |
| Four ARA quadrants | signs of \(u\) and \(v\), ordered by the development-derived rotation direction |
| Visible relation | \(D=C_1-C_2\) |
| Forward continuation | \(C_3+D\) |
| Relation reversal | \(C_3-D\) |
| Ba strand | quadrant label 1 under the frozen Q40 coordinate convention |

Here \(C_1,C_2,C_3,C_4\) are successive connected-correlation identities in one
complete four-quadrant cycle. Q41 predicts \(C_4\) using only \(C_1,C_2,C_3\),
the visible closure path and development-derived normalisation.

## Exact Q41 operator

\[
D=C_1-C_2,
\qquad
F=C_3+D.
\]

The original Q40 visible flag is

\[
g_{\rm vis}
=
\mathbf 1\!\left[
\cos(F,C_3)<0
\right].
\]

The cadence-defined strand flag is

\[
g_{\rm strand}
=
\mathbf 1\!\left[
7.35\leq T_{\rm orbit}\leq7.65
\;\land\;
r_{15}\geq0.95
\;\land\;
q_4=\mathrm{Ba}
\right].
\]

The frozen Q41 flag and prediction are

\[
g_{41}=g_{\rm vis}\lor g_{\rm strand},
\]

\[
\widehat C_4^{(41)}
=
\begin{cases}
C_3-D,&g_{41}=1,\\
C_3+D,&g_{41}=0.
\end{cases}
\]

The closure path may be observed across the evaluation interval. The connected
matrix \(C_4\), its sign relative to \(F\), and all Q41 scores remain hidden
until the prediction file is written and hashed.

## What is inherited and what is new

Inherited:

- the ARA diameter and movement cuts;
- the four-quadrant cycle;
- \(D=C_1-C_2\);
- the Q40 visible flag;
- the Q40C 7.5/15 cadence windows; and
- Ba as the lower-left quadrant in the fixed chart.

New empirical claim:

- the cadence-defined two-turn Ba strand transfers to a different compatible
  archive and improves prediction of the hidden connected identity.

## Failure conditions

The proposed extension is not supported if any of the following occurs on the
untouched archive:

1. the two-turn Ba rule does not improve seed-balanced scaled error over Q40;
2. it improves recall only by creating enough false reversals to worsen the
   primary reconstruction error;
3. its apparent benefit disappears under seed-cluster bootstrap uncertainty;
4. the compatible archive does not contain enough eligible two-turn Ba cycles
   for the predeclared minimum of 100 cycles; or
5. implementation validation cannot reproduce the stored predictions and
   scores.

## Interpretation boundary

Passing Q41 would show that an ARA-derived cadence/strand distinction carries
prospective information about a hidden matrix orientation in another archive.
It would not prove that the simulator contains literal physical helices, that
all quantum dynamics obey this operator, or that ARA replaces quantum theory.

