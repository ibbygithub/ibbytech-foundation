---
description: Kick off a scoped task with a required observable completion condition, then hand it to the planner agent.
argument-hint: <task description + completion condition>
---

# Goal

Kick off a scoped piece of work.

## Step 1 — Require an observable completion condition

Look at the invocation (`$ARGUMENTS`). It must state, or clearly imply, a
concrete, observable condition that marks the task done — something you
could check without asking the requester's opinion. Examples of observable
conditions: a specific test passes, a command returns a specific status
code, a row count matches an expected value, a page renders without a
console error, a file exists with expected content.

- If the invocation already states one: restate it back in one line so it's
  pinned down, then proceed to Step 2.
- If the invocation does **not** state one: STOP. Do not proceed, and do not
  guess one on the requester's behalf. Ask directly, e.g.:
  > "Before I scope this — what's the observable condition that tells us
  > it's done? (a test passing, a specific output, a status check, etc.)"

Do not hand anything to the planner agent until a completion condition is
stated in the conversation.

## Step 2 — Hand off to the planner agent

Once the completion condition is pinned down, spawn the `planner` agent
with a self-contained prompt that includes:
- The task description as given
- The exact completion condition from Step 1
- Any constraints already known (which repo, which files are off-limits,
  which conventions apply — check for a project CLAUDE.md first)

The planner is read-only and produces a scoped implementation spec ending
in that same completion condition — it does not write code. Its output is
the spec that `implementer` will later execute exactly.

## Notes

- Do not expand scope beyond what's stated. If the request is genuinely
  ambiguous beyond the completion condition, let the planner surface that
  ambiguity rather than resolving it here.
- This command only starts the task — it does not commit, push, or open a
  PR. Use the `commit` and `commit-push-pr` commands for that once
  implementation is done.
