# Repo cleanup plan — pre-Substack pass

**Date:** 5 Jul 2026 (Claude/Fable 5 for Dylan)
**Design constraint:** every phase is a self-contained ~30–45 min block,
independently committable, safe to stop after. Do them across days, not in one
burst. Phases 1–2 and 6 are the ones that matter; 3–5 are optional polish.

## Rule zero — what is NOT cleaned

- **No git history rewrite, ever.** No force-push, no `git lfs migrate` on
  existing history, no squash of old commits. The commit timestamps ARE the
  provenance record; rewriting history destroys the priority claim.
- **No deleting the mess that is history:** archive/numbered_tests (all 376),
  SUPERSEDED.md lineage, nulls, failed scripts, session notes. Signpost, never
  sanitize.
- **Decoy seal discipline:** nothing that unblinds the deck goes in any commit —
  no seal.txt, no scope notes naming which framework is real/fake, no chat
  references linking a framework name to "decoy". Check `git status` output
  against this before every commit in this plan.

## Phase 0 — safety (5 min)

```powershell
cd F:\SystemFormulaFolder\GIT\ARA-GIT
git checkout -b cleanup-2026-07
git status   # confirm what's untracked before touching anything
```

## Phase 1 — FableConvo intake (the uncommitted July work)

1. Delete junk (inspect zijWy4kv first — if it's a stray paste, delete):
```powershell
Remove-Item -Recurse FableConvo\__pycache__
Remove-Item FableConvo\ara_test_kit.zip     # the unzipped dir is the real copy
# inspect then: Remove-Item FableConvo\zijWy4kv
```
2. Create `.gitignore` at repo root:
```
__pycache__/
*.pyc
*.zip
Output for scripts/
```
3. Move FableConvo content to permanent homes (git mv preserves history):
   - `CANON_FOR_AI.md`, `README_FOR_AI.md`, `WHAT_IS_ARA_FOR_PEOPLE.md`,
     `PROVENANCE_LEDGER.md`, `TEST_PROTOCOL.md`, `THE_HANDOVER.md`,
     `CLEANUP_PLAN.md`, `REGISTRATION_UPDATE_CORE_KILL_2026-07-05.md` → repo root
   - `ARA_MAPPING_*.md` → `Mapping/`
   - `SESSION_*.md`, `THE_WALK_2026-07-02.html` → `journey/`
   - test scripts + outputs (`test5_*`, `test6*`, `digital_rig_L1*`,
     `golden_stars_*`, `numbers_as_waves_test.py`, `primes_zeta_verification.py`,
     figures) → `analysis/` (new subfolders: `analysis/separatrix/`, `analysis/primes/`)
   - `llm_*.py`, LLM audit docs, `LLM_WORK_SAFEGUARDS.md` → `LLM/`
   - `ara_test_kit/` → repo root or `TheFormula/` (it's the runnable kit)
   - `decoy_experiment/` → commit ONLY per DECOY_RUNBOOK rules (hash + blinded
     frameworks; walks/scores when locked). If unsure, hold the whole folder back.
   - `zeros1.txt` (1.8MB) → `analysis/primes/data/` (acceptable size) or release asset
   - `MASTER_PREDICTION_LEDGER.md` in FableConvo is a COPY — diff against root
     version, merge newer content, keep one.
4. Merge the F1 registration (after sign-off) into MASTER_PREDICTION_LEDGER.md
   Part D per REGISTRATION_UPDATE_CORE_KILL_2026-07-05.md instructions.
5. Commit: `git commit -m "Merge 2-5 Jul session work: provenance ledger, anti-drift rule, F1 restatement"`

## Phase 2 — root declutter (the entry path)

Keep at root (the entry set, ~12 files):
README.md, README_FOR_AI.md, INDEX.md, GLOSSARY.md, CLAIMS_STATUS.md,
SUPERSEDED.md, MASTER_PREDICTION_LEDGER.md, WHAT_IS_ARA_FOR_PEOPLE.md,
CANON_FOR_AI.md, PROVENANCE_LEDGER.md, THE_FRAMEWORK_FORMULATION.md,
REPRODUCIBILITY.md, LICENSE, CITATION.cff

Move everything else at root:
- `*_RESULT.md`, `*_RESULTS.md` result write-ups → `results/`
- theory/application docs (ARA_Fusion_Theory, ARA_Battery_Theory,
  FRACTAL_UNIVERSE_THEORY, ARA_SCALE, ARA_ROSETTA_STONE, etc.) → `theory/`
- how-tos (HOW_TO_map_a_system, MAPPING_TO_THE_FRAMEWORK, ARA_decomposition_rules)
  → `methods/`
- `META_ARA_DARK_SECTOR.pdf` → `theory/`

Then: update INDEX.md paths (ask an AI to regenerate the file map — that's what
librarians are for), spot-check 10 links. Commit.

## Phase 3 (optional) — big data files

Do NOT lfs-migrate history (rule zero). Lowest-energy acceptable option: leave
them; 250MB clones are tolerable. Better option when energy allows: move the
>3MB data dumps (the .js/.json/.npz in TheFormula/, LLM/, analysis/pendulum_viz)
to a GitHub Release asset ("data-2026-07"), replace each with a small
DATA_MOVED.md pointing at the release. Track NEW large files with LFS going
forward only.

## Phase 4 (optional) — archive dedupe

`archive/old_git_mirror/` mostly duplicates `archive/early_papers/` but holds
unique dirs (Peer-Review, computations, an older Supporting). Move the unique
dirs up to `archive/`, verify with `diff -rq`, then delete the mirror. Add one
line to archive/README.md recording what was merged and when.

## Phase 5 — public-facing essentials

1. **LICENSE:** recommend MIT for code + CC BY 4.0 for text/docs (state the
   split in the LICENSE file). Without this, nobody can legally build on or
   even quote the work at length.
2. **CITATION.cff** so GitHub renders a "cite this" box.
3. **Zenodo snapshot:** link the repo to Zenodo, cut a v1.0 release → permanent
   DOI, timestamped, independent of GitHub and of you. One-time, ~20 min,
   highest preservation value per unit energy in this whole plan.
4. **README.md top section for humans:** first screen = what ARA is (3
   sentences), the tier system, the credential paragraph (misses kept, nulls
   published, 41% blind rate stated plainly), then the AI entry path link.
5. **FRACTAL_UNIVERSE_THEORY.md:** add supersession pointers at Section 1
   Claims 2 (φ-attractor framing) per the F1 registration note.

## Phase 6 — verify and publish

```powershell
git checkout main; git merge cleanup-2026-07; git push
# then fresh-clone into a temp dir and check: README renders, INDEX links work,
# no seal material present, repo size acceptable
```
Then, and only then, first Substack post.
