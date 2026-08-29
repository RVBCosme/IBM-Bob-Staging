import sys, datetime
from pathlib import Path
raw = sys.stdin.buffer.read().decode("utf-8-sig")
Path(r"C:\ratchet\probe.log").open("a", encoding="utf-8").write(
    datetime.datetime.now().isoformat() + " " + raw.strip() + "\n")
sys.exit(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
