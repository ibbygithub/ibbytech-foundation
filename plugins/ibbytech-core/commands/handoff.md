---
description: Write a terse next-session handoff note to outputs/work-log/YYYY-MM-DD-HH-MM-summary.md.
argument-hint: [optional one-line note about what to emphasize]
---

# Handoff

Write a next-session handoff note. This is the manual companion to the
`handoff_writer` Stop hook — use it any time a session ends and the hook
either isn't configured for this repo or the requester wants an explicit
write now.

## Steps

1. Determine the current timestamp for the filename. Get it from the
   system rather than guessing:
   `date +"%Y-%m-%d-%H-%M"` (or the PowerShell equivalent
   `Get-Date -Format "yyyy-MM-dd-HH-mm"` on Windows).
2. Confirm/create the target directory `outputs/work-log/` at the repo
   root (create it if it doesn't exist).
3. Write `outputs/work-log/<timestamp>-summary.md` using the structure
   below. Keep it terse and factual — one page, no filler. This uses the
   same shape as the agent handoff format in the `team-orchestrator` skill.

## Note structure

```markdown
# Session Handoff — <YYYY-MM-DD HH:MM>

## What was done
- [Concrete, completed items — not intentions]

## Files changed
- [path]: [what changed, one line]
- [path]: [what changed, one line]

## Decisions made
- [Any decision that constrains future work, and why]

## Open items / not done
- [Anything scoped but not completed, and why it stopped there]

## Next session start point
- [The concrete next step — specific enough that the next session doesn't
  need to re-derive context: which file, which function, which test to
  run first]
```

## Hard rules

- Terse: this is a scan-in-30-seconds document, not a narrative.
- Factual only — no marketing language, no "seamlessly," no unverified
  claims. If something is uncertain, say so explicitly rather than
  smoothing over it.
- Do not include secret values, credentials, or tokens in the note.
- Do not commit the note as part of this command — writing the file is the
  full scope of this command. Use `commit` / `commit-push-pr` separately if
  the note should be committed.
