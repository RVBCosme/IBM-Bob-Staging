"""PreToolUse hook. Exit 2 = Bob refuses the tool call. Any failure is also exit 2 (fail closed)."""
import json
import sys
from pathlib import Path

from rx import ledger, policy


def rel_to(root, path):
    """Workspace-relative POSIX path, or None if the path escapes the workspace."""
    p = Path(path)
    try:
        return p.resolve().relative_to(root.resolve()).as_posix() if p.is_absolute() else p.as_posix()
    except ValueError:
        return None


def decide(payload, phase, root):
    """Return (allow, reason, rel_path)."""
    tool = payload.get("tool")
    if not isinstance(tool, str):
        return False, "malformed payload", ""
    if tool in policy.EXEC_TOOLS:
        return False, "terminal commands are blocked in every phase", ""
    if tool not in policy.WRITE_TOOLS:
        return True, "not a write tool", ""
    inp = payload.get("input") or {}
    path = next((inp[k] for k in policy.PATH_KEYS if isinstance(inp.get(k), str)), None)
    if not path:
        return False, "no path in payload", ""
    rel = rel_to(root, path)
    if rel is None:
        return False, "outside workspace", path
    if ":" in rel or ".." in rel.split("/"):
        return False, "unsafe path", rel
    if rel.startswith(policy.PROTECTED):
        return False, "protected path", rel
    allowed = policy.PHASE_DIRS.get(phase)
    if allowed is None:
        return False, f"unknown phase {phase!r}", rel
    if any(rel.startswith(a) for a in allowed):
        return True, "in phase scope", rel
    return False, f"outside {phase} scope", rel


def main():
    try:
        root = Path.cwd()
        state_file = root / ".ratchet" / "state.json"
        if not state_file.exists():
            return 0  # not a RATCHET workspace: never interfere
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
        state = json.loads(state_file.read_text(encoding="utf-8"))
        allow, reason, rel = decide(payload, state["phase"], root)
        if allow:
            return 0
        ledger.append(root / ".ratchet" / "runs" / state["run"] / "ledger.jsonl",
                      {"event": "deny", "phase": state["phase"], "tool": payload.get("tool"),
                       "path": rel, "reason": reason})
        print(f"RATCHET blocked {payload.get('tool')} on {rel or '-'}: {reason}", file=sys.stderr)
        return 2
    except BaseException:
        return 2


if __name__ == "__main__":
    sys.exit(main())
