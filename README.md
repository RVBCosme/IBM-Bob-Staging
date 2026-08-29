# RATCHET

A gated change pipeline for IBM Bob: five phase modes that each hold only the tools their phase
needs, a `PreToolUse` hook that blocks any tool call outside the phase written on disk, and an
HMAC-chained ledger — written by hooks, never by the model — that a script verifies.

*Not an autopilot.* A human opens each gate. Once open, the agent works inside a tool surface it did
not choose, and every transition, allowed write and blocked call is recorded and machine-checked.

## What is enforced, in full

> No RATCHET phase mode holds the `execute`, `mode`, or `subtask` groups — IBM's rule is that
> omitting a group means the mode does not get those tools — and a `PreToolUse` hook installed in
> *global* settings, so no mode change can remove it, exits 2 on every write falling outside
> the phase written on disk — and on every terminal command in every phase — so the block holds
> even when the mode changes underneath it. We do not call this a sandbox: a person at the keyboard
> can still switch modes, edit inline, or roll files back. The Stop reconciliation flags any file
> left changed in the working tree with no write record; a rollback to HEAD, or a human edit of a
> file that already carries a write record, is not detected — say so rather than imply otherwise.

> The ledger is written by Bob's lifecycle hooks and by the human-run gate script — never by the
> model, which holds no terminal in any phase — HMAC-chained with a key that lives outside the
> workspace, sequence-numbered so a deleted or reordered line fails the run instead of passing
> quietly, and reconciled at Stop against the git working tree — the only check that can see a
> record that was never written. Tamper-evident, and gap-evident for deleted or reordered lines,
> against everything the agent can reach; not tamper-proof against a person with a shell.

Two honest footnotes from running it on Bob 2.0.3: Bob's own rules and skills refuse most
out-of-phase requests *before any tool call*, so those leave no record — the hook catches what gets
past them. And each mode's `fileRegex` is enforced by Bob's edit-group validator before the hook
runs (bundle-derived; in our smokes Bob declined at the instruction layer first, so the validator
itself was never observed), so an in-mode out-of-phase write would also leave no deny record.

## 60-second quickstart

Prerequisites: Windows, Python 3.10 on `PATH` as `python` with `pytest` and `bandit`
(`python-docx` only if you regenerate the sample ticket), IBM Bob IDE ≥ 2.0.2 (built and verified
on 1.126.0+bob2.0.3). Clone to a path without spaces, e.g. `C:\ratchet` — the hook wrappers run
under `cmd /c` and `rx init` refuses a path with a space.

1. **Trust the folder.** Open it in Bob and grant workspace trust (`/permissions`). Hooks respect
   trust; a fresh clone silently does nothing until you do this.
2. **Start a run** in a terminal:
   ```powershell
   python -m rx init --doc demo/SHOP-412.docx
   git add -A; git commit -m "run started"
   ```
   This writes the genesis ledger line (with the document's SHA-256), the hook wrappers under
   `.bob/hooks/`, and the four hooks into `%USERPROFILE%\.bob\settings\settings.json`
   (a copy is written to `.bob/settings.example.json`; `--no-install` skips the global write).
   The HMAC key is created at `%USERPROFILE%\.ratchet\key`, outside the workspace.
   Commit after every `rx init` and after every edit you make by hand — the Stop hook reconciles
   `git status` against the ledger, and an uncommitted human change reads as an unrecorded write.
3. **Spec.** Start a new Bob task, pick `1 - Ratchet Spec` from the **mode picker**, prompt
   `Spec @/demo/SHOP-412.docx`, answer its questions. When it stops, open the next gate:
   ```powershell
   python -m rx gate --to red
   ```
4. **Loop.** New Bob task per phase (the `SessionStart` hook announces the phase):
   `2 - Ratchet Red` → `gate --to green` → `3 - Ratchet Green` → tick the finished task in
   `docs/specs/plan.md` by hand and commit (the red skill picks the first *unchecked* task; the
   gate never edits the plan) → `gate --to red` for the next task, or `gate --to review` →
   `4 - Ratchet Review` → `gate --to memory` → `5 - Ratchet Memory` → `gate --to done`.

The `/ratchet-*` completions in the chat box are *skills*, not modes: they load a phase's
instructions into whatever mode is current. Phase entry is the mode picker.

## The five modes (`.bob/custom_modes.yaml`)

No phase mode holds `execute`, `mode`, `subtask`, `mcp` or `workflow`.

| Mode | Tool groups | Honest claim |
|---|---|---|
| `1 - Ratchet Spec` | `read`, `edit` (`^docs[\\/]specs[\\/].*\.md$`), `skill`, `todo` | No terminal; writes only specs |
| `2 - Ratchet Red` | `read`, `edit` (`^tests[\\/].*`), `skill`, `todo` | Writes a failing test and cannot run it |
| `3 - Ratchet Green` | `read`, `edit` (`^src[\\/].*`), `skill`, `todo` | Cannot reach `tests/`, so cannot pass by editing the test |
| `4 - Ratchet Review` | `read`, `subagent`, `skill`, `todo`; `allowedSubagents: [explore, code-reviewer, security-auditor, test-analyst]` | Read-only; the personas in `.bob/agents/` are `groups: [read]` |
| `5 - Ratchet Memory` | `read`, `edit` (`^memory[\\/].*`), `skill`, `todo` | Writes only memory |

## What each gate checks (`python -m rx gate --to <phase>`)

| Transition | Check |
|---|---|
| `spec → red` | transition legal |
| `red → green` | `pytest tests` must **fail** (a passing or empty suite keeps the gate closed); hash of `tests/` recorded |
| `green → red` | transition legal (next task) |
| `green → review` | `pytest tests` must pass; `tests/` unchanged since the red gate; `bandit -r src` runs and its exit code is recorded |
| `review → red` | reopen (the debug path) |
| `review → memory`, `memory → done` | transition legal; `done` additionally requires the ledger to verify |

In every phase the hook blocks terminal commands, writes outside the phase directory, and any write
under `.ratchet/` or `.bob/`. After `done`, every write is blocked until a new `rx init`.

## Where the ledger lives

`.ratchet/runs/<run-id>/ledger.jsonl` — one JSON object per line. Every line carries `seq`, `ts`,
`event` (`init` / `gate` / `write` / `deny` / `stop`), `prev`, `mac`, and every line except `gate`
carries `phase`. Per event: `init` adds `run`, `doc`, `doc_sha256`; `gate` adds `from`, `to` (plus
`tests_exit`, `tests_sha` at `--to green`; `tests_exit`, `security_exit` at `--to review`); `write`
and `deny` add `tool`, `path` (`deny` also `reason`); `stop` adds `changed`, `unrecorded`.
`.ratchet/state.json` holds the current run and phase; the hook reads **that**, not the mode
(Bob's hook payload carries no mode field). `.bobignore` hides the ledger and `referee/` from Bob's
file tools; both are committed to git.

## How to verify

```powershell
python -m rx verify    # PASS: <n> records ok, phase=<phase>   (exit 1 on FAIL, naming the line)
python -m rx report    # gates, recorded writes, and every BLOCK line
```

`verify` asserts: `init` first · every transition legal · no `seq` gaps · chain unbroken · every
MAC matches · no Stop record with unrecorded changes. Flip one byte inside a value — e.g. `"green"`
→ `"greem"` — and run it again to see it fail, naming the line; restore the file and it passes with
the same count.

Optional: `python -m tools.watsonx_summary .ratchet/runs/<run>/ledger.jsonl` sends the run receipt
(gates, blocked calls, write count, security exit) to watsonx.ai `granite-4-h-small` for a
release-readiness verdict. Needs `WATSONX_APIKEY` and `WATSONX_PROJECT_ID` in the environment —
never in a committed file.

## Layout

| Path | What |
|---|---|
| `rx/` | the gate, record, session and ledger code (never edited during a run) |
| `.bob/custom_modes.yaml`, `.bob/skills/`, `.bob/agents/`, `.bob/rules/`, `.bob/hooks/` | the Bob configuration |
| `AGENTS.md` | the workspace router (memory convention, layout) |
| `Karpathy-Guidelines.md` | the behavioural constitution; summarised in `.bob/rules/00-karpathy.md` |
| `demo/` | the SHOP-412 ticket, the A / A′ / B protocol and results (`demo/README.md`), the video script; `demo/placeholder.txt` is the stand-in document of the committed smoke run `r20260830-005639` — that ledger's genesis line hashes it, not the DOCX |
| `referee/` | hidden acceptance tests, SHA-256 committed before any run |
| `bob_sessions/` | Bob task screenshots and evidence |
| `docs/specs/probe-findings.md` | what Bob 2.0.3 actually sends to hooks, and every smoke result |
| `docs/submission/` | problem/solution and Bob-usage statements |
| `THIRD_PARTY_NOTICES.md` | prior art and credits |

## Tests

```powershell
python -m pytest rx_tests -q
```
