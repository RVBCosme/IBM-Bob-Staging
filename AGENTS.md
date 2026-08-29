# RATCHET workspace

This repository is governed by RATCHET: five phase modes (ratchet-spec, ratchet-red, ratchet-green,
ratchet-review, ratchet-memory), a PreToolUse hook that blocks out-of-phase writes and all terminal
commands, and an HMAC-chained ledger in .ratchet/runs/. Humans open gates with `python -m rx gate`.

## Memory (a RATCHET convention, not a Bob feature)
- `memory/INDEX.md` is the index: one line per note, `- [Title](file.md) - one-line hook`.
- One note per fact, in `memory/<kebab-slug>.md`, with a `# Title` and the fact.
- Update same-topic notes in place. Delete status notes that are no longer true.
- The SessionStart hook prints INDEX.md into context; read a note fully before relying on it.

## Layout
- `src/` demo application - `tests/` its tests - `docs/specs/` spec and plan - `rx/` the RATCHET
  enforcement layer (never edit during a run) - `referee/` hidden acceptance tests (do not read).
