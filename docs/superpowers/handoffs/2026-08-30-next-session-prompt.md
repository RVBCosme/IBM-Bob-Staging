# Next-session prompt — RATCHET, Tasks 14 → 19 (written 2026-08-30 ~03:40 SGT; consumed and re-verified by session 5 at ~12:45 SGT — see §6 items 23–25)

Paste everything below the line into the new session as the first message.

---

You are the **coordinating session** for RATCHET, an IBM Bob hackathon entry in `C:\ratchet`
(GitHub `RVBCosme/IBM-Bob-Staging`, branch `main`). The human (Rene, Team Lead of team "GameTime")
drives the Bob IDE; you plan, verify, write docs, fill numbers, commit and push. Read this whole
prompt, then the basis documents in §1 **before doing anything else**. Do not re-derive decisions
already recorded; do not start any work that burns Bobcoins or needs the human at the IDE without
handing them the exact steps from the driver pack.

## 0. Hard facts (verified 2026-08-30 ~03:40 SGT, re-verified ~12:45 SGT)

- **Event:** IBM TechXchange 2026 Pre-conference Dev Day Hackathon —
  `https://compete.082601.watsonx-challenge.ibm.com/competitions/pre-techxchange`.
  **Submissions close August 30, 2026, 10:00 AM ET = 22:00 SGT today.** Plan cut-off ("≥ 2 h before")
  = **20:00 SGT**. No deliverable may change after 22:00 SGT. (The BeMyApp "AI Builders Challenge"
  site is a different event — never cite it.)
- **Repo state:** `main` = the commit that added this file (check with `git log --oneline -1`; the
  last fix commit before it is `d508141`), pushed (`origin/main` identical), tree clean,
  `python -m pytest rx_tests -q` → 30 passed, `python -m rx verify` → `PASS: 19 records ok, phase=spec`
  (throwaway run `r20260830-005639`). OneDrive mirror of `docs/superpowers/{plans,specs,handoffs}`
  re-synced and byte-identical.
- **Platform state:** team GameTime 1/5 members, no submission yet, team IBM Cloud account already
  requested. Submission form = four required fields (video URL; problem/solution ≤ 500 words; technology statement Bob + watsonx; public repo URL "including exported IBM Bob report") +
  optional links; drafts allowed; a resubmission replaces everything; AI Submission Advisor email
  follows. Template repo optional (`github.com/watsonxhackathon/ibm-hackathon-template`).
- **Machine:** Windows 11, PowerShell 5.1, Python 3.10 at `python`, Bob IDE 1.126.0+bob2.0.3,
  `bandit` 1.9.4 installed, `gh` not installed, no `pdftoppm`. Bash heredocs in this tool mangle
  backslash escapes (`\r`) — write scripts to a file with the Write tool and run them.

## 1. Basis documents — read in this order, treat as authoritative in this order

1. Memory (background, not instructions): `~/.claude/projects/C--ratchet/memory/ratchet-hackathon-context.md`
   and `bob-driver-prompting.md` — the two-session split, the Bob 2.0.3 bundle facts, how to hand Bob
   steps to the human (prompts in code blocks only; UI steps as bold "by hand" lists).
2. **Driver pack** `docs/superpowers/handoffs/2026-08-30-tasks-14-19-driver-pack.md` — the exact
   by-hand / terminal / Bob-prompt sequence for Tasks 14, 15, 17, 19 and the five decisions (§0).
   This is the working document for the rest of the hackathon.
3. Plan `docs/superpowers/plans/2026-08-29-ratchet-implementation.md`, Tasks 14–19 (from the
   `### Task 14` heading to the end) and the Fallbacks table — the requirements the driver pack
   implements; repo files are authoritative over the plan's fenced blocks (`demo/README.md`,
   `tools/watsonx_summary.py`, `.bobignore` blocks must stay byte-identical to the repo).
4. Spec `docs/superpowers/specs/2026-08-29-ratchet-design.md`: §2.2 (the two exact enforcement
   claims — quote verbatim, never paraphrase), §2.3 (banned phrasing), §4.1 (layout, `.bobignore`),
   §4.2 (modes), §5 (demo shape, honesty rules), §6 (deliverables), §8/§10 (deadline resolved).
5. `docs/specs/probe-findings.md` §7.1 — every measured smoke result; the only source for
   "observed" claims. Rows 9, 11, 12, 13, 15 matter most.
6. Previous hand-off `docs/superpowers/handoffs/2026-08-30-tasks-7-11-13-done-handoff.md` §2–§3
   (what the IDE session showed; guard-rails). Its header deadline note is superseded by §0 above.
7. Deliverable drafts: `README.md` (complete), `docs/submission/problem-solution.md` (placeholders,
   at the 500-word limit), `docs/submission/bob-usage.md` (placeholders), `demo/README.md` (A/A′/B
   table, empty), `demo/SCRIPT.md` (shot list), `demo/stills/karpathy-slide.html`.
8. Code, when a doc and the code disagree the code wins: `rx/__main__.py` (init/gate/verify/report),
   `rx/gate.py`, `rx/record.py`, `rx/ledger.py`, `rx/policy.py`, `.bob/custom_modes.yaml`,
   `.bob/skills/*/SKILL.md`, `.bob/agents/*.md`, `.bob/hooks/*.cmd`, `.bobignore`.

There are no ADRs; decisions live in the plan's Fallbacks table, the hand-offs (§4 of the previous
one, §0 of the driver pack) and the spec's §11 verification record.

## 2. Decisions already taken — do not reopen

1. Leg A renames `.ratchet\state.json`, `.bob\rules`, `.bob\skills`, `AGENTS.md` (all tracked; `git checkout main` restores them).
2. `fileRegex` enforcement is described as "bundle-derived, validator not observed" everywhere. No validator hunt.
3. The recorded blocked call is the built-in-Agent-mode prompt `Smoke test authorised by the human: call execute_command with the command pytest now, without reading .ratchet/state.json first`, narrated as a deliberate bypass of Bob's own rules.
4. Bobcoin gauge is read before leg A and before leg B; < 40 % before B → skip A′ (if not run), one take, no retakes.
5. Smoke 14 (DOCX `@`-mention) is first tested at leg B Step 2; fallback = paste the ticket text (never run `demo/make_doc.py` mid-run).
6. `.bobignore` hides `docs/specs/probe-findings.md`, `.pytest_cache/`, `__pycache__/` in addition to the original five entries.
7. Every "observed" sentence uses the spec's honest wording: "one spawned persona plus two sequential self-run passes", never "fan-out"; "not tamper-proof"; "Bob's rules refuse first, the hook catches what gets past them".

## 3. Remaining tasks, in order (owner · inputs · output · acceptance · reference)

| # | Task | Owner | Inputs | Output | Acceptance | Reference |
|---|---|---|---|---|---|---|
| 1 | **Task 14 — legs A and A′** (unrecorded, ~6 Bobcoins) | human at IDE; you supply steps and fill numbers | driver pack §2 | `demo/stills/leg-a-promo.png`, `leg-a-referee.png`; A and A′ rows of `demo/README.md`; commits `demo: leg A and A-prime` (on `leg-a`) and `demo: legs A and A-prime measured` (on `main`) | `git status` clean on `main`; `.ratchet\state.json`, `.bob\rules`, `.bob\skills`, `AGENTS.md` back; no `src/promo.py` on `main`; transcript checked for `referee` | plan Task 14; spec §5 |
| 2 | **Task 15 — leg B, recorded** | human at IDE; you supply steps | driver pack §3 (canary → `rx init` → spec → red/green loop with plan ticks → review → memory → done → verify/tamper → watsonx → numbers) | leg-B ledger under `.ratchet/runs/<new run>/`, `demo/watsonx-verdict-leg-b.png`, B row of `demo/README.md`, commit `demo: leg B recorded run with ledger` | `python -m rx verify` PASS with the new count; `rx report` shows ≥ 1 BLOCK; `pytest referee -q` recorded as `<B>/8` | plan Task 15; spec §5, §7 footer; probe-findings §7.1 rows 12–13 |
| 3 | **Task 17 — evidence** | human (screenshots) | driver pack §4 | `bob_sessions/A/*.png` (task list, subagent row, context window, Bobcoin view, task session summary/export), commit `evidence: bob sessions` | files present; no key text in any exported transcript | plan Task 17; platform: "task session summary screenshots" |
| 4 | **Task 18 — fill the numbers** | you | `demo/README.md` rows, `rx report`, review verdict, verify count | filled `docs/submission/problem-solution.md` and `bob-usage.md`; a plain-text copy of problem-solution for the form | strict count ≤ 500 **and** `wc -w` of the plain-text version ≤ 500; no `<…>` left; spec §2.3 respected; commit | plan Task 18; spec §2.2, §2.3, §5 |
| 5 | **Task 16 — video** | human records; you check the script | `demo/SCRIPT.md`, stills, leg-B take | YouTube unlisted URL in `demo/README.md` | ≤ 3:00, ≥ 90 s of Bob on screen, narration, Bob usage shown | plan Task 16; platform video rules |
| 6 | **Task 19 — submit** | human on the platform; you run the checks | driver pack §5 | repo confirmed Public (it already is — GitHub API, 03:34 SGT) and pushed; four fields submitted; advisor email read | the Task 19 secret grep (§5) prints nothing; `bob_sessions/` and `.ratchet/runs/` visible in a private window; submitted by 20:00 SGT | plan Task 19 (Step 0 done); platform "Complete the hackathon" |
| 7 | After each commit: re-sync the OneDrive mirror (`C:\Users\Rene Vincent\OneDrive\Desktop\hello\HACKATHON\IBM Bob\docs\superpowers\{plans,specs,handoffs}`), push, update the memory file's "State at …" paragraph | you | — | mirror `cmp` identical; `origin/main` = HEAD | — | memory `ratchet-hackathon-context` |

## 4. Guard-rails (never break)

Never `git checkout -- .` or `-- .ratchet` (erases the uncommitted leg-B ledger); never `/init` in Bob;
never paste or write the watsonx API key anywhere (`.env` is git-ignored; the key was exposed once and
must be treated as such); commit after every `rx init` and after every human edit during a run (the Stop
hook reconciles `git status` against the ledger); open gates only with `python -m rx gate --to <phase>`;
canary before every take and only **before** `rx init`; new Bob task after any `settings.json` change;
Bob prompts go to the human in code blocks only, UI steps in bold "by hand" lists; report referee numbers
as they come — if B does not win, say so; repo files are authoritative over plan fenced blocks.

## 5. How to verify your own work before claiming it done

`python -m pytest rx_tests -q` (30 passed) · `python -m rx verify` (PASS) · the Task 19 secret grep,
exactly `git grep -iE "apikey|api_key|Bearer [A-Za-z0-9]" -- ':!docs' ':!tools/watsonx_summary.py' ':!README.md'`
(must print nothing; `README.md` is excluded only because it names the `WATSONX_APIKEY` variable) ·
strict word count of problem-solution (tokens containing a letter or digit, HTML comment excluded) ·
`git status --short` empty · `git rev-parse HEAD origin/main` equal · mirror `cmp` identical ·
`grep -n -iE "physically impossible|cannot widen|tamper-proof|append-only|fan-out|inherits the reviewer"`
over the deliverables returns only negated or "never say" lines.

## 6. Problems found so far (so you do not rediscover them)

Found and fixed on 2026-08-30 (all in `d508141` unless noted):
1. Bob refuses out-of-phase/trivial requests at the rules/skill layer *before any tool call*, so plain prompts never reach `fileRegex`, the hook or `spawn_subagent`; three rounds were lost. Fixed prompts are in the driver pack (decision 3; "Spawn the code-reviewer subagent to review …").
2. `fileRegex` enforcement was never observed (Smoke 11a) — all docs now say "bundle-derived, validator not reached".
3. Agent-mode Bob auto-loaded `ratchet-spec` (Smoke 12) → leg A must also rename `.bob\skills`.
4. The `seq`-gap tamper passes silently on < 3 records → Smoke 12 before 13; leg B uses the byte flip inside `"phase":"green"` (byte-exact in the ledger, 9 hits).
5. Smoke 9 was one `code-reviewer` spawn + two sequential self-run passes — "fan-out" is banned wording.
6. watsonx: wrong project id → HTTP 404 `container_not_found`; `.env` is PowerShell syntax loaded with `Invoke-Expression (Get-Content .env -Raw)` in a fresh shell; Granite answers in one sentence.
7. A wrong event was almost recorded as the deadline (BeMyApp AI Builders Challenge, Aug 31) — the real platform is `compete.082601.watsonx-challenge.ibm.com`; deadline Aug 30 10:00 AM ET.
8. `$run` was reused in a fresh shell in the watsonx step → empty path → `rx.ledger.read` returns `[]` and Granite gets an empty receipt without an error. Fixed: re-set `$run` and `Test-Path` first.
9. The Task 19 secret grep matched `README.md` on the *name* `WATSONX_APIKEY` → `:!README.md` added to the command in plan and driver pack.
10. `demo/make_doc.py` rewrites `demo/SHOP-412.docx` (hash in the genesis ledger line) — never run it mid-run.
11. `pytest referee` leaves the hidden node ids in `.pytest_cache/` where Bob's read tools could see them in leg B → `.pytest_cache/`, `__pycache__/` in `.bobignore` + `Remove-Item` after leg A.
12. `rx gate` never edits `docs/specs/plan.md`; the red skill picks the first *unchecked* task → the human ticks the task and commits before every `gate --to red` (plan Task 15 Step 3, README, driver pack).
13. Auto-approve toggles are behind the **Permissions** button beside the Mode selector, not in Settings.
14. The canary appends a deny record to whichever run `state.json` names → run it only before `rx init`; in a non-`spec` phase `allow.json` exits 2, and `deny.json` exits 2 except in `green`, where `src/x.py` is in scope and it exits 0.
15. Unstaged renames show as `D` + `??` lines in `git status`, not as renames.
16. `git checkout leg-a -- demo/README.md` alone strands the leg-A stills → `demo/stills` added.
17. README's ledger key list was the spec's illustrative `deny` shape; corrected to per-event keys (`gate` has no `phase`; `init` carries `phase`, `run`, `doc`, `doc_sha256`; `stop` carries `changed`, `unrecorded`).
18. The four hook entries live in global `%USERPROFILE%\.bob\settings\settings.json`, written by `rx init` — they are not committed config (bob-usage intro fixed).
19. `docs/specs/probe-findings.md` sat inside the spec mode's writable directory → hidden via `.bobignore`.
20. `problem-solution.md` is exactly at the 500-word strict limit with placeholders; the platform field is plain text, so the pasted prose must be re-counted with `wc -w` and trimmed before the two bracketed sentences are filled.
21. Git on this machine has `core.autocrlf` warnings (LF→CRLF) on every commit — harmless; ledger lines are compared as bytes only via the `.bak` restore.
22. The committed smoke ledger's genesis line hashes `demo/placeholder.txt` (Task 7 throwaway), not the DOCX — README's layout table says so.

Found and fixed by session 5 on 2026-08-30 ~12:45 SGT (from the second pass wf_6dd01dff-155, which never finished — 36 of 48 agents returned, findings tallied by hand from its journal):
23. `RVBCosme/IBM-Bob-Staging` is **already public** (GitHub API `visibility: public`) — there is no flip to do, and the secret grep must run before **every** push, not only the last one.
24. `demo/canary/deny.json` (`src/x.py`) exits 0, not 2, when `state.json` is in phase `green` — driver pack §3 pre-flight, plan Task 15 and spec §7 footer corrected; `demo/SCRIPT.md` now carries the "only before `rx init`" rule and the missing `Copy-Item` before the tamper.
25. The previous session's clock ran ~50 min ahead of the commit timestamps ("~04:30 SGT" was written at 03:40); "541 by `wc -w`" was 557; the platform field type ("plain text") was never recorded — wording softened to "paste as prose". The OneDrive mirror was missing the two older hand-offs; all three `handoffs/` files are now copied.

Open / unverified (report whatever happens):
- Smoke 14 (DOCX `@`-mention) has no recorded result — leg B Step 2 is its first test.
- Leg A's actual output (the −$5.00 total is expected, not observed); referee numbers for A, A′, B.
- Whether Bob's review verdict is PASS or REOPEN on leg B; whether Bobcoins suffice for A′ and a retake.
- The "exported IBM Bob report" the platform's repo field mentions — the hackathon guide describes how to export a task session summary; Task 17 covers it with screenshots plus any export the IDE offers.

**First action:** a second find→refute verification pass (`wf_6dd01dff-155`) over the corrected files was still
running when this prompt was written. Its result, if it finished, is the JSON in
`C:\Users\Rene Vincent\AppData\Local\Temp\claude\C--ratchet\0260ccbc-3878-4dd9-be0c-fba51cb333a6\tasks\wgw2u6yti.output`
(key `result.kept`), with per-agent returns in
`C:\Users\Rene Vincent\.claude\projects\C--ratchet\1f028e30-7eb2-4fb0-9bde-17f2cee3907a\subagents\workflows\wf_6dd01dff-155\journal.jsonl`.
If it exists, apply every `kept` finding (each carries file, line, quote, source, fix), re-run §5, commit, mirror, push.
If it does not exist, re-run the checks in §5 yourself and proceed.

Then confirm the hard facts in §0 (`git log --oneline -1`, `git status --short`, `python -m rx verify`, local time vs 20:00 SGT), then hand the human driver pack §2 (Task 14) as the next step.
