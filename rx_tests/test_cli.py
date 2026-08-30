import json, os, subprocess, sys
from pathlib import Path
from rx import ledger

ENV = dict(os.environ, PYTHONPATH=os.getcwd())


def rx(cwd, *args):
    return subprocess.run([sys.executable, "-m", "rx", *args], cwd=cwd, env=ENV, capture_output=True, text=True)


def fresh(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "req.txt").write_text("requirements")
    r = rx(tmp_path, "init", "--doc", "req.txt", "--no-install")
    assert r.returncode == 0, r.stderr
    return tmp_path


def test_init_creates_run_and_state(tmp_path):
    fresh(tmp_path)
    s = json.loads((tmp_path / ".ratchet" / "state.json").read_text())
    assert s["phase"] == "spec"
    rows = ledger.read(tmp_path / ".ratchet" / "runs" / s["run"] / "ledger.jsonl")
    assert rows[0]["event"] == "init" and len(rows[0]["doc_sha256"]) == 64
    for d in ("docs/specs", "tests", "src", "memory"):
        assert (tmp_path / d).is_dir()
    assert (tmp_path / ".bob" / "hooks" / "gate.cmd").read_text().startswith("@echo off")


def test_gate_refuses_green_when_tests_pass(tmp_path):
    fresh(tmp_path)
    (tmp_path / "tests" / "test_ok.py").write_text("def test_ok():\n    assert True\n")
    assert rx(tmp_path, "gate", "--to", "red").returncode == 0
    r = rx(tmp_path, "gate", "--to", "green")
    assert r.returncode != 0 and "failing test" in r.stderr


def test_gate_refuses_green_when_no_tests_collected(tmp_path):
    fresh(tmp_path)
    assert rx(tmp_path, "gate", "--to", "red").returncode == 0
    r = rx(tmp_path, "gate", "--to", "green")  # tests/ is empty: pytest exit 5
    assert r.returncode != 0 and "failing test" in r.stderr


def test_full_happy_path_and_verify(tmp_path):
    fresh(tmp_path)
    assert rx(tmp_path, "gate", "--to", "red").returncode == 0
    (tmp_path / "tests" / "test_x.py").write_text("from src.x import f\n\ndef test_f():\n    assert f() == 1\n")
    assert rx(tmp_path, "gate", "--to", "green").returncode == 0
    (tmp_path / "src" / "__init__.py").write_text("")
    (tmp_path / "src" / "x.py").write_text("def f():\n    return 1\n")
    r = rx(tmp_path, "gate", "--to", "review")
    assert r.returncode == 0, r.stderr
    assert rx(tmp_path, "gate", "--to", "memory").returncode == 0
    assert rx(tmp_path, "gate", "--to", "done").returncode == 0
    v = rx(tmp_path, "verify")
    assert v.returncode == 0 and v.stdout.startswith("PASS")
    assert "gates" in rx(tmp_path, "report").stdout


def test_gate_red_to_review_when_red_test_already_passes(tmp_path):
    """Green over-delivered: the next red test passes on first run, so green cannot open; review can."""
    fresh(tmp_path)
    assert rx(tmp_path, "gate", "--to", "red").returncode == 0
    (tmp_path / "tests" / "test_x.py").write_text("from src.x import f\n\ndef test_f():\n    assert f() == 1\n")
    assert rx(tmp_path, "gate", "--to", "green").returncode == 0
    (tmp_path / "src" / "__init__.py").write_text("")
    (tmp_path / "src" / "x.py").write_text("def f():\n    return 1\n\n\ndef g():\n    return 2\n")  # g() is the next task, done early
    assert rx(tmp_path, "gate", "--to", "red").returncode == 0
    (tmp_path / "tests" / "test_y.py").write_text("from src.x import g\n\ndef test_g():\n    assert g() == 2\n")
    r = rx(tmp_path, "gate", "--to", "green")
    assert r.returncode != 0 and "failing test" in r.stderr
    r = rx(tmp_path, "gate", "--to", "review")
    assert r.returncode == 0, r.stderr
    s = json.loads((tmp_path / ".ratchet" / "state.json").read_text())
    last = ledger.read(tmp_path / ".ratchet" / "runs" / s["run"] / "ledger.jsonl")[-1]
    assert (last["from"], last["to"]) == ("red", "review") and len(last["tests_sha"]) == 64
    assert rx(tmp_path, "gate", "--to", "memory").returncode == 0
    assert rx(tmp_path, "gate", "--to", "done").returncode == 0
    assert rx(tmp_path, "verify").stdout.startswith("PASS")


def test_gate_refuses_review_if_tests_changed_since_red(tmp_path):
    fresh(tmp_path)
    rx(tmp_path, "gate", "--to", "red")
    (tmp_path / "tests" / "test_x.py").write_text("def test_f():\n    assert False\n")
    rx(tmp_path, "gate", "--to", "green")
    (tmp_path / "tests" / "test_x.py").write_text("def test_f():\n    assert True\n")
    r = rx(tmp_path, "gate", "--to", "review")
    assert r.returncode != 0 and "tests/ changed" in r.stderr
