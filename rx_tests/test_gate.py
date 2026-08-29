import json
from pathlib import Path
from rx.gate import decide

ROOT = Path("C:/ratchet")

# Verbatim PreToolUse line captured from Bob 2.0.3 (probe.log, 2026-08-29).
REAL = json.loads(
    '{"session_id":"448e42284ee101f74667a92307dfa1be","cwd":"c:\\\\ratchet","hook_event_name":"PreToolUse",'
    '"tool_name":"write_file","tool_input":{"path":"scratch/hello.txt","content":"hi","line_count":1},'
    '"tool_use_id":"tooluse_nlNOJmVQ2Jawzsukwvfk56"}'
)


def w(path, tool="write_file"):
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"path": path, "content": "x"}}


def test_real_bob_payload_is_scoped():
    assert decide(REAL, "green", ROOT) == (False, "outside green scope", "scratch/hello.txt")


def test_documented_keys_still_accepted():
    assert decide({"tool": "write_file", "input": {"path": "tests/a.py"}}, "red", ROOT)[0] is True


def test_read_tools_always_allowed():
    assert decide({"tool_name": "read_file", "tool_input": {"path": "src/x.py"}}, "review", ROOT)[0] is True


def test_in_phase_write_allowed():
    assert decide(w("tests/test_a.py"), "red", ROOT)[0] is True
    assert decide(w("src/a.py"), "green", ROOT)[0] is True


def test_done_phase_blocks_every_write():
    assert decide(w("src/a.py"), "done", ROOT) == (False, "outside done scope", "src/a.py")


def test_out_of_phase_write_denied():
    assert decide(w("src/a.py"), "red", ROOT)[0] is False
    assert decide(w("tests/test_a.py"), "green", ROOT)[0] is False
    assert decide(w("src/a.py"), "review", ROOT)[0] is False


def test_backslashes_and_absolute_paths_normalised():
    assert decide(w("src\\a.py"), "green", ROOT)[0] is True
    assert decide(w("C:\\ratchet\\src\\a.py"), "green", ROOT)[0] is True
    assert decide(w("C:\\elsewhere\\a.py"), "green", ROOT)[0] is False


def test_protected_and_unsafe_paths_denied():
    for p in (".ratchet/state.json", ".bob/custom_modes.yaml", "../x.py", "src/a.py:stream"):
        assert decide(w(p), "green", ROOT)[0] is False, p


def test_terminal_denied_in_every_phase():
    for ph in ("spec", "red", "green", "review", "memory"):
        assert decide({"tool_name": "execute_command", "tool_input": {"command": "echo"}}, ph, ROOT)[0] is False


def test_malformed_denied():
    assert decide({"tool_input": {}}, "green", ROOT)[0] is False
    assert decide(w(None), "green", ROOT)[0] is False
    assert decide(w("src/a.py"), "nonsense", ROOT)[0] is False
