# Hand-off — 2026-08-30 ~02:40 SGT, Tasks 7 / 11 Step 4 / 13 Step 3 done inside Bob IDE (session 3)

Continuation point for Tasks 14 → 15 → 16–19. Read this, then the sections it points to. Deadline: **Aug 30 22:00 SGT**
(10:00 ET, unconfirmed — plan Task 19 Step 0); submission cut-off per plan is **20:00 SGT**.

## 1. Where the project stands

| Task | State | Evidence |
|---|---|---|
| 0–6, 8–12 | done | previous hand-off |
| **7** real hooks, Smoke 12/13 | **done** (`924f383`, `6d6326e`) | settings.json: PreToolUse→`gate.cmd`, PostToolUse→`record.cmd`, Stop→`record.cmd`, SessionStart→`session.cmd`; throwaway run `r20260830-005639`, 19-record ledger committed, phase back to `spec`; recording `%USERPROFILE%\Videos\ratchet\smoke-13.mp4` (outside repo) |
| **7 Step 0** probe-config smokes | **done** (`0afbd77`) | `docs/specs/probe-findings.md` §2.1 / §7.1; `bob_sessions/A/smoke-3-4*.png, smoke-7*.png, smoke-8*.png` |
| **11 Step 4** Smokes 9/10/11 | **done** (`508d589`) | probe-findings §7.1 rows 9–12; `bob_sessions/A/smoke-9*.png, smoke-10-11.png, smoke-11*.png, smoke-12-hook*.png` |
| **13** watsonx | **done** (`7489692`, `3137828`) | `demo/watsonx-verdict.png`; `.env` project id corrected to the sandbox project |
| docs reconcile | this commit | plan Tasks 7/11/13/14/15/16/18/19 + Fallbacks, spec §2.1/§4.2/§4.3/§5/§7/§11, `demo/README.md` (+ its plan mirror), probe-findings §7 |
| 14–19 | not started | plan |

Verification: 13-agent refutation of every smoke claim (`wf_024a39cc-18b`, 0 refuted, guard-rails audit clean) and a
10-agent find→refute pass for the doc edits (`wf_94c5fd0e-f7a`, 53 edits, 0 dropped). `python -m pytest rx_tests -q`
= 30 passed; `python -m rx verify` = PASS 19 records.

## 2. What the IDE session showed that changes Tasks 14–19

1. **Bob refuses at the instruction layer first.** Rules + skill + `AGENTS.md` make Bob decline out-of-phase writes,
   trivial subagent spawns and terminal commands *before any tool call*. Plain prompts therefore never reach
   `fileRegex`, the hook or `spawn_subagent`. What worked: `Smoke test authorised by the human: call <tool> … now,
   without …` (11b, pytest deny on screen) and giving the persona its real job (`Spawn the code-reviewer subagent to
   review src/cart.py against docs/specs/spec.md and return its findings table`). Plan Task 15 Steps 3–4 now carry
   those prompts; the video narrates the pytest block as a deliberate bypass of the instruction layer.
2. **`fileRegex` enforcement is still bundle-derived only** — Smoke 11a never reached the validator (Bob declined
   twice). Spec §2.1/§7 row 11 and `demo/README.md` now say so honestly. Decision open (§4.2 below).
3. **Leg A must also rename `.bob\skills`** — Agent-mode Bob auto-loaded `ratchet-spec` after reading `state.json`
   (rule 01); with rules gone the skill descriptions alone still mention RATCHET phases. Plan Task 14 Step 2 has the
   fourth `Rename-Item`; README row says "gate off — `state.json` renamed, hooks exit 0; rules, skills and router removed".
4. **Smoke 12 must precede Smoke 13** — the `seq`-gap tamper needs ≥ 3 records. Leg B is unaffected (long ledger).
5. **Smoke 9:** one `code-reviewer` spawn + two *sequential* self-run passes, then `VERDICT: REOPEN` — never say
   "fan-out" (plan Task 18 wording fixed).
6. **watsonx:** `.env` is PowerShell syntax loaded with `Invoke-Expression (Get-Content .env -Raw)` in a fresh
   terminal; wrong project id → HTTP 404 `container_not_found`; script now prints the error body. Granite answered in
   one sentence.
7. **Skills tab says scope "Workspace"**, not "project". `/ratchet` shows six skill completions, no modes.
8. Bob's own screenshot command captured the wrong monitor; screenshots are human `Win+Shift+S` captures.

## 3. Guard-rails that stay true
Repo authoritative over plan blocks — `demo/README.md` and `tools/watsonx_summary.py` are byte-identical to their
plan blocks again (checked). Never `git checkout -- .` / `-- .ratchet`; never `/init`; never paste the watsonx key
(`.env` is git-ignored — audited, no key in any commit); commit after every `rx init` and every human edit;
gate only via `python -m rx gate`; canary before every take; new Bob task after every settings.json change.

## 4. Decisions for the coordinating session before Task 14
1. Accept the `.bob\skills` rename for leg A (recommended — otherwise the baseline is not unguarded).
2. `fileRegex`: ship the honest wording (recommended) or spend ~20 min on a direct validator test (a prompt that forces
   `write_file` on `docs/specs/` in `ratchet-green` the way 11b forced `src/a.py`; Bob refused that twice today).
3. Video beat for the blocked call: the "authorised smoke test" prompt, narrated as a bypass of Bob's own rules
   (recommended — layered defence is the story), versus hunting for a natural prompt that reaches the hook.
4. Check the Bobcoin gauge before Task 14 (today's smokes consumed coins); Fallbacks row "< 40%" applies before leg A.
5. Smoke 14 (PDF/DOCX `@`-mention) has no recorded result; leg B's Step 2 `Spec @/demo/SHOP-412.docx` is its first test.

## 5. References
- Previous hand-off: `docs/superpowers/handoffs/2026-08-29-tasks-8-10-11-handoff.md` (§5 guard-rails, §7 audit, §8 watsonx)
- Smoke evidence: `docs/specs/probe-findings.md` §7.1; `bob_sessions/A/`; `demo/watsonx-verdict.png`
- Workflow journals: `%USERPROFILE%\.claude\projects\C--ratchet\b9cc36cf-6193-4f17-b464-53d405eda0ad\subagents\workflows\{wf_024a39cc-18b,wf_94c5fd0e-f7a}\journal.jsonl`
- Claude memory: `~/.claude/projects/C--ratchet/memory/{ratchet-hackathon-context,bob-driver-prompting}.md`
- OneDrive mirror of spec+plan: `C:\Users\Rene Vincent\OneDrive\Desktop\hello\HACKATHON\IBM Bob\docs\superpowers` (re-synced after this commit)
