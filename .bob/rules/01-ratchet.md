# RATCHET protocol
- This workspace is a RATCHET run. The current phase is in .ratchet/state.json and is announced at session start.
- Only the human opens gates, with `python -m rx gate --to <phase>`. Never ask to switch modes yourself.
- Writes outside the phase directory and all terminal commands are blocked by a hook and recorded in the ledger. Do not retry a blocked call; tell the human why you needed it.
- Never edit .ratchet/ or .bob/.
- When the phase's work is done, stop and print the exact gate command the human should run.
