import json, os, subprocess, sys
from rx import ledger

ENV = dict(os.environ, PYTHONPATH=os.getcwd())


def setup_repo(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".ratchet" / "runs" / "r1").mkdir(parents=True)
    (tmp_path / ".ratchet" / "state.json").write_text(json.dumps({"run": "r1", "phase": "green"}))
    ledger.ensure_key()
    ledger.append(tmp_path / ".ratchet" / "runs" / "r1" / "ledger.jsonl", {"event": "init", "phase": "green", "run": "r1"})


def hook(tmp_path, mod, payload):
    return subprocess.run([sys.executable, "-m", f"rx.{mod}"], input=json.dumps(payload).encode(),
                          cwd=tmp_path, env=ENV, capture_output=True, text=False)


def post(path):
    return {"session_id": "s", "cwd": "c:\\x", "hook_event_name": "PostToolUse", "tool_name": "write_file",
            "tool_input": {"path": path, "content": "", "line_count": 0}, "tool_response": "ok", "tool_use_id": "t"}


def test_post_tool_use_records_write(tmp_path):
    setup_repo(tmp_path)
    r = hook(tmp_path, "record", post("src\\a.py"))
    assert r.returncode == 0
    last = ledger.read(tmp_path / ".ratchet/runs/r1/ledger.jsonl")[-1]
    assert last["event"] == "write" and last["path"] == "src/a.py"


def test_post_tool_use_absolute_path_is_made_relative(tmp_path):
    setup_repo(tmp_path)
    hook(tmp_path, "record", post(str(tmp_path / "src" / "b.py")))
    assert ledger.read(tmp_path / ".ratchet/runs/r1/ledger.jsonl")[-1]["path"] == "src/b.py"


def test_stop_flags_unrecorded_change(tmp_path):
    setup_repo(tmp_path)
    (tmp_path / "src").mkdir(); (tmp_path / "src" / "ghost.py").write_text("x")
    hook(tmp_path, "record", {"session_id": "s", "cwd": "c:\\x", "hook_event_name": "Stop", "last_assistant_message": None})
    last = ledger.read(tmp_path / ".ratchet/runs/r1/ledger.jsonl")[-1]
    assert last["event"] == "stop" and last["unrecorded"] == ["src/ghost.py"]


def test_session_start_prints_state_and_memory(tmp_path):
    setup_repo(tmp_path)
    (tmp_path / "memory").mkdir(); (tmp_path / "memory" / "INDEX.md").write_text("- note one")
    r = hook(tmp_path, "session", {"session_id": "s", "cwd": "c:\\x", "hook_event_name": "SessionStart", "source": "startup"})
    out = r.stdout.decode()
    assert "phase 'green'" in out and "note one" in out
