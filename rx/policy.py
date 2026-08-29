"""RATCHET policy constants. Pin WRITE_TOOLS/EXEC_TOOLS/PATH_KEYS from docs/specs/probe-findings.md."""
WRITE_TOOLS = {"write_file", "apply_diff", "insert_content", "search_and_replace"}
EXEC_TOOLS = {"execute_command"}
PATH_KEYS = ("path",)
PHASE_DIRS = {
    "spec": ("docs/specs/",),
    "red": ("tests/",),
    "green": ("src/",),
    "review": (),
    "memory": ("memory/",),
}
PROTECTED = (".ratchet/", ".bob/")
