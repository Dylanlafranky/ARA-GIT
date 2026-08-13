# ARA paper Version 2 working package

This directory contains the current Version 2 manuscript, its April-to-current claim-migration audit, a reproducible PDF build, and rendered review outputs.

## Principal files

- `ARA_PAPER_V2_MANUSCRIPT.md` — canonical editable manuscript.
- `ARA_PAPER_V2_CLAIM_MIGRATION.md` — bridge from the April 2026 paper to the current framework and claim status.
- `build_paper_pdf.cjs` — local Markdown/KaTeX/Chromium renderer.
- `output/html/ARA_Geometric_Relational_Framework_V2_DRAFT.html` — browser-readable render.
- `output/pdf/ARA_Geometric_Relational_Framework_V2_DRAFT.pdf` — review PDF.

## Rebuilding

The renderer uses pinned local versions of KaTeX, Marked and Playwright. From `paper_v2/`, install the locked dependencies with `pnpm install`, then run `pnpm build`. The build uses an installed Microsoft Edge executable and does not fetch equation assets from a CDN.

Temporary page renders used for visual QA are written under `tmp/` and are intentionally excluded from version control.

## Current boundary

This is a complete working manuscript, not a publication-ready final. The remaining editorial rung is deliberate figure selection followed by external technical review. Crosswalks are labelled as crosswalks, empirical verdicts retain failures and partial results, and the universal generative fractal-sphere proposal remains a hypothesis rather than a demonstrated conclusion.
