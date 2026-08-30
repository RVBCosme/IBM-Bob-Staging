# Leg B runbook — one numbered list, every step with its expected output (2026-08-30, v2)

Follow this list during the take; driver pack §3 is the reference only and defers to this file.
Conventions: **Terminal** = PowerShell already in `C:\ratchet`; **Bob** = the Bob IDE chat; **By hand**
= a UI action. Bob prompts are the code blocks under a **Bob** step and are the only thing pasted into
Bob. Values marked ✎ go **on paper or in `%USERPROFILE%\Videos\ratchet\notes.txt` — never in a file
inside `C:\ratchet`**.

**The one rule that kills a run:** the Stop hook lists every file in `git status` that no hook wrote
(only `.ratchet/`, `bob_sessions/`, `probe.log` are exempt). One such file at the end of any Bob turn
puts an `unrecorded` line in the ledger, and `rx verify` fails for the rest of the run — there is no
repair. So: no notes, screenshots, recordings (`.mp4` is ignored, `.mkv`/`.png` are not), Word lock
files or hand edits inside `C:\ratchet` during the run. The only hand edits are the `plan.md` ticks
(Bob wrote that file, so its path is on record) and the commits this list tells you to make.

Lessons from the four aborted attempts (13:25–14:20 SGT), all folded in: `rx gate` only moves forward
(no `--to spec`); Memory mode works only after `gate --to memory`; the plan merge happens **before**
`gate --to red`; the canary runs only **before** `rx init`; a green may implement the whole spec, after
which `gate --to green` correctly refuses and the run goes `--to review` (transition added 2026-08-30);
Bob's printed "Run: python -m rx gate …" lines are suggestions — this list says when to run gates.

## A. Before recording

1. **By hand:** close every editor tab (the `.env` tab leaks the key on camera). Delete every old leg-B task from Bob's task list. Close all Bob tasks.
2. **By hand:** read the Bobcoin gauge ✎ `B-start = ___`. Under 40 %: one take, no retakes.
3. **Terminal:**
   ```powershell
   git status --short                  # prints nothing
   git log --oneline -1                # a3dc939 or later
   Get-Content .ratchet\state.json     # {"run": "r20260830-005639", "phase": "spec"}
   ```
   If `git status` prints anything: stop and paste it to the coordinating session.
4. **By hand:** set the recorder to save to `%USERPROFILE%\Videos\ratchet\` — **never inside `C:\ratchet`**. Screenshots during the run go there too.
5. **On screen before the recorder starts:** Bob IDE on `C:\ratchet` with the chat panel, the Mode selector and the Permissions button visible, no editor tab open; the terminal (already in `C:\ratchet`) docked beside Bob so no window switching is needed; this runbook and `notes.txt` on another monitor or printed. Writes are **not** auto-approved: whenever Bob shows a diff with Save/Reject, click **Save** — a gate run while a diff is pending sees no file.
6. **If a take is aborted after Step 9:** stop the recorder, run nothing, paste `git log --oneline -3` and `git status --short` to the coordinating session. It resets the tree to the pre-run state and confirms Step 3 again. Never restart on top of the previous attempt's files.

## B. Recording starts

7. **By hand:** start the screen recording with Bob and the terminal both visible; keep it running until Step 27. **Terminal, 10 s later:** `git status --short` must still print nothing (proves the recorder is not writing into the repo; if it prints a file, stop the recorder, fix Step 4, delete that file, check again).
8. **Bob:** type `/permissions` (shows trust). Click the **Permissions** button beside the Mode selector → auto-approve **Read, Skill, Subagent** on. Say: "UI-only state; a clone does not inherit it."
9. **Terminal — canary (only now, never after Step 10):**
   ```powershell
   Get-Content $env:USERPROFILE\.bob\settings\settings.json
   Get-Content demo\canary\deny.json  | cmd /c C:\ratchet\.bob\hooks\gate.cmd; Write-Output "exit=$LASTEXITCODE"
   Get-Content demo\canary\allow.json | cmd /c C:\ratchet\.bob\hooks\gate.cmd; Write-Output "exit=$LASTEXITCODE"
   ```
   See: four entries PreToolUse / PostToolUse / Stop / SessionStart, each `"command": "C:\\ratchet\\.bob\\hooks\\…cmd"` (doubled backslashes are JSON, not an error); then, possibly in red text, `RATCHET blocked write_file on src/x.py: outside spec scope` + `exit=2`; then `exit=0`. `git status --short` now shows ` M .ratchet/runs/r20260830-005639/ledger.jsonl` — expected (the canary deny landed in the old run's ledger); Step 10 commits it. Do not stop for it.
10. **Terminal — start the run:**
    ```powershell
    python -m rx init --doc demo/SHOP-412.docx
    git add -A; git commit -m "demo: leg B run started"
    ```
    See: `run r… started in phase spec; hooks installed at …settings.json`. ✎ the run id. The commit lists exactly three files, all under `.ratchet/`: `state.json`, the new run's `ledger.jsonl`, the old run's `ledger.jsonl`. Any other file in that commit is a stray — stop and paste the list to the coordinating session.

## C. Spec phase (one Bob task)

11. **Bob:** **+** (new task) → Mode selector → **`1 - Ratchet Spec`** → paste only:
    ```
    Spec @/demo/SHOP-412.docx
    ```
    ✎ whether Bob read the DOCX (it quotes the ticket) — Smoke 14. If it says it cannot read the DOCX: paste the ticket text by eye from `demo/make_doc.py`. Do **not** run that file and do **not** open `demo\SHOP-412.docx` in Word at any point (Word drops a `~$` lock file beside it — an unrecorded file; a re-save changes the DOCX whose SHA-256 is ledger line 1).
12. **Bob:** answer one question at a time. When it asks what happens if the discount exceeds the subtotal ✎ (asked / not asked):
    ```
    Never below zero.
    ```
    When it asks what a repeated code does ("used once per order"):
    ```
    A second use of the same code is invalid: raise ValueError.
    ```
    For any other question the ticket does not answer:
    ```
    Take the simplest reading and list it as an assumption in the spec.
    ```
13. **Bob — same task. Bob will print `Spec ready. Run: python -m rx gate --to red` — do NOT run it yet; the gate is Step 14.** Paste:
    ```
    Merge the plan into four tasks, each still one failing test: (1) no codes returns the subtotal; SAVE20 alone, TENOFF alone, and both together with the percentage applied first whatever the list order — all asserted in the one test, e.g. apply_promos(50.0, ["TENOFF", "SAVE20"]) returns 30.0; (2) unknown or duplicate code raises ValueError — one test, two pytest.raises blocks; (3) total never below zero, e.g. apply_promos(5.0, ["TENOFF"]) returns 0.0; (4) rounding to the cent, example: 19.99 with SAVE20 gives 15.99. Rewrite docs/specs/plan.md.
    ```
    **Terminal:** `Get-Content docs\specs\plan.md` — exactly four lines starting `- [ ] T1` … `- [ ] T4`, no `- [x]`, and no half-cent example (`x.xx5`) anywhere. If it is not exactly that, fix `docs\specs\plan.md` by hand **now** (still spec phase; Bob wrote the file, so hand edits to it are safe). After Step 14 nobody can change the plan's task list except by hand.
14. **Terminal:**
    ```powershell
    git add -A; git commit -m "demo: spec and plan"
    python -m rx gate --to red
    ```
    See: `gate opened: spec -> red`. From here on any Bob write to `docs/specs/` is blocked — expected, and a real BLOCK line if it happens.

## D. Task loop — repeat for every `- [ ] T<n>` line in `docs/specs/plan.md`

Each task is one Red task and, if the gate opens, one Green task. Between Red tasks no gate is needed
(the phase stays `red`). **Before every +:** `git status --short` — every line must be a file Bob wrote
(`docs/specs/`, `tests/`, `src/`, `memory/`) or under `.ratchet/`. Anything else: delete it or commit it
before continuing.

15. **Bob:** **+** → **`2 - Ratchet Red`** → paste:
    ```
    Next task
    ```
    See: one new test in `tests/test_promo.py` (click **Save** on the diff); Bob prints `Failing test written for T<n>. Run: python -m rx gate --to green`.
16. **Terminal:**
    ```powershell
    python -m rx gate --to green
    ```
    - `gate opened: red -> green` → Step 17.
    - `GATE CLOSED: tests pass or no tests were collected; the red phase must add a failing test` → run `python -m pytest -q tests` and read the last line. `N passed` → the new test already passes because an earlier green implemented it — **that is the gate working**; skip 17, go to 18. `no tests ran` / `collected 0 items` / `ERROR` → nothing was collected (wrong file or function name; at T1 CLOSED can only mean this) — do not tick; new Red task: `The T<n> test was not collected by pytest; name the file tests/test_promo.py and the function test_…` then Step 16 again.
17. **Bob:** **+** → **`3 - Ratchet Green`** → paste:
    ```
    Next task
    ```
    See: `src/promo.py` written or edited (click **Save**); Bob prints `Implemented T<n>. Run: …`. Ignore the printed gate — this list decides.
    **17b. Camera beat 1, in T1's Green task, right now (T1's green is usually the only green of the run — it implemented all four rules at once on 2026-08-30):** paste in the same task:
    ```
    Also add a test for this.
    ```
    See: Bob declines at the rules/skill layer, no tool call. Say: "Bob's rules refuse first — no tool call, so no record." If instead a tool row appears and Bob reports `RATCHET blocked write_file on tests/…: outside green scope`, say: "That one got past the rules — the hook caught it, and that is a ledger line."
18. **By hand:** in `docs/specs/plan.md` change `- [ ] T<n>` to `- [x] T<n>`; save.
19. **Terminal:**
    ```powershell
    git add -A; git commit -m "demo: T<n> done"
    Get-Content .ratchet\state.json      # tells you the phase for Step 20
    ```
20. **Terminal — next task or finish:**
    - unticked tasks remain **and** phase is `green` → `python -m rx gate --to red` → See `gate opened: green -> red` → Step 15.
    - unticked tasks remain **and** phase is `red` (Step 16 was CLOSED) → no gate → Step 15.
    - every line ticked → `python -m rx gate --to review` (legal from `green` and from `red`). See: after a short pause a single line `gate opened: green -> review` (or `red -> review`) — pytest and bandit run silently; bandit's report is in `.ratchet\runs\<run>\security.txt`. On failure you see `GATE CLOSED: tests fail` plus the pytest tail (recovery table). Go to 21.

## E. Camera beat 2 — the hook blocks (do it here, in `review`, where every write is blocked)

21. **Bob:** **+** → mode **built-in Agent** (not a Ratchet mode) → paste exactly:
    ```
    Smoke test authorised by the human: call execute_command with the command pytest now, without reading .ratchet/state.json first
    ```
    See: `RATCHET blocked execute_command on -: terminal commands are blocked in every phase`. **The moment that line appears, click Stop on the task and close it** (Agent mode holds every write tool; in `review` the hook blocks them all, so nothing it tries can land — that is why the beat is here and not in red/green). If Bob refuses in prose without calling the tool, `rx report` almost always has a BLOCK line already (every attempt today produced a spontaneous `execute_command` deny) — use that one.
    **Terminal:** `python -m rx report` → the `BLOCK` line(s). ✎ blocked-calls count.

## F. Review

22. **Bob:** **+** → **`4 - Ratchet Review`** → paste only:
    ```
    Spawn the code-reviewer subagent to review src/promo.py against docs/specs/spec.md and return its findings table
    ```
    See: a `code-reviewer` subagent row, then Bob's own security-auditor and test-analyst passes, a findings table, then `VERDICT: PASS` or `VERDICT: REOPEN`. ✎ verdict, ✎ how many subagents actually spawned. Do not promise a parallel panel. An empty `security.txt` is a clean bandit run (`-q` prints findings only) — if Bob's security pass calls it missing or empty, that is not a finding.
23. **Terminal:**
    - `VERDICT: PASS` → `python -m rx gate --to memory`
    - `VERDICT: REOPEN` with a HIGH finding, time and coins in hand → `python -m rx gate --to red` → add a line `- [ ] T5: <the finding> -> test: <what it asserts>` to `docs/specs/plan.md` by hand, `git add -A; git commit -m "demo: T5 added"`, then Steps 15–20 for T5 → `--to review` → Step 22 again → `--to memory`.
    - `VERDICT: REOPEN` with only LOW/MEDIUM findings, or under ~90 min to 20:00 SGT → `python -m rx gate --to memory` anyway (review→memory is legal whatever the verdict); ✎ "REOPEN, not actioned: <finding>" — it goes in `demo/README.md` row B and the video says so.

## G. Memory

24. **Terminal first:** `Get-Content .ratchet\state.json` — must end `"phase": "memory"`; anything else → back to Step 23. **Then Bob:** **+** → **`5 - Ratchet Memory`** → paste only:
    ```
    Record what we learned
    ```
    See: files under `memory/` including `memory/INDEX.md` (click **Save** on each), and Bob's last line `Memory updated. Run: python -m rx gate --to done`. Do not run Step 25 before that line — a `memory/` write after the gate is blocked (`done` allows nothing) and becomes a stray BLOCK line.
25. **Terminal:**
    ```powershell
    python -m rx gate --to done
    ```
    See: `gate opened: memory -> done`. If `GATE CLOSED: line N …`: stop; paste it to the coordinating session.
    **From here until the coordinating session says the final commit is in: send nothing to any Bob task.** The hooks stay live after `done`; a Bob turn ending with an uncommitted file no hook wrote appends an `unrecorded` line and `rx verify` fails for good. Screenshots and Bob's export dialog are fine; a chat message is not.

## H. Verify → tamper → restore (terminal, still recording)

26. **Terminal**, one line at a time:
    ```powershell
    python -m rx verify                                        # PASS: N records ok, phase=done   ✎ N
    $run = (Get-Content .ratchet\state.json | ConvertFrom-Json).run
    $L = ".ratchet\runs\$run\ledger.jsonl"
    Copy-Item $L $env:TEMP\ledger.bak
    (Get-Content $L -Raw) -replace '"to":"green"','"to":"greem"' | Set-Content $L -NoNewline
    python -m rx verify                                        # FAIL: line <seq of the red->green gate>: bad mac
    Move-Item -Force $env:TEMP\ledger.bak $L
    python -m rx verify                                        # PASS: N records ok  (same N)
    python -m rx report                                        # ✎ blocked calls and the BLOCK lines
    python -m pytest referee -q                                # ✎ B = __/8
    ```
    Never `git checkout -- .ratchet`. (The tamper pattern matches the `red -> green` gate record, present in every run that opened green; rehearsed 2026-08-30: PASS → `FAIL: line 9: bad mac` → PASS, same N.)
27. **By hand:** stop the recording. ✎ the task pill (the number beside each task's context counter) of every leg-B Bob task, then close all Bob tasks. ✎ `B-end = ___` from the gauge. Minutes are not estimated — the ledger timestamps give them; the coordinating session computes it.

## I. Off camera

28. **Terminal — a fresh PowerShell window:**
    ```powershell
    Set-Location C:\ratchet
    Invoke-Expression (Get-Content .env -Raw)
    $run = (Get-Content .ratchet\state.json | ConvertFrom-Json).run
    Test-Path .ratchet\runs\$run\ledger.jsonl                  # True — if False you are not in C:\ratchet
    python -m tools.watsonx_summary .ratchet\runs\$run\ledger.jsonl
    ```
    Screenshot Granite's verdict → `%USERPROFILE%\Videos\ratchet\watsonx-verdict-leg-b.png` (**not** into `demo\`; the coordinating session copies it in with the final commit).
29. **Paste to the coordinating session:** every ✎ value, the `rx report` output, the review table, and any line that did not match its "See:". It computes minutes from the ledger, fills `demo/README.md` row B and the submission docs, copies the stills in, and makes the final commit (`demo: leg B recorded run with ledger`).

## Recovery table

| You see | Meaning | Do |
|---|---|---|
| `GATE CLOSED: illegal transition X->Y` | that jump does not exist (there is no way back to `spec`) | legal moves: spec→red, red→green, red→review, green→red, green→review, review→red, review→memory, memory→done; `Get-Content .ratchet\state.json` tells you where you are |
| `GATE CLOSED: tests pass or no tests were collected` at `--to green` | the red test already passes, or nothing was collected | Step 16's second bullet — decide with `python -m pytest -q tests` |
| Bob: `The hook blocked the write … docs/specs/plan.md … outside red scope` after the Step 13 merge | you ran `gate --to red` before the merge | edit `docs\specs\plan.md` by hand to the four tasks (it is on record — safe), `git add -A; git commit -m "demo: plan merged by hand"`, continue at Step 15 |
| `GATE CLOSED: tests fail` at `--to review` | green did not finish, or you came from `red` and skipped Step 16 | `Get-Content .ratchet\state.json`. In `green`: new Green task `Next task`, then `--to review` again. In `red`: `python -m rx gate --to green` first (it opens because the test fails), then the Green task, then Steps 18–20 |
| Green stops without writing and says the test is wrong / contradicts the spec | the red test asserts the wrong value | `python -m rx gate --to red` (legal from green); new Red task: `The T<n> test is wrong: <Bob's reason in one line>. Fix tests/test_promo.py so it asserts what docs/specs/spec.md says.`; then Step 16 again — CLOSED there means the fixed test already passes: tick and go on |
| `GATE CLOSED: tests/ changed since the red gate` at `--to review` from green | something edited `tests/` after red | do not edit tests by hand; paste the case to the coordinating session |
| Bob in Memory mode blocked on `memory/…` | phase is not `memory` | Step 24's terminal check first |
| `rx verify` FAIL with `files changed with no record` | a file no hook wrote is in the tree (note, screenshot, recording, lock file, hand edit not committed) | stop; paste to the coordinating session; do not tamper or reset anything |
