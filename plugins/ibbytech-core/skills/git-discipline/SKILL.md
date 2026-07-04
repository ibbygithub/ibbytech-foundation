---
name: git-discipline
description: >
  Commit message convention, TWO-COMMIT discipline, branch promotion, release
  tagging, changelog generation, stale branch cleanup, and PR standards. Use
  this skill when committing, promoting a branch, creating a release,
  reviewing PR quality, or managing repository hygiene in any IbbyTech repo.
user-invocable: true
---

# Git Discipline — Commit Convention, Promotion, and Repository Hygiene

## Purpose

Operational procedures for the full code lifecycle, applicable to any
IbbyTech repository regardless of its specific branch names or service
layout. Defines commit conventions, the TWO-COMMIT discipline, promotion
logic, tagging, changelogs, and cleanup.

---

## Repository Shape (generic)

Repos in this ecosystem generally follow one of two shapes:

| Shape | Default Branch | Integration Branch | Applies to |
|:------|:----------------|:--------------------|:-----------|
| Three-tier | `main` or `master` | `develop` | Application and infrastructure repos with staged rollout |
| Direct | `main` | — | Standards/docs-only repos where changes land on `main` directly (lightweight task or PR) |

Confirm which shape a given repo uses before promoting — check for a
`develop` branch rather than assuming.

---

## TWO-COMMIT Discipline

Every scoped task produces exactly two commits, in this order:

1. **Implementation commit** — the code/config change itself. Stage only
   the files that realize the scoped change. Review the staged diff before
   committing. Do not push yet.
2. **Completion commit** — tests, fixtures, and documentation that round
   out the change (plus anything deferred from commit 1 for review clarity).
   This commit is followed by push and PR.

Do not collapse these into one commit, and do not split either one further
without a reason tied to genuine separate concerns. This discipline exists
so a reviewer can see "what changed" and "what proves/documents it changed"
as distinct, reviewable units.

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

## Branch Promotion: develop to main

The most consequential git operation for three-tier repos. Updates
production-canonical state.

### Pre-Promotion Checklist (all must pass)

1. No known regressions (no open fix-in-progress on develop)
2. All features complete (no half-merged branches targeting this promotion)
3. Planning/tracking docs reflect reality
4. Infrastructure changes have validation evidence recorded
5. `git status` clean on develop
6. Tests pass (if applicable)
7. Project CLAUDE.md reflects current architecture
8. `git diff main...develop` contains no leaked credentials

### Promotion Procedure

1. Checkout `develop`, pull latest
2. `git diff main...develop --stat` and `git log main...develop --oneline`
3. Present **Promotion Ready** notice (below)
4. Wait for explicit human approval — always treat as a confirm-first action
5. `git checkout main && git merge develop --no-ff`
6. Tag the release (see Release Tagging)
7. `git push origin main --tags`
8. Write evidence of the promotion (what changed, when, checklist result)

### Promotion Ready Notice

```
╔══════════════════════════════════════════════════════════════════╗
║  PROMOTION READY — develop → main                               ║
╠══════════════════════════════════════════════════════════════════╣
║  Repo:       <repo-name>                                        ║
║  Commits:    N since last promotion (YYYY-MM-DD to YYYY-MM-DD)  ║
║  Files:      N modified, N added, N deleted                     ║
║  Checklist:  8/8 passed                                         ║
╚══════════════════════════════════════════════════════════════════╝
Key changes:
- [features] / [fixes] / [infrastructure]
Respond "proceed" to promote, or "hold" to pause.
```

---

## Release Tagging

Tags mark promotion points on `main` (or `master`). Always annotated.

**Format:** `v<YYYY.MM.DD>` (e.g., `v2026.03.19`). Same-day repeat: `v2026.03.19.2`

```bash
git tag -a v2026.03.19 -m "Release 2026-03-19: <one-line summary>"
```

**Rules:**
- Tags only on `main`/`master`, never on `develop` or feature branches
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

All must be true: last commit older than 14 days, fully merged into the
integration branch (or `main`/`master`), no active work declared.

### Workflow

1. Detect: `git branch -r --merged origin/develop`
2. Check age: `git log -1 --format="%ci" origin/<branch>`
3. Present candidates with dates and merge status to human
4. Wait for approval
5. For each approved: verify `git log --oneline origin/<branch> ^develop` is
   empty, then `git push origin --delete <branch>`
6. Record cleanup evidence (branch name, last-commit date, approval)

**Protected (never delete):** `main`, `master`, `develop`, any node/service
identity branches, any branch with unmerged commits.

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

- Feature branch push: propose and wait for confirmation
- Integration-branch push (docs/chore on approved paths): can proceed autonomously
- Integration-branch push (code changes): propose and wait
- Main/master push: only after promotion approval
- Force push: never

---

## Post-Merge Validation

After any merge to the integration branch:

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
