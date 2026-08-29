import json
from rx import ledger

KEY = b"k" * 32


def test_append_chains_and_verifies(tmp_path):
    lp = tmp_path / "ledger.jsonl"
    ledger.append(lp, {"event": "init", "phase": "spec", "run": "r1"}, KEY)
    ledger.append(lp, {"event": "gate", "from": "spec", "to": "red"}, KEY)
    rows = ledger.read(lp)
    assert [r["seq"] for r in rows] == [1, 2]
    assert rows[0]["prev"] == "genesis" and rows[1]["prev"] == rows[0]["mac"]
    ok, msg = ledger.verify(lp, KEY)
    assert ok, msg


def test_byte_flip_fails(tmp_path):
    lp = tmp_path / "ledger.jsonl"
    ledger.append(lp, {"event": "init", "phase": "spec", "run": "r1"}, KEY)
    ledger.append(lp, {"event": "write", "phase": "spec", "path": "docs/specs/a.md"}, KEY)
    lines = lp.read_text().splitlines()
    lines[1] = lines[1].replace("a.md", "b.md")
    lp.write_text("\n".join(lines) + "\n")
    ok, msg = ledger.verify(lp, KEY)
    assert not ok and "line 2" in msg


def test_deleted_record_is_a_seq_gap(tmp_path):
    lp = tmp_path / "ledger.jsonl"
    for i in range(3):
        ledger.append(lp, {"event": "write", "phase": "spec", "path": f"docs/specs/{i}.md"} if i else {"event": "init", "phase": "spec", "run": "r1"}, KEY)
    lines = lp.read_text().splitlines()
    lp.write_text(lines[0] + "\n" + lines[2] + "\n")
    ok, msg = ledger.verify(lp, KEY)
    assert not ok and "line 2" in msg


def test_wrong_key_fails(tmp_path):
    lp = tmp_path / "ledger.jsonl"
    ledger.append(lp, {"event": "init", "phase": "spec", "run": "r1"}, KEY)
    ok, _ = ledger.verify(lp, b"x" * 32)
    assert not ok


def test_illegal_transition_fails(tmp_path):
    lp = tmp_path / "ledger.jsonl"
    ledger.append(lp, {"event": "init", "phase": "spec", "run": "r1"}, KEY)
    ledger.append(lp, {"event": "gate", "from": "spec", "to": "green"}, KEY)
    ok, msg = ledger.verify(lp, KEY)
    assert not ok and "illegal transition" in msg


def test_unrecorded_change_fails(tmp_path):
    lp = tmp_path / "ledger.jsonl"
    ledger.append(lp, {"event": "init", "phase": "spec", "run": "r1"}, KEY)
    ledger.append(lp, {"event": "stop", "phase": "spec", "changed": ["src/x.py"], "unrecorded": ["src/x.py"]}, KEY)
    ok, msg = ledger.verify(lp, KEY)
    assert not ok and "no record" in msg
