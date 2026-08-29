"""SessionStart: stdout is injected into the model's context. This is the memory FETCH mechanism."""
import json
import sys
from pathlib import Path


def main():
    try:
        root = Path.cwd()
        state_file = root / ".ratchet" / "state.json"
        if not state_file.exists():
            return 0
        s = json.loads(state_file.read_text(encoding="utf-8"))
        if s["phase"] == "done":
            print(f"RATCHET run {s['run']} is done: every write is blocked until a new `python -m rx init`.")
        else:
            print(f"RATCHET run {s['run']} is in phase '{s['phase']}'. Work only in the ratchet-{s['phase']} mode; "
                  f"writes outside this phase's directory are refused by the mode, anything that still reaches "
                  f"the hook outside it and every terminal command is blocked and recorded.")
        idx = root / "memory" / "INDEX.md"
        if idx.exists():
            print("\nMEMORY INDEX from previous sessions:\n" + idx.read_text(encoding="utf-8")[:2048])
    except BaseException:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
