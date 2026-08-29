---
name: ratchet-red
description: RATCHET phase 2. Writes exactly one failing test for the next unchecked task in docs/specs/plan.md. Use in ratchet-red mode.
---
# Red phase
1. Open docs/specs/plan.md; pick the first unchecked task.
2. Write one test under tests/ that imports the symbol the spec names and asserts the promised behaviour. Do not create the symbol. Do not stub.
3. You cannot edit plan.md in this phase. Put `T<n>` in the test's docstring; the human ticks the task at the gate.
4. Stop. Print: `Failing test written for T<n>. Run: python -m rx gate --to green`
