"""Append-structured, HMAC-chained run ledger. Written only by hooks and by `python -m rx`."""
import datetime
import hashlib
import hmac
import json
import os
from pathlib import Path

KEY_PATH = Path.home() / ".ratchet" / "key"

# Legal phase transitions. review->red is the debug path: a bug is a missing test.
TRANSITIONS = {
    ("spec", "red"), ("red", "green"), ("green", "red"), ("green", "review"),
    ("review", "red"), ("review", "memory"), ("memory", "done"),
}


def ensure_key():
    if not KEY_PATH.exists():
        KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        KEY_PATH.write_text(os.urandom(32).hex())
    return load_key()


def load_key():
    return bytes.fromhex(KEY_PATH.read_text().strip())


def _mac(key, rec):
    body = {k: v for k, v in rec.items() if k != "mac"}
    canon = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(key, canon, hashlib.sha256).hexdigest()


def read(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def append(path, rec, key=None):
    key = key or load_key()
    rows = read(path)
    rec = dict(rec)
    rec["ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    rec["seq"] = rows[-1]["seq"] + 1 if rows else 1
    rec["prev"] = rows[-1]["mac"] if rows else "genesis"
    rec["mac"] = _mac(key, rec)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
    return rec


def verify(path, key=None):
    """Return (ok, message). Deterministic; no model involved."""
    key = key or load_key()
    rows = read(path)
    if not rows:
        return False, "empty ledger"
    if rows[0].get("event") != "init":
        return False, "line 1: first record must be init"
    phase, prev = rows[0]["phase"], "genesis"
    for i, r in enumerate(rows, 1):
        if r.get("seq") != i:
            return False, f"line {i}: seq gap (got {r.get('seq')})"
        if r.get("prev") != prev:
            return False, f"line {i}: broken chain"
        if not hmac.compare_digest(r.get("mac", ""), _mac(key, r)):
            return False, f"line {i}: bad mac"
        if r["event"] == "gate":
            if r["from"] != phase or (r["from"], r["to"]) not in TRANSITIONS:
                return False, f"line {i}: illegal transition {r['from']}->{r['to']} (phase was {phase})"
            phase = r["to"]
        if r["event"] == "stop" and r.get("unrecorded"):
            return False, f"line {i}: files changed with no record: {r['unrecorded']}"
        prev = r["mac"]
    return True, f"{len(rows)} records ok, phase={phase}"
