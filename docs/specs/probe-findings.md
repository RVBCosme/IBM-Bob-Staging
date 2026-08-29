# Hook probe findings (Task 1 / smoke tests 1–6)

**Date:** 2026-08-29 · **Bob IDE build:** `1.126.0+bob2.0.3` (commit `00eba1eb`, 2026-08-10) — ≥ 2.0.2, hooks exist
**Evidence:** `probe.log` (session `448e42284ee101f74667a92307dfa1be`, 9 lines, one Agent-mode task), Bob's own task DB
(`~/.bob/db/bob.db`), and Bob's hook runner in
`…\Programs\IBM Bob\resources\app\extensions\bob-code\dist\extension.js` (function `runHooks`).
IBM's Lifecycle hooks page documents `event`/`tool`/`input`/`output`; the 2.0.3 bundle sends
`hook_event_name`/`tool_name`/`tool_input`/`tool_response` — the bundle is the spec.

## 0. Verdict

| Smoke | Result | Basis |
|---|---|---|
| 1 trust | **GREEN** | Hooks fired → workspace was trusted |
| 2 do hooks fire? | **GREEN** | All five events logged in one task: `SessionStart`, `UserPromptSubmit`, 3× `PreToolUse`, 3× `PostToolUse`, `Stop` |
| 3 exit 2 blocks | **GREEN (source) / pending (live)** | `runHooks`: `exitCode === 2` on `PreToolUse` → `{blocked:true}` → tool call cancelled. `probe2.cmd` measured exit 2 through `cmd /c`. Not yet exercised inside Bob — see §7 |
| 4 exit 0 allows | **GREEN** | The whole probe session ran with exit-0 hooks on every event; all three tools executed |
| 5 failure mode | **GREEN — fails OPEN** | Missing script → 1, uncaught exception → 1, missing interpreter → 3, timeout → `null`; every one is ignored by Bob (§4, §5) |
| 6 tool vocabulary | **GREEN** | §2. Subagent tool is `spawn_subagent` (advertised; not yet observed through a hook — §7) |

**One blocking finding (§6): the payload keys are `hook_event_name` / `tool_name` / `tool_input`, not
`event` / `tool` / `input`. As committed, `rx/gate.py` denies every tool call as "malformed payload" and
`rx/record.py` records nothing. Fix before Task 7.**

## 1. Payload schema — exact keys per event

Bob builds each payload in code and writes `JSON.stringify(payload)` to the hook's stdin (no BOM; `utf-8-sig`
decoding is harmless). Common keys on every event: `session_id`, `cwd`, `hook_event_name`.

| Event | Extra keys | Notes |
|---|---|---|
| `SessionStart` | `source` | `"startup"` when the task has no messages yet, `"resume"` otherwise. Fires once per root task |
| `UserPromptSubmit` | `prompt` | The raw user message. **Blockable** (exit 2 → "Prompt blocked by hook") |
| `PreToolUse` | `tool_name`, `tool_input`, `tool_use_id` | `tool_input` is the tool's argument object verbatim. **Blockable** |
| `PostToolUse` | `tool_name`, `tool_input`, `tool_response`, `tool_use_id` | `tool_response` is a **string**. Fires only when the tool did **not** error (`isError` tools skip PostToolUse) |
| `Stop` | `last_assistant_message` | String or `null`. Fires once per turn end |

There is **no `mode`, no `transcript_path`, no `matcher`, no `permission` field** — the spec's §4.3 assumption that
the hook must read `.ratchet/state.json` for the phase is confirmed.

`session_id` = Bob's root task id (same value as `bob.db.tasks.id`). `cwd` = the workspace folder as Bob opened
it: **`c:\ratchet` — lowercase drive letter, backslash**. The hook process is spawned with that `cwd`, so
`Path.cwd()` in the hook is the workspace root.

Observed `PreToolUse` line, verbatim:

```json
{"session_id":"448e42284ee101f74667a92307dfa1be","cwd":"c:\\ratchet","hook_event_name":"PreToolUse",
 "tool_name":"write_file","tool_input":{"path":"scratch/hello.txt","content":"hi","line_count":1},
 "tool_use_id":"tooluse_nlNOJmVQ2Jawzsukwvfk56"}
```

## 2. Tool vocabulary

### 2.1 Observed through the hook (`probe.log`)

| `tool_name` | `tool_input` keys | Bob permission class |
|---|---|---|
| `write_file` | `path`, `content`, `line_count` | `edit` |
| `apply_diff` | `path`, `diff` (SEARCH/REPLACE block with `:start_line:`) | `edit` |
| `execute_command` | `command` | `execute` |

### 2.2 Advertised to the model in the same session (`availableTools`, 23 names, from `bob.db`)

Matches IBM's tools reference (bob.ibm.com/docs/ide/core-concepts/tools) exactly.

| Class for `rx/policy.py` | Tools |
|---|---|
| **`WRITE_TOOLS`** (gate by path) | `write_file`, `apply_diff`, `insert_content`, `search_and_replace` |
| **`EXEC_TOOLS`** (always deny) | `execute_command` |
| **Subagent / task spawners** (decide in Task 8 / smoke 10) | `spawn_subagent`, `start_subtask`, `start_workflow` |
| Read / navigate (always allow) | `read_file`, `list_files`, `glob`, `grep`, `GetSymbolsOverview`, `FindSymbol`, `FindReferencingSymbols`, `read_xlsx`, `search_bob_docs` |
| Control / UI (always allow) | `use_skill`, `switch_mode`, `update_todo_list`, `ask_followup_question`, `create_chart`, `create_html_artifact` |

`insert_content` and `search_and_replace` were not exercised; by IBM's reference they take a file path and are
expected to use `path` like the two observed write tools. Confirm with the prompt in §7 before relying on it.
MCP tools (none configured here) arrive under their MCP names — anything not in `WRITE_TOOLS`/`EXEC_TOOLS` is
allowed by the block-list design, so an MCP filesystem tool would be an audit hole; keep `taskAllowedMcpTools`
empty for the demo.

### 2.3 Pinned values for `rx/policy.py`

```python
WRITE_TOOLS = {"write_file", "apply_diff", "insert_content", "search_and_replace"}   # names confirmed
EXEC_TOOLS  = {"execute_command"}                                                   # confirmed
PATH_KEYS   = ("path",)                                                             # confirmed for write_file, apply_diff
```

The values already in `rx/policy.py` are correct. **The keys read in `rx/gate.py` and `rx/record.py` are not** (§6).

## 3. Path shape

- Key: **`tool_input.path`**.
- **Workspace-relative**, exactly as the model wrote it: `scratch/hello.txt`.
- Separator: **forward slash** in both observed writes. Bob does not normalise, so a model could emit `scratch\hello.txt`
  or an absolute path; `rel_to()` in `gate.py` already handles all three (`as_posix()`, `resolve().relative_to(root)`).
- Case: `cwd` arrives as `c:\ratchet`. `Path.resolve()` returns the on-disk case (`C:\ratchet`) and
  `PureWindowsPath.relative_to` compares case-insensitively, so absolute paths inside the workspace still resolve.

## 4. Exit-code contract (from `runHooks` in `extension.js`, bob2.0.3)

Bob runs the `command` string with Node `child_process.exec` — i.e. **`cmd.exe /d /s /c "<command>"`** — with
`cwd = workspace`, `windowsHide`, `maxBuffer` 1 MiB, and `timeout = (settings.timeout ?? 10) s`. It writes the
JSON payload to stdin and waits for exit.

| Hook exit | `PreToolUse` / `UserPromptSubmit` | `SessionStart` / `PostToolUse` / `Stop` |
|---|---|---|
| `0` | allowed; trimmed stdout becomes `additionalContext` (SessionStart / UserPromptSubmit inject it into the model's context) | same |
| `2` | **BLOCKED.** Reason shown to the model = `stderr.trim() \|\| stdout.trim() \|\| "<event> blocked by hook"`. PreToolUse → tool call cancelled with that note; UserPromptSubmit → `UserPromptHookError "Prompt blocked by hook"` | logged "hooks cannot block", **ignored** |
| any other (`1`, `3`, …) | logged "hook exited with code N", **ignored → fails open** | ignored |
| `null` (spawn failure, **timeout**, killed) | logged "hook failed", **ignored → fails open** | ignored |

Consequences already reflected in the design: `gate.py` must exit 2 on *every* internal failure (it does); the
deny reason goes to **stderr** (it does); anything that makes the interpreter itself fail (bad path, import error,
timeout > 5 s) silently disables the gate.

Multiple hooks on one event run **sequentially**; the first block wins. Matcher: omitted or `"*"` matches all;
otherwise a JS `RegExp` tested against `tool_name` (or `source` for SessionStart). The matcher-less config is correct.

Hooks are read from `~/.bob/settings/settings.json` (global) and workspace `.bob/settings.json`; the probe used
global only, as the spec requires. Changelog 2.0.2: hooks respect workspace trust.

## 5. Smoke 5 — failure characterisation (measured 2026-08-29 through `cmd /c` with a stdin pipe)

| Case | Exit | Bob's reaction (§4) |
|---|---|---|
| `probe.cmd` (exit-0 wrapper) | `0` | allow |
| `probe2.cmd` (exit-2 wrapper) | `2` | **block** |
| `C:\ratchet\.bob\hooks\nope.cmd` (missing script, space-free path) | `1` — `'…nope.cmd' is not recognized as an internal or external command` | **ignored → fail open** |
| `raise RuntimeError` as line 1 of `probe.py` | `1` — traceback on stderr | **ignored → fail open** |
| wrapper pointing at a non-existent `python.exe` | `3` — `The system cannot find the path specified` | **ignored → fail open** |
| hook slower than `timeout` | `null` (process killed) | **ignored → fail open** |

Same conclusion the plan predicted: **a missing or crashing gate fails open.** The pre-take checklist (Task 7
Step 2) must assert `gate.cmd` exists and the deny canary returns 2 before every recording.

## 6. BLOCKING: `rx/gate.py` and `rx/record.py` read the wrong keys

Both modules (and the plan text they were pasted from) read `payload["tool"]`, `payload["input"]`,
`payload["event"]`. Bob sends `tool_name`, `tool_input`, `hook_event_name`. Run against the real captured
payloads on 2026-08-29 (temp workspace, `state.json` phase `green`):

| Input piped to hook | Expected | Actual |
|---|---|---|
| real `PreToolUse` `write_file scratch/hello.txt` → `rx.gate` | deny "outside green scope" | **deny "malformed payload"** (`tool=None`) — exit 2 |
| same payload re-keyed to `tool`/`input` → `rx.gate` | deny "outside green scope" | deny "outside green scope" ✓ |
| real `PreToolUse` `execute_command` → `rx.gate` | deny "terminal commands are blocked" | deny "malformed payload" |
| real `PostToolUse` `write_file` → `rx.record` | ledger `write` row | **no row written** (silent) |
| real `Stop` → `rx.record` | ledger `stop` row | **no row written** (silent) |

Net effect if installed as-is: the gate blocks **every** tool call including reads (Bob unusable), and the
ledger never records a write or a stop — the opposite of the block-list design. `rx.session` is unaffected
(reads no payload keys).

**What to change (Task 4 pin):**

1. `rx/gate.py::decide` — `payload.get("tool_name")`, `payload.get("tool_input")`; the deny record and the stderr
   message use `tool_name`.
2. `rx/record.py::main` — `p.get("hook_event_name")`, `p.get("tool_name")`, `p.get("tool_input")`.
3. `rx_tests/test_gate.py`, `test_gate_stdin.py`, `test_record.py` — fixtures to the real shape; add one test that
   feeds the verbatim line 3 of `probe.log` to `rx.gate` with phase `green` and expects "outside green scope".
4. `demo/canary/deny.json`, `allow.json` —
   `{"session_id":"canary","cwd":"c:\\ratchet","hook_event_name":"PreToolUse","tool_name":"write_file","tool_input":{"path":"src/x.py","content":"","line_count":0},"tool_use_id":"canary"}`
   (and `docs/specs/x.md` for allow).
5. Spec §4.3 first sentence (`{event, session_id, tool, input}`) and plan Task 3/5/7 fixture text — correct to the
   §1 schema. Ledger record keys (`"event":"deny"` etc.) are RATCHET's own and stay as they are.

## 7. Still to confirm inside Bob (cannot be done from outside the IDE)

Each is one settings rewrite + one prompt. Re-run 3/4 before the first take and after any `settings.json` edit.

| # | Settings | Prompt in Agent mode | Expected | Record as |
|---|---|---|---|---|
| Smoke 3 | `PreToolUse` → `probe2.cmd`, other four → `probe.cmd` | `Create scratch/blocked.txt containing "x".` | Bob reports the tool blocked; file absent; `probe.log` has the PreToolUse line and **no** PostToolUse line | `bob_sessions/A/smoke-3-4.png` |
| Smoke 4 | `PreToolUse` back to `probe.cmd` | same prompt | file exists | same screenshot |
| Smoke 6b | all `probe.cmd` | `Use a subagent to list every .py file in this workspace.` | a `PreToolUse` line with `"tool_name":"spawn_subagent"` — note its `tool_input` keys | append to §2.1 |
| Smoke 10 | all `probe.cmd` | `Use a subagent to create scratch/sub.txt containing "sub".` | does a `PreToolUse write_file` line appear **for the subagent's write**, and under which `session_id`? If not, hooks have a subagent hole → drop the `subagent` group from every mode | append here |
| Smoke 6c | all `probe.cmd` | `Use insert_content to add a line "two" at line 2 of scratch/hello.txt, then use search_and_replace to change "hello" to "hey" in it.` | two PreToolUse lines confirming both tools use `path` | append to §2.1 |

Settings rewrite for smoke 3 (PowerShell, from `C:\ratchet`):

```powershell
python -c "import json,pathlib; h=lambda c:[{'hooks':[{'type':'command','command':c,'timeout':5}]}]; P=r'C:\ratchet\.bob\hooks\probe.cmd'; P2=r'C:\ratchet\.bob\hooks\probe2.cmd'; p=pathlib.Path.home()/'.bob'/'settings'/'settings.json'; p.write_text(json.dumps({'hooks':{'SessionStart':h(P),'UserPromptSubmit':h(P),'PreToolUse':h(P2),'PostToolUse':h(P),'Stop':h(P)}},indent=2))"
```

Start a new Bob task (new chat) after each rewrite — the `SessionStart` line shows whether the new config loaded.

## 8. Other facts worth keeping

- Approval latency is visible in the log: PreToolUse → PostToolUse took 15 s and 22 s for the two edits (human
  approval), 6 s for the command. The 5 s hook `timeout` applies to the hook process only, not to approval.
- Bob's Agent-mode task ran with `autoApprovalEnabled: true`, `allowed_permissions: ["read"]`, and an
  `execute_command` allow-list (`git status`, `ls`, `grep`, …). `python --version` was not on it and still ran after
  approval — Bob's own allow-list is advisory for the demo; the hook is the control.
- Model tool calls carry `tool_use_id` (`tooluse_…`); Pre and Post share it, so the ledger could pair them.
- `PostToolUse` is skipped for errored tools, so a write that Bob itself failed never reaches `rx.record`; the
  Stop reconciliation against `git status` remains the safety net.

## Sources

- `probe.log` (committed with this file) and `scratch/hello.txt` (final content `hello`; local only — `scratch/` is git-ignored).
- `~/.bob/db/bob.db` — `tasks.env`, `tasks.approval_config`, `messages.data[].availableTools`, `toolUsage.permission`.
- `…\IBM Bob\resources\app\extensions\bob-code\dist\extension.js` — `runHooks` / `HookLifecycle` (payload builders,
  `exec` options, exit-code switch).
- https://bob.ibm.com/docs/ide/changelog (2.0.2 "Command lifecycle hooks"; 2.0.2 "Lifecycle hooks now correctly respect the workspace trust setting"; 2.0.3 latest)
- https://bob.ibm.com/docs/ide/configuration/lifecycle-hooks (documented payload `event`/`session_id`/`tool`/`input` + `output`; exit-code table; "Default timeout: 10 seconds"; "Global hooks always run" — says nothing about trust)
- https://bob.ibm.com/docs/ide/core-concepts/tools (tool names by category)
