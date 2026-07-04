---
description: Make the SECOND commit of the two-commit discipline (tests/fixtures/docs), push the branch, and open a PR.
argument-hint: [optional PR title override]
---

# Commit, Push, PR (step 2 of 2)

This is the **completion commit** — the second half of the two-commit
discipline from the `git-discipline` skill, followed by push and PR. Load
`git-discipline` and `documentation` if not already in context — this
command applies both.

## Steps

1. Run `git status` and `git diff` to confirm what remains: tests,
   fixtures, and documentation that round out the implementation commit
   already made by `commit`.
2. Re-run the pre-commit security check from `secret-hygiene` (`.env`
   staged, `.env` tracked, literal secret patterns in the diff). Stop and
   report on any hit.
3. Stage the remaining files by name, show the staged diff/summary, and
   commit with a Conventional Commits message (`docs:`, `test:`, or `chore:`
   as appropriate per `git-discipline`'s type table).
4. Run the `git-discipline` pre-push checklist:
   - Clean working tree
   - Correct branch (not `main`/`master` directly, unless this repo uses
     the direct-to-main shape)
   - Meaningful commit history (`git log --oneline -5`)
   - No secrets in `git diff origin/<branch>...HEAD`
   - Pushing to `origin`
5. Push the branch: `git push -u origin <branch>`. **Never force-push.** If
   the push is rejected as non-fast-forward, stop and report — do not
   force, do not rebase over shared history without explicit instruction.
6. Open a PR using the `documentation` skill's PR description template:
   - Title under 70 characters, conventional-commit prefix
   - Summary (why, not just what), Changes, Breaking Changes (if any),
     Test Plan (actionable steps, not "ran tests"), Links
   - Check for a repo PR template first and use its structure if one exists
7. Return the PR URL.

## Hard rules

- Never force-push, never skip hooks, never bypass signing.
- Do not push to `main`/`master` directly unless the repo has no
  integration branch and this is the established direct-to-main shape
  (see `git-discipline`'s Repository Shape section) — and even then, this
  is a propose-and-wait action, not autonomous.
- If a secret is found in the diff at any point, stop and follow
  `secret-hygiene`'s exposed-secret protocol before continuing.
