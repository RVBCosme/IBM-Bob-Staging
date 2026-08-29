# A/B protocol — SHOP-412

Same repo commit (`ab-start`), same requirements document, same machine, same model.
Referee suite `referee/test_promo_acceptance.py` was authored before any run; its SHA-256 is in
`referee/SHA256.txt`. Bob's file tools cannot see it in either run (`.bobignore`); leg A also holds a
terminal, so its transcript is checked for any `referee` access.

| Leg | What ran | Referee | Minutes | Bobcoins | Files touched | Blocked calls |
|-----|----------|---------|---------|----------|---------------|---------------|
| A   | Default Agent mode, one prompt (gate off — `state.json` renamed, hooks exit 0; rules, skills and router removed) | /8 | | | | n/a |
| A'  | A + one repair prompt with the referee failure pasted in | /8 | | | | n/a |
| B   | RATCHET gates | /8 | | | | |

Fill with real numbers only. If B does not win, say so and say why.
The one number the ledger proves deterministically is "Blocked calls" for leg B.
Leg B's blocked calls come from the built-in Agent mode (the authorised-smoke `pytest` prompt, Smoke 12): in the phase
modes Bob refuses out-of-scope writes at the rules/skill layer before any tool call (Smoke 11a, 2026-08-30), and the
bundle's `fileRegex` (never reached in that smoke) would be enforced by Bob before the hook, so either way there is no record.
Everything else: n=1, single seed, nondeterministic model - an illustration, not a benchmark.
