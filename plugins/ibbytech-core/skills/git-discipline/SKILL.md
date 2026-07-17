---
name: git-discipline
description: >
  Commit message convention, TWO-COMMIT discipline, pre-merge checklist, release
  tagging, changelog generation, stale branch cleanup, and PR standards. Use
  this skill when committing, landing a PR on main, creating a release,
  reviewing PR quality, or managing repository hygiene in any IbbyTech repo.
user-invocable: true
---

# Git Discipline — Commit Convention, Merge Checklist, and Repository Hygiene

## Purpose

Operational procedures for the full code lifecycle, applicable to any
IbbyTech repository regardless of its specific branch names or service
layout. Defines commit conventions, the TWO-COMMIT discipline, the
pre-merge checklist, tagging, changelogs, and cleanup.

---

## Repository Shape

Every repo in this ecosystem is trunk-based: one default branch (`main` or
`master`) plus short-lived `feature/<name>` or `fix/<name>` branches that
land via pull request. There is no `develop` or other integration branch,
in any repo — do not create one, do not check for one, do not reference one.
This is Git Doctrine v2 (see the foundation repo's
`.claude/rules/04-git-discipline.md`, the canonical source for branch/merge
rules — this skill's procedures must stay identical to it).

---

## TWO-COMMIT Discipline

Every scoped task produces exactly two commits, in this order:

1. **Implementation commit** — the code, configuration, or documentation
   change itself, including any tests or fixtures it needs. Stage only the
   files that realize the scoped change. Review the staged diff before
   committing. Do not push yet.
2. **Evidence-artifact commit** — the report in `outputs/validation/` (plus
   any task specification documents). This commit is followed by push and PR.

Do not collapse these into one commit, and do not split either one further
without a reason tied to genuine separate concerns. This discipline exists
so a reviewer can see "what changed" and "what proves it changed" as
distinct, reviewable units.

---

## Commit Message Convention

Format: `<type>(<scope>): <short description>` (Conventional Commits).

| Type | Use | Type | Use |
|:-----|:----|:-----|:----|
| `feat` | New capability | `deploy` | Deployment config |
| `fix` | Bug or misconfig | `security` | Credential/access |
| `docs` | Docs only | `ops` | Migration/recovery |
| `chore` | Maintenance | | |

**Scopes:** Service or component name relevant to the repo (e.g. a service
directory or module name). Cross-cutting: `infra`, `tools`, `planning`.
Always lowercase, hyphen-separated.

**Forbidden:** `fix`, `update stuff`, `changes`, `WIP`, or descriptions
that restate the type (`fix(chat): fix the chat`).

---

## Pre-Merge Checklist: Landing a PR on main

The most consequential git operation in a trunk-based repo. Updates
production-canonical state. main is protected server-side (PR required,
force-push and deletion blocked per Doctrine v2 Rule 2) — this checklist is
what the agent verifies before presenting the Merge Ready notice and asking
for the human confirmation Doctrine v2 requires.

### Pre-Merge Checklist (all must pass)

1. No known regressions (no open fix-in-progress on this branch)
2. The scoped task is complete (no half-finished work targeting this PR)
3. Planning/tracking docs reflect reality
4. Infrastructure changes have validation evidence recorded
5. `git status` clean on the feature/fix branch
6. Tests pass (if applicable)
7. Project CLAUDE.md reflects current architecture
8. `git diff main...<branch>` contains no leaked credentials

### Procedure

1. Checkout the feature/fix branch, ensure it's pushed
2. `git diff main...<branch> --stat` and `git log main...<branch> --oneline`
3. Present the **Merge Ready Notice** defined in `04-git-discipline.md`
4. Wait for explicit human approval — always treat as a confirm-first action
5. Merge the PR (`gh pr merge` or web UI) — human executes, or agent on
   explicit human instruction only
6. Tag the release if this lands a release (see Release Tagging)
7. Write evidence of the merge (what changed, when, checklist result)

---

## Release Tagging

Tags mark promotion points on `main` (or `master`). Always annotated.

**Format:** `v<YYYY.MM.DD>` (e.g., `v2026.03.19`). Same-day repeat: `v2026.03.19.2`

```bash
git tag -a v2026.03.19 -m "Release 2026-03-19: <one-line summary>"
```

**Rules:**
- Tags only on `main`/`master`, never on feature/fix branches
- Tag creation requires human confirmation before pushing
- Push immediately: `git push origin --tags`
- Never delete or move a pushed tag — treat as irreversible

---

## Changelog Generation

Uses **Keep a Changelog** format. Each repo maintains `CHANGELOG.md` at root.

### Type-to-Section Mapping

| Commit Type | Section |
|:------------|:--------|
| `feat` | Added |
| `fix` | Fixed |
| `docs` | Documentation |
| `chore`, `deploy`, `ops` | Changed |
| `security` | Security |

### Procedure

1. `git log <last-tag>...HEAD --oneline` to collect commits
2. Group by type into sections
3. Write human-readable descriptions where raw messages are unclear
4. Prepend new version block to `CHANGELOG.md`
5. Commit as `docs(changelog): add vYYYY.MM.DD release notes`

---

## README Update Triggers

### Must Update

| Change | Update Required |
|:-------|:---------------|
| New API endpoint | Service doc |
| Env var added/changed | `.env.example` and service doc |
| New platform service consumed | CLAUDE.md service table |
| Port or FQDN change | CLAUDE.md infrastructure section |
| New dependency | Setup/installation docs |
| Breaking behavior change | Migration path documentation |
| New skill or rule | Foundation CLAUDE.md contents list |

Internal refactoring, test-only changes, and cosmetic fixes do not
trigger doc updates.

---

## PR Description Standards

Every PR needs a description. Empty descriptions are a review failure.

### Required Template

```markdown
## Summary
- [1-3 bullet points]

## Changes
- [significant changes, grouped logically]

## Test Plan
- [how validated — manual, automated, evidence reports]

## Notes
- [risks, dependencies, follow-up, limitations]
```

**Title:** Under 70 characters, conventional commit prefix.
**Evidence:** Reference validation reports/output when applicable.
**Cross-repo:** If changes affect another repo, state it explicitly.

---

## Stale Branch Cleanup

### Definition of Stale

All must be true: last commit older than 14 days, fully merged into `main`
(or `master`), no active work declared.

### Workflow

1. Detect: `git branch -r --merged origin/main`
2. Check age: `git log -1 --format="%ci" origin/<branch>`
3. Present candidates with dates and merge status to human
4. Wait for approval
5. For each approved: verify `git log --oneline origin/<branch> ^origin/main`
   is empty, then `git push origin --delete <branch>`
6. Record cleanup evidence (branch name, last-commit date, approval)

**Protected (never delete):** `main`, `master`, any node/service identity
branches, any branch with unmerged commits.

---

## Multi-Repo Coordination

### When Required

- A shared service's API changes and another repo consumes it
- A shared standards/rule change affects multiple projects
- Infrastructure spans more than one repo's service/application tier
- Shared env var or FQDN change

### Procedure

1. Identify all affected repos
2. Change in dependency order (foundation/standards first, then consumers)
3. Each repo gets its own branch, commits, and merge cycle
4. Document cross-repo dependencies in PR descriptions
5. Verify downstream consumers after upstream changes land

### Anti-Patterns

- Changing a shared API without updating the consumer
- Adding a rule without verifying existing projects comply
- Promoting one repo while a dependent has breaking changes pending

---

## Transport Rule

Code moves via **Git push/pull only**. No SCP, SFTP, rsync, or direct copy.
Violation is a hard block: `TRANSPORT_BYPASS`.

---

## Pre-Push Checklist

| # | Check | Command |
|:--|:------|:--------|
| 1 | Clean working tree | `git status` |
| 2 | On correct branch | `git branch --show-current` |
| 3 | Meaningful commits | `git log --oneline -5` |
| 4 | No secrets | `git diff origin/<branch>...HEAD` |
| 5 | Correct remote | Pushing to `origin` |

### Push Zones (risk framing)

- Feature/fix branch push: propose and wait for confirmation, except
  docs/chore commits on the Green Zone paths listed in `04-git-discipline.md`,
  which can proceed autonomously
- Main/master push: never direct — main only changes via a merged PR
- Force push: never

---

## Post-Merge Validation

After any PR merges to main:

1. `git log --oneline -5 <branch>` — confirm merge commit present
2. Check for conflict markers (`<<<<<<<`) in merged files
3. Run tests if the repo has them
4. If infrastructure files changed (compose, env, gateway config), flag for
   deployment verification on the target node

**Conflict resolution:** Stop, report conflicting files, wait for human
guidance. Never auto-resolve by choosing one side blindly.

---

## Never Force-Push

Force push is never performed as part of routine work (see `commit-push-pr`
command). If a push is rejected as non-fast-forward, stop and report —
do not force, do not rebase over shared history without explicit instruction.
