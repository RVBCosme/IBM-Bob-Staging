from pathlib import Path
from rx.gate import decide

ROOT = Path("C:/ratchet")


def w(path, tool="write_file"):
    return {"event": "PreToolUse", "tool": tool, "input": {"path": path, "content": "x"}}


def test_read_tools_always_allowed():
    assert decide({"tool": "read_file", "input": {"path": "src/x.py"}}, "review", ROOT)[0] is True


def test_in_phase_write_allowed():
    assert decide(w("tests/test_a.py"), "red", ROOT)[0] is True
    assert decide(w("src/a.py"), "green", ROOT)[0] is True


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
        assert decide({"tool": "execute_command", "input": {"command": "echo"}}, ph, ROOT)[0] is False


def test_malformed_denied():
    assert decide({"input": {}}, "green", ROOT)[0] is False
    assert decide(w(None), "green", ROOT)[0] is False
    assert decide(w("src/a.py"), "nonsense", ROOT)[0] is False
