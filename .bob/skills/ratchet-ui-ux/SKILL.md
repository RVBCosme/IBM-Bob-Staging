---
name: ratchet-ui-ux
description: UI/UX standards applied automatically during RATCHET spec phase when a change has a user-facing surface. Adapted from ui-ux-pro-max and frontend-design methodology.
---
# UI/UX section for the spec
Add a `## UI` section to docs/specs/spec.md covering, in this order:
1. Users and the one job each screen does.
2. States: empty, loading, error, success - each with the exact copy shown.
3. Accessibility: keyboard path, focus order, contrast >= 4.5:1, labels on every input.
4. Visual direction in one paragraph: typography pairing, palette (3 colours max), spacing scale. No generic "clean modern" defaults - choose and justify.
5. Each UI behaviour becomes a plan task with a testable assertion.
