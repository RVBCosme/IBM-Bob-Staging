# RATCHET — problem and solution

<!-- Numbers in <angle brackets> are filled from demo/README.md after Tasks 14 and 15. -->

**Problem.** AI coding agents made *writing* code nearly free, so the bottleneck moved to
*trusting* it. Agents are unreliable narrators: they report success they never verified, skip
tests and edit outside the agreed scope. The existing answers are prompts. A prompt *asks* the
agent to follow TDD; a confident model agrees and then doesn't. Nothing checks, so a human
re-reads everything anyway.

**Target user.** A team adopting AI agents that cannot merge agent output without
re-auditing it line by line. **Workflow improved:** requirements document to reviewed, tested,
merged code.

**What RATCHET is.** IBM Bob configuration files plus a small Python gate, in four layers:

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
personas) → *Memory* — opening each gate by hand with `python -m rx gate --to <phase>`. The gate
opens green only on a failing test, and review only when tests pass with `tests/` unchanged
since red.

**Why it is different.** IBM's own actor-critic tutorial proves the pattern; community
templates ship governed Bob modes. We made the pattern auditable: write scoping tied to SDLC
gates, a hook keyed on a phase file rather than the mode (so it survives a mode switch), and a
gap-checked HMAC ledger verified without an LLM. Each Karpathy guideline becomes a gate with a
receipt.

**What it is not.** Not a sandbox: a person with a shell can switch modes, edit inline or roll
files back. Bob's own rules refuse most out-of-phase requests before any tool call; the hook
catches what gets past them. Not tamper-proof: tamper-evident and gap-evident against everything
the agent can reach.

**Measured result.** One ticket (SHOP-412: promo codes, silent on a discount larger than the
subtotal); a hidden eight-test referee suite hashed before either run.

| Leg | Referee | Minutes | Bobcoins | Blocked calls |
|---|---|---|---|---|
| A — unguarded Bob, one prompt | <A>/8 | <min> | <coins> | n/a |
| A′ — A plus one repair prompt | <A′>/8 | <min> | <coins> | n/a |
| B — RATCHET | <B>/8 | <min> | <coins> | <N> |

<One sentence on what leg A shipped for the negative-total case.> "<N> blocked calls" is the one
number the ledger proves; everything else is n = 1 — an illustration, not a benchmark. Compare B with A′, not A. <If B did not win, say so here, and why.>
