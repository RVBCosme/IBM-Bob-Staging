---
name: ratchet-memory
description: RATCHET phase 5. Records what the next session must know under memory/, one file per fact, index in memory/INDEX.md. Use in ratchet-memory mode.
---
# Memory phase
1. Read memory/INDEX.md (it was injected at session start) and the run's docs/specs/.
2. For each durable fact from this run (a decision, a constraint, a gotcha): update the existing same-topic note in place, or create `memory/<kebab-slug>.md` with a `# Title` line and the fact.
3. Delete any status note that is no longer true.
4. Rewrite memory/INDEX.md: one line per note, `- [Title](file.md) - hook`.
5. Stop. Print: `Memory updated. Run: python -m rx gate --to done`
