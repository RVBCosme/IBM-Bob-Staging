"""Human-run RATCHET commands. The model never holds a terminal, so it can never run these."""
import argparse
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from rx import ledger

ROOT = Path.cwd()
RX = ROOT / ".ratchet"
STATE = RX / "state.json"
HOOKS = ROOT / ".bob" / "hooks"
TESTS_CMD = [sys.executable, "-m", "pytest", "-q", "tests"]
SEC_CMD = [sys.executable, "-m", "bandit", "-q", "-r", "src"]
CMD = '@echo off\nset "PYTHONPATH={root}"\n"{py}" -m rx.{mod}\nexit /b %ERRORLEVEL%\n'  # text mode adds \r


def state():
    return json.loads(STATE.read_text(encoding="utf-8"))


def save_state(s):
    STATE.write_text(json.dumps(s), encoding="utf-8")


def ledger_path(s):
    return RX / "runs" / s["run"] / "ledger.jsonl"


def sha_tree(d):
    h = hashlib.sha256()
    for p in sorted(Path(d).rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            h.update(p.relative_to(d).as_posix().encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def write_hooks(install):
    HOOKS.mkdir(parents=True, exist_ok=True)
    for mod in ("gate", "record", "session"):
        (HOOKS / f"{mod}.cmd").write_text(CMD.format(root=ROOT, py=sys.executable, mod=mod), encoding="ascii")

    def h(mod, timeout):
        return [{"hooks": [{"type": "command", "command": str(HOOKS / f"{mod}.cmd"), "timeout": timeout}]}]

    hooks = {"PreToolUse": h("gate", 5), "PostToolUse": h("record", 5), "Stop": h("record", 8), "SessionStart": h("session", 5)}
    (ROOT / ".bob" / "settings.example.json").write_text(json.dumps({"hooks": hooks}, indent=2), encoding="utf-8")
    if not install:
        return None
    gs = Path.home() / ".bob" / "settings" / "settings.json"
    gs.parent.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(gs.read_text(encoding="utf-8")) if gs.exists() else {}
    cfg["hooks"] = hooks
    gs.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return gs


def cmd_init(a):
    if not a.no_install and " " in str(ROOT):
        sys.exit("refusing: workspace path contains a space (hook command strings break under cmd /c)")
    ledger.ensure_key()
    for d in ("docs/specs", "tests", "src", "memory"):
        (ROOT / d).mkdir(parents=True, exist_ok=True)
    run = "r" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    s = {"run": run, "phase": "spec"}
    RX.mkdir(exist_ok=True)
    save_state(s)
    doc = Path(a.doc)
    ledger.append(ledger_path(s), {"event": "init", "phase": "spec", "run": run, "doc": doc.as_posix(),
                                   "doc_sha256": hashlib.sha256(doc.read_bytes()).hexdigest()})
    gs = write_hooks(install=not a.no_install)
    print(f"run {run} started in phase spec" + (f"; hooks installed at {gs}" if gs else ""))


def run_tests():
    return subprocess.run(TESTS_CMD, cwd=ROOT, capture_output=True, text=True)


def cmd_gate(a):
    s = state()
    frm, to = s["phase"], a.to
    if (frm, to) not in ledger.TRANSITIONS:
        sys.exit(f"GATE CLOSED: illegal transition {frm}->{to}")
    rec = {"event": "gate", "from": frm, "to": to}
    if to == "green":
        r = run_tests()
        if r.returncode in (0, 5):  # 5 = pytest collected no tests
            sys.exit("GATE CLOSED: tests pass or no tests were collected; the red phase must add a failing test")
        rec["tests_exit"], rec["tests_sha"] = r.returncode, sha_tree(ROOT / "tests")
    if to == "review":
        r = run_tests()
        if r.returncode != 0:
            sys.exit("GATE CLOSED: tests fail\n" + r.stdout[-2000:])
        last_red = [x for x in ledger.read(ledger_path(s)) if x["event"] == "gate" and x["to"] == "green"][-1]
        if sha_tree(ROOT / "tests") != last_red["tests_sha"]:
            sys.exit("GATE CLOSED: tests/ changed since the red gate")
        sec = subprocess.run(SEC_CMD, cwd=ROOT, capture_output=True, text=True)
        (RX / "runs" / s["run"] / "security.txt").write_text(sec.stdout + sec.stderr, encoding="utf-8")
        rec["tests_exit"], rec["security_exit"] = 0, sec.returncode
    if to == "done":
        ok, msg = ledger.verify(ledger_path(s))
        if not ok:
            sys.exit("GATE CLOSED: " + msg)
    ledger.append(ledger_path(s), rec)
    s["phase"] = to
    save_state(s)
    print(f"gate opened: {frm} -> {to}")


def cmd_verify(a):
    ok, msg = ledger.verify(ledger_path(state()))
    print(("PASS: " if ok else "FAIL: ") + msg)
    sys.exit(0 if ok else 1)


def cmd_report(a):
    rows = ledger.read(ledger_path(state()))
    by = lambda e: [r for r in rows if r["event"] == e]
    print(f"run {rows[0]['run']}: {len(by('gate'))} gates, {len(by('write'))} recorded writes, {len(by('deny'))} blocked calls")
    for g in by("gate"):
        print(f"  GATE  {g['from']:>6} -> {g['to']:<6} {g['ts']}")
    for d in by("deny"):
        print(f"  BLOCK [{d['phase']}] {d['tool']} {d['path'] or '-'}: {d['reason']}")


def main():
    ap = argparse.ArgumentParser(prog="rx")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("--doc", required=True); p.add_argument("--no-install", action="store_true"); p.set_defaults(f=cmd_init)
    p = sub.add_parser("gate"); p.add_argument("--to", required=True); p.set_defaults(f=cmd_gate)
    sub.add_parser("verify").set_defaults(f=cmd_verify)
    sub.add_parser("report").set_defaults(f=cmd_report)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
