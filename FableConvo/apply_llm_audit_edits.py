"""Apply AUDIT_LLM_FOLDER_2026-07-03 edits 1-4. Run from repo root: python3 apply_llm_audit_edits.py"""
import re, sys, os

edits = []
p = "LLM/LLM_PHI_FORCED_CLOCK_RESULT.md"
s = open(p).read()
old_title = "# LLM training is a FORCED CLOCK driven up toward the φ landmark — Pythia result (14 June 2026)"
new_title = ("# ⚠️ SUPERSEDED TITLE — curve-level findings stand; \"FORCED CLOCK\" verdict RETRACTED "
             "(see correction note + 00_LLM_THREAD_SUMMARY)\n"
             "## (original title: LLM training is a FORCED CLOCK driven up toward the φ landmark — Pythia result, 14 June 2026)")
s = s.replace(old_title, new_title)
old_verdict = "**Verdict: Dylan's mechanism prediction lands.**"
s = s.replace(old_verdict, "**Verdict (SUPERSEDED — see banner):** ~~Dylan's mechanism prediction lands.~~")
old_d4 = "**φ is the framework's measuring stick, not a hypothesis on trial here.**"
s = s.replace(old_d4, "**[AUDIT 3 Jul: sentence retracted — φ IS on trial; its trial is the duty table.]** ~~φ is the framework's measuring stick, not a hypothesis on trial here.~~")
edits.append((p, s))

p = "LLM/00_LLM_THREAD_SUMMARY.md"
s = open(p).read()
retrofit = """
> # ⚠️ BOUNDARY RETROFIT — 3 July 2026 (audit: AUDIT_LLM_FOLDER_2026-07-03.md)
> The 2-Jul pinned motion/slice boundary postdates this folder. Under it, ALL substrate ARA numbers
> here (~1.25 node/edge, 1.36–1.44 base wave) are rise/fall SHAPE measures = classifier positions —
> they CANNOT speak to φ either way. The thread's motion-measures (handover dominance) were
> artifact-contaminated and never cleanly re-run. **Therefore "φ does not cleanly appear" is
> UNADJUDICATED, not negative — the φ-jurisdiction measurement in LLM dynamics has never been made.**
> That measurement is T-LLM-2 (free vs forced decoding; dominance duty vs full crowded neighborhood;
> LOCK DETECTION per the L1 correction, never folded-angle-nearest).
> **Reclassification:** the telephone null is a FORCED task (templated copying) — its clock-or-snap
> result is the forced-column PREDICTION confirmed, not a "sixth clock lens." It joins the duty
> table's forced column (cf. the Josephson star).

"""
s = s.replace("# LLM thread — is training a φ-engine or a forced clock?",
              "# LLM thread — is training a φ-engine or a forced clock?", 1)
i = s.index("\n", s.index("# LLM thread"))
s = s[:i+1] + retrofit + s[i+1:]
edits.append((p, s))

for p, s in edits:
    open(p, "w").write(s)
    print("edited", p)
print("Verify: grep -n 'SUPERSEDED TITLE\\|BOUNDARY RETROFIT\\|sentence retracted' LLM/*.md")
