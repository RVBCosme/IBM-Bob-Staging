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
        print(f"RATCHET run {s['run']} is in phase '{s['phase']}'. Work only inside /ratchet-{s['phase']}; "
              f"writes outside this phase's directory and all terminal commands are blocked and recorded.")
        idx = root / "memory" / "INDEX.md"
        if idx.exists():
            print("\nMEMORY INDEX from previous sessions:\n" + idx.read_text(encoding="utf-8")[:2048])
    except BaseException:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
