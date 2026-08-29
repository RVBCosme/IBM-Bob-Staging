# How IBM Bob was used

<!-- Observations marked <fill> are completed from leg B (plan Task 15) before submission. -->

Everything below is configuration committed in this repository, except two things a fresh clone
does not inherit: the four hook entries, which `python -m rx init` writes into the global
`%USERPROFILE%\.bob\settings\settings.json` (a copy is committed as `.bob/settings.example.json`),
and the UI-only state — workspace trust, granted on camera, and the auto-approve toggles for
Read / Skill / Subagent, pre-enabled and narrated. Build: Bob IDE 1.126.0+bob2.0.3 on
Windows 11. Every "observed" note cites `docs/specs/probe-findings.md` §7.1 or `bob_sessions/A/`.

## Custom modes — `.bob/custom_modes.yaml`

Five workspace modes, one per SDLC phase. No phase mode holds `execute`, `mode`, `subtask`, `mcp`
or `workflow` — IBM's rule is that an omitted group grants nothing.

| Mode | `groups` | `fileRegex` on `edit` |
|---|---|---|
| `ratchet-spec` (`1 - Ratchet Spec`) | `read`, `edit`, `skill`, `todo` | `^docs[\\/]specs[\\/].*\.md$` |
| `ratchet-red` (`2 - Ratchet Red`) | `read`, `edit`, `skill`, `todo` | `^tests[\\/].*` |
| `ratchet-green` (`3 - Ratchet Green`) | `read`, `edit`, `skill`, `todo` | `^src[\\/].*` |
| `ratchet-review` (`4 - Ratchet Review`) | `read`, `subagent`, `skill`, `todo` | — (no `edit`) |
| `ratchet-memory` (`5 - Ratchet Memory`) | `read`, `edit`, `skill`, `todo` | `^memory[\\/].*` |

Each mode's `customInstructions` opens with IBM's own Plan-mode pattern — *call `use_skill` with
`skill_name: "ratchet-<phase>"`* — followed by a short inline checklist as a backstop, because
`use_skill` is strong instruction, not enforcement. The regexes are double-quoted YAML strings
(`"^src[\\\\/].*"`); one invalid regex would unload all five modes silently, so Smoke 8 checks the
picker. Observed: Settings → Modes lists the five modes with scope Workspace (`smoke-8.png`).

`fileRegex` is enforced by Bob's edit-group validator before any hook runs (from the 2.0.3
bundle). We state it as bundle-derived: in Smoke 11a the `ratchet-green` mode declined an
out-of-phase write at the instruction layer, before any tool call, so the validator itself was
never observed and an in-mode out-of-phase write leaves no ledger record.

## Skills — `.bob/skills/<name>/SKILL.md`

Six workspace skills: `ratchet-spec`, `ratchet-red`, `ratchet-green`, `ratchet-review`,
`ratchet-memory`, `ratchet-ui-ux`. Each carries the phase workflow; `ratchet-spec` ships the full
Karpathy Guidelines as a sibling file (`karpathy.md`). Skills are loaded by name from the mode's
`customInstructions`; the call reaches the hook as `tool_name: "use_skill"`,
`tool_input: {"skill_name": …}` (Smoke 7). Observed: Settings → Skills lists all six with scope
"Workspace" (`smoke-7b.png`); typing `/ratchet` offers exactly six completions, one per skill and
no mode among them — Bob 2.0.3 generates no slash command from a mode (`smoke-8b.png`). In built-in
Agent mode Bob auto-loaded `ratchet-spec` after reading `.ratchet/state.json` (Smoke 12).

## Rules — `.bob/rules/` and per-mode rule folders

`00-karpathy.md` (four lines, injected into every conversation) and `01-ratchet.md` (the
protocol: only the human opens gates; never retry a refused or blocked call). Mode-specific
folders `.bob/rules-ratchet-red/` and `.bob/rules-ratchet-green/` add one rule each. `AGENTS.md`
is the workspace router. Observed: these layers make Bob refuse out-of-phase writes and terminal
commands *before any tool call* (Smokes 11a, 12); Bob also declined a trivial subagent spawn on its
own judgment (Smoke 9) — the honest consequence is that most refusals leave no ledger record.

## Personas — `.bob/agents/*.md`

`code-reviewer`, `security-auditor`, `test-analyst`. Each declares `groups: [read]` — the key the
2.0.3 persona parser actually reads — and keeps `tools: [read]` as the documented form. The
read-only claim is carried by the hook, not by the persona file: every tool call a subagent makes
passes through `PreToolUse` under the parent's `session_id` (Smokes 6b and 10).

## Subagents

`ratchet-review` holds the `subagent` group with
`allowedSubagents: [explore, code-reviewer, security-auditor, test-analyst]`; the allow-list filters
built-in presets and `.bob/agents/*` together, so the three personas must be named. Observed
(Smoke 9): a generic `Use the code-reviewer persona to list the files under src/` was declined
twice as too trivial; `Spawn the code-reviewer subagent to review src/cart.py against docs/specs/spec.md and
return its findings table` spawned **one** `code-reviewer` subagent (subagent row, 8 tools, 43 s;
`smoke-9.png`), after which Bob ran the security-auditor and test-analyst passes itself,
sequentially, and issued `VERDICT: REOPEN`. One spawned persona plus two sequential self-run
passes — we did not observe, and do not claim, a parallel fan-out. <fill: leg B review outcome.>

## Lifecycle hooks — global `%USERPROFILE%\.bob\settings\settings.json`

Written by `python -m rx init` (copy in `.bob/settings.example.json`); global so no mode change can
remove them. Hooks respect workspace trust.

| Event | Command | Role |
|---|---|---|
| `PreToolUse` | `.bob/hooks/gate.cmd` → `rx.gate` | exit 2 blocks the call: every terminal command in every phase, every write outside the phase directory, every write under `.ratchet/` or `.bob/`; writes a `deny` record |
| `PostToolUse` | `.bob/hooks/record.cmd` → `rx.record` | writes a `write` record for each allowed write |
| `Stop` | `.bob/hooks/record.cmd` | reconciles `git status --porcelain --untracked-files=all` against write records; flags unrecorded changes |
| `SessionStart` | `.bob/hooks/session.cmd` → `rx.session` | announces the run and phase; prints `memory/INDEX.md` |

The `PreToolUse` stdin payload measured on 2.0.3 is `{session_id, cwd, hook_event_name,
tool_name, tool_input, tool_use_id}`; `PostToolUse` adds `tool_response` (a string), and
`SessionStart` / `Stop` carry only the three common keys plus `source` / `last_assistant_message`
(the docs page shows different keys; the gate reads the measured ones and accepts the documented
ones as a fallback). There is no mode field, so the hook reads
`.ratchet/state.json`. Exit 2 has no effect on `PostToolUse` or `Stop` — those record, they cannot
block. Observed live: `RATCHET blocked execute_command on -: terminal commands are blocked in every
phase` on screen and as ledger record 16 (Smoke 12, `smoke-12-hook.png`); the earlier probe hooks
showed exit 2 blocking and exit 0 allowing (Smokes 3/4).

## Document understanding

The requirements ticket is a real DOCX, `demo/SHOP-412.docx`, `@`-mentioned by the human in the
spec mode (`Spec @/demo/SHOP-412.docx`); its SHA-256 is in the ledger's genesis line. XLSX was
avoided because context mentions do not support it. <fill: how Bob read the DOCX in leg B.>

## watsonx.ai

`tools/watsonx_summary.py` — *our script* calls watsonx.ai; Bob itself does not route to a model
of our choosing. Stdlib `urllib` only: IAM API-key exchange, then `POST
https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2024-03-14` with
`model_id: ibm/granite-4-h-small`, the run receipt (gates, blocked calls, write count, security
exit) as the user message, `max_completion_tokens: 300`. Credentials come from the environment
only. Observed: one HTTP 200 on 2026-08-30 (`demo/watsonx-verdict.png`); Granite answered in one
sentence. <fill: leg B verdict.>

## Evidence

`bob_sessions/A/` — task screenshots for Smokes 3/4, 7, 8, 9, 10/11, 12 (mode refusals, skill
refusals, the hook block); `demo/watsonx-verdict.png`; the committed ledgers under
`.ratchet/runs/`; `docs/specs/probe-findings.md` §7.1 for every result. <fill: leg B task list,
context-window and Bobcoin screenshots.>

## Wording we hold ourselves to

Never "physically impossible", "cannot widen", "tamper-proof", "append-only" (say
append-structured, gap-checked), "a subagent inherits the reviewer's read-only surface",
"deterministic three-reviewer fan-out", or any implication that the ledger blocks anything live.
