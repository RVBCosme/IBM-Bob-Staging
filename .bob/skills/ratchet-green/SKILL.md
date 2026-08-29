---
name: ratchet-green
description: RATCHET phase 3. Makes the current failing test pass with the minimum change under src/. Use in ratchet-green mode.
---
# Green phase
Follow Simplicity First and Surgical Changes (karpathy.md in ../ratchet-spec).
1. Read the newest test under tests/ and the spec section it covers.
2. Make the smallest change under src/ that satisfies exactly that test. No extra parameters, no defensive code for cases the spec excludes.
3. If satisfying the test would contradict the spec, stop and say so - do not "fix" the test; you cannot.
4. Stop. Print: `Implemented T<n>. Run: python -m rx gate --to review` (or `--to red` if plan tasks remain).
