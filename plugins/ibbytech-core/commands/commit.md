---
description: Make the FIRST commit of the two-commit discipline - stage and commit the implementation change only. Does not push.
argument-hint: [optional scope/context for the commit message]
---

# Commit (step 1 of 2)

This is the **implementation commit** — the first half of the two-commit
discipline defined in the `git-discipline` skill. Load that skill for the
full commit-message convention and discipline rules if it isn't already in
context.

## Steps

1. Run `git status` and `git diff` to see what's changed. Identify which
   changed files are the actual implementation (the scoped code/config
   change) versus tests, fixtures, or docs that belong in the second commit.
2. Run the pre-commit security check from the `secret-hygiene` skill before
   staging anything:
   - Any `.env` files about to be staged?
   - Any `.env` files already tracked?
   - Any literal secret-shaped patterns in the diff?
   Stop and report if any check hits — do not stage past a hit.
3. Stage only the implementation files by name (never `git add -A` or
   `git add .`).
4. Show the staged diff/summary (`git diff --cached --stat` and a brief
   description of the substantive change) to the requester before
   committing.
5. Write a commit message following the `git-discipline` convention:
   `<type>(<scope>): <short description>` — Conventional Commits, lowercase
   hyphenated scope, no filler messages like "fix" or "WIP".
6. Commit. Do **not** push.
7. Run `git status` to confirm the commit landed and show what (if
   anything) remains unstaged for the second commit.

## Hard rules

- Do not push in this command — that happens in `commit-push-pr`.
- Do not bundle tests/fixtures/docs into this commit if the task also
  touches those — save them for the completion commit.
- Never skip hooks (no `--no-verify`) and never amend an existing commit
  unless explicitly asked.
- If a pre-commit check flags a secret, stop and follow the `secret-hygiene`
  skill's exposed-secret protocol rather than committing anyway.
