---
name: ratchet-review
description: RATCHET phase 4. Read-only review of the change against the spec for correctness, simplicity, scope and security; emits VERDICT PASS or REOPEN. Use in ratchet-review mode.
---
# Review phase
You cannot edit or run anything. Review the diff of src/ and tests/ against docs/specs/spec.md.
1. Use the code-reviewer persona: correctness and simplicity findings.
2. Use the security-auditor persona: read .ratchet/runs/<run>/security.txt (bandit output) plus your own review of inputs and secrets.
3. Use the test-analyst persona: does each plan task have a test, does each spec bullet have an assertion?
4. Output one table: Severity | File | Finding | Spec bullet. Then `VERDICT: PASS` or `VERDICT: REOPEN` with the single most important reason.
5. Stop. Print: `Run: python -m rx gate --to memory` (PASS) or `--to red` (REOPEN: a bug is a missing test).
