# RATCHET — Design Spec

**Date:** 2026-08-29
**Event:** IBM TechXchange 2026 Pre-conference Dev Day Hackathon
**Team:** 2–3 participants, 40 Bobcoins each
**Target machine:** Windows 11, Python 3.10.11 at `python`, Bob IDE ≥ 2.0.2
**Status:** Approved for planning. Supersedes the "IBM Bob Hackathon Idea.pdf" research report.

> **Provenance note.** This design was verified by two adversarial multi-agent passes (95 agents,
> 8.5M tokens) against all ~124 pages of `bob.ibm.com/docs`. Every enforcement claim below is
> traceable to verbatim IBM documentation or to a live measurement on the target machine.
> Claims that could not be sourced were deleted rather than softened. See §11.

---

## 1. Problem

AI coding agents made *writing* code nearly free, so the bottleneck moved to *trusting* it.
Agents are unreliable narrators: they report success they never verified, skip tests, edit files
outside the agreed scope, and lose context between sessions. Every team adopting them pays the
same tax — a human re-reads everything anyway.

The existing answers are prompts. A prompt **asks** an agent to follow TDD; a confident model
agrees and then doesn't. Nothing checks afterward.

**Target user:** a development team adopting AI agents who cannot merge agent output without a
human re-auditing it line by line.

**Workflow improved:** the change lifecycle — requirements document to reviewed, tested, merged code.

---

## 2. Solution

RATCHET is a set of IBM Bob configuration files that turn a Bob workspace into a gated change
pipeline. Each SDLC phase runs in a custom mode granted only the tool groups that phase needs.
A `PreToolUse` lifecycle hook blocks any tool call that falls outside the phase currently written
on disk. Every gate transition is recorded by hooks — not by the model — into an HMAC-chained,
sequence-numbered ledger that a deterministic non-LLM script verifies.

**Positioning:** *not an autopilot.* A human opens each gate. Once open, the agent works inside a
tool surface it did not choose, and every transition is recorded and machine-checked.

### 2.1 Four layers

| Layer | Mechanism | Sourced IBM wording |
|---|---|---|
| **WITHHOLD** | mode `groups` | *"If you omit groups, the mode does not get any grouped tools"*; *"Unknown group names do not grant access"* |
| **DECLARE** | `fileRegex` on `edit` | *"Restrict which files a mode can edit"* — **stated as intent, never claimed as enforcement** |
| **BLOCK** | `PreToolUse` hook, exit 2 | *"Exit code 2 prevents the tool from running. Bob reports the tool as blocked"* |
| **AUDIT** | HMAC-chained ledger written by hooks + gate script | Records; cannot block (*exit 2 has no effect on `PostToolUse`/`Stop`*) |

### 2.2 The two claims we make, in full

**Enforcement:**
> No RATCHET phase mode holds the `execute`, `mode`, or `subtask` groups — IBM's rule is that
> omitting a group means the mode does not get those tools — and a `PreToolUse` hook installed in
> *global* settings, where folder trust cannot suspend it, exits 2 on every write falling outside
> the phase written on disk — and on every terminal command in every phase — so the block holds
> even when the mode changes underneath it. We do not call this a sandbox: a person at the keyboard
> can still switch modes, edit inline, or roll files back, and the reconciler catches those rather
> than blocking them.

**Ledger integrity:**
> The ledger is written by Bob's lifecycle hooks and by the human-run gate script — never by the
> model, which holds no terminal in any phase — HMAC-chained with a key that lives outside the
> workspace, sequence-numbered so a missing record fails the run instead of passing quietly, and
> reconciled at Stop against the git working tree. Tamper-evident and gap-evident against
> everything the agent can reach; not tamper-proof against a person with a shell.

### 2.3 Banned phrasing

Never say: *"physically impossible"* · *"cannot widen"* · *"tamper-proof"* · *"append-only"*
(say **append-structured, gap-checked**) · *"a subagent inherits the reviewer's read-only surface"* ·
*"deterministic three-reviewer fan-out"* · any implication the ledger blocks anything live.

---

## 3. Differentiation

Close prior art exists and judges may know it:

- `thomassuedbroecker/review_and_sdd_custom_ibm_bob_configuration_template` (Apache-2.0) already
  ships governed Bob modes, skills, `.bobignore`.
- IBM's own tutorial *"Generate secure code with an actor-critic workflow"* already has a Critic
  subagent reviewing with *"no access to the Actor's reasoning."*

**Lead with:** *"IBM's own actor-critic tutorial proves the pattern; we made it auditable."*

Differentiate on the three things neither has:
1. Per-phase write scoping tied to SDLC gates.
2. A `PreToolUse` hook that hard-blocks out-of-phase tool calls, keyed on a phase file rather than
   on mode, so it survives a mode switch.
3. An HMAC-chained, gap-checked ledger verified by a deterministic non-LLM script, reconciled
   against git.

Ship `THIRD_PARTY_NOTICES.md` crediting Superpowers (MIT, Jesse Vincent) as methodology
inspiration, and the two items above as prior art.

---

## 4. Architecture

### 4.1 Repository layout

```
C:\ratchet\                          <- NOT under OneDrive, NO spaces in path
  AGENTS.md                          auto-loaded router; memory conventions INLINED
  .bobignore                         .env, *.key, secrets/, referee/, .ratchet/runs/*/ledger.jsonl
                                     (NOT .ratchet/runs/ - review must read security.txt there)
  .gitignore
  THIRD_PARTY_NOTICES.md
  .bob\
    custom_modes.yaml                5 phase modes
    settings.example.json            reference copy ONLY; rx-init installs the real one globally (see 4.3)
    skills\
      ratchet-spec\SKILL.md
      ratchet-red\SKILL.md
      ratchet-green\SKILL.md
      ratchet-review\SKILL.md
      ratchet-memory\SKILL.md
      ratchet-ui-ux\SKILL.md         secondary skill, loaded by name from spec mode
    agents\
      code-reviewer.md               tools: [read]
      security-auditor.md            tools: [read]
      test-analyst.md                tools: [read]
    rules\
      00-karpathy.md                 always-on behavioural constitution (see 4.8)
      01-ratchet.md                  always-on gate protocol; keep both SHORT
    rules-ratchet-red\01-tdd.md      phase-scoped, keeps per-turn token cost down
    rules-ratchet-green\01-scope.md
    hooks\
      gate.cmd / record.cmd / session.cmd   GENERATED by `python -m rx init` with the
                                            interpreter that ran it - never hand-edited
  rx\                                the whole non-LLM layer, one package, stdlib only
    ledger.py                        HMAC chain: append / read / verify / TRANSITIONS
    policy.py                        the constants: block-listed tools, phase -> allowed dirs
    gate.py                          PreToolUse blocker, FAIL-CLOSED
    record.py                        PostToolUse write records + Stop git reconciliation
    session.py                       SessionStart: injects run state + memory/INDEX.md
    __main__.py                      `python -m rx init|gate|verify|report` (human-run)
  rx_tests\                          RATCHET's own pytest suite (NOT the demo app's tests\)
  .ratchet\
    state.json                       {run, phase} <- the gate reads THIS, humans write it via rx
    runs\<run-id>\ledger.jsonl       committed as evidence
  tools\
    watsonx_summary.py               stdlib urllib only
  docs\specs\                        spec + plan artifacts
  src\  tests\  memory\              created BEFORE first mode use
  referee\                           hidden acceptance tests, published pre-run
  demo\SCRIPT.md
  bob_sessions\                      per-member Bob session evidence
```

### 4.2 The five phase modes

`.bob/custom_modes.yaml`. **No phase mode holds `execute`, `mode`, `subtask`, `mcp`, or `workflow`.**

| # | Slug | groups | Honest claim |
|---|---|---|---|
| 1 | `ratchet-spec` | `read`, `edit`(`^docs[\\/]specs[\\/].*\.md$`), `skill`, `todo` | No terminal; writes only specs |
| 2 | `ratchet-red` | `read`, `edit`(`^tests[\\/].*`), `skill`, `todo` | Writes a failing test and **cannot run it** |
| 3 | `ratchet-green` | `read`, `edit`(`^src[\\/].*`), `skill`, `todo` | Cannot reach `tests/`, so cannot pass by editing the test |
| 4 | `ratchet-review` | `read`, `subagent`, `skill`, `todo`, `allowedSubagents: [explore]` | IBM's read-only Ask surface minus `mcp`/`mode`, plus `todo` |
| 5 | `ratchet-memory` | `read`, `edit`(`^memory[\\/].*`), `skill`, `todo` | Writes only memory |

**Phase 0 (`init`) is not a mode.** A human runs `python -m rx init --doc <requirements>` in a
terminal. It creates the run, writes the genesis ledger line, generates the hook `.cmd` wrappers with
the interpreter that ran it, and installs the global hook config (§4.3). `AGENTS.md` is hand-authored
and committed. If the built-in `/init` is used at all, run it **before** authoring `AGENTS.md`;
running it afterward overwrites the router.

**Regex note:** the patterns in the table are the regexes. In `custom_modes.yaml` they are
double-quoted YAML strings, so every backslash is doubled: `"^src[\\\\/].*"`. One invalid regex
*"can prevent the mode file from loading"* — all five modes vanish silently. Smoke test 8 catches this.

**Phase entry** is the auto-generated mode slash command (`/ratchet-red`), which is documented and
*"cannot be overridden by custom workflow commands."* **Do not create `.bob/commands/*.md` for any
phase** — the mode slug wins and the command file would be dead code.

Each mode's `customInstructions` opens with IBM's own Plan-mode pattern:
`call use_skill with skill_name: "ratchet-<phase>"` — plus a short inline checklist as backstop,
because `use_skill` is strong instruction, not enforcement.

### 4.3 The gate hook

`PreToolUse` stdin, **as measured on Bob IDE 2.0.3** (`probe.log`, 2026-08-29), is
`{session_id, cwd, hook_event_name, tool_name, tool_input, tool_use_id}`; `PostToolUse` adds
`tool_response` (a string). IBM's docs page shows `{event, session_id, tool, input}` — the build
disagrees with the page, so `rx/gate.py` reads the measured keys and accepts the documented ones as
a fallback. **There is no `mode` field**, so the hook physically cannot learn which mode is running.
It therefore reads `.ratchet/state.json`.

**All four hooks** (`PreToolUse` gate, `PostToolUse` record, `Stop` reconcile, `SessionStart`
memory) are installed in **global** `~/.bob/settings/settings.json` by `rx-init` — global hooks
*"always run"* and are *"unaffected by folder trust"*. Every hook has the same cwd guard: no
`.ratchet/state.json` in the working directory → exit 0 immediately, so unrelated projects are never
touched. The workspace `.bob/settings.json` is **not** used — one location, no double-firing.
`.bob/settings.example.json` ships in the repo for judges to read.

```json
{
  "hooks": {
    "PreToolUse":   [ { "hooks": [ { "type": "command", "command": "C:\\ratchet\\.bob\\hooks\\gate.cmd",    "timeout": 5 } ] } ],
    "PostToolUse":  [ { "hooks": [ { "type": "command", "command": "C:\\ratchet\\.bob\\hooks\\record.cmd",  "timeout": 5 } ] } ],
    "Stop":         [ { "hooks": [ { "type": "command", "command": "C:\\ratchet\\.bob\\hooks\\record.cmd",  "timeout": 8 } ] } ],
    "SessionStart": [ { "hooks": [ { "type": "command", "command": "C:\\ratchet\\.bob\\hooks\\session.cmd", "timeout": 5 } ] } ]
  }
}
```

Matcher is **omitted** (matches all tools). The gate classifies by tool name using a **block list**
pinned in `rx/policy.py` after smoke test 6: the write tools (only `write_file` is
documented, with `input.path` carrying the path; `apply_diff`, `insert_content`,
`search_and_replace` are expected) plus `execute_command`. **Tools not on the block list — reads,
searches, todo, skill loads — are always allowed**; a gate that blocked reads would make Bob
unusable. Fail-closed (§4.3 below) applies to malformed payloads and to block-listed tools, not to
unlisted tools.

Phase rules: `spec` → writes allowed only under `docs/specs/`; `red` → `tests/`; `green` → `src/`;
`review` → nothing; `memory` → `memory/`. `execute_command` is blocked in **every** phase, which
also covers a human who switches to the built-in Agent mode mid-run.

`gate.cmd` — generated by `python -m rx init` with the interpreter that ran it, never hand-written
(`record.cmd`/`session.cmd` are identical with `rx.record`/`rx.session`):
```
@echo off
set "PYTHONPATH=C:\ratchet"
"C:\Users\Rene Vincent\AppData\Local\Programs\Python\Python310\python.exe" -m rx.gate
exit /b %ERRORLEVEL%
```

**Non-negotiable invocation rules — all live-measured:**
- Never run `gate.py` as a script. Script mode puts the script's directory on `sys.path`, not the
  workspace, so `from rx import ledger` fails → exit 1 → ignored → the gate fails **open**. Always
  `-m rx.gate` with `PYTHONPATH` at the workspace root.
- Never `sh` (not on PATH; IBM's own example exits 1 → fail-open).
- Never `python3` (resolves to a WindowsApps alias running **3.11.9**, a different interpreter).
- Never forward slashes in the command path (measured: exit 1 vs exit 2).
- Command must be a single space-free token pointing at the `.cmd`; `cmd /c "<exe>" "<script>"`
  returns exit 1 because cmd strips the leading quote.
- Generate `settings.json` with `json.dump`, never hand-typed — a stray `\r`/`\t` parses silently corrupted.
- Decode stdin as `utf-8-sig` (BOM observed).

**`gate.py` fails CLOSED.** Entire body wrapped in `try/except BaseException: sys.exit(2)`.
Blocks on: empty stdin, non-string `tool`, missing path key, any `:` in the path (NTFS ADS /
drive-relative), unresolvable path, unknown phase, unreadable state file. Unconditionally blocks
all writes to `.ratchet/**` and `.bob/**`.

**The gate writes its own DENY record before exiting 2.** `PostToolUse` runs only after a tool
*completes*; a blocked tool never completes, so without this the ledger records only successes and
the blocks — the entire point — are invisible.

### 4.4 The ledger

`.ratchet/runs/<run-id>/ledger.jsonl`, one JSON object per line:

```json
{"seq":7,"ts":"...","run":"r7","phase":"red","event":"deny",
 "tool":"write_file","path":"src/pricing.py","reason":"out-of-phase",
 "prev":"<hmac of line 6>","mac":"<hmac of this line>"}
```

- **HMAC**, key at `%USERPROFILE%\.ratchet\key`, never in the repo. An unkeyed chain proves
  self-consistency, not integrity — a forged 4-line chain was rebuilt in 18 lines of stdlib Python
  and the naive verifier returned OK.
- **Monotonic `seq`** — a hash chain cannot see a record that was *never written* (a crashed
  `PostToolUse` hook exits non-zero, is "logged and ignored", and the chain still verifies clean).
- **Git reconciliation at Stop** — `git status --porcelain --untracked-files=all` against write
  records (untracked files included — agent output is mostly new files); any file changed with no
  record = FAIL.

`python -m rx verify` asserts: init first · every transition legal (spec→red, red→green,
green→red|review, review→red|memory, memory→done) · no `seq` gaps · chain unbroken · every MAC
matches · no Stop record with unrecorded changes. Red re-entry after review is legal (that is the
debug path).

### 4.5 Phase coverage vs. the original request

| Requested | Where it lives |
|---|---|
| Setup | `python -m rx init`, human-run, once |
| Spec | `ratchet-spec` |
| Plan | An **artifact**, not a gate: `docs/specs/plan.md`, written at the spec gate |
| Execution (task-by-task) | `ratchet-red` → `ratchet-green`, one task per cycle |
| TDD | The red/green mode pair *is* the TDD loop |
| Code review | `ratchet-review` + `code-reviewer` persona (our code-review-plugin equivalent). The built-in `/review` is **optional** — it writes nothing to disk and cannot feed the ledger; if used, the gate still blocks its "Fix with Bob" writes during review |
| **Security** | Gate script runs `bandit -r src` at the review gate, output to `.ratchet/runs/<run>/security.txt`; `security-auditor` persona reads it |
| Debug | **Policy, not a gate**: a bug is a missing test → re-enter `ratchet-red` |
| Memory | `ratchet-memory` + `SessionStart` hook injecting `memory/INDEX.md` |
| UI/UX auto-invocation | `ratchet-ui-ux` skill, loaded **by name** from `ratchet-spec`'s `customInstructions` |

Ten requested items collapse to **five** mode slugs, six `SKILL.md` files (five primary + one
secondary), and one human-run initializer.

### 4.6 Memory

`AGENTS.md` must **inline** the memory conventions. Only `AGENTS.md` itself is auto-loaded; nothing
documents that a file it links to gets read. The `SessionStart` hook prints the first ~2 KB of
`memory/INDEX.md` to stdout, which is *"injected as context"* — that is the fetch mechanism.

State this honestly: **Bob has no memory subsystem.** This is a RATCHET convention layered on
Bob's auto-loaded `AGENTS.md`.

### 4.7 watsonx.ai

`tools/watsonx_summary.py` reads the run receipt and returns a release-readiness verdict.

- **stdlib `urllib` only** — `requests` is not installed, and `ibm-watsonx-ai>=1.4` requires
  Python ≥3.11.
- IAM token exchange → `POST https://iam.cloud.ibm.com/identity/token`, `grant_type=urn:ibm:params:oauth:grant-type:apikey`. Token expires in 3600s.
- `POST https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2024-03-14`
  (`/text/generation` is marked legacy). `eu-de` also valid; `granite-4-h-small` is **absent** from
  `eu-gb`/`jp-tok`/`au-syd`/`ca-tor`.
- `model_id: ibm/granite-4-h-small`; `max_completion_tokens` (not deprecated `max_tokens`);
  user content as an **array**.
- API key via env var only. In PowerShell use `curl.exe`, not `curl`.
- Frame as *"our script calls watsonx.ai."* Never *"Bob routes to a model"* — the FAQ says flatly
  *"Can I choose which model Bob uses? — No."*

### 4.8 The Karpathy Guidelines as the behavioural constitution

`Karpathy-Guidelines.md` (in the project root) is summarised to four lines as
`.bob/rules/00-karpathy.md`, injected into every conversation across all modes; the verbatim text
ships as `.bob/skills/ratchet-spec/karpathy.md`. Rules *"cannot be overridden or bypassed by a
custom mode."*

This is not decoration — it is the pitch's spine. RATCHET is the mechanization of those four
principles:

| Karpathy principle | RATCHET gate that enforces it | Proof in the ledger |
|---|---|---|
| **1. Think Before Coding** — state assumptions, ask when unclear | `ratchet-spec`: no code can be written before a spec artifact exists | `spec.approved` precedes any `red` |
| **2. Simplicity First** — minimum code, nothing speculative | `ratchet-green` scoped to `src/`; `code-reviewer` persona checks over-engineering | review verdict |
| **3. Surgical Changes** — every changed line traces to the request | `fileRegex` + gate hook + git reconciliation at Stop | any file changed with no record = FAIL |
| **4. Goal-Driven Execution** — failing test, then make it pass | the `red` → `green` mode pair *is* this loop | every `green` preceded by a `red` |

**Pitch line:** *"Everyone agrees with these guidelines. Nobody can prove they were followed.
RATCHET makes each one a gate with a receipt."*

**Two rules for the rule file:** (a) keep it to the four headings and one line each — rules are
re-billed on every turn; the full text lives in the skill sibling files. (b) The "Simplicity
First" principle also governs *this project's own build*: no abstraction for single-use code, no
configurability that wasn't asked for, and the gate script stays under ~150 lines.

---

## 5. Demo

**Shape:** legs A and A′ are run **once, unrecorded, cheaply** (short prompt, default Agent mode)
purely to produce referee numbers. Only leg B is recorded in full. The video shows B on screen
plus one static table of A / A′ / B. **Not** a live three-leg race — ruled infeasible on budget
and clock.

**Referee:** `referee/` acceptance tests authored and **published (hash committed) before** either
run, hidden from both.

**Seeded ticket:** a real **PDF or DOCX** requirements document (never XLSX — unsupported in
context-mentions), `@`-mentioned by a human, its SHA-256 written into the genesis ledger line.
This is what satisfies the brief's fourth named feature, "document understanding."

**Ticket:** promo codes at checkout, deliberately underspecified on what happens when the discount
exceeds the subtotal. Unguarded Bob ships `total = subtotal - discount` → a $5 cart with `TENOFF`
totals **−$5.00**. The checkout pays the customer. Visually unmistakable in three seconds.

**Legs:** A (unguarded) · A′ (A + the *unguarded repair pass*) · B (RATCHET).
Compare **B against A′**, not against A — B costs more up front and saves the rework. Leading with
that honesty is itself a scoring advantage.

**The one deterministic number the ledger proves:** *N out-of-phase tool calls blocked.*
Everything else is `n=1, single seed, nondeterministic model — an illustration, not a benchmark.`
**If the real numbers do not favour RATCHET, report them.** Fabricated metrics fail
"completeness and feasibility" the moment a judge opens the repo.

**Money shot:** run `rx-verify` on an intact ledger (green), tamper one byte, run again (red,
naming the line). Record this at hour 2 while the ledger is short, not at hour 23.

**Demo hygiene:** grant workspace trust on camera via `/permissions` and narrate it as part of the
governance story — a judge's fresh clone silently does nothing without it. Pre-enable auto-approve
for Skill/Subagent/Read before recording and **say out loud** which prompts were disabled and that
they are UI-only state a clone will not inherit.

---

## 6. Deliverables → artifacts

| Deliverable | Artifact |
|---|---|
| 3-min video (≥90s on-screen) | `demo/SCRIPT.md`, recorded take |
| Problem/solution ≤500 words | §1–§3 of this spec, condensed |
| Bob usage statement | §4 + `bob_sessions/` |
| Public repo | `C:\ratchet` pushed to GitHub |
| Bob task session screenshots | `bob_sessions/<member>/` — **fill as you go, not at the end** |

**Corollary:** every hour of design done outside Bob generates zero Bob session evidence.
Author the `.bob/` config **inside Bob IDE**.

**Hard disqualifier:** credentials in the public repo. `.env`, `*.key`, `secrets/` in **both**
`.gitignore` and `.bobignore`. Scrub exported session markdown before upload — transcripts echo
command lines.

---

## 7. Day-one smoke tests (execution order, do not proceed past a red)

| # | Test | If red |
|---|---|---|
| 0 | Relocate to `C:\ratchet`; `git init`; record absolute 3.10.11 path; create `docs/specs`, `tests`, `src`, `memory` | BLOCKING |
| 1 | Open in Bob, answer **"Yes, I trust the authors"** | Untrusted = all config + hooks suspended, silently |
| 2 | **Does any hook fire?** matcher-less `PostToolUse` probe | **KILL** — fall back to WITHHOLD+DECLARE + human-written ledger |
| 3 | **Does exit 2 block?** | **KILL** — no BLOCK layer |
| 4 | **Does exit 0 allow?** | **KILL — mandatory pair with 3.** One direction alone proves nothing |
| 5 | Failure characterisation: missing script / exception / timeout | Measured: missing script and uncaught exception both exit **1 → fail open**. Assert `gate.cmd` exists + canary returns 2 before every take |
| 6 | **Payload discovery** — exercise every write tool, `execute_command`, `spawn_subagent`; record exact `tool` strings and the path key | Must precede a line of `gate.py`. Commit the log |
| 7 | Do skills load in a **custom** mode? | Fall back to `customInstructions` bodies |
| 8 | Do all five modes load, do `/ratchet-*` appear? | One bad `fileRegex` kills all five silently |
| 9 | `allowedSubagents: [explore]` loads | BRANCH → omit key, drop `subagent` |
| 10 | Do hooks fire for subagent tool calls? | BRANCH → drop `subagent`; do not ship an audit hole |
| 11 | `fileRegex`: enforced or advisory? | Informs DECLARE wording only — the hook carries the claim |
| 12 | Gate end-to-end **both directions** + deny record present | Non-negotiable |
| 13 | Verifier PASS and FAIL (byte flip; deleted record → `seq` gap) | The money shot |
| 14 | PDF `@`-mention returns text | PDF/DOCX only |
| 15 | watsonx: IAM → model specs → one real 200 | Cut the watsonx leg |

Re-run 3, 4, 12 immediately before the first take and after **any** `settings.json` edit.

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| Hook layer fails open, silently | Fail-closed `gate.py`; canary self-test; smoke tests 2–5 |
| Bob build < 2.0.2 (no hooks) | Check first; no documented version UI — budget 45 min |
| Workspace trust suspends everything | Step zero of README and demo |
| Bobcoin exhaustion (no published rate) | Meter after phase 1, extrapolate; scripts/referee/video built outside Bob |
| OneDrive corrupts the chain | Repo at `C:\ratchet`, outside OneDrive |
| Bob declines to spawn subagents | *"Bob uses subagents sparingly"* — say "in our run, three", never a concurrency number |
| Prior-art overlap | §3 framing + `THIRD_PARTY_NOTICES.md` |
| Deadline uncertainty | Portal text says Aug 30 10:00 ET; public listings conflict — **confirm on BeMyApp** |

---

## 9. Out of scope

watsonx Orchestrate Developer Edition (8 cores / 16 GB / Docker — zero judging points for the
cost) · MCP servers · Bob Shell · any dependency on the unreleased `workflow` authoring API ·
porting Superpowers files verbatim.

---

## 10. Open items for the user

1. **Confirm the real deadline and the repository-template URL on the BeMyApp platform.**
   `github.com/IBM/ibm-hackathon-template` returns 404.
2. Confirm the installed Bob IDE version is ≥ 2.0.2 on all machines.
3. Confirm who on the team can mint an IBM Cloud API key and obtain a `project_id`.
4. Confirm the demo stack is Python + pytest.

## 11. Verification record

- Pass 1 — 55 agents, 4.5M tokens, 1,267 tool calls: platform facts + hackathon constraints.
  Found 4 FATAL issues in the original design.
- Pass 2 — 40 agents, 4.0M tokens, 957 tool calls: verbatim schema extraction + 8 red-team attacks,
  each adjudicated by 3 independent lenses. All 8 attacks succeeded against the pre-correction design.
- Retained artifacts: exact `.bob/settings.json` hook schema, all five stdin payload schemas,
  IBM's path-blocking example, live Windows exit-code measurements, live watsonx model catalogue.
