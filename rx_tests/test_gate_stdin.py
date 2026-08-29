import json, os, subprocess, sys
from rx import ledger


def run_gate(tmp_path, payload, phase="red"):
    (tmp_path / ".ratchet" / "runs" / "r1").mkdir(parents=True)
    (tmp_path / ".ratchet" / "state.json").write_text(json.dumps({"run": "r1", "phase": phase}))
    env = dict(os.environ, PYTHONPATH=os.getcwd())
    raw = b"" if payload is None else json.dumps(payload).encode()
    return subprocess.run([sys.executable, "-m", "rx.gate"], input=raw,
                          cwd=tmp_path, env=env, capture_output=True)


def test_denied_write_exits_2_and_is_recorded(tmp_path):
    ledger.ensure_key()
    r = run_gate(tmp_path, {"event": "PreToolUse", "tool": "write_file", "input": {"path": "src/a.py", "content": ""}})
    assert r.returncode == 2
    rows = ledger.read(tmp_path / ".ratchet" / "runs" / "r1" / "ledger.jsonl")
    assert rows[-1]["event"] == "deny" and rows[-1]["path"] == "src/a.py"


def test_allowed_write_exits_0(tmp_path):
    r = run_gate(tmp_path, {"event": "PreToolUse", "tool": "write_file", "input": {"path": "tests/t.py", "content": ""}})
    assert r.returncode == 0


def test_empty_stdin_exits_2(tmp_path):
    r = run_gate(tmp_path, None)
    assert r.returncode == 2


def test_non_ratchet_dir_exits_0(tmp_path):
    env = dict(os.environ, PYTHONPATH=os.getcwd())
    r = subprocess.run([sys.executable, "-m", "rx.gate"], input=b"", cwd=tmp_path, env=env, capture_output=True)
    assert r.returncode == 0
