# Local Cowork session transcripts — ARA framework work

These are the raw `.jsonl` files written by Cowork to the local agent-mode-sessions
folder, copied verbatim here so the cataloging chat has full access. A readable
`.md` companion is generated next to each main session (tool calls compressed).

## Chronological session chain

The ARA-framework consolidation arc spans several Cowork sessions on this folder
(separate from the older `session_20260423_*` and `session_20260509_raw.jsonl`
files in the parent transcripts/ folder, which are different snapshots).

| date span | file | size | summary |
|---|---|---|---|
| 2026-04-28 → 04-30 | session_20260428_catchup_0f8595bd | 7.5 MB | Initial catch-up session ("Can you please catch up on the project…") |
| 2026-04-30 | session_20260430a_short_51119eea | 3.0 MB | Short follow-up ("Number 3 please. Visually helps massively.") |
| 2026-04-30 → 05-02 | session_20260430-0502_main_8cf263f3 | 10.0 MB | Continuation of the visual-aid thread; long arc |
| 2026-05-02 → 05-09 | session_20260502-0509_main_88903ff3 | 15.4 MB | **Main consolidation arc** — canonical predictor, 3/4 ceiling test, multi-mammal vertical-ARA, quantum-entanglement framing, geometric inventory, INDEX.md, GitHub staging |
| 2026-05-02 (forks) | session_20260502_fork_*.jsonl (×6) | 4.8 MB each | Six forked branches that all start with "Yes, lets test your recommendation." — same starting state, slight content divergence; cataloging chat can dedupe |

## Subagent transcripts

`subagents/` contains transcripts of any spawned subagents (e.g.
`agent-ae9b83c775514a82e.jsonl` from session 88903ff3).

## Raw vs readable

For each main session there is both:
- `<name>.jsonl` — original Cowork transcript, full tool inputs/outputs
- `<name>_readable.md` — markdown render with tool calls/results compressed for browsing

The forked May 2 files only have `.jsonl` (cataloging chat can pick which to
render if it wants).

## Notes for the cataloging chat

- Memory files in `spaces/.../memory/MEMORY.md` are the durable distillation; these
  transcripts are the raw record of how the framework was developed.
- The `originSessionId` field in some memory files maps to the UUIDs above.
- `MASTER_PREDICTION_LEDGER.md` records confirmed/provisional empirical claims;
  cross-reference against transcript dates to build the timeline.
