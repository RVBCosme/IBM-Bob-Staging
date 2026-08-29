"""PostToolUse: record every write. Stop: reconcile git working tree against the ledger.
Audit hooks cannot block (exit 2 has no effect here), so this never returns non-zero."""
import json
import subprocess
import sys
from pathlib import Path

from rx import ledger, policy
from rx.gate import rel_to

IGNORE = (".ratchet/", "bob_sessions/", "probe.log")


def changed_files(root):
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                         cwd=root, capture_output=True, text=True).stdout
    return sorted(l[3:].strip().strip('"') for l in out.splitlines() if l.strip())


def main():
    try:
        root = Path.cwd()
        state_file = root / ".ratchet" / "state.json"
        if not state_file.exists():
            return 0
        state = json.loads(state_file.read_text(encoding="utf-8"))
        lp = root / ".ratchet" / "runs" / state["run"] / "ledger.jsonl"
        p = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
        if p.get("event") == "PostToolUse" and p.get("tool") in policy.WRITE_TOOLS:
            inp = p.get("input") or {}
            raw = next((inp[k] for k in policy.PATH_KEYS if isinstance(inp.get(k), str) and inp[k]), None)
            if raw:
                ledger.append(lp, {"event": "write", "phase": state["phase"], "tool": p["tool"], "path": rel_to(root, raw) or "?"})
        elif p.get("event") == "Stop":
            recorded = {r["path"] for r in ledger.read(lp) if r["event"] == "write"}
            changed = [f for f in changed_files(root) if not f.startswith(IGNORE)]
            ledger.append(lp, {"event": "stop", "phase": state["phase"], "changed": changed,
                               "unrecorded": [f for f in changed if f not in recorded]})
    except BaseException:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
