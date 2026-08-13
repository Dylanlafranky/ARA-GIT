# T372 — child-half handover with parent-asymmetry displacement

**Recorded:** 13 August 2026  
**Claim class:** strong ARA theory; not yet confirmed  
**Origin:** post-T371 interpretation, after the coarse T371 figure had exposed an apparent `(time, cumulative ARA) ~= (0.5, 0.5)` intersection

## Theory

For an ordered two-branch Di-ARA release, let `r_A(t)` and `r_B(t)` be the
instantaneous release flows of the two coupled branches.  Define the handover
time by

\[
r_A(t_H)=r_B(t_H).
\]

Let the cumulative parent release be normalized onto the ARA diameter:

\[
x(t)=2\frac{\int_0^t[r_A(u)+r_B(u)]\,du}
{\int_0^T[r_A(u)+r_B(u)]\,du}.
\]

The proposed pure child-scale landmark is

\[
\boxed{x(t_H)=0.5}.
\]

The physical version is deliberately weaker.  Unequal parent abundance,
cadence or branch shape may displace the observed handover:

\[
\boxed{x(t_H)=0.5+\Delta_H},
\]

where `Delta_H` is identity-specific and must be measured rather than supplied
after seeing the answer.  Reversing the declared branch orientation reverses
the sign convention.

In ARA language, `0.5` is therefore proposed as the pure child landmark, while
the observed offset records the asymmetry of the coupled parents at the chosen
measurement boundary.  This does **not** reinstate a universal Phi law.

## What would support it

1. A native-resolution reconstruction locates both the equality handover and
   its cumulative ARA coordinate without using coarse-bin centres as completed
   intervals.
2. The handover survives uncertainty, energy cuts and a source-model
   crosscheck.
3. Changing the declared parent balance moves the handover coordinate in a
   stable, oriented gradient rather than leaving it arbitrary.
4. A future independent physical dataset, frozen before inspection, predicts
   the direction and approximate size of `Delta_H` from parent asymmetry.

## What would not support it

- treating time in microseconds as though it were already an ARA coordinate;
- counting `x_A+x_B=2`, which is normalization bookkeeping;
- calling any value near `0.5` a child handover without independently defined
  branch equality;
- fitting an arbitrary correction after observing the target;
- recovering only the known decay chronology without predicting its handover
  location.

## Evidence boundary

T372 is an internal reconstruction and calibration on the already opened T371
COHERENT record.  It can correct the measurement, map the gradient and prepare
a frozen external prediction.  It cannot independently confirm the theory on
the same data that suggested it.

## T373 external-detector update

T373 attempted to transfer the frozen coordinate to the independent COHERENT
CENNS-10 liquid-argon release. The released argon signal model predicted
`x_H=0.565`; the event central estimate was `x_H=1.239`. Although the frozen
compatibility gate passed, Dylan's originator review identified that the test
had changed from solid CsI to liquid argon without first declaring a new ARA
identity/rung. The same-coordinate transfer interpretation is therefore
invalid. The stopped-pion/muon source relation and CEvNS interaction remain a
shared child lineage; the corrected comparison is nested child-to-liquid-parent.

A post-result likelihood-profile audit found that both the model prediction
and pure `x=0.5` remain compatible. Exact child-half is still unconfirmed and
not excluded. A new post-result lead interprets `1.239` against a
movement-heavy, one-further-rung candidate `1+0.5/2=1.25`; the difference is
`0.902%`. This is not confirmation and needs a fresh frozen same-identity test.
