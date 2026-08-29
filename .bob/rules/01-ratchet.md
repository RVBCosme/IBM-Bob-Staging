# RATCHET protocol
- This workspace is a RATCHET run. The current phase is in .ratchet/state.json and is announced at session start.
- Only the human opens gates, with `python -m rx gate --to <phase>`. Never ask to switch modes yourself.
- Writes outside the phase directory are refused by the mode's file restriction. Any write that still reaches the hook outside the phase directory, and every terminal command, is blocked by the hook and recorded in the ledger. Do not retry a refused or blocked call; tell the human why you needed it.
- Never edit .ratchet/ or .bob/.
- When the phase's work is done, stop and print the exact gate command the human should run.
