---
name: ratchet-spec
description: RATCHET phase 1. Turns a requirements document into docs/specs/spec.md and docs/specs/plan.md by surfacing assumptions and ambiguities first. Use in ratchet-spec mode.
---
# Spec phase
Follow karpathy.md in this folder (Think Before Coding).
1. Read the requirements document the human @-mentioned. Do not guess at anything it does not say.
2. Write a numbered list of assumptions and a numbered list of ambiguities. For each ambiguity, ask the human ONE question at a time and wait.
3. Write docs/specs/spec.md: Problem, Interface (exact function signatures), Behaviour (one bullet per rule, including every edge case you asked about), Out of scope.
4. Write docs/specs/plan.md: an ordered list of tasks, each small enough for one failing test. Format: `- [ ] T<n>: <behaviour> -> test: <what the test asserts>`.
5. If the work has a user-facing surface, the ratchet-ui-ux skill applies: add a UI section to spec.md.
6. Stop. Print: `Spec ready. Run: python -m rx gate --to red`
