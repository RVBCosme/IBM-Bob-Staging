# A/B protocol — SHOP-412

Same repo commit (`ab-start`), same requirements document, same machine, same model.
Referee suite `referee/test_promo_acceptance.py` was authored before any run; its SHA-256 is in
`referee/SHA256.txt`. Bob's file tools cannot see it in either run (`.bobignore`); leg A also holds a
terminal, so its transcript is checked for any `referee` access.

| Leg | What ran | Referee | Minutes | Bobcoins | Files touched | Blocked calls |
|-----|----------|---------|---------|----------|---------------|---------------|
| A   | Default Agent mode, one prompt (gate off — `state.json` renamed, hooks exit 0; rules, skills and router removed) | 8/8 — **tainted** (see below) | not timed (≈3; screenshots 12:50–12:53 SGT) | 0.218 (task pill) | 1 (`src/promo.py`: written, then patched by Bob) | n/a |
| A'  | A + one repair prompt with the referee failure pasted in — **no repair was needed**, A already passed; the prompt went in with the referee screenshot instead. Bob read it, ran `pytest referee -q` itself, changed nothing | 8/8 (tainted, same reason) | ~0 | 0.089 (task pill) | 0 | n/a |
| B   | RATCHET gates | /8 | | | | |

Fill with real numbers only. If B does not win, say so and say why.

**Leg A, observed 2026-08-30 ~12:50 SGT (`demo/stills/leg-a-transcript.png`).** Bob's first write of
`src/promo.py` returned −5.00 for a $5 cart with `TENOFF` — its own words: *"apply_promos(5.0, ["TENOFF"])
should return 0.0, not -5.0"*. It found that out by running `python -m pytest --tb=short -q` over the whole
tree: 38 tests, i.e. the 30 `rx_tests` plus the 8 hidden referee tests. `.bobignore` hides `referee/` from
Bob's file tools, not from a terminal. Bob then patched the last line to `return round(max(total, 0.0), 2)`
and reported "All 38 tests pass". So A's 8/8 is tainted: the referee was the answer key. Bob did not ask the
ticket's open question (never below zero?) — it read the answer instead. A′ touched the referee a second time
(Bob ran `python -m pytest referee -q` on its own). The untainted observation from leg A is the first write:
the negative total the ticket dodged. Stills: `leg-a-transcript.png` (the −5.0 line), `leg-a-promo.png`
(the patched total line), `leg-a-referee.png` (8 passed), `leg-a-aprime-transcript.png`. In leg B no phase can
run a terminal (the hook blocks `execute_command` in every phase), so this path does not exist there; the
referee is run by the human, after the run.

The one number the ledger proves deterministically is "Blocked calls" for leg B.
Leg B's blocked calls come from the built-in Agent mode (the authorised-smoke `pytest` prompt, Smoke 12): in the phase
modes Bob refuses out-of-scope writes at the rules/skill layer before any tool call (Smoke 11a, 2026-08-30), and the
bundle's `fileRegex` (never reached in that smoke) would be enforced by Bob before the hook, so either way there is no record.
Everything else: n=1, single seed, nondeterministic model - an illustration, not a benchmark.
