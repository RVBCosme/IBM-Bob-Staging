# RATCHET — problem and solution

**Problem.** AI coding agents made *writing* code nearly free, so the bottleneck moved to
*trusting* it. Agents report success they never verified, skip tests and edit outside the agreed scope. The existing answers are prompts. A prompt *asks* the
agent to follow TDD; a confident model agrees and then doesn't. Nothing checks, so a human
re-reads everything.

**Target user.** A team adopting AI agents that cannot merge agent output without
re-auditing it. **Workflow improved:** requirements document to reviewed, tested,
merged code.

**What RATCHET is.** IBM Bob configuration plus a small Python gate, in four layers:

1. **Withhold** — each SDLC phase runs in a custom mode granted only the tool groups it needs;
   no phase mode holds `execute`, `mode` or `subtask`.
2. **Declare** — each editing mode's `fileRegex` names the one directory it may edit.
3. **Block** — a `PreToolUse` hook in global settings (no mode change can remove it) exits 2 on
   every write outside the phase written on disk and on every terminal command.
4. **Audit** — hooks and the human-run gate script, never the model, record every transition,
   write and blocked call into an HMAC-chained, sequence-numbered ledger that a non-LLM script
   verifies and reconciles against git.

**How a developer uses it.** `python -m rx init --doc <requirements.docx>` starts a run. The
developer walks five modes from Bob's mode picker — *Spec* → *Red* (one failing test the mode
cannot run) → *Green* (minimum change under `src/`; cannot touch the test) → *Review* (read-only
personas) → *Memory* — opening each gate with `python -m rx gate --to <phase>`. The gate
opens green only on a failing test, and review only when tests pass with `tests/` unchanged
since red.

**Why it is different.** IBM's actor-critic tutorial and community templates ship governed
modes; we made the pattern auditable: write scoping tied to SDLC
gates, a hook keyed on a phase file rather than the mode (so it survives a mode switch), and a
gap-checked HMAC ledger verified without an LLM. Each Karpathy guideline becomes a gate with a
receipt.

**What it is not.** Not a sandbox: a person with a shell can switch modes, edit inline or roll
files back. Bob's own rules refuse most out-of-phase requests before any tool call; the hook
catches what gets past them. Not tamper-proof: tamper-evident and gap-evident against everything
the agent can reach.

**Measured result.** One ticket (SHOP-412: promo codes, silent on a discount larger than the
subtotal); a hidden eight-test referee suite hashed before either run.

| Leg | Referee | Minutes | Task pill | Blocked calls |
|---|---|---|---|---|
| A — unguarded Bob, one prompt | 7/8, then 8/8 self-patched (tainted) | ≈3 | 0.218 | n/a |
| A′ — A plus one repair prompt | 8/8 (tainted) | ~0 | 0.089 | n/a |
| B — RATCHET | 8/8 | 32 | 2.41 (15 tasks) | 1 |

Leg A shipped −5.00, then ran the whole test tree — hidden referee included — and patched itself:
tainted. B earned 8/8 through four red→green gates, two review verdicts (one REOPEN actioned, one
time-boxed) and no terminal. "1 blocked call" is the number the ledger proves; the rest is n = 1 — an
illustration, not a benchmark.
